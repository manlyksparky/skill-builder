---
name: skill-builder
description: Interviews the user, then writes a new agent skill (SKILL.md plus any reference files and scripts) and checks it before handing it over. Use when the user wants to create or design a skill from a goal, or turn a workflow or the current conversation into a skill. Also use when the user brings back road-test failures for a skill and wants those specific spots fixed. Not for benchmarking, running evals on, or wholesale rewriting an existing skill.
---

# Skill builder

The user describes what they want a skill to achieve. Interview them first, then write the skill, check it, and hand it over. Write nothing before the interview is done. If they haven't stated a goal yet, ask for it.

**Pick the mode first:**
- **New skill** (the default): follow Steps 1–4 below.
- **Fixing a skill after road-testing** (the user reports what they ran, what happened, and what they expected): read references/revise.md and follow it instead of Steps 1–2.

## How a skill gets used (keep this model in mind)
At startup the agent sees only each skill's name and description, and decides from those alone whether to open it. Once inside, it reads SKILL.md from the top, opens a reference file only when told to, and stops when it believes it's done. Assume the agent is already capable: the skill's job is to put signs only where it would otherwise take a wrong turn.

## Step 1: Interview

**Start from what already exists.** If the conversation already shows the workflow (the user just did the task with you), or they've pasted a spec, doc or example output, fill in every answer you can from it. Ask only about the gaps, and quote what you took from the source so they can correct it.

Then ask in small batches (3–5 questions). Ask only what you can't infer, and offer your best guess as an option the user can confirm. Aim to finish in three rounds or fewer: interview fatigue produces worse answers than a marked assumption. Cover:

1. **Scope.** What single job does it do? If the goal is really several jobs, say so and propose separate skills.
2. **Invocation.** Picked up automatically from what the user says, or always called by name? If automatic: which genuinely different requests should trigger it, and which similar requests should not?
3. **Inputs and outputs.** What goes in, and what exactly comes out (files, names, format, location)?
4. **Fragile vs. flexible.** Which parts have exactly one right answer (values, names, formats, step order), and where is judgment fine if it follows a principle? For the flexible parts, what's the principle and why does it matter?
5. **Branches.** Does every run do the same thing, or are there modes or request types needing their own instructions or templates?
6. **Done.** How will the agent know it's finished? What check can it run or point to? What would a lazy run that only looks finished look like?
7. **Failures.** Specific cases where the agent got this wrong without a skill: what was asked, what it did, what was expected.
8. **Hidden knowledge.** Conventions, gotchas, or reasons behind choices the agent couldn't discover by looking.
9. **Vocabulary.** Strong shorthand that conveys the standard instantly (e.g. "8pt grid", "think Tufte"), and the one name used for each key concept.
10. **Where it runs.** Claude Code, claude.ai, the API, or several? This decides which frontmatter fields are allowed and whether scripts can rely on network access.

**Fast path.** If the user says "just write it", or the rounds run out, fill the remaining gaps with your best guesses and mark each one as an assumption.

When you have enough, summarise your understanding in a few lines, with assumptions listed separately, and get confirmation before writing.

## Step 2: Write the skill

Before writing the description, read references/example-skill.md to calibrate the level of detail.

**The Door (frontmatter)**
- `name`: short, lowercase-hyphenated, matching the folder name.
- Called by name only: add `disable-model-invocation: true` (Claude Code only) and write the description as a one-line note for the human.
- Otherwise the description says what it does and when to use it, in third person ("Extracts…"). Most important word first. One trigger per genuinely different request, not several phrasings of one. Add "Not for…" if a nearby request could wrongly open it. Well under 1,024 characters, calm in tone.
- If the skill must work on claude.ai or the API, use only the portable frontmatter fields listed in references/packaging.md. Any other field makes the upload fail.

**The Map (structure)**
- What every run needs stays in SKILL.md. What only one branch needs moves to `references/<topic>.md`, with a line saying exactly when to read it ("If the request is a refund, read `references/<topic>.md`").
- When a step has one computable right answer (a format, an order, a validation), put it in `scripts/` and tell the agent the exact command. A script is more reliable than prose for that step, and only its output costs context.
- Templates and files the skill copies or fills in go in `assets/`.
- SKILL.md under ~500 lines; references one level deep only.
- The most important rule or principle goes near the top, not in a closing notes section.

**The Path (instructions)**
- For each line, ask: if the agent did this differently, would the result be wrong? If yes, write it exactly. If no, give a direction plus the reason.
- State the target behaviour rather than a ban ("write in flowing prose paragraphs" beats "don't use markdown"). If a ban is unavoidable, give its reason.
- Explain consequences in a normal tone. Words shouted in capitals make newer models overreact.
- Use strong, well-known words where they carry a whole standard, and one name per concept throughout.

**The Finish Line**
- End with a definition of done the agent can see is met: a check that runs, a count, a list each output must satisfy.
- Where the agent could skip the work and still look finished, add a checkpoint (e.g. "for each item, cite the evidence it rests on").
- If the task has no natural end, define what each pass must leave behind.

**Clear the Path**
Before checking, cut every line that wouldn't change what the agent does: duplicates, information it can find itself, stale workarounds, generic advice like "be thorough". Keep gotchas and reasons it can't discover on its own.

## Step 3: Check

A draft that reads well can still fail to load or never trigger, so check it before handing over.

**If you can run code**, save the draft to a folder named after the skill and run the validator bundled with this skill, `scripts/validate_skill.py`, on it:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/validate_skill.py" <new-skill-folder>
```

`${CLAUDE_SKILL_DIR}` is set in Claude Code. Elsewhere, use the path of this skill's folder. Fix every ERROR. Fix each WARN, or tell the user why it's fine for this skill.

**If you can't run code**, check the same rules by hand:
- `name` uses only lowercase letters, digits and single hyphens; is at most 64 characters; doesn't contain "anthropic" or "claude"; and matches the folder name.
- `description` is present, at most 1,024 characters, and contains no `<` or `>`.
- Frontmatter uses only the portable fields, unless the skill is for Claude Code alone.
- Every `references/`, `scripts/` and `assets/` path named in SKILL.md exists, every bundled file is named in SKILL.md, and no reference file points to another reference file.
- SKILL.md is under 500 lines.

**In both cases, also check what no script can:**
- Each trigger in the description is a genuinely different request, and the "Not for" line covers the nearest wrong request.
- Every instruction is either exact or carries its reason.
- Each key concept has one name throughout.
- There's a definition of done the agent can see is met, and a checkpoint wherever a lazy run could look finished.
- Every assumption from Step 1 is either confirmed or flagged for the user.

Done means the validator output (or the hand checklist, each line marked pass or fail) and the five judgment checks are included in the handoff, with nothing left failing.

## Step 4: Hand off
1. Save the skill as described in references/packaging.md, which covers checking for a name clash, where the skill goes in each environment, and what to show when you can't write files. Show the full SKILL.md and any other files, each in its own code block with its path.
2. Include the Step 3 results and any assumptions still open.
3. Give a short road-test plan: 2–3 realistic test prompts (one that should *not* trigger the skill), and what success looks like for each. Remind the user to run each in a fresh session at least twice.
4. Tell the user how to come back with failures, in this form: "Fix my `<name>` skill: I ran ___, it did ___, I expected ___." That brings them back to this skill in fixing mode, so the exact spot that broke gets fixed.
