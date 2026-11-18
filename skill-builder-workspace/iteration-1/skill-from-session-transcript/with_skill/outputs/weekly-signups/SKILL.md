---
name: weekly-signups
description: Produces the weekly signups table (ISO week number, signups, % change from the previous week) for the last 6 complete weeks from a signups CSV export, counted the same way as the dashboard. Use when the user asks for the weekly signup numbers or shares signups.csv for the Monday report. Not for other metrics such as activations or revenue, or for ad-hoc signup questions outside the weekly table.
argument-hint: "[path to signups.csv]"
allowed-tools: Bash(python3 *)
---

# Weekly signups

The numbers must match the dashboard. Three rules make them match, and each one was found by a mismatch: drop test accounts, count in Europe/Oslo time rather than UTC, and group by ISO week (Monday start). The bundled script applies all three, so run it rather than writing your own pandas groupby.

## Steps
1. Find the CSV. Use `$ARGUMENTS` if a path was given; otherwise look for `signups.csv` in the working directory. If there is none, ask the user for the file instead of using some other CSV.
2. Run the script:
   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/weekly_signups.py" <path-to-csv>
   ```
   It writes `weekly_signups.md` in the working directory, replacing last week's copy, and prints the table plus diagnostics. Options: `--weeks N` (default 6), `--today YYYY-MM-DD` to report as of another date, `--out <file>` for another output path.
3. If it stops with `missing column(s)`, the export's column names have changed. It expects `created_at` (UTC timestamp) and `email`. Ask the user which columns hold those, because a wrong guess silently gives wrong numbers, then rerun with `--created-col <name> --email-col <name>`.
4. Act on every `WARNING:` line before reporting:
   - **Timestamps could not be parsed**: the line shows up to five raw values. Show them to the user and say the table isn't final until the format is sorted out.
   - **Export ends before the last reported Sunday**: the export was pulled too early and the latest week is undercounted. Ask the user for a fresh export.
   - **Export starts after the baseline week**: the earliest week or the first % change is undercounted. Tell the user which rows are affected.
   Also mention it if `test accounts dropped in reported weeks` is 0, since there are normally some and 0 may mean the export already filtered them or the domain changed.

## What the script does, and why
- **Test accounts.** Any email ending `@example-test.com` (case-insensitive) is an internal account. Counting them was the first mismatch: weeks came out about 25 too high.
- **Timezone.** `created_at` is stored in UTC, but the dashboard uses Europe/Oslo. Signups after 22:00 UTC on a Sunday (23:00 in winter) are already Monday in Oslo, so grouping in UTC puts them in the wrong week. That left each week off by a few.
- **Weeks.** ISO weeks, Monday to Sunday. The table shows the ISO week number only, as the dashboard does; the date-range line under the table pins down the year.
- **Window.** The last 6 complete weeks; the current, partial week is left out. The week before the first reported week (the baseline week) is counted too, so the first row also has a % change.
- **% change.** `(this week - previous week) / previous week`, rounded to one decimal, with a sign (`+4.2%`, `-3.1%`). If the previous week had 0 signups it shows `n/a`.

## Done when
- `weekly_signups.md` exists with columns Week, Signups, % change and one row per reported week (6 unless `--weeks` was given).
- Every `WARNING:` line from the script was resolved or passed on to the user.
- Your reply contains the table, the date range it covers, and the number of test accounts dropped in those weeks, so the user can compare it with the dashboard at a glance.
