#!/usr/bin/env python3
"""Check an agent skill folder for problems that break loading or triggering.

Usage: python3 validate_skill.py <skill-dir | path/to/SKILL.md>

Prints one ERROR or WARN line per problem. Exits 1 if there is any ERROR,
otherwise 0. Standard library only.
"""

import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NAME_MAX = 64
RESERVED_NAME_WORDS = ("anthropic", "claude")
DESC_MAX = 1024
COMPAT_MAX = 500
REF_TOC_LINES = 100
# Fields accepted everywhere (claude.ai upload, Skills API, Claude Code).
SPEC_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
# Extra fields only Claude Code understands; claude.ai and the API reject them.
CLAUDE_CODE_FIELDS = {
    "when_to_use", "argument-hint", "arguments", "disable-model-invocation",
    "user-invocable", "disallowed-tools", "model", "effort", "context", "agent",
    "background", "hooks", "paths", "shell",
}
BODY_MAX_LINES = 500
SHOUT_RE = re.compile(r"\b(MUST|CRITICAL|NEVER|IMPORTANT|ALWAYS)\b")
# A bundled path like references/x.md or scripts/run.py, not preceded by
# another path segment (so src/scripts/build.sh is not picked up).
PATH_RE = re.compile(
    r"(?:(?<=\$\{CLAUDE_SKILL_DIR\}/)|(?<![\w./-]))((?:references|scripts|assets)/[\w.\-/]*\w)"
)
FENCE_RE = re.compile(r"^(```|~~~).*?^\1", re.S | re.M)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
BLOCK_MARKERS = {">", "|", ">-", "|-", ">+", "|+"}


def parse_frontmatter(text):
    """Return (fields, body) or (None, text) if there is no frontmatter."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return None, text

    fields, key, mode, buf = {}, None, None, []

    def flush():
        if key is None:
            return
        joiner = "\n" if mode == "|" else " "
        value = joiner.join(s.strip() for s in buf).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        fields[key] = value

    for line in lines[1:end]:
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m and not line[:1].isspace():
            flush()
            key, raw = m.group(1), m.group(2).strip()
            if raw in BLOCK_MARKERS:
                mode, buf = raw[0], []
            else:
                mode, buf = "plain", [raw]
        elif key is not None and (line[:1].isspace() or not line.strip()):
            buf.append(line)
    flush()
    return fields, "\n".join(lines[end + 1:])


def strip_code(text, inline=True):
    text = FENCE_RE.sub("", text)
    return INLINE_CODE_RE.sub("", text) if inline else text


def bundled_paths(text):
    return {m.group(1).rstrip(".") for m in PATH_RE.finditer(text)}


def validate(skill_dir):
    errors, warns = [], []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [f"No SKILL.md in {skill_dir}"], warns

    text = skill_md.read_text(encoding="utf-8")
    fields, body = parse_frontmatter(text)
    if fields is None:
        errors.append("SKILL.md must start with a frontmatter block between two '---' lines")
        fields, body = {}, text

    name = fields.get("name", "")
    if not name:
        errors.append("frontmatter: 'name' is missing")
    else:
        if not NAME_RE.match(name):
            errors.append(f"name '{name}': use lowercase letters, digits and single hyphens only")
        if len(name) > NAME_MAX:
            errors.append(f"name is {len(name)} characters; the limit is {NAME_MAX}")
        for word in RESERVED_NAME_WORDS:
            if word in name:
                errors.append(f"name contains the reserved word '{word}'")
        if name != skill_dir.name:
            errors.append(f"name '{name}' differs from the folder name '{skill_dir.name}'; claude.ai rejects the upload")

    desc = fields.get("description", "")
    if not desc:
        errors.append("frontmatter: 'description' is missing or empty")
    else:
        if len(desc) > DESC_MAX:
            errors.append(f"description is {len(desc)} characters; the limit is {DESC_MAX}")
        if "<" in desc or ">" in desc:
            errors.append("description contains '<' or '>'; some platforms reject it as an XML tag")

    compat = fields.get("compatibility", "")
    if len(compat) > COMPAT_MAX:
        errors.append(f"compatibility is {len(compat)} characters; the limit is {COMPAT_MAX}")

    unknown = sorted(set(fields) - SPEC_FIELDS - CLAUDE_CODE_FIELDS)
    if unknown:
        errors.append(f"unknown frontmatter field(s): {', '.join(unknown)}")
    code_only = sorted(set(fields) & CLAUDE_CODE_FIELDS)
    if code_only:
        warns.append(f"{', '.join(code_only)}: Claude Code only; uploading to claude.ai or the API will fail")

    n_lines = len(text.splitlines())
    if n_lines > BODY_MAX_LINES:
        warns.append(f"SKILL.md is {n_lines} lines; move branch-only detail into references/ (aim under {BODY_MAX_LINES})")

    mentioned = bundled_paths(text)
    for rel in sorted(mentioned):
        if not (skill_dir / rel).exists():
            errors.append(f"SKILL.md mentions '{rel}' but that file does not exist in the skill folder")

    for sub in ("references", "scripts", "assets"):
        folder = skill_dir / sub
        if not folder.is_dir():
            continue
        for f in sorted(p for p in folder.rglob("*") if p.is_file() and not p.name.startswith(".")):
            rel = f.relative_to(skill_dir).as_posix()
            if "__pycache__" in rel:
                continue
            if rel not in mentioned:
                warns.append(f"'{rel}' is never mentioned in SKILL.md, so the agent will not know to use it")
            if sub == "references" and f.suffix == ".md":
                ref_text = f.read_text(encoding="utf-8")
                ref_lines = ref_text.splitlines()
                head = "\n".join(ref_lines[:20]).lower()
                if len(ref_lines) > REF_TOC_LINES and "contents" not in head:
                    warns.append(f"'{rel}' is {len(ref_lines)} lines; add a short table of contents at the top")
                nested = sorted(p for p in bundled_paths(strip_code(ref_text, inline=False)) if p.startswith("references/"))
                if nested:
                    warns.append(f"'{rel}' points to {', '.join(nested)}; keep references one level deep (link them from SKILL.md)")
                for word in sorted(set(SHOUT_RE.findall(strip_code(ref_text)))):
                    warns.append(f"'{rel}' uses '{word}' in capitals; state the consequence in a normal tone instead")

    for word in sorted(set(SHOUT_RE.findall(strip_code(body)))):
        warns.append(f"SKILL.md uses '{word}' in capitals; state the consequence in a normal tone instead")

    return errors, warns


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip())
        return 2
    target = Path(argv[1]).expanduser().resolve()
    skill_dir = target.parent if target.name == "SKILL.md" else target
    errors, warns = validate(skill_dir)
    for e in errors:
        print(f"ERROR  {e}")
    for w in warns:
        print(f"WARN   {w}")
    status = "FAILED" if errors else "PASSED"
    print(f"{status}: {len(errors)} error(s), {len(warns)} warning(s) in {skill_dir}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
