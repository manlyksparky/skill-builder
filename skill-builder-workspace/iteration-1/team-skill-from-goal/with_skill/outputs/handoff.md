I've written the `whats-new-notes` skill from your answers and taken them all as confirmed. Before I wrote anything I checked for a name clash: no existing skill is called `whats-new-notes`. The validator passes and the cold read is done. The full files are below, along with the assumptions I had to make and a road-test plan for the team.

## What I understood (confirmed from your message)
- **Job:** write only the App Store and Play Store "What's new" text from the PRs merged in a release. It doesn't touch CHANGELOG.md.
- **Trigger:** it opens on its own when someone asks for release notes or "what's new" text for an app version. It stays closed for PR descriptions and the internal changelog.
- **Output:** `release-notes.md` with an `## iOS` section and an `## Android` section, each 500 characters or less.
- **What gets mentioned:** PRs labelled internal or chore never appear, and neither do ticket or PR numbers. Features come first, then fixes. The text says "stability improvements", never "crash".
- **Hotfix:** exactly "Bug fixes and performance improvements." and nothing else.
- **Done:** both sections are within the limit, and every user-facing PR is either mentioned or grouped into a line.

## Assumptions still open (please confirm or correct)
1. **How a hotfix is recognised:** the user calls it a hotfix, or its PRs carry a `hotfix` label. A patch version number on its own does *not* make a hotfix.
2. **Platform-only PRs:** a PR labelled only `ios` or only `android` goes in that platform's section only. Everything else goes in both. You said you "keep both the same length", and I read that as both sections having the same 500 limit.
3. **Label names:** the labels are exactly `internal` and `chore`, matched without regard to case. Feature and fix labels are read loosely (`feature`/`enhancement` versus `bug`/`fix`).
4. **Unlabelled refactors:** a PR with no label but no visible change, like a refactor, counts as user-facing by your definition. It goes into one "Performance and stability improvements." line at the end, and the skill flags it to the user as possibly mislabelled. That's how it covers PRs like the "Refactor auth module" one without listing them.
5. **Choosing the PRs:** when the PRs aren't pasted, the agent asks which ones belong to the release (milestone, branch or date range) before it runs `gh pr list`. The example command assumes milestones are named after the version.
6. **Character counting:** the check counts conservatively, so an emoji counts as 2. Bullet markers and line breaks count too, because they get pasted into the store.
7. **File layout:** nothing goes above `## iOS`, so the file has no version title, and it's written to the working directory unless the user names a path.
8. **Bullet style:** I left the bullet style and wording to the agent, since you said tone is the flexible part.

## Files
Skill folder: `outputs/whats-new-notes/`. For claude.ai there's also a ready-to-upload zip at `outputs/whats-new-notes.zip`, with the folder at the root of the zip.

```text
whats-new-notes/
├── SKILL.md
└── scripts/
    └── check_notes.py
```

### whats-new-notes/SKILL.md
````markdown
---
name: whats-new-notes
description: Writes the App Store and Play Store "What's new" text for a mobile app release from the merged PRs and their labels, saved as release-notes.md with an iOS and an Android section of 500 characters or less each. Use when someone asks for release notes or "what's new" text for an app version, including a hotfix. Not for writing PR descriptions or updating the internal CHANGELOG.md.
---

# What's new notes

This text goes straight into the App Store and the Play Store, so it is written for customers, not for the team. Two rules matter most:

- **500 characters or less per section.** The Play Store cuts off anything longer, mid-sentence, and the team keeps iOS to the same limit so both stores match. A previous run wrote 900 characters and the store truncated it.
- **Only user-facing PRs, in customer language.** A *user-facing PR* is any PR without the `internal` or `chore` label. PRs with either label are never mentioned. No PR or ticket numbers ever appear. A previous run wrote "Refactor auth module (#4312)": internal work, written as a dev title, with a PR number.

## Steps

1. **Get the PR list.** The input is merged PR titles with their labels, either pasted by the user or fetched with `gh`. If nothing was pasted and you can run `gh`, ask which PRs belong to the release (a milestone, a base branch, or a merge date range) instead of guessing, then fetch them, e.g.:
   ```bash
   gh pr list --state merged --search "milestone:<version>" --json number,title,labels --limit 200
   ```
   Without labels you can't tell user-facing PRs from internal ones, so if the pasted list carries no labels at all, ask for them. In a labelled list, a PR with no labels is user-facing (see step 3).

2. **Check for a hotfix.** A release is a hotfix when the user calls it one or its PRs carry a `hotfix` label. A hotfix gets exactly one line in both sections, and nothing else:
   ```
   Bug fixes and performance improvements.
   ```
   Write release-notes.md in the shape shown in step 4 with that line as the whole text of each section, skip steps 3 and 4, and run the check in step 5 with `--hotfix`.

3. **Sort the PRs.** Match all label names case-insensitively. Drop every PR labelled `internal` or `chore`. Put each user-facing PR in one of two groups: *features* (new or changed things a user can see or do; labels like `feature` or `enhancement`) and *fixes* (labels like `bug` or `fix`). With no such label, judge from the title. A user-facing PR whose title describes no visible change (a refactor or upgrade that nobody labelled `internal` or `chore`) still has to be covered: fold it into one general line, "Performance and stability improvements.", placed last, and list it for the user as possibly mislabelled. If a fix already became a stability line, merge them into that one line rather than writing two.

4. **Write release-notes.md** in the working directory, unless the user names another path, in exactly this shape, with nothing above the first heading:
   ```markdown
   ## iOS

   <text>

   ## Android

   <text>
   ```
   - Features first, then fixes. The PM wants new things to lead.
   - Rewrite each dev title as what the user gets: "Add dark mode to settings" becomes "You can now switch to dark mode in Settings."; "Fix wrong currency in receipts" becomes "Receipts now show the right currency." Group small related changes into one line rather than dropping them; grouping is how everything fits in 500 characters.
   - Say "stability improvements", never "crash", "crashes" or "crashing", even when the PR title says crash.
   - Tone: friendly but plain. Short sentences a customer understands, no internal names for screens or systems.
   - Both sections carry the same text, except a PR labelled only `ios` or only `android` goes only in that platform's section.
   - Bullet markers and line breaks count toward the 500, because they are pasted into the store too.

5. **Run the check** and fix every ERROR, then run it again until it prints PASS:
   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/check_notes.py" release-notes.md
   ```
   Use the path you actually wrote to, and add `--hotfix` for a hotfix. `${CLAUDE_SKILL_DIR}` is set in Claude Code; on claude.ai use the path of this skill's folder. The script checks the two headings, counts each section conservatively (an emoji counts as 2), and flags PR or ticket numbers and the word "crash". If you can't run code, check those same things by hand and count the characters of each section exactly, including line breaks.

## Done when

- The check prints PASS (or, without code, each item of the hand check is marked pass), and you show the user the character count of each section.
- Coverage adds up (skip this for a hotfix). Show the user a short table with every PR from the input and where it went: the line that mentions or groups it, or "excluded (internal)" / "excluded (chore)", noting "iOS only" or "Android only" where it applies. User-facing PRs + excluded PRs = PRs in the input. A run that quietly drops PRs to get under 500 characters looks finished but isn't; group them instead.
- PRs folded into a general line as possibly mislabelled are listed so the user can confirm.
````

### whats-new-notes/scripts/check_notes.py
```python
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
```

## Installing it
- **Claude Code:** because the whole team uses it, the best home is the mobile repo's `.claude/skills/whats-new-notes/`, committed to the repo. Each person could instead put it in their own `~/.claude/skills/whats-new-notes/`. If the `skills` folder didn't exist when the session started, run `/reload-skills`.
- **claude.ai:** go to Customize → Skills → + → Create skill → Upload a skill, choose `whats-new-notes.zip`, then switch it on. Code execution has to be on for the check script to run. Skills don't sync between the two, so each environment needs its own copy.
- The frontmatter uses only `name` and `description`, so the upload works on claude.ai as well as in Claude Code.

## Check results (Step 3)
Validator:
```
PASSED: 0 error(s), 0 warning(s) in .../outputs/whats-new-notes
```
I also tested the bundled `check_notes.py` on sample files:
- A file with a title above the headings is rejected.
- On a bad file it caught all of these: the 900-character overflow, `#4312`, `APP-991`, "crash", and sections in the wrong order.
- A correct hotfix file passes with `--hotfix`.
- A normal file run with `--hotfix` is rejected.
- The cold-read sample passes at 211/248 characters.

Judgment checks:
- **Triggers:** pass. Two different requests trigger it: normal release notes, and a hotfix. The "Not for" line covers the two closest wrong requests you named, PR descriptions and CHANGELOG.md.
- **Every instruction is exact or carries its reason:** pass. The 500 limit cites Play Store truncation, features-first cites the PM, and labels are needed to tell user-facing PRs apart.
- **One name per concept:** pass. "User-facing PR" is defined once and used throughout.
- **Done is visible:** pass. The check script must print PASS and the character counts are shown. The coverage table must add up (user-facing + excluded = input), which is there to catch a lazy run that drops PRs to fit under 500.
- **Every interview answer is in the skill:** pass.
  - Both failures ("Refactor auth module (#4312)" and the 900-character overflow) are written in near the top.
  - Both pieces of hidden knowledge (features before fixes, and "stability improvements" instead of "crash") are in step 4 and enforced by the script.
- **Assumptions:** flagged above.

The cold read was a subagent given only the skill files and one test release. I fixed what it tripped on:
- It wasn't clear whether to ask or carry on when only *some* PRs lacked labels. Now it asks only when there are no labels at all.
- "Skip to step 5" for a hotfix skipped writing the file. Now the hotfix branch says to write the file first.
- Two near-duplicate stability lines appeared on Android. Now they merge into one line, placed last.
- Case-insensitive matching covered only internal/chore. Now it covers all labels.
- Nothing said which label means feature and which means fix. Now `enhancement` maps to features and `bug`/`fix` to fixes.
- The check command hard-coded the file path. Now it uses the path that was actually written.
- "Exactly this shape" wasn't enforced. The script now rejects text above `## iOS`.
- There was no example of rewriting a fix. One is added.
- The coverage table had no way to mark platform-only PRs. "iOS only" and "Android only" are added.

Left as is:
- The ticket-number pattern could flag strings like "COVID-19", and `#\d+` could flag "#1". Both are rare in store copy, and catching real ticket numbers matters more.
- The script doesn't check tone or whether features come before fixes. Those are left to the agent's judgment.

## Road-test plan
Because this is a team skill, I saved 8 prompts with success criteria to `outputs/evals.md`, next to the skill folder:
1. A normal pasted release.
2. A 25-PR release that has to group lines to fit.
3. A hotfix.
4. "Pull the PRs from GitHub". It should ask which PRs belong to the release before fetching.
5. An unlabelled refactor in a labelled list.
6. **Key input missing:** "what's new text for our next version". It should ask for the version and the PRs, not invent features.
7. Titles with no labels. It should ask for the labels.
8. **Should not trigger:** "Update CHANGELOG.md…" and "Write a description for my PR…".

Run each one in a fresh session, at least twice, in both Claude Code and claude.ai, since the team uses both.

## When something breaks
Come back with: "Fix my `whats-new-notes` skill: I ran ___, it did ___, I expected ___." That puts me in fixing mode, and I'll change just the part that broke.
