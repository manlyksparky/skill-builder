# skill-builder

An agent skill that writes other agent skills. You describe what you want a skill to do, it interviews you until it understands the job, and then it writes the `SKILL.md` (plus any reference files) for you.

Most skills that don't work fail in predictable ways: a vague description that never triggers, instructions that read like generic advice, no clear point where the agent knows it's finished. This skill is built to catch those before the draft reaches you.

## What it does

The skill runs in three steps.

**1. Interview.** It asks 3–5 questions at a time, only about things it can't work out on its own, and offers its best guess so you can just confirm. It covers:

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

Before writing anything, it summarises what it heard and asks you to confirm.

**2. Write.** It drafts the skill against four checks:

- **The Door** (frontmatter): a name and description that make the agent open the skill for the right requests and leave it closed for near-misses.
- **The Map** (structure): what every run needs stays in `SKILL.md`; branch-specific detail moves to `references/` with an explicit pointer to when it should be read.
- **The Path** (instructions): exact wording only where a different choice would give a wrong result; everywhere else, a direction and the reason behind it.
- **The Finish Line**: a definition of done the agent can verify, with checkpoints where it could otherwise skip the work and still look finished.

It then cuts every line that wouldn't change what the agent does.

**3. Hand off.** You get the full `SKILL.md` and reference files, each with its path, plus a short road-test plan: 2–3 realistic prompts (including one that should *not* trigger the skill) and what success looks like for each.

## Installation

### Claude Code

Copy the `skill-builder` folder into your skills directory.

For all projects:

```bash
git clone https://github.com/manlyksparky/skill-builder.git
mkdir -p ~/.claude/skills
cp -r skill-builder/skill-builder ~/.claude/skills/
```

For a single project, copy it into that project's `.claude/skills/` folder instead.

Start a new session and the skill will be available.

### Claude.ai

Zip the inner `skill-builder` folder (the one containing `SKILL.md`) and upload it under **Settings → Capabilities → Skills**.

### Other agents

The skill is a single Markdown file with YAML frontmatter, so any agent that supports the `SKILL.md` format can load it from its usual skills location.

## Usage

Ask for a new skill in plain language. For example:

> I want a skill that turns our sprint retro notes into a Linear ticket for each action item.

> Help me build a skill for writing release notes in our house style.

> Make a skill that reviews Figma handoff specs before they go to engineering.

You don't need a fully formed idea. If you haven't stated a goal, the skill will ask for one.

**When it won't trigger:** the skill is for creating a *new* skill from a goal. It isn't meant for editing an existing skill or benchmarking one's performance.

## Testing the skill you get

The output is a first draft, so test it before relying on it:

1. Run each road-test prompt from the hand-off in a **fresh session**, at least twice.
2. Check the negative prompt doesn't open the skill.
3. When something goes wrong, note what you ran, what the agent did, and what you expected.
4. Bring those specifics back so the exact line that broke gets fixed, rather than rewriting the whole skill.

## Repository layout

```
skill-builder/
├── skill-builder/
│   └── SKILL.md      # the skill itself
├── LICENSE
└── README.md
```

## License

[MIT](LICENSE) © 2026 Victor Adeyemo
