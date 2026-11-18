---
name: weekly-signups
description: Produces the weekly signup report from a signups CSV export, counting signups per ISO week in Europe/Oslo time with test accounts removed, and writes weekly_signups.md with week number, signups and % change. Use when the user shares signups.csv or asks for this week's or the last few weeks' signup numbers. Not for other metrics (revenue, churn, activation) or for a one-off signup query with different rules.
---

# Weekly signups

The numbers must match the signups dashboard. The dashboard counts in Europe/Oslo time with ISO weeks starting Monday and leaves out our test accounts. Counting in UTC moves Sunday-evening signups (22:00–00:00 UTC) into the next week, and keeping test accounts inflates every week, so these three rules are fixed:

- Drop every row whose email ends with `@example-test.com` (case-insensitive). Those are our own test accounts.
- `created_at` is in UTC. Convert it to `Europe/Oslo` before assigning a week.
- Group by ISO week (Monday start). The week label is the ISO week number.

The script below applies all three. Use it rather than writing pandas code each time, so the rules can't drift.

## Steps
1. Find the export. Default is `signups.csv` in the working directory; if the user named another file, use that.
2. Run:
   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/weekly_signups.py" signups.csv
   ```
   It writes `weekly_signups.md` in the working directory and prints the same table plus a reconciliation.
   - "Last 6 weeks" means the 6 complete ISO weeks before the current one, because on a Monday the current week has almost no data. The script also counts one earlier week so the first row has a % change.
   - If the user asks for a different number of weeks, add `--weeks N`. To reproduce a past report, add `--as-of YYYY-MM-DD` (any day in the week after the last week you want).
   - If the script stops with "column(s) not found", it lists the file's columns. Pick the email and UTC timestamp columns and rerun with `--email-col` and `--date-col`.
3. Show the user the table and the reconciliation lines.

## Table format
Columns are exactly `Week | Signups | % change`. % change is against the previous week, rounded to one decimal with a sign (`+2.1%`), and `n/a` when the previous week had 0. The script produces this; if you edit the table by hand, keep that format.

## Done when
- `weekly_signups.md` exists and has one row per requested week (6 by default).
- The reconciliation's `balanced` line says `yes`: rows read = test accounts + unparseable + outside window + counted.
- `test accounts` is above 0. If it is 0, or the script prints a WARN, tell the user before handing over: the email column or the export is probably wrong, and the numbers won't match the dashboard.
- Any `unparseable date` rows are reported with the examples the script prints, not silently left out.
