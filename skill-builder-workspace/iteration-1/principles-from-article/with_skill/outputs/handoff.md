Your skill is written: `error-message-copy`. You said to go ahead without checking back, so I've marked every guess I made as an assumption below.

## What I took from the post

These are the principles that change what Claude writes. I kept your author's terms ("the three questions", "dead end", "blame the system, not the person").

1. **The three questions.** "What happened? Why? What now?" A message that can't answer "what now" isn't finished.
2. **No dead ends.** "Every message ends in an action, even if the action is 'try again in a few minutes' or 'contact support with code 4F2'."
3. **Blame the system, not the person.** "You entered an invalid date" becomes "That date isn't in a format we can read. Try 14/03/2026".
4. **Next to the thing that broke.** "The message belongs beside the field", not in a red banner at the top of the form.
5. **Say it once, in plain words.** "No 'Oops!', no 'Uh oh', no apologies stacked three deep. Jokes age badly."
6. **Don't hide the useful detail.** Show the code support needs, "but put it last, after the human sentence."

I left out the opening point that "Error 0x80070057" tells the engineer something. It became the skill's one-line framing rather than a rule of its own.

## What I understood from your message
- **Job:** write new error, validation and empty-state messages, and review existing ones. It's one skill with two modes.
- **Trigger:** picked up automatically. It's not for log messages, exception names or other developer-only text.
- **Output:** the message text. Add one note line only when Claude had to guess what the user can do next.
- **Audience and home:** just you, in Claude Code.

## Assumptions (please check)
1. **Review output.** For an existing message, Claude shows the original, names the checks it fails, and gives the rewrite. A message that already passes gets "Keep as is". You only described the output for writing, so I chose this format for reviews.
2. **Asking vs. guessing.** If Claude doesn't know *what broke*, it asks. If it only doesn't know *what the person can do about it*, it guesses and adds the note. A next step that follows directly from the failure (add the missing @) doesn't count as a guess.
3. **Placement line.** If the request says a message will show far from its cause (a top banner, or a toast for a field error), Claude adds one line suggesting it move beside the field. This is a second possible note on top of the one you asked for. It's the only way the "next to the thing that broke" principle can affect text-only output.
4. **Error codes.** When the next step is "contact support", the code goes at the end of that sentence. That way the message still ends in an action and the code still comes last. Claude never makes up a code. It uses the one you give it or a `{code}` placeholder.
5. **Apologies.** The post only bans *stacked* apologies, so I allowed one short "Sorry" when the system is at fault.
6. **Editing files.** If the messages are in source files and you ask Claude to fix them there, it edits the strings in place and still shows the new copy.
7. **Name.** I named it `error-message-copy`. Your `~/.claude/skills` has nothing with that name (it holds dxe-hiring-manager-bar, find-skills, humanizer, impeccable, structural-humanizer and synced).

## Where it goes
Copy the folder to `~/.claude/skills/error-message-copy/` to use it in every project. That folder already exists, so Claude Code picks the skill up without `/reload-skills`. For this test run it's saved in `outputs/error-message-copy/`.

```text
error-message-copy/
└── SKILL.md
```

There are no reference files or scripts. Everything applies to every run, and nothing in it has one computable answer a script could check.

### error-message-copy/SKILL.md
```markdown
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
```

## Check results

**Validator** (`scripts/validate_skill.py`), run on the final version:
```text
PASSED: 0 error(s), 0 warning(s) in .../outputs/error-message-copy
```
SKILL.md is 47 lines long and the description is 348 characters.

**Judgment checks**
- **Each trigger is a different request: pass.** One trigger is writing new copy and the other is reviewing or rewriting existing copy. The "Not for" line covers the closest wrong request: log messages and exception or error class names.
- **Every instruction is exact or gives its reason: pass.** The fixed parts are exact: the note format, the order of the code, and the check labels. The flexible parts each carry their reason from the post (dead ends make people give up, distant messages make people hunt, jokes age badly).
- **One name per concept: pass.** The skill always says "the three questions", "next step", "error code", "guess note" and "placement line".
- **Definition of done: pass.** There is a checklist for each message. Review mode adds a checkpoint: every original message must get a verdict, so a lazy review can't rewrite only the obvious ones.
- **Assumptions: pass.** All of them are flagged above.

**Cold read.** I gave a fresh subagent only SKILL.md and one test prompt that mixed both modes. The test prompt asked it to fix the "Oops! Something went wrong. Invalid email." banner and to write a timeout message. Its output followed the skill. It also raised 12 points where it was unsure, and I fixed these:
- **Mixed requests:** the skill didn't say how to handle a request that is part writing, part review. It now does, and all notes go once at the end of the reply.
- **"No dead ends" vs. "the three questions":** these overlapped as review labels. Each label now says what it covers.
- **Checks that don't apply:** they are now left out of the review.
- **"Invalid email":** it's now an explicit example of a message that fails "what happened, and why".
- **"You" vs. "your":** the blame test is now about who did the failing, with examples.
- **Guessing:** the skill now says when a next step counts as a guess.
- **Apology:** the skill now says when one is allowed.
- **"Last human sentence":** this was undefined and has been reworded.
- **Title and body:** messages split into a title and a body are covered.
- **Editing source files:** the skill says what to do when the messages live in code.

I didn't add a rule about timeouts possibly creating the account anyway. It's too specific to one case, and the guess note already flags uncertain next steps.

## Road-test plan
Run each prompt in a fresh Claude Code session, at least twice.

1. **Should trigger (review plus write):** "Our signup form shows a red banner at the top saying 'Oops! Something went wrong. Invalid email.' when there's no @. Fix it, and write the message for when the server times out during signup."
   *Success:* the review names the failed checks and the rewrite blames no one. The timeout message ends in a next step. The reply ends with one guess note (about the timeout retry) and a placement line about the banner. There's no "Oops".
2. **Should trigger (empty state, with a code):** "Write the empty-state copy for the Projects page when a user has no projects, and an error for when loading projects fails with code PRJ-503."
   *Success:* the empty state ends in "create your first project" or similar. The error ends with PRJ-503 after the human sentences, and no other code appears.
3. **Missing key input:** "Write me an error message for the upload."
   *Success:* Claude asks what went wrong with the upload instead of making up a failure.
4. **Should not trigger:** "Add a log line in `payment_service.py` when the Stripe webhook signature check fails, and name the exception class."
   *Success:* the skill doesn't load. Claude writes a normal developer log message and exception name, without the three questions or user-facing phrasing.

## If something goes wrong
Come back with: "Fix my `error-message-copy` skill: I ran ___, it did ___, I expected ___." That brings me back in fixing mode, so I change only the part that broke.
