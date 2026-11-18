# Run notes: principles-from-article (old_skill)

1. Read the skill snapshot `skill-snapshot/SKILL.md` and the user message `iteration-1/principles-from-article/task.md`.
2. Picked **New skill** mode. The user isn't bringing back road-test failures, so I didn't open `references/revise.md`.
3. **Step 1 (Interview).** I ran no question rounds. The user said "Go ahead and write it, no need to check back with me", so I took the skill's fast path. I filled the answers from the message and the pasted post:
   - **Scope:** writing and reviewing user-facing error, validation and empty-state copy.
   - **Invocation:** automatic. It triggers on writing or reviewing error, validation or empty-state copy. It doesn't trigger on log messages or exception names.
   - **Output:** the message text, plus a one-line note when the next step was guessed.
   - **Where it runs:** Claude Code only, for this user only.
   - **Fragile rules from the post:**
     - Answer the three questions (what happened, why, what now).
     - End with an action.
     - Blame the system.
     - Put the message beside the field.
     - No "Oops", "Uh oh", stacked apologies or jokes.
     - Put the code last.

   I didn't need user confirmation of the summary. The assumptions are listed in the handoff.
4. Listed the skill folder.

   ```
   $ ls -R skill-snapshot/
   SKILL.md  references  scripts
   references: example-skill.md  packaging.md  revise.md
   scripts: validate_skill.py
   ```
5. **Step 2.** Read `references/example-skill.md` to calibrate detail before writing the description, as Step 2 says. Read `references/packaging.md` because Step 4 points to it.
6. **Name-clash check** (from packaging.md):

   ```
   $ ls ~/.claude/skills/
   dxe-hiring-manager-bar  find-skills  humanizer  impeccable  structural-humanizer  synced
   $ ls .claude/skills  -> No such file or directory
   $ ls ~/.claude/skills/synced
   fe10f8e0-53ff-478b-8842-8afd3aee6c78_47fe33b0-b96b-46c7-adeb-49370761651d
   ```

   The name `error-messages` is free.
7. Wrote `outputs/error-messages/SKILL.md`.
   - **Frontmatter:** `name` and `description` only. These fields are portable, even though the skill is only for Claude Code.
   - **Files:** no references, scripts or assets. The skill is short, every branch needs all of it, and no step has a single computable answer that would justify a script.
8. **Step 3 (Validator).**

   ```
   $ cd outputs && python3 skill-snapshot/scripts/validate_skill.py error-messages; echo "exit=$?"; wc -l error-messages/SKILL.md
   PASSED: 0 error(s), 0 warning(s) in .../old_skill/outputs/error-messages
   exit=0
         42 error-messages/SKILL.md
   ```
9. **Judgment check: one name per concept.** It failed at first. The note was called "the note below", "the guess note" and "`Assumed:` line". I fixed it with sed so it's "`Assumed:` line" everywhere, then re-ran the validator:

   ```
   PASSED: 0 error(s), 0 warning(s) in .../old_skill/outputs/error-messages
   ```

   The other judgment checks all pass: distinct triggers, a "Not for" line, instructions that are exact or carry a reason, and a done list. The details are in the handoff.
10. **Step 4.** Wrote `outputs/handoff.md`. It contains:
    - the intended install location (`~/.claude/skills/error-messages/`) and the name-clash result
    - the assumptions
    - the check results
    - the full SKILL.md
    - a road-test plan with 3 prompts, one of which should not trigger the skill
    - the "Fix my skill" return format

    I didn't install anything into `~/.claude`.

**Subagents:** none started.

**Unsure about:**
- **Empty states:** the post never mentions them. I extended the three questions to cover them.
- **Review output format:** the user specified only the output for writing, so I invented the format for reviews (rewrite plus the rule broken).
- **Placement rule:** the output is text only, so I limited this rule to flagging placement when the request or code shows a message away from its field. This could be too weak.
- **Apologies:** I read "no apologies stacked three deep" as allowing at most one short apology.
- **Install scope:** the skill doesn't say whether it belongs in personal or project skills. I chose personal (`~/.claude/skills/`) because the user said "just for me".
- **The `${CLAUDE_SKILL_DIR}` variable:** it wasn't set in this subagent context, so I ran the validator by its absolute path.
