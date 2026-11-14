---
name: skill-builder
description: Interviews the user, then writes a new agent skill (SKILL.md plus reference files). Use when the user wants to create or design a new skill from a goal. Not for editing or benchmarking an existing skill.
---

# Skill builder

The user describes what they want a skill to achieve. Interview them first, then write the skill. Write nothing before the interview is done. If they haven't stated a goal yet, ask for it.

## How a skill gets used (keep this model in mind)
At startup the agent sees only each skill's name and description, and decides from those alone whether to open it. Once inside, it reads SKILL.md from the top, opens a reference file only when told to, and stops when it believes it's done. Assume the agent is already capable: the skill's job is to put signs only where it would otherwise take a wrong turn.

## Step 1: Interview
Ask in small batches (3–5 questions). Ask only what you can't infer, and offer your best guess as an option the user can confirm. Continue until you could write the skill without guessing at anything important. Cover:

1. **Scope.** What single job does it do? If the goal is really several jobs, say so and propose separate skills.
2. **Invocation.** Picked up automatically from what the user says, or always called by name? If automatic: which genuinely different requests should trigger it, and which similar requests should not?
3. **Inputs and outputs.** What goes in, and what exactly comes out (files, names, format, location)?
4. **Fragile vs. flexible.** Which parts have exactly one right answer (values, names, formats, step order), and where is judgment fine if it follows a principle? For the flexible parts, what's the principle and why does it matter?
5. **Branches.** Does every run do the same thing, or are there modes or request types needing their own instructions or templates?
6. **Done.** How will the agent know it's finished? What check can it run or point to? What would a lazy run that only looks finished look like?
7. **Failures.** Specific cases where the agent got this wrong without a skill: what was asked, what it did, what was expected.
8. **Hidden knowledge.** Conventions, gotchas, or reasons behind choices the agent couldn't discover by looking.
9. **Vocabulary.** Strong shorthand that conveys the standard instantly (e.g. "8pt grid", "think Tufte"), and the one name used for each key concept.

When you have enough, summarise your understanding in a few lines and get confirmation before writing.

## Step 2: Write the skill

**The Door (frontmatter)**
- `name`: short, lowercase-hyphenated.
- Called by name only: add `disable-model-invocation: true` and write the description as a one-line note for the human.
- Otherwise the description says what it does and when to use it, in third person ("Extracts…"). Most important word first. One trigger per genuinely different request, not several phrasings of one. Add "Not for…" if a nearby request could wrongly open it. Well under 1,024 characters, calm in tone.

**The Map (structure)**
- What every run needs stays in SKILL.md. What only one branch needs moves to `references/<name>.md`, with a line saying exactly when to read it ("If X, read references/x.md").
- SKILL.md under ~500 lines; references one level deep only.
- The most important rule or principle goes near the top, not in a closing notes section.

**The Path (instructions)**
- For each line, ask: if the agent did this differently, would the result be wrong? If yes, write it exactly. If no, give a direction plus the reason.
- State the target behaviour rather than a ban ("write in flowing prose paragraphs" beats "don't use markdown"). If a ban is unavoidable, give its reason.
- Explain consequences in a normal tone; capitalised CRITICAL/MUST makes newer models overreact.
- Use strong, well-known words where they carry a whole standard, and one name per concept throughout.

**The Finish Line**
- End with a definition of done the agent can see is met: a check that runs, a count, a list each output must satisfy.
- Where the agent could skip the work and still look finished, add a checkpoint (e.g. "for each item, cite the evidence it rests on").
- If the task has no natural end, define what each pass must leave behind.

**Clear the Path**
Before showing the draft, cut every line that wouldn't change what the agent does: duplicates, information it can find itself, stale workarounds, generic advice like "be thorough". Keep gotchas and reasons it can't discover on its own.

## Step 3: Hand off
1. Show the full SKILL.md and any reference files, each in its own code block with its path. If skills can be saved in this environment, offer to save it.
2. Give a short road-test plan: 2–3 realistic test prompts (one that should NOT trigger the skill), what success looks like for each, and a reminder to run each in a fresh session at least twice and bring back specific failures (what was run, what it did, what was expected) so the exact spot that broke gets fixed.
