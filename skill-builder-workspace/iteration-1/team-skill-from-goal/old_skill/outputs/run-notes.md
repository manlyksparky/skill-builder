# Run notes: app-whats-new (old_skill)

## Steps

1. **Read the inputs.** I read `skill-snapshot/SKILL.md` and `task.md`, and listed the snapshot folder (`references/example-skill.md`, `packaging.md`, `revise.md`, `scripts/validate_skill.py`). I chose **New skill** mode, so I didn't open `revise.md`.

2. **Step 1, interview.** The user gave all 10 answers up front and said to treat them as confirmed. The skill asks for a summary and confirmation before writing. Nobody was available to reply, so I took the summary as confirmed. I wrote the summary at the top of `handoff.md` and listed the gaps I filled myself as eight assumptions.

3. **Read the references.** Step 2 says to read `references/example-skill.md` before writing the description, so I did. Step 2 also points to `references/packaging.md` for portable frontmatter, and Step 4 points to it for saving, so I read it too.

4. **Checked for a name clash.** Command: `ls ~/.claude/skills` (read only). Output: `dxe-hiring-manager-bar find-skills humanizer impeccable structural-humanizer synced`. No clash with `app-whats-new`. The outputs folder was empty.

5. **Wrote `app-whats-new/scripts/check_notes.py`.** It checks:
   - the section headings
   - the 500-character count for each section
   - PR and ticket numbers
   - "crash" wording
   - markdown formatting
   - the exact hotfix line, when run with `--hotfix`

   I wrote a script because these checks each have one computable right answer.

6. **Wrote `app-whats-new/SKILL.md`.**
   - The frontmatter uses only portable fields, because the team uses both Claude Code and claude.ai.
   - The description is 327 characters.
   - The body has the main rule and the definition of "user-facing PR" at the top, five steps, and a "Done when" section. The last part of "Done when" is a coverage checkpoint: each PR mapped to a line, plus three counts that must add up.

7. **Ran the validator.** Command: `python3 skill-snapshot/scripts/validate_skill.py outputs/app-whats-new`. Output:
   ```
   PASSED: 0 error(s), 0 warning(s) in .../old_skill/outputs/app-whats-new
   exit=0
   ```
   `wc -l SKILL.md` gave 55 lines.

8. **Tested `check_notes.py` on sample files** in `outputs/script-tests/`. On the first run, the shell loop passed `"hotfix.md --hotfix"` as a single argument (zsh doesn't split words in a variable), so I got "not found". That was a problem with my test loop, not the script. The run also showed two weaknesses in the script, which I fixed:
   - `- ` bullets weren't flagged, so I added `^\s*[-*+]\s` to the markdown pattern.
   - The same match was reported many times, so I removed duplicate matches.

   Results after the fixes:
   ```
   --- good.md
   iOS: 141/500 characters
   Android: 141/500 characters
   PASS
   exit=0
   --- bad.md
   iOS: 879/500 characters
   Android: 881/500 characters
   FAIL: iOS: 879 characters, 379 over the limit
   FAIL: iOS: PR or issue number: "#4312"
   FAIL: iOS: ticket number: "JIRA-881"
   FAIL: iOS: "crash" wording (use "stability improvements"): "crash"
   FAIL: iOS: markdown formatting: "**"
   FAIL: Android: 881 characters, 381 over the limit
   FAIL: Android: PR or issue number: "#4312"
   FAIL: Android: ticket number: "JIRA-881"
   FAIL: Android: "crash" wording (use "stability improvements"): "crash"
   FAIL: Android: markdown formatting: "**", "-"
   exit=1
   --- hotfix.md --hotfix
   iOS: 39/500 characters
   Android: 39/500 characters
   PASS
   exit=0
   --- hotfix-bad.md --hotfix
   iOS: 64/500 characters
   Android: 39/500 characters
   FAIL: iOS: a hotfix section must be exactly "Bug fixes and performance improvements."
   exit=1
   --- missing arg
   Usage: python3 check_notes.py release-notes.md [--hotfix]
   exit=2
   ```

9. **Re-ran the validator** after editing the script. Result: `PASSED: 0 error(s), 0 warning(s)`, exit 0. I removed `__pycache__` first.

10. **Zipped the skill for claude.ai.** Command: `zip -r app-whats-new.zip app-whats-new`. The zip holds `app-whats-new/`, `app-whats-new/scripts/check_notes.py` and `app-whats-new/SKILL.md`, with the folder at the root as `packaging.md` requires.

11. **Did the judgment checks from Step 3.** I checked the triggers, that every instruction is exact or explained, one name per concept, that done is visible, and that assumptions are flagged. All pass. The details are in `handoff.md`.

12. **Wrote `handoff.md`.** It covers:
    - the understanding and the assumptions
    - the full file contents
    - the validator and script results
    - the judgment checks
    - install notes
    - a three-prompt road-test plan
    - the "Fix my ... skill" return form

    I installed nothing into `~/.claude`.

## Subagents
None started.

## Things I was unsure about
- **Confirmation gate.** The skill says to get confirmation of the summary before writing. The user had already declared the answers confirmed and wasn't available, so I wrote without a separate confirmation. The leftover gaps are flagged as assumptions instead.
- **Output format.** Plain text lines versus markdown bullets wasn't specified. I chose plain text because the stores render raw text.
- **Identical sections.** The answers said "we keep both the same length". I read that as the same 500 limit and the same lines on both platforms, with platform-only PRs as the exception.
- **Hotfix detection.** How to tell that a release is a hotfix wasn't specified. I chose: the user says so, or every PR has a `hotfix` label; otherwise the agent asks.
- **Choosing a release's PRs.** How the team defines which PRs are in a release (milestone, tag range or dates) is unknown. The `gh` command in the skill is an example, and the agent asks when the scope isn't clear.
- **`${CLAUDE_SKILL_DIR}` in a portable skill.** `packaging.md` says to use it for Claude Code-only skills. This skill also runs on claude.ai, so SKILL.md uses it with a plain fallback ("elsewhere use the folder this SKILL.md is in").
- **Ticket-number regex.** `[A-Z][A-Z0-9]+-\d+` can give false positives on things like "COVID-19". I judged that acceptable and noted it in the handoff.
- **Extra files.** The extra files under `outputs/` (`script-tests/`, `app-whats-new.zip`) aren't part of the skill folder itself.
