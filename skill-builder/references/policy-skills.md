# Policy skills

Source: Claude Academy, "Skills as institutional knowledge" (AI-native SDLC playbook), November 2026. Paraphrased.

Read this when the skill encodes a rule that a team or organisation must apply the same way every time: a security standard, an API convention, a brand or legal rule.

## Is a skill the right tool?
A skill fits institutional knowledge: rules that must be applied consistently, kept under version control, and updated in one place when the policy changes. Working knowledge about one repo (build commands, folder layout) belongs in CLAUDE.md. A one-off preference belongs in the prompt. If the request is really one of those, say so before the interview goes further.

## Extra interview questions
Add these to Step 1:
- **Owner.** Who owns the policy? It should be a named person or team, and they sign off on every change to the skill.
- **Source of truth.** Where is the written policy? Write the skill from that document (quote it in Step 0), never from memory or a paraphrase. A skill whose text drifts from the policy enforces the wrong rule with full confidence.
- **Strength.** Must the rule always hold, or is "almost always" enough? The answer decides whether the skill needs enforcement behind it (below).
- **Scope.** Which tasks and files does it apply to? These become the triggers in the description and the paths the check covers.

## Writing the rules
- Make each rule imperative, specific and checkable. "Every endpoint requires the gateway JWT; no anonymous routes except /health" can be checked. "Keep endpoints secure" can't.
- Number the rules so checks and reviewers can cite them ("rule 4").
- End with output someone can verify: run the policy's check script and include its output in the summary.

The source's example is a `secure-api-review` skill. Its description triggers on creating or changing an external endpoint, reviewing API code, or writing an OpenAPI spec. The body has four numbered rules:
1. Authentication: the gateway token is required on every endpoint.
2. Input validation: request bodies are checked against the schema, and unknown fields are rejected.
3. Audit: every state-changing call emits an audit event with actor, action, entity and time.
4. Data classification: fields tagged `pii` never appear in logs or error messages.

It finishes by running the check script and including the result.

## A skill is advisory
"A skill is a control, though an advisory one." It makes violations rare, but nothing forces a session to follow it. If the owner says the rule must always hold, recommend a deterministic layer in the handoff, built on the same check script:

- **Hook (Claude Code only).** A `PostToolUse` hook on `Edit|Write`, limited to the policy's paths. When a check fails, the hook exits with code 2 and a message naming the rule and `file:line`. A post-edit hook can't undo the edit, but exit code 2 shows the message to Claude, which then fixes the line.
- **Required CI check on pull requests.** An `Edit|Write` hook doesn't fire when a shell command rewrites a file, so the PR check catches what the hook misses.
- **Keep hooks fast and scoped to the changed file.** Heavy checks such as the full test suite belong at commit or PR. Don't put human approval prompts in hooks that run during the build: they put a person on the critical path of every parallel session. Approvals belong at the deploy stage.

The skill tells the agent to run the check, the hook runs it after each edit, and CI runs it on each PR, all with one script. Hooks and CI are configuration outside the skill folder, so offer them as optional extras and let the user decide.

## Where it lives
For one repo, put it in the repo's `.claude/skills/<name>/` so it ships and is versioned with the code. For the whole organisation, distribute it as a plugin. People get the new version in their next session.

## Road-test and measure
- **Trigger test.** Ask for the task in several genuinely different ways (create an endpoint, review API code, write a spec) and confirm the skill loads every time. Put these prompts in `evals.md`.
- **What the owner should watch:**
  - Leading signal: the time from a policy change being approved to the skill change being merged.
  - Lagging signal: PR review findings that cite the policy. These should fall towards zero.
  - If the findings don't fall, either the skill isn't triggering or its text has drifted from the policy.
