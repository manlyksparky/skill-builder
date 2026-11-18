# Road-test plan: whats-new-notes

Run each prompt in a fresh session, at least twice. Before each run, have the skill installed (Claude Code: `~/.claude/skills/whats-new-notes/` or the repo's `.claude/skills/`; claude.ai: uploaded and switched on).

## 1. Normal release, pasted list (should trigger)
> Write the what's new text for 4.3.0. Merged PRs:
> - Add saved searches to home [feature]
> - Show delivery estimate on order page [enhancement]
> - Fix crash when opening shared links [bug, android]
> - Fix wrong currency symbol in receipts (APP-2231) [bug]
> - Bump Kotlin to 2.0 [chore]
> - Migrate analytics SDK [internal]

**Success:** release-notes.md with `## iOS` then `## Android`, each 500 characters or less; saved searches and delivery estimate come before the fixes; the shared-link fix appears only in Android and says "stability improvements", not "crash"; no "APP-2231"; Kotlin and analytics never mentioned; check script shows PASS; a coverage table with all 6 PRs (4 placed + 2 excluded).

## 2. Long release that would overflow (should trigger)
> Release notes for 5.0 please. [paste 25 labelled PRs, ~18 of them user-facing, several small UI tweaks]

**Success:** both sections still at or under 500 characters because small changes are grouped into lines, not dropped; the coverage table lists every one of the user-facing PRs against a line.

## 3. Hotfix (should trigger, hotfix branch)
> We're shipping 4.3.1 as a hotfix, can you do the store notes? PRs: "Fix login loop on SSO [bug]", "Fix null pointer in cart [bug]"

**Success:** both sections are exactly "Bug fixes and performance improvements." and nothing else; the check run with `--hotfix` shows PASS.

## 4. Fetch from GitHub (should trigger, different phrasing)
> What's new copy for the 4.4 app release, pull the merged PRs from GitHub.

**Success:** the agent asks which PRs belong to 4.4 (milestone, branch or date range) before running `gh pr list`, then follows the normal flow. It should not guess a date range on its own.

## 5. Unlabelled refactor in a labelled list (should trigger, edge case)
> Store release notes for 4.5: "Add widget for order tracking [feature]", "Refactor image cache", "Update deps [chore]"

**Success:** the refactor is folded into "Performance and stability improvements." placed last, and flagged to the user as possibly mislabelled; deps never mentioned.

## 6. Key input missing (should ask, not guess)
> Can you write the what's new text for our next app version?

**Success:** the agent asks for the version and the PR list (or which PRs to fetch) and writes nothing until it has them. It does not invent features.

## 7. Titles without labels (should ask)
> What's new for 4.6: "Add dark mode", "Refactor auth module", "Fix crash on launch"

**Success:** the agent asks for the labels, since it can't tell user-facing PRs from internal ones without them. If it proceeds anyway, "Refactor auth module" must not appear as its own line.

## 8. Should NOT trigger
> Update CHANGELOG.md with the PRs merged since 4.2.0.

Also try: "Write a description for my PR that adds saved searches."

**Success:** the skill doesn't open; no release-notes.md is written and no 500-character limit is applied.
