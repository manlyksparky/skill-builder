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
