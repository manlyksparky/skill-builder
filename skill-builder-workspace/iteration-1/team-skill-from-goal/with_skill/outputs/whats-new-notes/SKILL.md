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
