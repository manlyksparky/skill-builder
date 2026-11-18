I've written the `weekly-signups` skill. Every Monday you can say "weekly signups" or hand over `signups.csv`, and it applies the rules you gave Claude in that session: test accounts out, Oslo time, ISO weeks. It writes `weekly_signups.md`.

## What I took from your session

- "anything with an email ending @example-test.com is ours, drop them": these rows are always removed. The match ignores case.
- "created_at is in UTC… dashboard is Europe/Oslo. and weeks start Monday, ISO weeks": timestamps are converted to Europe/Oslo and then grouped by ISO week.
- "week number, signups, and % change from the previous week, and round % to one decimal": the table has exactly those three columns, and % is shown to one decimal with a sign.
- "writes weekly_signups.md": that's the output file, saved in the working directory.
- "It's just for me, in Claude Code": the skill is personal and uses Claude Code paths (`${CLAUDE_SKILL_DIR}`).

You weren't around to answer questions, so I made the calls listed under "Assumptions" below.

## Files

The skill is in `weekly-signups/`. For real use it belongs in `~/.claude/skills/weekly-signups/`, since it's personal and not tied to one project. That folder already exists, so the skill is picked up without `/reload-skills`. No existing skill there is called `weekly-signups`.

```
weekly-signups/
├── SKILL.md
└── scripts/
    └── weekly_signups.py
```

The counting has exactly one right answer, so a script does it instead of fresh pandas code each week. That way the three rules can't drift between runs. The script uses only the standard library (Python 3.9+, `zoneinfo`).

### weekly-signups/SKILL.md
````markdown
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
````

### weekly-signups/scripts/weekly_signups.py
```python
#!/usr/bin/env python3
"""Count signups per ISO week in Europe/Oslo time, excluding test accounts.

Usage:
    python3 weekly_signups.py signups.csv [--weeks 6] [--as-of YYYY-MM-DD]
                              [--out weekly_signups.md]
                              [--email-col email] [--date-col created_at]

Standard library only (Python 3.9+).
"""
import argparse
import csv
import sys
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

OSLO = ZoneInfo("Europe/Oslo")
TEST_DOMAIN = "@example-test.com"


def parse_utc(raw):
    """Parse an ISO 8601 timestamp. Naive timestamps are treated as UTC."""
    s = raw.strip()
    if s.endswith("Z") or s.endswith("z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def pct_change(cur, prev):
    if prev == 0:
        return "n/a"
    value = round((cur - prev) / prev * 100, 1)
    if value == 0:
        return "0.0%"
    return f"{value:+.1f}%"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv_path")
    ap.add_argument("--weeks", type=int, default=6)
    ap.add_argument("--as-of", help="Oslo date to count back from (default: today in Oslo)")
    ap.add_argument("--out", default="weekly_signups.md")
    ap.add_argument("--email-col", default="email")
    ap.add_argument("--date-col", default="created_at")
    args = ap.parse_args()

    as_of = date.fromisoformat(args.as_of) if args.as_of else datetime.now(OSLO).date()
    current_monday = as_of - timedelta(days=as_of.weekday())
    # The reported weeks are the complete ISO weeks before the current one.
    # One extra week in front is the baseline for the first row's % change.
    week_starts = [current_monday - timedelta(weeks=k) for k in range(args.weeks + 1, 0, -1)]
    counts = {monday: 0 for monday in week_starts}

    rows = test = unparseable = outside = 0
    bad_examples = []

    with open(args.csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = [c for c in (args.email_col, args.date_col) if c not in (reader.fieldnames or [])]
        if missing:
            sys.exit(f"ERROR: column(s) {missing} not found. Columns in file: {reader.fieldnames}. "
                     f"Pass --email-col / --date-col.")
        for row in reader:
            rows += 1
            email = (row.get(args.email_col) or "").strip().lower()
            if email.endswith(TEST_DOMAIN):
                test += 1
                continue
            raw = row.get(args.date_col) or ""
            try:
                local_day = parse_utc(raw).astimezone(OSLO).date()
            except ValueError:
                unparseable += 1
                if len(bad_examples) < 5:
                    bad_examples.append(raw)
                continue
            monday = local_day - timedelta(days=local_day.weekday())
            if monday in counts:
                counts[monday] += 1
            else:
                outside += 1

    reported = week_starts[1:]
    lines = [
        "# Weekly signups",
        "",
        f"Source: {args.csv_path}. Europe/Oslo time, ISO weeks (Monday start), "
        f"test accounts ({TEST_DOMAIN}) excluded. Last {args.weeks} complete weeks before "
        f"{current_monday.isoformat()}.",
        "",
        "| Week | Signups | % change |",
        "|---:|---:|---:|",
    ]
    for prev_monday, monday in zip(week_starts[:-1], reported):
        week_no = monday.isocalendar()[1]
        lines.append(f"| {week_no} | {counts[monday]} | {pct_change(counts[monday], counts[prev_monday])} |")
    table = "\n".join(lines) + "\n"

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(table)

    in_window = sum(counts.values())
    print(table)
    print(f"Wrote {args.out}")
    print("Reconciliation:")
    print(f"  rows read            {rows}")
    print(f"  test accounts        {test}")
    print(f"  unparseable date     {unparseable}")
    print(f"  outside window       {outside}")
    print(f"  counted (incl. baseline week {week_starts[0].isocalendar()[1]}: {counts[week_starts[0]]})  {in_window}")
    balanced = rows == test + unparseable + outside + in_window
    print(f"  balanced             {'yes' if balanced else 'NO'}")
    if bad_examples:
        print(f"  unparseable examples {bad_examples}")
    if test == 0:
        print(f"WARN: no {TEST_DOMAIN} rows found; check the email column is right.")
    if counts[reported[-1]] == 0:
        print("WARN: the latest reported week has 0 signups; the export may be stale.")


if __name__ == "__main__":
    main()
```

## Check results

Validator (`scripts/validate_skill.py`):
```
PASSED: 0 error(s), 0 warning(s) in .../outputs/weekly-signups
```

I also ran the script on a 12-row test CSV with known answers:
- A signup on Sunday 11 Oct at 22:30 UTC fell into week 42. That's 00:30 Monday in Oslo, which is the off-by-a-few bug from your session.
- Sunday 21:30 UTC stayed in week 41.
- Around the DST change, Sunday 8 Nov at 22:30 UTC stayed in week 45 and 23:30 UTC moved to week 46.
- An `@EXAMPLE-TEST.com` row was dropped.
- A bad date was reported, not silently lost.
- Rows from the current week and from August counted as "outside window".
- The reconciliation balanced (12 = 1 + 1 + 2 + 8).
- A wrong column name stopped the script with a list of the real columns.

Judgment checks:
1. Distinct triggers and a "Not for" line: pass. The two triggers are "shares signups.csv" and "asks for signup numbers". "Not for" covers other metrics and one-off signup queries with different rules.
2. Every instruction is exact or has its reason: pass. The three fixed rules say why (the dashboard match), and "complete weeks" says why (Monday has almost no data).
3. One name per concept: pass. The skill uses "test accounts", "ISO week" and "reconciliation" consistently.
4. A definition of done the agent can see is met: pass. It requires the row count, `balanced` = `yes` and test accounts above 0. Zero test rows or unparseable dates must be reported, so a run that looks finished but used the wrong column gets caught.
5. Assumptions confirmed or flagged: pass. They're listed below.

## Assumptions (please check)

1. **"Last 6 weeks" means the 6 complete ISO weeks before the current one.** Run on Monday 16 Nov, that's weeks 41–46, which matches the "Week 41…" your session started with. If the dashboard also shows the current partial week, tell me.
2. **The first row's % change uses the week before it.** For example, week 41 is compared with week 40, so no row shows a blank.
3. **The column names are `email` and `created_at`.** `created_at` came from the session; `email` is a guess. If the export uses another name, the script stops and lists the columns, and the skill tells Claude to rerun with `--email-col`.
4. **`created_at` is ISO 8601.** A trailing `Z`, `+00:00` or no offset all work, and no offset is treated as UTC.
5. **Only addresses ending exactly `@example-test.com` count as test accounts.** Subdomains like `@qa.example-test.com` are not matched.
6. **If the previous week had 0 signups, % change shows `n/a`.**
7. **Weeks are labelled by number only, as you asked.** Across New Year the table will read 52, 1, 2…
8. **Claude picks up the skill on its own** when you ask for signup numbers, and you can also call it as `/weekly-signups`. If you'd rather it only runs when you call it by name, add `disable-model-invocation: true` to the frontmatter.
9. **`weekly_signups.md` is overwritten each run.** It's written in the working directory.

## Road test

Run each prompt in a fresh session, at least twice.

1. "Here's this week's signups.csv, give me the weekly signups." It should run the script and show a 6-row table (weeks 41–46 if run on 16 Nov) plus the reconciliation with `balanced` = `yes`. The numbers should match the dashboard.
2. "Signups per week for the last 10 weeks please." It should rerun with `--weeks 10` and show 10 rows, with the same rules applied.
3. Should *not* trigger: "What was our churn rate last month?" The skill shouldn't open, because it's a different metric.

## If something breaks

Come back with: "Fix my `weekly-signups` skill: I ran ___, it did ___, I expected ___." That puts me in fixing mode, and I'll fix the exact spot that broke.
