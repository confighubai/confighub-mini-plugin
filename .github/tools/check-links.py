#!/usr/bin/env python3
"""Checks every link between this repository's pages: that each relative link,
and each link to this repository on GitHub, reaches a file, and that its
#anchor is a heading (or an id) in that file.

    python3 .github/tools/check-links.py [ROOT]

Links to other sites are not fetched. Code blocks and inline code are skipped.
"""
import os
import re
import sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
REPO = os.environ.get("GITHUB_REPOSITORY", "confighubai/confighub-mini-plugin")
SELF = [f"https://raw.githubusercontent.com/{REPO}/main/", f"https://github.com/{REPO}/blob/main/", f"https://github.com/{REPO}/tree/main/"]
SKIP = {".git", "node_modules"}


def slug(heading):
    """GitHub's anchor for a heading."""
    h = heading.strip().lower()
    h = re.sub(r"<[^>]+>", "", h)
    h = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", h)
    h = h.replace("`", "")
    return "".join(c for c in h if c.isalnum() or c in "-_ ").replace(" ", "-")


_anchors = {}


def anchors(path):
    if path not in _anchors:
        text = open(path, encoding="utf-8", errors="replace").read()
        found = set()
        if path.endswith(".md"):
            seen, fenced = {}, False
            for line in text.split("\n"):
                if re.match(r"^\s*(```|~~~)", line):
                    fenced = not fenced
                    continue
                m = None if fenced else re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
                if m:
                    s = slug(m.group(2))
                    n = seen.get(s, 0)
                    seen[s] = n + 1
                    found.add(s if n == 0 else f"{s}-{n}")
        found.update(re.findall(r'\b(?:id|name)="([^"]+)"', text))
        _anchors[path] = found
    return _anchors[path]


LINK = re.compile(r"(?<!!)\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)|!\[[^\]]*\]\(\s*([^)\s]+)\s*\)|^\[[^\]]+\]:\s*(\S+)", re.M)
HREF = re.compile(r'\b(?:href|src)="([^"]+)"')


def targets(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    if path.endswith(".html"):
        return HREF.findall(text)
    text = re.sub(r"(?ms)^\s*```.*?^\s*```", "", text)
    text = re.sub(r"`[^`\n]*`", "", text)
    return [m.group(1) or m.group(2) or m.group(3) for m in LINK.finditer(text)]


def broken(root):
    files = []
    for d, dirs, names in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP]
        files += [os.path.join(d, n) for n in names if n.endswith((".md", ".html")) or n == "llms.txt"]
    out = []
    for f in sorted(files):
        for t in targets(f):
            ours = next((p for p in SELF if t.startswith(p)), None)
            if not ours and (re.match(r"^[a-z][a-z0-9+.-]*:", t) or t.startswith("//")):
                continue
            rel = t[len(ours):] if ours else t
            path, _, frag = rel.partition("#")
            path = path.split("?")[0]
            if ours or path.startswith("/"):
                target = os.path.join(root, path.lstrip("/"))
            elif path:
                target = os.path.normpath(os.path.join(os.path.dirname(f), path))
            else:
                target = f
            where = os.path.relpath(f, root)
            if not os.path.exists(target):
                out.append(f"{where}: {t}: no such file")
            elif frag and target.endswith((".md", ".html")) and frag not in anchors(target) and not re.fullmatch(r"L\d+(-L\d+)?", frag):
                out.append(f"{where}: {t}: no heading for #{frag}")
    return out, len(files)


if __name__ == "__main__":
    problems, n = broken(ROOT)
    for p in problems:
        print(p)
    print(f"{len(problems)} broken links in {n} pages")
    sys.exit(1 if problems else 0)
