#!/usr/bin/env python3
"""Writes the plugin repository's llms.txt from its docs/README.md and its
walkthroughs index, so that the two never list different pages.

    scripts/llms-txt.py --write PLUGIN_CHECKOUT

What comes before the first "## " heading of the current llms.txt is kept as
it is: the title, the summary and what to read first. Everything after it is
made here: every walkthrough, then each section of docs/README.md with its
pages, each as a raw URL an agent can fetch. --write replaces llms.txt only
once the new file is made; without it, the file is printed. Do not redirect
the output into llms.txt: the shell empties the file before it is read, and
the preamble with it. A llms.txt with no title before its first section is
refused rather than written without one. the release checks
that the file matches, when PUBLIC_DOCS names the checkout.
"""
import os
import re
import sys
import tempfile

RAW = "https://raw.githubusercontent.com/confighubai/confighub-mini-plugin/main/"
LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def url(base_dir, target):
    if re.match(r"^[a-z]+:", target):
        return target
    path, _, frag = target.partition("#")
    full = os.path.normpath(os.path.join(base_dir, path))
    return RAW + full + ("#" + frag if frag else "")


def links(base_dir, text):
    """Text with each relative link made a raw URL."""
    return LINK.sub(lambda m: f"[{m.group(1)}]({url(base_dir, m.group(2))})", text)


def rows(text):
    """Each table row with a link in its first cell: (title, target, description)."""
    for line in text.split("\n"):
        if not line.startswith("| ") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        m = LINK.fullmatch(cells[0]) if cells else None
        if m and len(cells) > 1:
            yield m.group(1), m.group(2), cells[1]


def sections(text):
    """docs/README.md's "## " sections that hold a table of pages."""
    parts = re.split(r"(?m)^## (.+)$", text)
    for i in range(1, len(parts), 2):
        found = list(rows(parts[i + 1]))
        if found:
            yield parts[i].strip(), found


def main(root):
    current = open(os.path.join(root, "llms.txt"), encoding="utf-8").read()
    head = re.split(r"(?m)^## ", current, maxsplit=1)[0].rstrip("\n")
    if not head.startswith("# "):
        raise SystemExit(f"{os.path.join(root, 'llms.txt')} has no title before its first section; "
                         "restore it (git checkout llms.txt) and run scripts/llms-txt.py --write again")
    out = [head, ""]

    index = open(os.path.join(root, "examples/walkthroughs/README.md"), encoding="utf-8").read()
    out.append("## Walkthroughs")
    out.append("")
    for title, target, what in rows(index):
        title = re.sub(r"`", "", title)
        out.append(f"- [{title}]({url('examples/walkthroughs', target)}): {links('examples/walkthroughs', what)}")
    out.append("")

    docs = open(os.path.join(root, "docs/README.md"), encoding="utf-8").read()
    for name, pages in sections(docs):
        out.append(f"## {name}")
        out.append("")
        for title, target, what in pages:
            title = re.sub(r"`", "", title)
            out.append(f"- [{title}]({url('docs', target)}): {links('docs', what)}")
        out.append("")
    out.append("## Optional")
    out.append("")
    out.append(f"- [README]({RAW}README.md): what ConfigHub and the plugin are, installing the plugin, a first try, and the slash commands")
    out.append(f"- [Documentation index]({RAW}docs/README.md): every page, grouped by what you are doing, and the glossary of the words they use")
    out.append(f"- [Words]({RAW}docs/README.md#words): hub, base, copy, change order, Space and every other word the pages use, each defined once")
    return "\n".join(out) + "\n"


def write(root):
    """Replace llms.txt with what main makes, in one rename, so that a failure
    leaves the old file as it was."""
    text = main(root)
    target = os.path.join(root, "llms.txt")
    fd, tmp = tempfile.mkstemp(prefix=".llms.txt.", dir=root)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.chmod(tmp, os.stat(target).st_mode & 0o777)
        os.replace(tmp, target)
    except BaseException:
        os.unlink(tmp)
        raise


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--write"] and len(args) == 2:
        write(args[1])
    elif len(args) == 1 and not args[0].startswith("-"):
        sys.stdout.write(main(args[0]))
    else:
        raise SystemExit("usage: scripts/llms-txt.py [--write] PLUGIN_CHECKOUT")
