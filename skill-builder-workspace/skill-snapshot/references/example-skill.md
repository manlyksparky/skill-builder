# Worked example

Use this to calibrate the level of detail, not as a template to copy. The skill you write should be shaped by the interview, not by this file.

## A complete small skill

~~~~markdown
---
name: retro-actions
description: Turns sprint retrospective notes into one tracker ticket per action item, with owner and due date, as a CSV ready to import. Use when the user shares retro notes or a retro board export, or asks to file the retro actions. Not for summarising a retro or writing meeting minutes.
---

# Retro actions

Every action item becomes exactly one ticket. An item nobody owns doesn't get done, so an item without an owner goes back to the user instead of being filed.

## Steps
1. Pull out the action items. An action item is something a named person or team committed to do. Discussion points, kudos and complaints are not action items, even when phrased as "we should…". If you can't tell, list it under "Unclear" for the user to decide.
2. Fill the fields for each item as described in references/ticket-fields.md. Titles start with a verb ("Add alert for failed payouts"), because the tracker's search and the team's board both scan the first word.
3. Write the items to `items.json`, then run this skill's script on it:
   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/to_csv.py" items.json > tickets.csv
   ```
   The importer rejects files whose columns are out of order; the script fixes the order so you don't have to. If you can't run code, write the CSV by hand with the columns in the order listed in references/ticket-fields.md.

## Done when
- The counts add up: items found = rows in tickets.csv + "Unclear" + "No owner". Show the user all four numbers.
- Every row has an owner and a due date.
- "Unclear" and "No owner" are listed by name so the user can resolve them in one reply.
~~~~

### Why it's built this way

- **Door.** The description says what it does first ("Turns…"), names two different ways people ask for it, and has a "Not for" line, because "summarise the retro" is the request most likely to open it by mistake.
- **Map.** The field rules only matter at step 2, so they live in a reference file with a pointer that says exactly when to read it. The column order is fragile and computable, so a script handles it instead of prose.
- **Path.** "Action item" gets one definition and keeps that name throughout. The rule about verb-first titles comes with its reason, so the agent can handle an edge case the rule doesn't cover.
- **Finish Line.** A lazy run would file the obvious items and skip the ambiguous ones. The count check makes a skipped item visible.

## Descriptions: before and after

**1. Too vague to trigger**

```text
Before: A helpful skill for retros.
After:  Turns sprint retrospective notes into one tracker ticket per action item ... Not for summarising a retro or writing meeting minutes.
```

The "before" gives the agent nothing to match a request against. The "after" states the output and the input, and rules out the nearest wrong request.

**2. Several phrasings of one trigger**

```text
Before: Use this when the user wants to write release notes, create release notes, draft release notes, or make a changelog.
After:  Writes release notes in the house style from merged PRs or a commit range. Use when the user asks for release notes or a changelog for a version. Not for writing individual PR descriptions.
```

The agent already knows "write", "create" and "draft" mean the same thing. Spend the words on what the skill does and on the request it shouldn't take.

**3. Shouting**

```text
Before: IMPORTANT: You MUST use this skill for ANY database question!!!
After:  Answers questions about the orders database using the approved read-only queries. Use when the user asks for order counts, revenue or customer lookups. Not for schema changes or writing migrations.
```

Capitals and "any" make newer models open the skill for everything nearby. A calm, specific description triggers more accurately.
