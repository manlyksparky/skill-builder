Your `error-messages` skill is written and it passes the checks. Since it's just for you in Claude Code, it belongs in `~/.claude/skills/error-messages/`, which makes it available in every project. Nothing else in your skills folder is called `error-messages`, so it won't clash with an existing skill.

(For this test run, I saved it to `old_skill/outputs/error-messages/SKILL.md` and left `~/.claude` alone.)

## What I took from your message and the post

- **When it runs:** it picks itself up when you ask Claude to write, rewrite or review error messages, validation messages or empty-state copy. It doesn't run for log messages or exception names.
- **What it returns:** the message text. If Claude had to guess what the user can do next, it adds one line after the message that starts `Assumed:`.
- **The rules, all from the post:**
  - Every message answers three questions: what happened, why, and what now. "What now" can never be left out.
  - Every message ends in an action.
  - The message blames the system, not the person.
  - The message goes next to the field that broke.
  - No "Oops", jokes or stacked apologies.
  - Any support code goes last.

## Assumptions (I filled these in without checking with you)

1. **Empty states:** the post doesn't mention them. I applied the same three questions: what's here (nothing yet), why, and the action that fills the screen.
2. **Reviews:** the skill returns the rewritten message plus a short line naming the rule the original broke. A message that already passes is left as it is. Your message only covered writing, so this format is my guess.
3. **Placement:** your output is text only, so the skill mentions placement only when the request or code shows a message away from its field. For example, a banner at the top of a form.
4. **Apologies:** the post says "no apologies stacked three deep". I read that as allowing at most one short apology.
5. **Format examples:** when a message shows an example (like "Try 14/03/2026"), it has to use the format your product accepts. If Claude doesn't know that format, it guesses and adds an `Assumed:` line.
6. **Name:** I called it `error-messages`, because that's how you'd describe the job.

## Check results

Validator (`scripts/validate_skill.py`):
```
PASSED: 0 error(s), 0 warning(s) in .../outputs/error-messages
```
SKILL.md is 42 lines long.

Checks the validator can't do:
- **Pass:** each trigger is a different request: writing a message, reviewing one, and empty-state copy. The "Not for" line covers the closest wrong requests, which are log messages, exception and class names, and other text only developers read.
- **Pass:** every instruction is either exact or explains why. For example, a real format example is quicker to copy than a description of the rule, and jokes age badly when someone has just lost their work.
- **Pass:** each idea has one name all the way through: "message", "what now", and the "`Assumed:` line".
- **Pass:** the skill ends with a "Done when" list that Claude checks each message against. The obvious shortcut is a message that sounds fine but has no next step. The "ends in a concrete action" line catches that, and so does the rule that every guess needs an `Assumed:` line.
- **Flagged:** the assumptions above are open for you to confirm.

## SKILL.md

`~/.claude/skills/error-messages/SKILL.md`
```markdown
---
name: error-messages
description: Writes and reviews user-facing error messages, validation messages and empty-state copy so each one tells the person what happened, why, and what to do next. Use when the user asks to write, rewrite or review the wording of an error, a form validation message or an empty state in a product. Not for log messages, exception or error class names, or other text only developers read.
---

# Error messages

A message is for the person looking at the screen, not the engineer. Every message answers three questions: **What happened? Why? What now?** "What now" is the one that can never be missing. A message with no next step is a dead end, and dead ends are where people give up. So every message ends in an action, even if that action is "Try again in a few minutes" or "Contact support with code 4F2".

## Writing a message

Build each message in this order:

1. **What happened**, in plain words the person would use. "We couldn't save your changes", not "Write operation failed".
2. **Why**, if you know it. Keep it to a clause; often it folds into the first sentence ("That date isn't in a format we can read").
3. **What now**: one concrete action. If there's an expected format, show a real example of it ("Try 14/03/2026"), because an example is quicker to copy than a description of the rule. Use the format the product actually accepts; if you don't know it, guess and flag it in an `Assumed:` line (see below).
4. **The code, last.** If there's an error code or reference support will need, keep it, but put it after the human sentences.

Rules that apply to every message:

- **Blame the system, not the person.** The thing that failed is the subject of the sentence, not "you". "You entered an invalid date" makes someone feel stupid; "That date isn't in a format we can read. Try 14/03/2026" fixes the problem without the finger-pointing.
- **Say it once, in plain words.** No "Oops!", no "Uh oh", no jokes, at most one short apology. Jokes age badly when someone has just lost their work.
- **Put it next to the thing that broke.** A validation message belongs beside its field, not in a banner at the top of the form, where people have to hunt for the problem. If the request or code shows a message placed away from its field, say so.

**Empty states** follow the same three questions: what's here (nothing yet), why (e.g. no projects created, or a filter hides everything), and what now (the action that fills it, such as "Create your first project" or "Clear filters").

## What to return

- **Writing:** the message text only, one per message requested. Where there are several, label each with the situation it's for.
- **Reviewing:** for each message, the rewritten text plus a short line naming which rule the original broke. If a message already passes, say so and leave it alone.
- **The `Assumed:` line:** if you had to guess what the person can do next (the action, a format, a support channel, a wait time), add one line after the message starting `Assumed:` that names the guess, so the user can correct it. No guess, no line.

## Done when

Before returning, check every message against this list. A message that fails any line isn't finished:

- It says what happened in words a non-engineer would use.
- It ends in a concrete action the person can take. "Something went wrong" with nothing after it fails.
- The person is not the subject of the fault.
- No "Oops", "Uh oh", jokes, or stacked apologies.
- Any code or reference number comes after the human sentences.
- Every guessed action, format or channel has an `Assumed:` line.
```

## Road-test plan

Run each prompt in a fresh session, at least twice.

1. **"Write the error message for when a file upload fails because it's over 25 MB."**
   - The skill should run.
   - The message should say what happened and why, then end in an action, such as making the file smaller or choosing a different one.
   - It shouldn't blame the user or open with "Oops".
   - If Claude made up a limit or an action, there should be an `Assumed:` line.
2. **"Review these: 'Invalid input.' / 'Oops! Something went wrong :(' / 'You forgot to enter your email.'"**
   - The skill should run.
   - You should get a rewrite for each message, with one line naming the rule it broke.
   - None of the rewrites should be a dead end.
   - "You forgot" should become a sentence about the field, not the person.
3. **"Add a log line and a custom exception class for when the payment webhook fails signature verification."**
   - The skill should *not* run. This text is for developers.
   - The log line and the class name should read like normal engineering text, without user-facing wording such as "Try again in a few minutes".

## If something goes wrong

Come back with: "Fix my `error-messages` skill: I ran ___, it did ___, I expected ___." That puts this skill builder in fixing mode, so it fixes the exact part that broke.
