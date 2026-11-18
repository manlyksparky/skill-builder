# Run notes: team-skill-from-goal (with skill-builder)

1. Read `skill-builder/SKILL.md` and `task.md`. Picked **new skill** mode, because the user gave a goal and no road-test failures.
2. **Step 0: mine what's already here.** There was no prior conversation or source material, but task.md answered all 10 interview topics.
3. **Step 1: interview.** Skipped the questions. The user said to treat the answers as confirmed and that they wouldn't be around to reply. I used those answers as the confirmed summary and noted my own assumptions for the gaps. Those assumptions are listed in handoff.md:
   - how a hotfix is recognised
   - platform-only PRs
   - exact label names
   - unlabelled refactors
   - how PRs are chosen when not pasted
   - character counting
   - nothing above `## iOS`
   - bullet style
4. Listed the skill folder, excluding evals/: `references/` holds example-skill.md, packaging.md and revise.md, and `scripts/` holds validate_skill.py. There is no `assets/`. I read references/example-skill.md (Step 2 says to read it before writing the description) and references/packaging.md (portable fields, where to save, name clash). I didn't read revise.md, because it's only for fixing mode.
5. **Name clash check.**
   - Command: `ls ~/.claude/skills`
   - Output: dxe-hiring-manager-bar, find-skills, humanizer, impeccable, structural-humanizer, synced
   - The outputs folder was empty, and there's no project `.claude/skills`. `whats-new-notes` is free. I didn't install anything into ~/.claude.
6. **Step 2: write the skill.**
   - Wrote `whats-new-notes/scripts/check_notes.py` (standard library only). It checks:
     - the headings and their order
     - 500 characters per section, counted in UTF-16 code units
     - `#\d+`, ticket IDs like `ABC-123`, and PR links
     - `crash*`
     - with `--hotfix`, the exact hotfix line
   - Wrote `whats-new-notes/SKILL.md` with only `name` and `description` in the frontmatter. The skill has to work on claude.ai too, so the frontmatter is portable and has no `argument-hint`.
   - No references/ or assets/. Everything fits in a 56-line SKILL.md, and the output structure is 5 lines, enforced by the script, so a template file would add a file without adding value.
7. **Step 3: first validator run.**
   ```
   $ python3 skill-builder/scripts/validate_skill.py outputs/whats-new-notes
   PASSED: 0 error(s), 0 warning(s) in .../outputs/whats-new-notes
   exit=0
   $ wc -l SKILL.md -> 56
   ```
8. **Script tests**, with sample files in the scratchpad.
   - Good file:
     ```
     iOS: 124/500 characters (ok)
     Android: 124/500 characters (ok)
     PASS
     exit=0
     ```
   - Bad file (Android first, "#4312", "APP-991", "crash", 900 chars):
     ```
     Android: 64/500 characters (ok)
     iOS: 900/500 characters (OVER by 400)
     ERROR: sections are ['Android', 'iOS']; expected exactly "## iOS" then "## Android"
     ERROR: Android: contains PR/issue number: '#4312'
     ERROR: Android: contains ticket number: 'APP-991'
     ERROR: Android: contains the word "crash" (say "stability improvements"): 'crash'
     ERROR: iOS: 900 characters, limit is 500; the Play Store cuts off the rest
     exit=1
     ```
   - Hotfix file with `--hotfix`:
     ```
     iOS: 39/500 characters (ok)
     Android: 39/500 characters (ok)
     PASS
     exit=0
     ```
   - Normal file with `--hotfix`: two `ERROR ... hotfix release must be exactly "Bug fixes and performance improvements."` lines, exit=1.
9. **Cold read: subagent (general-purpose).** It was given only SKILL.md and check_notes.py, plus a 7-PR test release with a crash fix, a chore, an internal PR, an unlabelled refactor, a ticket ID and an Android-only label.
   - **What it produced:** the PRs sorted correctly. iOS 211 and Android 263 characters, and the coverage table added up (5 placed + 2 excluded = 7).
   - **What it stumbled on:**
     - With a partly labelled list, it wasn't sure whether to ask for labels or carry on.
     - Hotfix "skip to step 5" skipped writing the file.
     - Android got two near-duplicate stability lines.
     - It wasn't clear where the general line goes.
     - Case-insensitive matching was stated only for internal/chore.
     - `enhancement` wasn't mapped to features or fixes.
     - The coverage table had no format for platform-only PRs.
     - The check command hard-coded the file path.
     - "Exactly this shape" wasn't enforced, so a title above the headings would pass.
     - There was no example of rewriting a fix.
     - The script can give false positives such as "COVID-19" or "#1".
     - It doesn't check tone or ordering.
     - "Internal names" had no examples.
     - The `milestone:<version>` naming was assumed.
10. **Fixes applied after the cold read:**
    - Ask for labels only when the list has none at all.
    - The hotfix branch writes the file, then runs the check with `--hotfix`.
    - All labels match case-insensitively.
    - `feature`/`enhancement` map to features, `bug`/`fix` to fixes.
    - One general stability line, placed last and merged with any stability fix.
    - Added an example of rewriting a fix.
    - "Labelled only ios / only android".
    - The check uses the path that was actually written.
    - The coverage table notes "iOS only" or "Android only".
    - The script rejects text above the first heading.
    - "Counts the way the stores do" became "counts conservatively". I can't verify which method the stores use, so the claim was softened.

    Left as is, and explained in the handoff: the false-positive edge cases and the unchecked tone and ordering. I didn't add a list of "internal names" because the user gave none, and inventing one would be an invented gotcha.
11. **Re-ran the validator and the tests after the fixes.**
    ```
    PASSED: 0 error(s), 0 warning(s) in .../outputs/whats-new-notes   exit=0
    title-above-headings file -> ERROR: text found above "## iOS"; the file starts with that heading   exit=1
    same file without title   -> PASS exit=0
    hotfix                    -> PASS exit=0
    cold-read sample (merged stability line) -> iOS 211/500, Android 248/500, PASS exit=0
    description length: 381 characters
    ```
12. **Packaging.**
    - The team uses claude.ai as well, so I built `outputs/whats-new-notes.zip` with the folder at the root of the zip:
      ```
      $ zip -qr whats-new-notes.zip whats-new-notes
      $ unzip -l -> whats-new-notes/, whats-new-notes/scripts/, whats-new-notes/scripts/check_notes.py, whats-new-notes/SKILL.md
      ```
    - I removed `__pycache__` before zipping.
13. **Step 4: road-test plan.** The audience is a team, so I wrote 8 prompts to `outputs/evals.md`. They include a should-not-trigger case (CHANGELOG / PR description) and a missing-key-input case ("next app version", with no PRs given).
14. Wrote `outputs/handoff.md`. It contains the full SKILL.md and script in code blocks, the Step 3 results, the open assumptions, install steps, the road-test plan, and the "Fix my ... skill" return form.

## Unsure about
- **Hotfix detection:** the user didn't say how a hotfix is identified. I assumed it's what the user says or a `hotfix` label, and didn't infer it from the version number.
- **"We keep both the same length":** I read this as both sections having the same 500 limit, and as the same text in both except for platform-labelled PRs.
- **Unlabelled refactor-like PRs:** under the user's definition these are user-facing, but the "Refactor auth module" failure shows they shouldn't be named. I resolved it by grouping them into a general stability line and flagging them, which satisfies both "covered" and "not named".
- **Character counting:** I chose UTF-16 as a conservative count, but haven't verified exactly how either store counts.
- **Where evals.md goes:** I put it beside the skill folder, not inside it. Inside, it would be a bundled file SKILL.md doesn't name, and it would ship in the zip.
- **How PRs are chosen when not pasted:** the `gh pr list --search "milestone:<version>"` example assumes milestone naming. The skill tells the agent to ask first.
