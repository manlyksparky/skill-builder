---
tags: [skill-creator]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Here's a session I had yesterday doing our weekly signup numbers. Turn this into a skill so I don't have to walk Claude through it every Monday. It's just for me, in Claude Code. I've pasted the session below; anything it doesn't answer, make a sensible call and flag it, I won't be around to answer questions.

--- session ---
Me: here's signups.csv, give me signups per week for the last 6 weeks
Claude: [loads signups.csv with pandas, groups created_at by week] Week 41: 312, Week 42: 298 ...
Me: those are too high, you're counting test accounts. anything with an email ending @example-test.com is ours, drop them
Claude: [filters out @example-test.com] Week 41: 287, Week 42: 271 ...
Me: still off vs the dashboard by a few each week
Claude: created_at is in UTC. If the dashboard uses Oslo time, signups between 22:00 and 00:00 UTC on Sundays land in the next week.
Me: yes, dashboard is Europe/Oslo. and weeks start Monday, ISO weeks
Claude: [converts to Europe/Oslo, groups by ISO week] Week 41: 289, Week 42: 270 ... These match the dashboard.
Me: great. put it in a table with week number, signups, and % change from the previous week, and round % to one decimal
Claude: [writes weekly_signups.md with the table]
--- end ---
