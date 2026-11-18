# Packaging and saving a skill

## Before you save: check the name

Two skills with the same name shadow each other, and the user won't see which one ran. List the existing skill folders in the target location, or ask the user if you can't see them. If the name is taken, propose a different one rather than overwriting.

## Where to save

Work out the environment from what you can do, not from what the user calls it:

| Environment | How to tell | Where the skill goes |
| --- | --- | --- |
| Claude Code | You can write files and see a `.claude` folder or the user's home directory | `~/.claude/skills/<name>/` for all projects, or `.claude/skills/<name>/` inside one project. Ask which one if the interview didn't settle it. Changes are picked up in the current session. If the top-level `skills` folder didn't exist when the session started, tell the user to run `/reload-skills`. |
| claude.ai (web or desktop chat) | You have a code sandbox but no access to the user's machine | Build the folder in the sandbox and zip it so the folder `<name>/` sits at the root of the zip, not loose files. The user uploads it under **Customize → Skills → + → Create skill → Upload a skill**, then switches it on. Code execution has to be on in their settings for skills to work. |
| Anything else | You can't write files | Show each file in its own code block headed with its path, and give the folder structure as a tree. |

A skill doesn't sync between claude.ai, the API and Claude Code. Each one needs its own copy.

## Frontmatter fields

These six work everywhere: `name`, `description`, `license`, `compatibility` (max 500 characters), `metadata` (a free-form map) and `allowed-tools`.

Claude Code accepts more, but **claude.ai and the API reject the upload** if any of them appear. Only use them when the skill is for Claude Code alone:

| Field | What it does |
| --- | --- |
| `disable-model-invocation: true` | Only runs when the user calls it by name |
| `user-invocable: false` | Hidden from the `/` menu; only the agent can open it |
| `when_to_use` | Extra trigger text appended to the description |
| `argument-hint` | Autocomplete hint, e.g. `[issue-number]` |
| `arguments` | Named arguments for `$name` substitution in the body |
| `disallowed-tools` | Tools removed while the skill is active |
| `model`, `effort` | Model or effort level for the turn |
| `context: fork`, `agent`, `background` | Run the skill in a subagent |
| `paths` | Glob patterns that limit when the skill activates |
| `hooks`, `shell` | Hooks to register; shell for inline commands |

## Scripts and assets

- Use a script when a step has one computable right answer (a format, a column order, a validation). The agent runs it and only the output enters its context, so it's cheaper and more reliable than prose for that step.
- Say in SKILL.md whether to **run** the script or **read** it, and give the exact command.
- Point to scripts by their place in the skill folder. In a skill only for Claude Code, write the path as `${CLAUDE_SKILL_DIR}/scripts/<file>`, so it works from any working directory.
- Prefer the Python standard library. On the API there's no package installation and no network, and on claude.ai network access depends on the user's settings.
- Never put credentials in a script or in SKILL.md. Read them from environment variables, and say in SKILL.md which variables the user needs to set.
- Say what the agent should do if the script can't run, e.g. "If you can't run code, do the same checks by hand using the list in Step 3."
- `assets/` holds files the skill copies or fills in (templates, boilerplate, images). The agent uses them as they are and doesn't read them as instructions.
- Use forward slashes in every path.
