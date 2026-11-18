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
