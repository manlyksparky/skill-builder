# skill-builder

An agent skill that writes other agent skills. You describe what you want a skill to do, it interviews you until it understands the job, writes the `SKILL.md` (plus any reference files and scripts), checks the result, and hands it over with a plan for testing it. When a test goes wrong, bring the failure back and it fixes the exact spot that broke.

Most skills that don't work fail in predictable ways: a vague description that never triggers, instructions that read like generic advice, frontmatter a platform rejects, no clear point where the agent knows it's finished. This skill is built to catch those before the draft reaches you.

## What it does

The skill has two modes.

### New skill

**1. Interview.** If you've already done the task in the conversation, or you paste a spec or an example, it fills in what it can from that and asks only about the gaps. Otherwise it asks 3–5 questions at a time, offers its best guess so you can just confirm, and aims to be done in three rounds. It covers:

| Topic | What it's trying to pin down |
| --- | --- |
| Scope | The single job the skill does. If you're describing several jobs, it suggests splitting them. |
| Invocation | Whether the skill triggers automatically or only by name, and which requests should and shouldn't open it. |
| Inputs and outputs | What goes in and exactly what comes out: files, names, format, location. |
| Fragile vs. flexible | Which parts have one right answer, and where judgment is fine. |
| Branches | Whether there are modes or request types that need their own instructions. |
| Done | How the agent knows it's finished, and what a lazy run that only looks finished would look like. |
| Failures | Real cases where an agent got this wrong without a skill. |
| Hidden knowledge | Conventions and gotchas the agent couldn't discover by looking. |
| Vocabulary | Shorthand that carries a whole standard ("8pt grid", "think Tufte") and one name per concept. |
| Where it runs | Claude Code, claude.ai, the API, or several. This decides which frontmatter fields are allowed. |

Say "just write it" at any point and it fills the rest with marked assumptions. Before writing anything, it summarises what it heard and asks you to confirm.

**2. Write.** It drafts the skill against four checks:

- **The Door** (frontmatter): a name and description that make the agent open the skill for the right requests and leave it closed for near-misses.
- **The Map** (structure): what every run needs stays in `SKILL.md`; branch-specific detail moves to `references/`, deterministic steps move to `scripts/`, and templates go in `assets/`.
- **The Path** (instructions): exact wording only where a different choice would give a wrong result; everywhere else, a direction and the reason behind it.
- **The Finish Line**: a definition of done the agent can verify, with checkpoints where it could otherwise skip the work and still look finished.

It then cuts every line that wouldn't change what the agent does.

**3. Check.** Where it can run code, it runs the bundled validator on the draft. Elsewhere it goes through the same rules by hand. Either way it adds judgment checks that no script can make (distinct triggers, a reason for every instruction, a verifiable definition of done).

**4. Hand off.** It saves the skill where your environment expects it, after checking that the name isn't already taken. You get the files, the check results, any open assumptions, and a road-test plan: 2–3 realistic prompts (including one that should *not* trigger the skill) with what success looks like for each.

### Fixing a skill after testing

Come back with a specific failure:

> Fix my `release-notes` skill: I ran "draft the changelog for 2.4", it didn't open, I expected it to write release notes.

It traces each failure to one layer (Door, Map, Path or Finish Line), changes only the lines responsible, re-runs the check, and adds the failing prompt to your road-test plan as a regression test. If a report is missing what you ran, what happened or what you expected, it asks before changing anything.

## The validator

`skill-builder/scripts/validate_skill.py` uses only the Python standard library and works on any skill folder, not just ones this skill wrote:

```bash
python3 skill-builder/scripts/validate_skill.py path/to/my-skill
```

**Errors** (exit code 1):
- Missing frontmatter.
- `name` uses characters other than lowercase letters, digits and single hyphens, is over 64 characters, contains `anthropic` or `claude`, or doesn't match the folder name.
- `description` is missing, over 1,024 characters, or contains `<` or `>`.
- An unknown frontmatter field.
- A `references/`, `scripts/` or `assets/` path that SKILL.md names but that doesn't exist.

**Warnings:**
- A Claude Code-only field (claude.ai and the API will reject the upload).
- SKILL.md over 500 lines.
- Bundled files that SKILL.md never mentions.
- References that point to other references.
- Long reference files without a table of contents.
- Instructions shouted in capitals.

## Installation

### Claude Code

Copy the `skill-builder` folder into your skills directory.

For all projects:

```bash
git clone https://github.com/manlyksparky/skill-builder.git
mkdir -p ~/.claude/skills
cp -r skill-builder/skill-builder ~/.claude/skills/
```

For a single project, copy it into that project's `.claude/skills/` folder instead. Claude Code picks up new skills in the current session. If the `skills` folder didn't exist when the session started, run `/reload-skills`.

### Claude.ai

1. Zip the inner `skill-builder` folder so that the folder (not loose files) sits at the root of the zip.
2. Go to **Customize → Skills**, click **+**, then **Create skill → Upload a skill**, and choose the zip.
3. Switch the skill on. Code execution needs to be enabled in your settings for skills to run.

### Other agents

The skill uses only the portable frontmatter fields, so any agent that supports the `SKILL.md` format can load it from its usual skills location.

## Usage

Ask for a new skill in plain language:

> I want a skill that turns our sprint retro notes into a ticket for each action item.

> Turn what we just did into a skill.

> Help me build a skill for writing release notes in our house style.

You don't need a fully formed idea. If you haven't stated a goal, the skill will ask for one.

**What it isn't for:** benchmarking a skill, running evals on one, or rewriting an existing skill wholesale.

## Testing the skill you get

The output is a first draft, so test it before relying on it:

1. Run each road-test prompt from the handoff in a **fresh session**, at least twice.
2. Check that the negative prompt doesn't open the skill.
3. When something goes wrong, note what you ran, what the agent did, and what you expected.
4. Bring it back in that form ("Fix my `<name>` skill: I ran…, it did…, I expected…") so the exact line that broke gets fixed.

## Repository layout

```
skill-builder/
├── skill-builder/
│   ├── SKILL.md                 # the skill: modes, interview, writing rules, check, handoff
│   ├── references/
│   │   ├── revise.md            # fixing mode, read after road-test failures
│   │   ├── example-skill.md     # worked example and description before/after pairs
│   │   └── packaging.md         # where to save, frontmatter fields, script rules
│   └── scripts/
│       └── validate_skill.py    # stdlib-only skill validator
├── LICENSE
└── README.md
```

## License

[MIT](LICENSE) © 2026 Victor Adeyemo
