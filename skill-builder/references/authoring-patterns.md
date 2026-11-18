# Authoring patterns

Source: Anthropic, "Skill authoring best practices" (platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), read November 2026. Paraphrased. This file keeps only what isn't already in SKILL.md. Where the two disagree, follow SKILL.md; the one disagreement is noted in the last section.

Contents: Concision · Degrees of freedom · Naming and files · Workflows and feedback loops · Output formats · Scripts · Tools and environment · Content that ages · Reading the signs after a test

## Concision
The context window is "a public good": every line of SKILL.md competes with the conversation, the system prompt and every other skill's description. Start from "Claude is already very smart" and add only what the agent lacks. Cut explanations of what a PDF is, that libraries exist, or how to install one. A heading, one sentence and a three-line code block (about 50 tokens) does the job of a 150-token explanation.

## Degrees of freedom
Match the form of an instruction to how fragile the step is. The source's picture: a narrow bridge with cliffs on both sides needs guardrails; an open field needs only a direction.

| Freedom | Form | Use when | Example |
| --- | --- | --- | --- |
| High | Prose directions | Several approaches are valid and context decides | Steps for a code review |
| Medium | Pseudocode or a script with parameters | A preferred pattern exists, some variation is fine | A report function with format options |
| Low | One exact command, plus "don't change the command or add flags" | The step is fragile, order matters, or results must be identical | A database migration |

This is the interview's fragile-vs-flexible answer turned into a choice of form, not just wording.

Give one default and an escape hatch for the known exception, never a menu: "Use pdfplumber. For scanned PDFs that need OCR, use pdf2image with pytesseract instead."

## Naming and files
- Names in gerund form read well (`processing-pdfs`); noun phrases (`pdf-processing`) and verb forms (`process-pdfs`) are fine too. Avoid vague names (`helper`, `utils`, `tools`) and generic ones (`documents`, `data`). Match the pattern of the user's other skills.
- Bundled file names say what's inside: `form_validation_rules.md`, not `doc2.md`.
- When a skill covers several domains, give each domain its own reference file (finance, sales, product), so a sales question never loads the finance material.

## Workflows and feedback loops
- For a task with several steps, number them and give a checklist the agent copies into its reply and ticks off. Clear steps stop it skipping validation.
- Make loops explicit: "If verification fails, return to step 2."
- Feedback loop: run the check, fix, repeat. "Only continue when validation passes."
- **Plan-validate-execute** for batch, destructive or high-stakes work: the agent writes a plan file (e.g. `changes.json`), a script validates the plan, the agent executes it, then verifies. Errors surface before anything changes.
- Validation messages name the problem and the way out: "Field 'signature_date' not found. Available fields: …".
- When a skill has branches, route at the top: "Creating new content → creation workflow. Editing existing content → editing workflow."

## Output formats
- Strict format (an API response, a data file): give the exact template and say it is exact.
- Flexible format: present the template as a sensible default and say to adjust sections as needed.
- When quality depends on style (commit messages, copy), give 2–3 input/output pairs. Examples show style better than descriptions do.

## Scripts
- **Solve, don't defer.** A script handles the errors it can expect (missing file, no permission) and prints a clear message. One that crashes leaves the agent to improvise.
- **No voodoo constants.** Every number in a script has a comment with its reason: `REQUEST_TIMEOUT = 30  # most requests finish within 30 s`. An unexplained `TIMEOUT = 47` gets "fixed" by the next reader.
- Say whether the agent should run the script or read it as reference. Running is the usual case, and only the output costs context.
- Don't assume a package is installed: give the install command, or stick to the standard library. The API has no network or package installs; claude.ai can install from PyPI and npm.
- If an input can be rendered (PDF pages, slides), converting it to images and having the agent look can beat parsing it.

## Tools and environment
- MCP tools: write the fully qualified name, `ServerName:tool_name` (e.g. `GitHub:create_issue`). Without the prefix the agent may not find the tool when several servers are connected.
- Use forward slashes in every path. Backslashes break on Unix.
- A reference file over 100 lines starts with a contents line, because the agent may read only the top of it.

## Content that ages
Don't write instructions that depend on a date ("before August 2025, use the old API"). Put the current method in the body. If the old one must stay, put it under a clearly labelled section such as "Legacy v1 API (deprecated 2025-08)".

## Reading the signs after a test
Use this table in fixing mode, when you have a transcript or notes from a test run:

| What the agent did | Likely cause | Fix |
| --- | --- | --- |
| Read files in an unexpected order | The structure doesn't match how the task unfolds | Reorder, and put the routing at the top |
| Never opened a reference it needed | The pointer is vague or buried | Make the when-to-read line explicit and move it up |
| Read the same file again and again | That content is needed on every run | Move it into SKILL.md |
| Never used a bundled file | It isn't needed, or nothing points to it | Delete it, or add a pointer |

- Test on every model the skill will run on. A smaller model may need more detail, and a larger one may be over-instructed by the same text.
- **Where this file and SKILL.md disagree:** the source suggests switching to stronger wording (`MUST`) when the agent misses a rule. SKILL.md says capitals make newer models overreact. So first move the rule higher and add its reason. Only make the wording firmer if a re-test still misses it, and keep it in a normal tone.
