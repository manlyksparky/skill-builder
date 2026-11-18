---
name: skill-builder
description: Interviews the user, then writes a new agent skill (SKILL.md plus any reference files and scripts) and checks it before handing it over. Use when the user wants to create or design a skill from a goal, a process worked out in the conversation, or source material such as an article. Also use when the user brings back road-test failures for a skill and wants those specific spots fixed. Not for benchmarking, running evals on, or wholesale rewriting an existing skill.
---

# Skill builder

The user describes what they want a skill to achieve. Interview them first, then write the skill, check it, and hand it over. Write nothing before the interview is done. If they haven't stated a goal yet, ask for it.

**Pick the mode first:**
- **New skill** (the default): follow Steps 0–4 below.
- **Fixing a skill after road-testing** (the user reports what they ran, what happened, and what they expected): read references/revise.md and follow it instead of Steps 0–2. If you have a transcript or notes from the test run, also read the "Reading the signs after a test" section of references/authoring-patterns.md.

## How a skill gets used (keep this model in mind)
At startup the agent sees only each skill's name and description, and decides from those alone whether to open it. Once inside, it reads SKILL.md from the top, opens a reference file only when told to, and stops when it believes it's done. Assume the agent is already capable: the skill's job is to put signs only where it would otherwise take a wrong turn.

## Step 0: Mine what's already here
Before asking anything, check for material the skill can be extracted from:
- **This conversation** already holds the process ("turn this into a skill", "capture what we just did"): pull out the steps, the decisions and why they were made, what went wrong before it went right, and the tools used. Show that as a short draft and interview only for the gaps.
- **Source material** (an article, talk, doc, spec or example output): extract 3–7 principles that change what the agent does, not a summary of the source. Test each one: could you state it without pointing at the source? Keep the author's signature terms; they feed Vocabulary.

Quote what you took from the source so the user can correct it. Every question this answers is one you don't need to ask.

## Step 1: Interview
Ask in small batches (3–5 questions). Ask only what you can't infer, and offer your best guess as an option the user can confirm. Use a multiple-choice question tool when one is available, with your best guess first. Aim to finish in three rounds or fewer: interview fatigue produces worse answers than a marked assumption. Cover:

1. **Scope.** What single job does it do? If the goal is really several jobs, say so and propose separate skills.
2. **Invocation.** Picked up automatically from what the user says, or always called by name? If automatic: which genuinely different requests should trigger it, and which similar requests should not?
3. **Inputs and outputs.** What goes in, and what exactly comes out (files, names, format, location)?
4. **Fragile vs. flexible.** Which parts have exactly one right answer (values, names, formats, step order), and where is judgment fine if it follows a principle? For the flexible parts, what's the principle and why does it matter?
5. **Branches.** Does every run do the same thing, or are there modes or request types needing their own instructions or templates?
6. **Done.** How will the agent know it's finished? What check can it run or point to? What would a lazy run that only looks finished look like?
7. **Failures.** Specific cases where the agent got this wrong without a skill: what was asked, what it did, what was expected.
8. **Hidden knowledge.** Conventions, gotchas, or reasons behind choices the agent couldn't discover by looking.
9. **Vocabulary.** Strong shorthand that conveys the standard instantly (e.g. "8pt grid", "think Tufte"), and the one name used for each key concept.
10. **Audience and home.** Just for the user, a team, or public? Running in Claude Code, claude.ai, the API, or several? Audience sets how much testing and documentation to hand over; home decides which frontmatter fields are allowed, which tools exist, and whether scripts can rely on network access.

If the skill encodes a policy or standard a team must apply consistently (security, API conventions, brand or legal rules), read references/policy-skills.md before summarising. It adds questions about the policy's owner, its source of truth, and whether it needs enforcement beyond the skill.

**Fast path.** If the user says "just write it", or the rounds run out, fill the remaining gaps with your best guesses and mark each one as an assumption.

When you have enough, summarise your understanding in a few lines, with assumptions listed separately, and get confirmation before writing.

## Step 2: Write the skill

Before writing the description, read references/example-skill.md to calibrate the level of detail. If the skill has a multi-step workflow, bundled scripts, a fixed output format, or uses MCP tools, also read references/authoring-patterns.md before writing those parts.

**The Door (frontmatter)**
- `name`: short, lowercase-hyphenated, matching the folder name.
- Called by name only: add `disable-model-invocation: true` (Claude Code only) and write the description as a one-line note for the human.
- Otherwise the description says what it does and when to use it, in third person ("Extracts…"). Most important word first. One trigger per genuinely different request, not several phrasings of one. Add "Not for…" if a nearby request could wrongly open it. Well under 1,024 characters, calm in tone.
- If the skill must work on claude.ai or the API, use only the portable frontmatter fields listed in references/packaging.md. Any other field makes the upload fail.
- For Claude Code: `allowed-tools` for tools it should use without prompting, and `argument-hint` plus `$ARGUMENTS` if it takes input when called. `argument-hint` is Claude Code only, so leave it out when the skill must also run on claude.ai.

**The Map (structure)**
- What every run needs stays in SKILL.md. What only one branch needs moves to `references/<topic>.md`, with a line saying exactly when to read it ("If the request is a refund, read `references/<topic>.md`").
- Code the agent would otherwise rewrite the same way every run, or any step with one computable right answer (a format, an order, a validation), goes in `scripts/` with the exact command. A script is more reliable than prose for that step, and only its output costs context.
- A fixed output structure goes in a template in `assets/`, along with other files the skill copies or fills in. Scripts and templates each get the same "when to use" line as a reference file.
- SKILL.md under ~500 lines; references one level deep only.
- The most important rule or principle goes near the top, not in a closing notes section.

**The Path (instructions)**
- For each line, ask: if the agent did this differently, would the result be wrong? If yes, write it exactly. If no, give a direction plus the reason.
- State the target behaviour rather than a ban ("write in flowing prose paragraphs" beats "don't use markdown"). If a ban is unavoidable, give its reason.
- Explain consequences in a normal tone. Words shouted in capitals make newer models overreact.
- Use strong, well-known words where they carry a whole standard, and one name per concept throughout.

**The Gotchas**
- Turn each interview failure into a line: what the agent tends to do, why that's wrong, what to do instead. Place it next to the step where the mistake happens; collect cross-cutting ones under `## Gotchas`.
- Write only gotchas that trace to an interview answer or an observed failure. An invented, plausible-sounding warning ("don't make assumptions") is noise.

**The Finish Line**
- End with a definition of done the agent can see is met: a check that runs, a count, a list each output must satisfy.
- Where the agent could skip the work and still look finished, add a checkpoint (e.g. "for each item, cite the evidence it rests on").
- If the task has no natural end, define what each pass must leave behind.

**Clear the Path**
Before the cold read, cut every line that wouldn't change what the agent does: duplicates, information it can find itself, stale workarounds, generic advice like "be thorough". Keep gotchas and reasons it can't discover on its own.

**Cold read**
Then reread the draft as an agent that never saw this interview. Fix anything that only makes sense with the conversation in mind: "as discussed", terms never defined, a default the user stated that the skill leaves out. If you can start a subagent, give it only the skill files and one test prompt, ask what it would do and where it's unsure, and fix what it trips on.

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

## Step 4: Hand off
1. Save the skill as described in references/packaging.md, which covers checking for a name clash, where the skill goes in each environment, and what to show when you can't write files. Show the full SKILL.md and any other files, each in its own code block with its path.
2. Include the Step 3 results and any assumptions still open.
3. Give a road-test plan sized to the audience: 2–3 realistic prompts for a personal skill; 5–8 covering different phrasings for a team or public one, saved as `evals.md` next to the skill. Always include one that should *not* trigger the skill and one that leaves out a key input (it should ask, not guess). Say what success looks like for each, and remind the user to run each in a fresh session at least twice.
4. Tell the user how to come back with failures, in this form: "Fix my `<name>` skill: I ran ___, it did ___, I expected ___." That brings them back to this skill in fixing mode, so the exact spot that broke gets fixed.

## Done when
Check these before handing over, and fix any that fail:
- Step 3 passes: the validator output (or the hand checklist, each line marked pass or fail) and the judgment checks are in the handoff, with nothing left failing.
- Every reference file is linked from SKILL.md with a when-to-read line, and every linked file exists.
- Every failure and hidden-knowledge answer from the interview appears in the skill, or you told the user why you cut it.
- The cold read is done and what it found is fixed or raised.
- The road-test plan includes a prompt that should not trigger the skill and one with a key input missing.
