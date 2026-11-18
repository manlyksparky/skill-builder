# Your `weekly-signups` skill is ready

I turned yesterday's session into a skill. It's saved as `weekly-signups/` (in a real run this goes to `~/.claude/skills/weekly-signups/`, so it's available in every project; no other skill there has that name). From now on, saying "do the weekly signup numbers" or `/weekly-signups signups.csv` gives you the table in one step.

## What I took from your session
- **Drop test accounts.** Any email ending `@example-test.com`. This was the first fix: Week 41 went from 312 to 287.
- **Count in Oslo time.** `created_at` is UTC and the dashboard is Europe/Oslo. Late-Sunday UTC signups belong to the next week.
- **ISO weeks, starting Monday.** With all three rules in place, the numbers matched the dashboard.
- **Output.** A table in `weekly_signups.md` with week number, signups, and % change from the previous week, rounded to one decimal.

All of this lives in a small Python script that uses only the standard library, no pandas needed. The skill tells Claude to run the script instead of rebuilding the grouping by hand each week. Rebuilding by hand is how the UTC mistake happened.

## Assumptions I made (you weren't around, so please check these)
1. **"Last 6 weeks" means the last 6 complete ISO weeks.** The week in progress is left out, since on a Monday it's nearly empty.
2. **The first row has a % change too.** The script also counts the week before the first reported week to make that possible. If that week's count is 0, the cell shows `n/a`.
3. **% change has a sign** (`+4.2%`, `-3.1%`) and uses the formula (this week - last week) / last week.
4. **Columns are `created_at` and `email`.** The session only implied the email column's name. If the export uses other names, the skill asks you which columns to use and passes them as `--created-col` / `--email-col`.
5. **Test-account matching ignores case** and only checks the email ending.
6. **Timestamps without a timezone are read as UTC.** The session said `created_at` is UTC.
7. **The Week column shows just the ISO week number**, as in the session ("Week 41"). A line under the table gives the date range, which settles the year around New Year.
8. **`weekly_signups.md` is replaced each run.** It's written to the working directory, and `--out` gives you a different file name.
9. **The skill triggers automatically** when you ask for weekly signups, and you can also call it by name. It's a personal skill for Claude Code only.
10. **A run that drops 0 test accounts gets flagged.** I assumed there are normally some, so 0 may mean the export changed.

## Checks
Validator (`scripts/validate_skill.py`):
```
WARN   argument-hint: Claude Code only; uploading to claude.ai or the API will fail
PASSED: 0 error(s), 1 warning(s)
```
That warning doesn't matter here: you said Claude Code only.

Review by hand:
- **Pass:** The description covers two different requests (asking for the weekly numbers, sharing signups.csv for the Monday report). Its "Not for" line rules out other metrics and one-off signup questions.
- **Pass:** Every rule is either done exactly by the script or comes with its reason (the test-account and timezone fixes include what went wrong before).
- **Pass:** Each idea has one name throughout: test accounts, baseline week, reported weeks.
- **Pass:** There's a clear finish line: the table file has one row per week, every `WARNING:` is handled, and the reply includes the date range and the number of test accounts dropped. Checkpoints catch an export pulled too early, timestamps that can't be read, and a test-account count of 0.
- **Pass:** All assumptions are listed above.

**Script test.** I made a small CSV that included a signup at Sunday 23:30 UTC. That one landed in the next week (it's Monday 00:30 in Oslo), and a 22:30 UTC signup stayed in Sunday's week. A test row with a capitalised domain was dropped, and the current week was left out. The warnings for unreadable timestamps and for an export that starts too late or ends too early all fired.

**Cold read.** A fresh agent with only the skill files raised seven issues, all fixed now:
- The script couldn't show the timestamps it failed to read. It now prints up to five.
- There was no way to use renamed columns. Added `--created-col` and `--email-col`.
- The test-account count covered the whole file. It now counts only the reported weeks.
- "Exactly 6 rows" clashed with the `--weeks` option.
- Nothing caught an export pulled too early or starting too late. Both now raise warnings.
- Two diagnostics were unexplained.
- It wasn't clear that the file gets overwritten.

## Files

### weekly-signups/SKILL.md
```markdown
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
```

### weekly-signups/scripts/weekly_signups.py
```python
#!/usr/bin/env python3
"""Weekly signup counts that match the dashboard.

Rules (each one fixed a mismatch with the dashboard):
  - Rows whose email ends with @example-test.com are internal test accounts and are dropped.
  - created_at is UTC; it is converted to Europe/Oslo before bucketing.
  - Weeks are ISO weeks (Monday start), keyed by their Monday date so year boundaries sort correctly.
  - The report covers the last N complete weeks before the week containing --today.
  - % change is vs the previous week, rounded to one decimal; the week before the first
    reported week is counted too, so every row has a % change.

Standard library only. Usage:
  python3 weekly_signups.py signups.csv [--weeks 6] [--today YYYY-MM-DD] [--out weekly_signups.md]
         [--created-col created_at] [--email-col email]
"""
import argparse
import csv
import sys
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

TEST_DOMAIN = "@example-test.com"
TZ = ZoneInfo("Europe/Oslo")


def parse_utc(raw):
    s = raw.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    s = s.replace(" UTC", "+00:00")
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def week_monday(d):
    return d - timedelta(days=d.isoweekday() - 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path")
    ap.add_argument("--weeks", type=int, default=6)
    ap.add_argument("--today", help="YYYY-MM-DD; defaults to today's date in Europe/Oslo")
    ap.add_argument("--out", default="weekly_signups.md")
    ap.add_argument("--created-col", default="created_at", help="column holding the UTC signup timestamp")
    ap.add_argument("--email-col", default="email", help="column holding the email address")
    args = ap.parse_args()

    today = date.fromisoformat(args.today) if args.today else datetime.now(TZ).date()
    current_monday = week_monday(today)
    # Mondays of the reported weeks, oldest first, plus one baseline week before for the first % change.
    mondays = [current_monday - timedelta(weeks=i) for i in range(args.weeks + 1, 0, -1)]
    counts = {m: 0 for m in mondays}
    reported = set(mondays[1:])

    total = test_in_window = out_of_range = 0
    unparsed = []
    earliest = latest = None
    with open(args.csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = {args.created_col, args.email_col} - set(reader.fieldnames or [])
        if missing:
            sys.exit(f"ERROR: missing column(s) {sorted(missing)}; found {reader.fieldnames}")
        for row in reader:
            total += 1
            raw = row[args.created_col]
            try:
                local = parse_utc(raw).astimezone(TZ)
            except (ValueError, AttributeError):
                unparsed.append(raw)
                continue
            earliest = local if earliest is None or local < earliest else earliest
            latest = local if latest is None or local > latest else latest
            m = week_monday(local.date())
            if (row[args.email_col] or "").strip().lower().endswith(TEST_DOMAIN):
                if m in reported:
                    test_in_window += 1
                continue
            if m in counts:
                counts[m] += 1
            else:
                out_of_range += 1

    first_day, last_day = mondays[1], mondays[-1] + timedelta(days=6)
    lines = [
        f"# Weekly signups (last {args.weeks} complete ISO weeks, Europe/Oslo)",
        "",
        "| Week | Signups | % change |",
        "| --- | ---: | ---: |",
    ]
    for prev, cur in zip(mondays, mondays[1:]):
        c, p = counts[cur], counts[prev]
        pct = "n/a" if p == 0 else f"{(c - p) / p * 100:+.1f}%"
        lines.append(f"| {cur.isocalendar()[1]} | {c} | {pct} |")
    lines += [
        "",
        f"Weeks {first_day:%d %b %Y} to {last_day:%d %b %Y}. "
        f"Test accounts ({TEST_DOMAIN}) excluded in these weeks: {test_in_window}.",
    ]
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print("\n".join(lines))
    print()
    print(f"rows read: {total}")
    print(f"test accounts dropped in reported weeks: {test_in_window}")
    print(f"unparseable {args.created_col}: {len(unparsed)}")
    print(f"real signups outside reported window: {out_of_range}")
    b = mondays[0].isocalendar()
    print(f"baseline week {b[0]}-W{b[1]:02d} (used only for the first % change): {counts[mondays[0]]}")
    print(f"export covers (Oslo time): {earliest:%Y-%m-%d %H:%M} to {latest:%Y-%m-%d %H:%M}" if earliest else "export has no parseable rows")
    print(f"current (incomplete) week starts {current_monday}; not reported")
    print(f"wrote {args.out}")
    warnings = []
    if unparsed:
        warnings.append(f"{len(unparsed)} timestamp(s) could not be parsed, e.g. {unparsed[:5]}")
    if earliest is None or earliest.date() > mondays[0]:
        warnings.append(f"export starts after {mondays[0]} (baseline week start); the earliest week(s) or first % change are undercounted")
    if latest is None or latest.date() < last_day:
        warnings.append(f"export ends before {last_day} (last reported Sunday); the latest week is undercounted, so re-export")
    for w in warnings:
        print("WARNING: " + w)


if __name__ == "__main__":
    main()
```

## Road test
Run each prompt in a fresh Claude Code session, at least twice:
1. **"Weekly signups please, signups.csv is in this folder."** Success: Claude runs the script without writing its own pandas code and replies with 6 rows and the date range. Compare the numbers with the dashboard. They should match exactly.
2. **"Do the weekly signup numbers"** with no CSV in the folder (missing input). Success: Claude asks you for the file and doesn't pick some other CSV.
3. **"How many people signed up yesterday from Norway?"** (should not trigger). Success: the skill doesn't load, or at least no weekly table is produced.

## If something breaks
Come back with: "Fix my `weekly-signups` skill: I ran ___, it did ___, I expected ___." That brings it back to the skill builder to fix exactly that spot.
