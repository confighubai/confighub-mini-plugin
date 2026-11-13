#!/usr/bin/env python3
"""Checks the format of every walkthrough in examples/walkthroughs/, and that
the folder's index lists each file and only files that are there.

    python3 .github/tools/lint-walkthroughs.py [FOLDER]
    python3 .github/tools/lint-walkthroughs.py --self-test

A walkthrough starts with a header block, then one title, then three sections
in order: Human (numbered steps, each command block marked <!-- run: STEP -->),
Agent, and Testing (an <!-- agent-task --> with a > quoted request, at least
one <!-- agent-check: COMMAND -->, a line starting "This proves: ", and at
most two <!-- next-step: NAME | OFFER --> lines, each in that form; a page
with none is warned about). Figures from test runs belong only in Testing.

    <!-- walkthrough
    id: starter-web            # the file name without .md
    starts_with: mini          # plugin | mini | both
    starter: web               # or story: "20. ...", or neither for a tool
    needs: [cub mini package]
    budget_seconds: 120
    -->

--self-test plants a fault in a copy of a passing walkthrough for each rule,
and fails unless the lint finds every one.
"""
from pathlib import Path
import re
import sys
import tempfile

SECTIONS = ["Human", "Agent", "Testing"]
MAX_LINES = 180
STEPS = (5, 10)
STARTS_WITH = {"plugin", "mini", "both"}
STARTER_TASKS = ["deploy", "update", "undo", "delete", "move"]
NAME = re.compile(r"^(starter-[a-z0-9-]+|story-\d\d-[a-z0-9-]+|tool-[a-z0-9-]+)\.md$")
NEVER_TOOLS = {"pkill", "killall", "kill", "sudo", "rm", "su", "doas", "launchctl", "shutdown", "reboot"}
# A walkthrough points only at this repository and public sites: never at
# another repository of this organization, or at run records kept elsewhere.
OUTSIDE = [
    (re.compile(r"github\.com/confighubai/(?!confighub-mini-plugin\b)[A-Za-z0-9_.-]+"), "links another confighubai repository"),
    (re.compile(r"stories/runs"), "points at run records kept outside this repository"),
]

HEADER = re.compile(r"\A<!-- walkthrough\n(.*?)\n-->\n", re.S)
MARK = re.compile(r"^<!-- run: ([a-z0-9-]+)((?: [a-z-]+)*) -->$")
TASK = re.compile(r"^<!-- agent-task(?:: ([a-z0-9-]+)(?: after=([a-z0-9-]+))?)? -->$")
PERSON = re.compile(r"^<!-- agent-person ([a-z0-9-]+): (.+) -->$")
TOOLS = re.compile(r"^<!-- agent-tools: ([^>]+) -->$")
CHECK = re.compile(r"^<!-- agent-check(-a)?(?: ([a-z0-9-]+))?: (.+) -->$")
NEXT_STEP = re.compile(r'^<!-- next-step(?: when "([^"]+)")?: ([^|]+?) \| ([^|]+?) -->$')
RESULTS_BEGIN, RESULTS_END = "<!-- results:begin -->", "<!-- results:end -->"
FIGURE = re.compile(r"\b\d+ of \d+ (?:checks|runs|persons|people|arms)\b|\b\d+/\d+ checks\b|\bpilot\b|\bsimulated persons?\b|"
                    r"\bmedian\b|\bconversion\b|\bchecks passed\b|\btried \d+ times\b|\bin[- ]the[- ]way\b", re.I)
INDEX_LINK = re.compile(r"\]\(([^)#\s]+\.md)\)")


def header(text):
    m = HEADER.match(text)
    if not m:
        return None
    out = {}
    for raw in m.group(1).split("\n"):
        line = re.sub(r"\s+#.*$", "", raw).strip()
        if not line:
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            value = [v.strip().strip('"') for v in value[1:-1].split(",") if v.strip()]
        elif len(value) > 1 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        elif re.fullmatch(r"\d+", value):
            value = int(value)
        out[key.strip()] = value
    return out


def lines_outside_code(text):
    fenced = False
    for line in text.split("\n"):
        if line.strip().startswith("```"):
            fenced = not fenced
            yield line, True
            continue
        yield line, fenced


def sections(text):
    return [l[3:].strip() for l, code in lines_outside_code(text) if not code and l.startswith("## ")]


def section(text, name):
    out, inside = [], False
    for l, code in lines_outside_code(text):
        if not code and l.startswith("## "):
            inside = l[3:].strip() == name
            continue
        if inside:
            out.append(l)
    return "\n".join(out)


def marked_steps(text):
    """Each <!-- run: STEP --> marker, which must be followed by a ```sh block."""
    lines, out = text.split("\n"), []
    for i, l in enumerate(lines):
        m = MARK.match(l.strip())
        if not m:
            continue
        j = i + 1
        while j < len(lines) and not lines[j].strip().startswith("```"):
            j += 1
        if j >= len(lines) or lines[j].strip() != "```sh":
            raise ValueError(f"the step {m.group(1)} is not followed by a ```sh block")
        k = j + 1
        while k < len(lines) and lines[k].strip() != "```":
            k += 1
        out.append({"step": m.group(1), "flags": m.group(2).split(), "commands": "\n".join(lines[j + 1:k])})
    return out


def task_list(text):
    lines, out = text.split("\n"), []
    for i, l in enumerate(lines):
        m = TASK.match(l.strip())
        if not m:
            continue
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        quoted = []
        while j < len(lines) and lines[j].lstrip().startswith(">"):
            quoted.append(lines[j].lstrip()[1:].strip())
            j += 1
        out.append({"name": m.group(1) or "task", "request": " ".join(q for q in quoted if q), "after": m.group(2)})
    return out


def numbered_steps(text):
    n, inside = 0, False
    for l, code in lines_outside_code(section(text, "Human")):
        if code:
            continue
        if l.startswith("### "):
            inside = l[4:].strip() == "Steps"
        elif inside and re.match(r"^\d+\. ", l):
            n += 1
    return n


def figures_outside_testing(text):
    out, where = [], None
    for l, code in lines_outside_code(text):
        if not code and l.startswith("## "):
            where = l[3:].strip()
        if where != "Testing" and not code and FIGURE.search(re.sub(r"<!--.*?-->", "", l)):
            out.append(l.strip())
    return out


def lint(path):
    """What is wrong with one walkthrough: [problem], empty when nothing."""
    path = Path(path)
    text = path.read_text()
    bad = []
    if not NAME.match(path.name):
        bad.append(f"the file name {path.name} is not starter-NAME.md, story-NN-SLUG.md or tool-NAME.md")
    h = header(text)
    if h is None:
        bad.append("the file does not start with the <!-- walkthrough ... --> header block")
        h = {}
    else:
        if h.get("id") != path.stem:
            bad.append(f"header id is {h.get('id')!r}, not the file name without .md, {path.stem!r}")
        if h.get("starts_with") not in STARTS_WITH:
            bad.append(f"header starts_with is {h.get('starts_with')!r}, not one of plugin, mini, both")
        if not isinstance(h.get("budget_seconds"), int) or h["budget_seconds"] <= 0:
            bad.append("header budget_seconds is not a whole number of seconds")
        if "needs" not in h:
            bad.append("header has no needs line")
        if path.name.startswith("starter-") and not h.get("starter"):
            bad.append("a starter's walkthrough has no starter line in its header")
        if path.name.startswith("story-") and not h.get("story"):
            bad.append("a story's walkthrough has no story line in its header")
    titles = [l for l, code in lines_outside_code(text) if not code and l.startswith("# ")]
    if len(titles) != 1:
        bad.append(f"{len(titles)} level-one titles; want one")
    if sections(text) != SECTIONS:
        bad.append(f"the sections are {sections(text)}; want exactly {SECTIONS}, in that order")
    n = len(re.sub(re.escape(RESULTS_BEGIN) + r".*?" + re.escape(RESULTS_END), "", text, flags=re.S).rstrip("\n").split("\n"))
    if n > MAX_LINES:
        bad.append(f"{n} lines; the limit is {MAX_LINES}")
    k = numbered_steps(text)
    if not STEPS[0] <= k <= STEPS[1]:
        bad.append(f"{k} numbered steps under Human's ### Steps; want {STEPS[0]} to {STEPS[1]}")
    try:
        marked = marked_steps(text)
    except ValueError as e:
        marked = []
        bad.append(f"a marked step cannot be read: {e}")
    if not marked:
        bad.append("no command block is marked <!-- run: STEP -->")
    elif len({s["step"] for s in marked}) != len(marked):
        bad.append("a step name is used twice")
    tasks = task_list(text)
    names = {t["name"] for t in tasks}
    checks = [m for m in map(CHECK.match, (l.strip() for l in text.split("\n"))) if m]
    if not tasks:
        bad.append("no <!-- agent-task --> with a > quoted request")
    for t in tasks:
        if not t["request"]:
            bad.append(f"agent-task {t['name']} has no > quoted request after it")
        if t["after"] and t["after"] not in {s["step"] for s in marked}:
            bad.append(f"agent-task {t['name']} starts after={t['after']}, which is no marked step")
    if not [c for c in checks if not c.group(1)]:
        bad.append("no <!-- agent-check: COMMAND -->")
    for c in checks:
        if c.group(2) and c.group(2) not in names:
            bad.append(f"agent-check names task {c.group(2)}, which no agent-task declares")
    for m in map(PERSON.match, (l.strip() for l in text.split("\n"))):
        if m and m.group(1) not in names:
            bad.append(f"agent-person names task {m.group(1)}, which no agent-task declares")
    for s in marked:
        if "sign-in" in s["flags"]:
            for l in s["commands"].split("\n"):
                m = re.match(r"\s*([A-Za-z_][A-Za-z0-9_]*)=", l)
                if m:
                    bad.append(f"the sign-in step sets {m.group(1)} without export")
    for m in map(TOOLS.match, (l.strip() for l in text.split("\n"))):
        if m:
            never = sorted(set(m.group(1).split()) & NEVER_TOOLS)
            if never:
                bad.append(f"agent-tools names {', '.join(never)}, which no agent run may use")
    if path.name.startswith("starter-"):
        missing = [x for x in STARTER_TASKS if x not in names]
        if missing:
            bad.append(f"a starter's walkthrough has no agent-task for {', '.join(missing)}")
    if not re.search(r"(?m)^This proves: \S", section(text, "Testing")):
        bad.append('the Testing section has no line starting "This proves: "')
    for l in text.split("\n"):
        if l.strip().startswith("<!-- next-step") and not NEXT_STEP.match(l.strip()):
            bad.append(f"a next-step line is not <!-- next-step[ when \"TEXT\"]: SHORT NAME | OFFER -->: {l.strip()[:80]}")
    if len([1 for l in text.split("\n") if NEXT_STEP.match(l.strip())]) > 2:
        bad.append("more than two next-step lines")
    if text.count(RESULTS_BEGIN) != text.count(RESULTS_END) or text.count(RESULTS_BEGIN) > 1:
        bad.append("the results block needs one results:begin and one results:end marker")
    elif RESULTS_BEGIN in text and RESULTS_BEGIN not in section(text, "Testing"):
        bad.append("the results block is outside the Testing section")
    for l in figures_outside_testing(text):
        bad.append(f"a figure outside the Testing section: {l[:80]}")
    for pat, why in OUTSIDE:
        if pat.search(text):
            bad.append(f"the page {why}")
    return bad


def lint_index(folder):
    folder = Path(folder)
    index = folder / "README.md"
    if not index.exists():
        return [f"{folder} has no README.md, the index"]
    linked = set()
    for line in index.read_text().split("\n"):
        if line.startswith("|"):
            linked.update(m for m in INDEX_LINK.findall(line) if "/" not in m)
    files = {p.name for p in folder.glob("*.md") if p.name != "README.md"}
    return ([f"{f} is not on a row of the index" for f in sorted(files - linked)]
            + [f"the index has a row for {f}, which is not in the folder" for f in sorted(linked - files)])


def lint_folder(folder):
    folder = Path(folder)
    problems = [f"README.md: {p}" for p in lint_index(folder)]
    for f in sorted(folder.glob("*.md")):
        if f.name != "README.md":
            problems += [f"{f.name}: {p}" for p in lint(f)]
    return problems


# Each planted fault: a name, and a change to a passing story walkthrough.
FAULTS = [
    ("no header", lambda t: HEADER.sub("", t, count=1)),
    ("sections out of order", lambda t: t.replace("\n## Agent\n", "\n## Agent-renamed\n", 1)),
    ("no agent-task", lambda t: re.sub(r"(?m)^<!-- agent-task.*-->$", "", t)),
    ("no agent-check", lambda t: re.sub(r"(?m)^<!-- agent-check(?!-a).*-->$", "", t)),
    ("no This proves", lambda t: t.replace("This proves: ", "It proves: ")),
    ("a bad next-step line", lambda t: t.replace("\n## Testing\n", "\n## Testing\n\n<!-- next-step: no offer -->\n", 1)),
    ("a figure outside Testing", lambda t: t.replace("\n## Agent\n", "\n## Agent\n\nIn the pilot, 3 of 4 runs passed.\n", 1)),
    ("another repository named", lambda t: t.replace("\n## Agent\n", "\n## Agent\n\nSee https://github.com/confighubai/other-repo.\n", 1)),
]


def self_test(folder):
    folder = Path(folder)
    good = next((f for f in sorted(folder.glob("story-*.md")) if not lint(f)), None)
    if good is None:
        print("self-test: no passing story walkthrough to plant faults in")
        return 1
    failed = 0
    with tempfile.TemporaryDirectory() as d:
        copy = Path(d) / good.name
        for name, plant in FAULTS:
            changed = plant(good.read_text())
            copy.write_text(changed)
            found = lint(copy)
            if changed == good.read_text() or not found:
                print(f"self-test: the planted fault '{name}' was not found")
                failed += 1
        index = Path(d) / "README.md"
        index.write_text(f"| [x]({good.name}) |\n| [y](missing.md) |\n")
        if not lint_index(d):
            print("self-test: an index row for a missing file was not found")
            failed += 1
    print(f"self-test: {len(FAULTS) + 1 - failed} of {len(FAULTS) + 1} planted faults found, in a copy of {good.name}")
    return 1 if failed else 0


if __name__ == "__main__":
    args = sys.argv[1:]
    folder = Path("examples/walkthroughs")
    if args and args[0] == "--self-test":
        sys.exit(self_test(args[1] if len(args) > 1 else folder))
    folder = Path(args[0]) if args else folder
    problems = lint_folder(folder)
    for p in problems:
        print(p)
    for f in sorted(folder.glob("*.md")):
        if f.name != "README.md" and not any(NEXT_STEP.match(l.strip()) for l in f.read_text().split("\n")):
            print(f"{f.name}: warning: no <!-- next-step: NAME | OFFER --> line says which next step the page aims for")
    print(f"{len(problems)} problems in {len([f for f in folder.glob('*.md')])} files")
    sys.exit(1 if problems else 0)
