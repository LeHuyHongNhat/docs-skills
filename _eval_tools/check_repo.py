#!/usr/bin/env python3
"""check_repo.py — structural checks that need no network and no skill-creator install.

Run in CI and before a commit:
    python _eval_tools/check_repo.py

Checks:
1. Sync drift: every file under _shared/{scripts,references,assets} that also exists in a
   skill must be byte-identical there (build.sh is the only writer of those copies).
2. SKILL.md frontmatter: name equals the folder, lowercase-hyphen, description present and
   within the 1024-character limit, body under 500 lines.
3. Relative links in SKILL.md resolve to files in the skill.
4. Eval cases: prompt.md, case.yaml and at least one grader exist.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "_shared"
SUBDIRS = ("scripts", "references", "assets")
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\]\(((?:references|scripts|assets)/[^)#\s]+)")
MAX_DESCRIPTION = 1024
MAX_BODY_LINES = 500


def skills() -> list[Path]:
    return sorted(p.parent for p in ROOT.glob("*/SKILL.md"))


def check_drift(skill: Path) -> list[str]:
    errors: list[str] = []
    for sub in SUBDIRS:
        for src in sorted((SHARED / sub).glob("*")):
            copy = skill / sub / src.name
            if src.is_file() and copy.exists() and copy.read_bytes() != src.read_bytes():
                errors.append(f"{copy.relative_to(ROOT)} differs from _shared/{sub}/{src.name} (run build.sh)")
    return errors


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, text
    import yaml  # PyYAML is already a dependency of charts.py and stats_check.py

    data = yaml.safe_load(m.group(1)) or {}
    return {str(k): str(v) for k, v in data.items()}, m.group(2)


def check_skill_md(skill: Path) -> list[str]:
    errors: list[str] = []
    rel = f"{skill.name}/SKILL.md"
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    if not meta:
        return [f"{rel}: missing or unparseable frontmatter"]
    name = meta.get("name", "")
    if name != skill.name:
        errors.append(f"{rel}: name '{name}' does not match folder '{skill.name}'")
    if not NAME_RE.match(name):
        errors.append(f"{rel}: name must be lowercase letters, digits and hyphens")
    description = meta.get("description", "").strip()
    if not description:
        errors.append(f"{rel}: description is empty")
    elif len(description) > MAX_DESCRIPTION:
        errors.append(f"{rel}: description is {len(description)} characters (limit {MAX_DESCRIPTION})")
    lines = body.count("\n") + 1
    if lines > MAX_BODY_LINES:
        errors.append(f"{rel}: body is {lines} lines (limit {MAX_BODY_LINES})")
    for target in sorted(set(LINK_RE.findall(body))):
        if not (skill / target).exists():
            errors.append(f"{rel}: link target '{target}' does not exist")
    return errors


def check_evals(skill: Path) -> list[str]:
    errors: list[str] = []
    for case in sorted(p for p in (skill / "evals").glob("*") if p.is_dir()):
        rel = case.relative_to(ROOT)
        for required in ("prompt.md", "case.yaml"):
            if not (case / required).is_file():
                errors.append(f"{rel}: missing {required}")
        if not list((case / "graders").glob("*.md")):
            errors.append(f"{rel}: no graders")
    return errors


def main() -> int:
    errors: list[str] = []
    found = skills()
    if not found:
        errors.append("no skills found")
    for skill in found:
        errors += check_drift(skill) + check_skill_md(skill) + check_evals(skill)
    for e in errors:
        print(f"FAIL {e}")
    print(f"{len(found)} skills checked, {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
