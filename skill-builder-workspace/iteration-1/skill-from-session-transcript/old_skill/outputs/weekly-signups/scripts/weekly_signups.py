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
