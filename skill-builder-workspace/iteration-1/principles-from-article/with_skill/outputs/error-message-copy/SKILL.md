---
name: error-message-copy
description: Writes and reviews user-facing error messages, form validation messages and empty-state copy so each one says what happened, why, and what the person can do next. Use when the user asks for new message copy, or wants existing messages critiqued or rewritten. Not for log messages, exception or error class names, or other text only developers read.
---

# Error message copy

Write for the person looking at the screen, not the engineer who built it. "Error 0x80070057" tells the engineer something and tells the person nothing.

## The rule that matters most: no dead ends
Every message answers the three questions: **What happened? Why? What now?** and ends in a next step. A message with no next step is a dead end, and dead ends are where people give up. The next step can be small ("Try again in a few minutes", "Contact support and give them code 4F2"), but it has to be there. If a message can't answer "what now", it isn't finished.

## Before you write
- **You need to know what broke**: the field, action or screen, and roughly how it failed. If the request doesn't say, ask, because a message about an unknown failure can't answer "what happened".
- **You don't need to be told the next step.** If you know what broke but not what the person can actually do about it (whether retrying helps, whether there is a support channel, which format is accepted), pick the most likely next step, write the message with it, and add the guess note described under Output. The user wants the message now with the guess flagged, not a question back. A next step counts as guessed when nothing in the request or the code you can see confirms it; one that follows directly from the failure (add the missing @ to an email) is not a guess.

## Writing each message
1. **What happened, and why.** One sentence covering both is enough: "That date isn't in a format we can read." A bare label such as "Invalid email" answers neither, because it doesn't say what is wrong with it.
2. **Blame the system, not the person.** "You entered an invalid date" makes someone feel stupid. "That date isn't in a format we can read. Try 14/03/2026" fixes the problem without the finger-pointing. The test is who did the failing: the person must never be the one at fault. "Your account" or "your file" is fine; "you entered", "you forgot", "you didn't" are not.
3. **Next step.** Make it concrete enough to do without thinking: a valid example, how long to wait, where to go. It is the last sentence written for the person; only an error code may follow it.
4. **Say it once, in plain words.** Each of the three questions gets one plain answer, not a restatement. No "Oops!", no "Uh oh", no jokes (they age badly when someone has just lost their work). An apology is optional; if you use one, keep it to a single short "Sorry" where the system is at fault, never a stack of them.
5. **Error code last.** If there is a code support will need, show it rather than hiding it, but after the human sentences. When the next step is contacting support, end that sentence with the code. Use only a code given in the request, or a placeholder such as `{code}`; a made-up code sends support looking for something that doesn't exist.
6. **Next to the thing that broke.** Write validation messages to sit beside the field they're about. If the request says a message will appear far from its cause (a banner at the top of a long form, a toast for a field error), add one placement line suggesting it move beside the field, because a distant message makes people hunt.

**Empty states** follow the same three questions: what happened is "there's nothing here", why is the reason (nothing created yet, a filter hides everything, no access), and what now is the action that fills the screen (create the first item, clear the filter, ask for access). An empty state with no action is a dead end too.

## Output
There are two modes, writing and reviewing, and one request can mix them ("fix this message and write one for the timeout"). Handle each message in the mode that fits it, in the order asked, and put any notes once at the end of the reply.

**Writing a new message** (the user describes a situation and asks for copy): give the message text, ready to paste. If there are several, label each with its case or field. If the UI splits a message into a title and a body, give both, labelled.

**Reviewing an existing message** (the user pastes copy or points at files that contain it): give the original, the checks it fails, and the rewrite. Name failed checks with these labels: the three questions (what happened or why is missing), no dead ends (what now is missing), blame the system, say it once, error code last, next to the thing that broke. Leave out checks that pass or don't apply. A message that passes everything gets "Keep as is", so the user can see it was checked.

**Notes at the end of the reply**, only when they apply:
- If you guessed any next step: `Note: I guessed the next step (<what you assumed>); replace it if that's not what users can do.` One line, covering every guess. No guess, no note.
- The placement line from step 6.

If the messages live in source files and the user asked you to fix them there, edit the strings in place and still show the new copy in the reply.

## Done when
Check every message you wrote or rewrote:
- You can point to the sentence that answers "what now", and only an error code follows it.
- No sentence makes the person the one at fault.
- No "Oops", "Uh oh", joke, or more than one apology; nothing is said twice.
- Every error code from the request appears, after the human sentences, and no code was invented.
- The guess note is there if and only if you guessed a next step.
- In review mode, every original message has a verdict, including the ones that pass. A review that only rewrites the obvious offenders looks finished but isn't.
