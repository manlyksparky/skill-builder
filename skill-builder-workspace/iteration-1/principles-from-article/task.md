Make me a skill from this post so Claude writes error messages the way it describes. It's just for me, in Claude Code. It should kick in whenever I ask Claude to write or review error messages, validation messages or empty-state copy, but not for log messages or exception names in code. Output is the message text, plus a one-line note if it had to guess what the user can do next. Go ahead and write it, no need to check back with me.

---

**Error messages people can act on**

Most error messages fail because they answer a question nobody asked. "Error 0x80070057" tells the engineer something. It tells the person staring at the screen nothing.

I review every message against the three questions: What happened? Why? What now? If a message can't answer "what now", it isn't finished. A message with no next step is a dead end, and dead ends are where people give up. No dead ends: every message ends in an action, even if the action is "try again in a few minutes" or "contact support with code 4F2".

Blame the system, not the person. "You entered an invalid date" makes someone feel stupid. "That date isn't in a format we can read. Try 14/03/2026" fixes the problem without the finger-pointing.

Put the message next to the thing that broke. A red banner at the top of a long form makes people hunt. The message belongs beside the field.

Say it once, in plain words. No "Oops!", no "Uh oh", no apologies stacked three deep. Jokes age badly when someone has just lost their work.

Finally, don't hide the useful detail. If there's a code support will need, show it, but put it last, after the human sentence.
