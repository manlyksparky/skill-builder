#!/usr/bin/env python3
"""Check a release-notes.md file against the store "What's new" rules.

Usage:
    python3 check_notes.py release-notes.md            # normal release
    python3 check_notes.py release-notes.md --hotfix   # hotfix release

Checks:
- The file has exactly two sections, "## iOS" then "## Android", and nothing
  above the first heading.
- Each section's text is 500 characters or less. The count covers everything
  pasted into the store: the text between the heading and the next heading,
  trimmed, including bullet markers and line breaks. Characters are counted
  as UTF-16 code units, the larger of the usual ways to count, so an emoji
  counts as 2 and the result errs on the safe side.
- No PR or ticket numbers (#1234, ABC-123, pull request URLs).
- The word "crash" (or crashes, crashed, crashing) does not appear.
- With --hotfix: each section is exactly "Bug fixes and performance improvements."

Prints the character count of each section and one ERROR line per problem.
Exits 1 if there is any ERROR, otherwise 0. Standard library only.
"""

import re
import sys
from pathlib import Path

LIMIT = 500
HOTFIX_LINE = "Bug fixes and performance improvements."
SECTIONS = ["iOS", "Android"]
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.M)
BANNED = [
    (re.compile(r"#\d+"), "PR/issue number"),
    (re.compile(r"\b[A-Z][A-Z0-9]+-\d+\b"), "ticket number"),
    (re.compile(r"github\.com/\S+/pull/\d+|/pull/\d+", re.I), "pull request link"),
    (re.compile(r"\bcrash\w*", re.I), 'the word "crash" (say "stability improvements")'),
]


def utf16_len(text):
    return len(text.encode("utf-16-le")) // 2


def split_sections(text):
    matches = list(HEADING_RE.finditer(text))
    sections = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.append((m.group(1), text[m.end():end].strip()))
    return sections


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    hotfix = "--hotfix" in argv[1:]
    if len(args) != 1:
        print("Usage: python3 check_notes.py release-notes.md [--hotfix]")
        return 2
    path = Path(args[0])
    if not path.is_file():
        print(f"ERROR: {path} not found")
        return 1

    errors = []
    text = path.read_text(encoding="utf-8")
    first = HEADING_RE.search(text)
    if first and text[: first.start()].strip():
        errors.append('text found above "## iOS"; the file starts with that heading')
    sections = split_sections(text)
    names = [name for name, _ in sections]
    if names != SECTIONS:
        errors.append(
            f'sections are {names or "none"}; expected exactly "## iOS" then "## Android"'
        )

    for name, body in sections:
        count = utf16_len(body)
        status = "ok" if count <= LIMIT else f"OVER by {count - LIMIT}"
        print(f"{name}: {count}/{LIMIT} characters ({status})")
        if not body:
            errors.append(f"{name}: section is empty")
        if count > LIMIT:
            errors.append(f"{name}: {count} characters, limit is {LIMIT}; the Play Store cuts off the rest")
        for pattern, label in BANNED:
            for hit in sorted(set(pattern.findall(body))):
                errors.append(f"{name}: contains {label}: {hit!r}")
        if hotfix and body != HOTFIX_LINE:
            errors.append(f'{name}: hotfix release must be exactly "{HOTFIX_LINE}"')

    for e in errors:
        print(f"ERROR: {e}")
    if not errors:
        print("PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
