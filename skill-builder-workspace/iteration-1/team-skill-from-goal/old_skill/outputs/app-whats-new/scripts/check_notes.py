#!/usr/bin/env python3
"""Check a release-notes.md file against the store rules.

Usage: python3 check_notes.py release-notes.md [--hotfix]

Checks the "## iOS" and "## Android" sections:
  - both present, each non-empty
  - each 500 characters or less (the text that gets pasted into the store,
    newlines included, leading and trailing blank lines ignored)
  - no PR or ticket numbers (#123, ABC-123, "PR 123")
  - no "crash" wording (we say "stability improvements")
  - no markdown formatting, since the stores show it as raw characters
  - with --hotfix: each section is exactly "Bug fixes and performance improvements."

Prints one line per section with its character count, then one FAIL line per
problem. Exits 1 if anything fails, otherwise 0. Standard library only.
"""

import re
import sys
from pathlib import Path

LIMIT = 500
HOTFIX_TEXT = "Bug fixes and performance improvements."
SECTIONS = ("iOS", "Android")
CHECKS = [
    (re.compile(r"#\d+"), "PR or issue number"),
    (re.compile(r"\b[A-Z][A-Z0-9]+-\d+\b"), "ticket number"),
    (re.compile(r"\b(PR|pull request|ticket|issue)\s*#?\d+", re.I), "PR or ticket number"),
    (re.compile(r"\bcrash\w*", re.I), '"crash" wording (use "stability improvements")'),
    (re.compile(r"\*\*|__|`|\[[^\]]*\]\([^)]*\)|^#+\s|^\s*[-*+]\s", re.M), "markdown formatting"),
]


def read_sections(text):
    sections, current, buf = {}, None, []
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buf).strip("\n").strip()
            current, buf = m.group(1), []
        elif current is not None:
            buf.append(line.rstrip())
    if current is not None:
        sections[current] = "\n".join(buf).strip("\n").strip()
    return sections


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    hotfix = "--hotfix" in argv
    if len(args) != 1:
        print(__doc__.strip().splitlines()[2])
        return 2
    path = Path(args[0])
    if not path.is_file():
        print(f"FAIL: {path} not found")
        return 1

    sections = read_sections(path.read_text(encoding="utf-8"))
    failures = []
    for name in SECTIONS:
        if name not in sections:
            failures.append(f'missing section "## {name}"')
            continue
        body = sections[name]
        count = len(body)
        print(f"{name}: {count}/{LIMIT} characters")
        if not body:
            failures.append(f"{name}: section is empty")
        if count > LIMIT:
            failures.append(f"{name}: {count} characters, {count - LIMIT} over the limit")
        for pattern, label in CHECKS:
            found = sorted({m.group(0).strip() for m in pattern.finditer(body)})
            if found:
                failures.append(f"{name}: {label}: " + ", ".join(f'"{x}"' for x in found))
        if hotfix and body != HOTFIX_TEXT:
            failures.append(f'{name}: a hotfix section must be exactly "{HOTFIX_TEXT}"')

    extra = [s for s in sections if s not in SECTIONS]
    if extra:
        failures.append("unexpected sections: " + ", ".join(extra))

    for f in failures:
        print("FAIL: " + f)
    if not failures:
        print("PASS")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
