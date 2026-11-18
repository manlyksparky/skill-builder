# Run notes: principles-from-article (with skill)

1. I read `skill-builder/SKILL.md` and `task.md`. I didn't open the skill's `evals/` folder. Listing the skill directory with `ls -R` printed its folder names, but I opened none of its files.
2. **Mode:** new skill, the default. The user gave no road-test failures.
3. **Step 0 (mine the source).** The source is the article in task.md. I took six principles from it, using the author's terms: the three questions, no dead ends, blame the system not the person, next to the thing that broke, say it once in plain words, and error code last. The "0x80070057" point became the skill's framing line. I quote all of these in the handoff.
4. **Step 1 (interview).** The user said "Go ahead and write it, no need to check back with me", so I took the fast path. The message settled four things:
   - Scope: write and review error, validation and empty-state copy.
   - Invocation: automatic. Not for log messages or exception names.
   - Output: the message text, plus a one-line note when the next step is guessed.
   - Audience and home: personal, Claude Code.
   I filled the remaining gaps with assumptions and list them in the handoff: review-mode output, ask vs. guess, the placement line, code ordering, apology, editing files, and the name.
5. **Step 2 (write).** I read `references/example-skill.md` before writing the description, as SKILL.md says.
   - I used no reference files and no scripts. Every rule applies to every run, and none has one computable right answer.
   - The frontmatter has only `name` and `description`. The skill doesn't need `allowed-tools` or an argument.
6. **Name clash check.** I listed the existing skills folders:
   ```
   $ ls ~/.claude/skills
   dxe-hiring-manager-bar  find-skills  humanizer  impeccable  structural-humanizer  synced
   $ ls <repo>/.claude/skills
   ls: ... No such file or directory
   ```
   No clash with `error-message-copy`.
7. **Step 3 (validator, first run):**
   ```
   $ python3 skill-builder/scripts/validate_skill.py skill-builder-workspace/iteration-1/principles-from-article/with_skill/outputs/error-message-copy
   PASSED: 0 error(s), 0 warning(s) in .../outputs/error-message-copy
   exit=0
   45 lines
   ```
8. **Cold read (subagent, general-purpose).** I told it to read only SKILL.md and gave it one mixed test prompt: fix the "Oops! Something went wrong. Invalid email." top banner, and write a message for a signup server timeout.
   - **Its output:** a review that named the failed checks (three questions, no dead ends, say it once, next to the thing that broke). The rewrite was "That email address is missing an @. Check it looks like name@example.com." plus a placement line. The timeout message was "We couldn't finish setting up your account because our server took too long to respond. Try again in a minute." with the guess note.
   - **Its 12 points of uncertainty:**
     1. How to combine the two modes in one request, and where the note goes.
     2. "No dead ends" and "the three questions" overlap as labels.
     3. Checks that don't apply have no place in the review format.
     4. It couldn't tell whether "Invalid email" counts as blaming the person.
     5. Whether the placement line applies in review mode.
     6. What counts as a guessed next step.
     7. Whether one sentence is enough for "why" in simple validation.
     8. A timeout might have created the account anyway.
     9. When an apology is allowed.
     10. Whether "you" vs. "your" breaks the blame rule.
     11. "Last human sentence" and "ready to paste" for a title and body are undefined.
     12. Whether "fix" means editing source files.
9. **Fixes after the cold read.**
   - I replaced the "Two modes" section with an "Output" section that covers mixed requests and puts notes once at the end. That fixes points 1 and 5.
   - Each review label now says what it covers, and checks that don't apply are left out. That fixes points 2 and 3.
   - "Invalid email" is now an explicit example of a message that fails "what happened, and why" (point 4).
   - I added a definition of a guessed next step (point 6) and said one sentence covering what happened and why is enough (point 7).
   - The apology rule now says when one is allowed (point 9), and the blame test is about who did the failing, with examples of "your" and "you" (point 10).
   - I reworded "last human sentence" and covered messages split into a title and a body (point 11), and added a line on editing strings in source files (point 12).
   - I didn't act on point 8. It's specific to one case, and the guess note already covers uncertain next steps.
10. **Step 3 (validator, final run, after the last edit):**
    ```
    PASSED: 0 error(s), 0 warning(s) in .../outputs/error-message-copy
    exit=0
    ```
    SKILL.md is 47 lines and the description is 348 characters. The hand checks also pass: there are no bundled files to link, the name matches the folder, and the description has no `<` or `>`.
11. **Step 4 (hand off).** I wrote `outputs/handoff.md`. It contains:
    - The quoted principles and the assumptions.
    - The install location, `~/.claude/skills/error-message-copy/`. I didn't install it, as instructed.
    - The full SKILL.md.
    - The check results.
    - A road-test plan with four prompts: two that should trigger, one with a missing input, and one that shouldn't trigger.
    - The format for coming back with failures.

    The skill is personal, so I didn't write a separate `evals.md`. The plan is in the handoff only.

## Things I was unsure about
- **Review-mode output.** The user only defined the output for writing ("message text plus a one-line note"). The review format is my assumption.
- **Placement line.** It goes beyond the user's output spec. I kept it because otherwise the "next to the thing that broke" principle couldn't affect text-only output. It's flagged as an assumption.
- **Apology.** The article bans stacked apologies, not every apology, so I allowed one short "Sorry". It's flagged.
- **Missing-input road test.** The test assumes the skill should ask when *what broke* is unknown. The user's guess-and-note rule covers only the next step, so I drew that line myself.
- **Skill name.** I picked `error-message-copy` myself. It's flagged in the handoff.
