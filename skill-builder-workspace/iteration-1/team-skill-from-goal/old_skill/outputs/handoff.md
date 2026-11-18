I've written the `app-whats-new` skill. It turns a list of merged PRs into `release-notes.md`, with an iOS section and an Android section. A small script checks the file before the skill counts as done.

You gave me all the interview answers up front, so I treated them as confirmed and went straight to writing. Below are the decisions I made that your answers didn't settle. Each is marked as an assumption so you can correct it.

## What I understood (confirmed by you)
- **Job:** only the App Store / Play Store "What's new" text, from merged PR titles plus labels. Not CHANGELOG.md, not PR descriptions.
- **Output:** `release-notes.md` with `## iOS` and `## Android`, each 500 characters or less.
- **Fixed rules:** no `internal` or `chore` PRs; no PR or ticket numbers; never "crash", always "stability improvements"; features first, then fixes.
- **Hotfix:** the only line in both sections is "Bug fixes and performance improvements."
- **Done:** both sections are 500 characters or less, and every user-facing PR is mentioned or grouped into a line.
- **Runs in:** Claude Code and claude.ai, so the frontmatter uses only the portable fields.

## Assumptions still open (please confirm or correct)
1. **Name:** `app-whats-new`. Nothing in `~/.claude/skills` uses it.
2. **Plain text output:** one change per line, with no markdown bullets, bold or links, because the stores show those as raw characters. The 500 count includes newlines.
3. **Same text on both platforms:** both sections carry the same lines. The exception is a PR that's for one platform only (labelled `ios`/`android`, or the title names the platform), which goes only in that platform's section.
4. **Spotting a hotfix:** a release is a hotfix if the user calls it one, or if every PR has a `hotfix` label. A patch version number alone isn't enough, so the agent asks.
5. **Features vs fixes:** the agent splits them by the labels `feature`/`enhancement` vs `bug`/`fix`, and by the title when there's no label. Labels are matched case-insensitively (`Internal` counts as `internal`).
6. **Which PRs are in a release:** when the user names a version but doesn't paste PRs, the agent asks for the milestone or date range. The `gh pr list --search "milestone:<version>"` command in the skill is only an example. Tell me how your team actually defines a release's PRs and I'll make that exact.
7. **Where the file goes:** `release-notes.md` is written to the current working directory. A title line above `## iOS` is allowed and ignored.
8. **The "crash" rule** also covers crashes, crashed and crashing. The ticket-number check flags any `ABC-123` pattern, so something like "COVID-19" in a PR title would be flagged too (a false positive, but a harmless one).

## Files
```text
app-whats-new/
├── SKILL.md
└── scripts/
    └── check_notes.py
```

### `app-whats-new/SKILL.md`

~~~~markdown
---
name: app-whats-new
description: Writes the App Store and Play Store "What's new" text for a mobile app release from its merged PRs, saved as release-notes.md with an iOS and an Android section of 500 characters or less each. Use when someone asks for release notes or "what's new" text for an app version. Not for PR descriptions or the internal CHANGELOG.md.
---

# App "What's new" notes

This text is read by people who use the app, in the store listing. Write about what changed for them, never about how the code changed. The Play Store cuts off anything past 500 characters mid-sentence, and we hold the iOS section to the same limit so the two stay the same length.

**User-facing PR** means any PR without the `internal` or `chore` label (match the labels case-insensitively). Every user-facing PR appears in the notes, either on its own line or grouped into a line with others. PRs labelled `internal` or `chore` are never mentioned, not even reworded.

## Steps

1. **Get the PRs.** Use the list the user pasted. If they gave a release instead of a list, ask for the PR list or the milestone or date range that defines the release, then fetch it with titles and labels, for example:
   ```bash
   gh pr list --state merged --search "milestone:<version>" --json title,labels --limit 200
   ```
   Don't guess the range: notes built from the wrong PRs look finished but describe a different release.

2. **Hotfix?** If the user calls the release a hotfix, or every PR carries a `hotfix` label, both sections are exactly this one line and nothing else:
   ```text
   Bug fixes and performance improvements.
   ```
   Skip to step 5 and run the check with `--hotfix`. A patch version number alone doesn't make a release a hotfix; if that's all you have, ask.

3. **Sort the PRs.** Set aside every `internal` and `chore` PR. Split the user-facing PRs into features and fixes, using labels such as `feature`, `enhancement`, `bug` or `fix`, or the title when there's no label. Note which PRs are for one platform only (an `ios` or `android` label, or a title that names the platform).

4. **Write release-notes.md** in the current working directory, in this shape:
   ```text
   ## iOS
   <one change per line>

   ## Android
   <one change per line>
   ```
   - Features first, then fixes. The PM wants the new things people can do read before the repairs.
   - Friendly but plain: short sentences saying what the user can now do or what works better ("You can now save drafts offline."). No hype, no emoji, no implementation words (refactor, migrate, API, module).
   - Never write "crash" or "crashes". Describe those fixes as stability improvements ("Stability improvements when uploading photos.").
   - No PR or ticket numbers. Strip them from titles before you rewrite.
   - Plain text only: no markdown bullets, bold or links, because the stores show those as raw characters. One change per line.
   - Both sections carry the same lines, except that a platform-only change goes only in its platform's section.
   - When the text runs over 500 characters, group fixes first ("Fixes for sign-in and notifications, plus stability improvements."), then shorten feature lines. Grouping keeps every user-facing PR covered; dropping one doesn't.

   What went wrong before, so you can see the target: a PR titled "Refactor auth module (#4312)" labelled `internal` was written up as a line, number included, and the text reached 900 characters, so the Play Store cut it off mid-sentence. Correct handling: that PR is left out entirely, and the whole section fits in 500.

5. **Check the file.** Run the script in this skill's `scripts/` folder (in Claude Code, `${CLAUDE_SKILL_DIR}` points to this skill's folder; elsewhere use the folder this SKILL.md is in):
   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/check_notes.py" release-notes.md
   ```
   Add `--hotfix` for a hotfix release. It prints each section's character count and a FAIL line for anything over 500, any PR or ticket number, any "crash" wording and any markdown. Fix every FAIL and run it again until it prints PASS. If you can't run code, count the characters of each section yourself (newlines included) and check the same rules by hand.

## Done when

- The check prints PASS, and both character counts are shown to the user.
- Every user-facing PR is covered. In your reply, list each user-facing PR title next to the line that covers it, then list the `internal` and `chore` PRs you left out. The counts must add up: user-facing PRs covered + PRs left out = PRs in the input. Show all three numbers. A PR that appears in neither list is a PR you dropped.
~~~~

### `app-whats-new/scripts/check_notes.py`

~~~~python
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
~~~~

## Check results (Step 3)

**Validator** (`validate_skill.py app-whats-new`):
```text
PASSED: 0 error(s), 0 warning(s) in .../outputs/app-whats-new
```
SKILL.md is 55 lines and the description is 327 characters.

**`check_notes.py` tests** (sample files are in `outputs/script-tests/`):
- `good.md`: iOS 141/500, Android 141/500, PASS.
- `bad.md` (your old failure: "Refactor auth module (#4312)", a ticket number, "crash", markdown, about 880 characters): FAIL for each of them on both sections, exit 1.
- `hotfix.md --hotfix`: PASS. `hotfix-bad.md --hotfix` (an extra line on iOS): FAIL, exit 1.

**Checks a script can't do:**
- **Triggers: pass.** The description has one trigger: a request for release notes or "what's new" text for an app version. Its "Not for" line covers the two nearest wrong requests you named, PR descriptions and CHANGELOG.md.
- **Every instruction exact or explained: pass.** The exact items are the 500 limit, the hotfix line, the label rule, the section headings and the script command. The flexible ones carry their reason: features first because the PM wants it, plain text because the stores show markdown as raw characters, and grouping before dropping because grouping keeps every PR covered.
- **One name per concept: pass.** "user-facing PR", "section", `release-notes.md` and "hotfix" each mean one thing and are used consistently.
- **Done is visible: pass.** The script has to print PASS. The agent also has to list each user-facing PR next to the line that covers it, list the PRs it left out, and show three counts that add up. That makes a dropped PR visible, which is how a lazy run would look finished.
- **Assumptions: flagged.** All eight are listed above.

## Installing it (I haven't installed anything)
- **Claude Code:** the whole mobile team uses it, so I'd put the folder in the mobile repo at `.claude/skills/app-whats-new/` and commit it. Everyone who works in that repo then gets it. For a personal install, use `~/.claude/skills/app-whats-new/`. If the `skills` folder is new, run `/reload-skills`.
- **claude.ai:** upload `outputs/app-whats-new.zip` (the zip root holds the `app-whats-new/` folder) under **Customize → Skills → + → Create skill → Upload a skill**, then switch the skill on. Code execution must be on so the check script can run. Without it, the skill tells the agent to check the rules by hand.
- Copies don't sync between Claude Code and claude.ai, so update both when the skill changes.

## Road-test plan
Run each prompt in a fresh session, at least twice.
1. **Normal release:** "Write the what's new text for 4.3.0 from these PRs:" followed by about 12 PRs. Include two labelled `internal`/`chore` (one of them "Refactor auth module (#4312)"), one titled "Fix crash when uploading photos (#4420)", one labelled `android`, and enough features that a line per PR would go past 500. Success looks like this:
   - `release-notes.md` exists, and the check prints PASS with both counts at 500 or less.
   - No internal or chore PR appears, and no numbers.
   - The crash fix reads as a stability improvement, features come before fixes, and the Android-only PR is only under Android.
   - The reply maps every user-facing PR to a line, and the counts add up.
2. **Hotfix:** "4.3.1 is a hotfix, give me the store release notes" plus two bug-fix PRs. Success: both sections are exactly "Bug fixes and performance improvements." and `check_notes.py --hotfix` passes.
3. **Should not trigger:** "Add the 4.3.0 changes to our CHANGELOG.md" (or "Write a PR description for this branch"). Success: the skill doesn't open, and no 500-character store text appears.

## If something breaks
Come back with: "Fix my `app-whats-new` skill: I ran ___, it did ___, I expected ___." That puts me in fixing mode, and I'll change only the part that broke.
