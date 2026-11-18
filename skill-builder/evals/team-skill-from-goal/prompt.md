---
tags: [skill-creator]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

I want a skill that writes the "What's new" release notes for our mobile app from the PRs merged in a release. I know you normally interview me, so here are my answers up front. Treat them as confirmed and go straight to writing it, I won't be around to reply.

- Scope: only the App Store / Play Store "What's new" text. Not our internal CHANGELOG.md.
- Trigger: automatically when someone asks for release notes or "what's new" text for an app version. It should not open for PR descriptions or for the internal changelog.
- Input: a list of merged PR titles with their labels, pasted in or from `gh pr list`. Output: release-notes.md with two sections, iOS and Android, each 500 characters or less, because the Play Store cuts off anything longer and we keep both the same length.
- Fixed rules: the 500-character limit; PRs labelled internal or chore are never mentioned; no ticket or PR numbers. Flexible: tone, friendly but plain.
- Branches: a hotfix release gets exactly one line, "Bug fixes and performance improvements."
- Done: both sections at or under 500 characters, and every user-facing PR either mentioned or grouped into a line.
- Failures: last time Claude wrote "Refactor auth module (#4312)", internal work with a ticket number, and the text was 900 characters so the Play Store cut it off mid-sentence.
- Hidden knowledge: our PM wants features first, then fixes. We never say "crash", we say "stability improvements".
- Vocabulary: "user-facing PR" means any PR without the internal or chore label.
- Audience and home: the whole mobile team will use it, in both Claude Code and claude.ai.
