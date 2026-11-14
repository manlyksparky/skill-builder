# Revise a skill after road-testing

The user ran a skill and it went wrong somewhere. Your job is to fix the exact spot that broke and leave everything that works alone. A full rewrite throws away what the earlier tests proved, so make the smallest change that fixes each failure.

## 1. Gather the inputs

- **The skill.** Read the skill folder from disk if you can. Otherwise ask the user to paste SKILL.md and any reference files or scripts.
- **The failures.** Each one needs three things: what they ran (the exact prompt), what the agent did, and what they expected. If any of the three is missing, ask for it before changing anything. Guessing at a vague report ("it didn't work well") usually fixes the wrong line.

If the user asks for a general rewrite or a performance benchmark instead of fixing specific failures, say this mode is for targeted fixes and ask which failures they've seen.

## 2. Find the layer that broke

Trace each failure to one of four layers:

| What happened | Layer | Where to look |
| --- | --- | --- |
| Didn't open for a request it should handle, or opened for one it shouldn't | Door | The `description`: missing trigger, triggers that are too broad, no "Not for" line |
| Opened, but skipped a reference file or used a script wrongly | Map | The pointer: is it there, does it say exactly when to read the file, is it buried below where the agent stopped reading? |
| Took a wrong step, picked the wrong format, ignored a rule | Path | That instruction: should it be exact instead of a direction, or is it missing the reason that would have stopped the mistake? |
| Stopped early, or claimed it was done when it wasn't | Finish Line | The definition of done: is there a check the agent can see is met, and a checkpoint where it could fake progress? |

If one failure seems to involve two layers, fix the earlier one first (Door comes before Map, Map before Path). Downstream symptoms often disappear once the upstream cause is fixed.

## 3. Make the change

- Edit only the lines tied to the failure. Keep the skill's existing names for things; introducing a second name for the same concept causes new failures.
- For a Door fix, check the new description against the other requests the skill should and shouldn't take. A wider trigger can start catching requests that belong to another skill.
- Then run Step 3 (Check) from SKILL.md on the revised skill.

## 4. Report back

For each failure, show:

1. **Failure:** the prompt, and what happened.
2. **Cause:** the layer, and the line responsible.
3. **Change:** the old and new text.

Then give the updated files, saved or shown as in Step 4 of SKILL.md, and add one regression prompt per fixed failure to the road-test plan: the original failing prompt, plus what success now looks like. Ask the user to rerun it in a fresh session.
