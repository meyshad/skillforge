#!/usr/bin/env python3
"""Validate every plugin and skill in the repository.

Checks:
  * marketplace.json is valid and every plugin source exists
  * each plugin has a valid plugin.json whose name matches its directory
  * each skill has SKILL.md with YAML frontmatter: `name` (matches folder,
    lowercase-hyphen, <= 64 chars) and `description` (<= 1024 chars, no angle brackets)
  * files referenced as scripts/... or references/... inside SKILL.md exist
  * no duplicate skill names across plugins
  * README skill count badge matches the real number of skills

Exit code 0 when everything passes, 1 otherwise. Standard library only.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REF_RE = re.compile(r"(?<![\w/.-])((?:scripts|references|assets)/[\w./-]+\.\w+)")
MAX_SKILL_LINES = 500

errors: List[str] = []
warnings: List[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def parse_frontmatter(text: str) -> Tuple[Dict[str, str], str]:
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter (file must start with '---')")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError("unterminated YAML frontmatter")
    meta: Dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, text[end + 4:]


def check_skill(skill_dir: Path) -> str:
    rel = skill_dir.relative_to(ROOT)
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        err(f"{rel}: missing SKILL.md")
        return ""
    text = skill_md.read_text(encoding="utf-8")
    try:
        meta, body = parse_frontmatter(text)
    except ValueError as exc:
        err(f"{rel}/SKILL.md: {exc}")
        return ""

    name = meta.get("name", "")
    desc = meta.get("description", "")
    if not name:
        err(f"{rel}: frontmatter 'name' is required")
    elif name != skill_dir.name:
        err(f"{rel}: name '{name}' must match folder name '{skill_dir.name}'")
    elif not NAME_RE.match(name) or len(name) > 64:
        err(f"{rel}: name must be lowercase letters, digits and hyphens, max 64 chars")
    if not desc:
        err(f"{rel}: frontmatter 'description' is required")
    else:
        if len(desc) > 1024:
            err(f"{rel}: description is {len(desc)} chars (max 1024)")
        if "<" in desc or ">" in desc:
            err(f"{rel}: description must not contain angle brackets")
        if not re.search(r"\buse (?:when|before|after|for|whenever)\b", desc, re.IGNORECASE):
            warnings.append(f"{rel}: description should say when to use the skill ('Use when ...')")
    if not body.strip():
        err(f"{rel}: SKILL.md body is empty")
    if len(text.splitlines()) > MAX_SKILL_LINES:
        warnings.append(f"{rel}: SKILL.md is over {MAX_SKILL_LINES} lines; move detail into references/")

    for ref in sorted(set(REF_RE.findall(body))):
        if not (skill_dir / ref).exists():
            err(f"{rel}: SKILL.md references missing file '{ref}'")
    return name


def main() -> int:
    marketplace_path = ROOT / ".claude-plugin" / "marketplace.json"
    try:
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: cannot read {marketplace_path.relative_to(ROOT)}: {exc}")
        return 1

    listed = set()
    seen_skills: Dict[str, str] = {}
    total = 0
    for entry in marketplace.get("plugins", []):
        pname = entry.get("name", "")
        listed.add(pname)
        pdir = (ROOT / entry.get("source", "")).resolve()
        if not pdir.is_dir():
            err(f"marketplace: plugin '{pname}' source {entry.get('source')} does not exist")
            continue
        manifest = pdir / ".claude-plugin" / "plugin.json"
        try:
            pjson = json.loads(manifest.read_text(encoding="utf-8"))
            if pjson.get("name") != pname:
                err(f"{manifest.relative_to(ROOT)}: name '{pjson.get('name')}' != marketplace name '{pname}'")
            if not re.match(r"^\d+\.\d+\.\d+", str(pjson.get("version", ""))):
                err(f"{manifest.relative_to(ROOT)}: version must be SemVer")
        except (OSError, json.JSONDecodeError) as exc:
            err(f"{pdir.relative_to(ROOT)}: invalid plugin.json: {exc}")

        skills_dir = pdir / "skills"
        skill_dirs = sorted(p for p in skills_dir.iterdir() if p.is_dir()) if skills_dir.is_dir() else []
        if not skill_dirs:
            err(f"{pdir.relative_to(ROOT)}: plugin has no skills")
        for sdir in skill_dirs:
            name = check_skill(sdir)
            total += 1
            if name:
                if name in seen_skills:
                    err(f"duplicate skill name '{name}' in {seen_skills[name]} and {pname}")
                seen_skills[name] = pname

    for pdir in sorted((ROOT / "plugins").iterdir()):
        if pdir.is_dir() and pdir.name not in listed:
            err(f"plugins/{pdir.name} exists but is not listed in marketplace.json")

    readme = ROOT / "README.md"
    if readme.is_file():
        m = re.search(r"skills-(\d+)-", readme.read_text(encoding="utf-8"))
        if m and int(m.group(1)) != total:
            err(f"README badge says {m.group(1)} skills but repository has {total}")

    for w in warnings:
        print(f"warn: {w}")
    for e in errors:
        print(f"FAIL: {e}")
    status = "OK" if not errors else "FAILED"
    print(f"\n{status}: {len(marketplace.get('plugins', []))} plugins, {total} skills, "
          f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
