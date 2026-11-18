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
