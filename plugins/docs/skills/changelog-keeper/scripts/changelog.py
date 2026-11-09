#!/usr/bin/env python3
"""Generate a "Keep a Changelog" section from Conventional Commits.

Zero dependencies: Python 3.8+ standard library only.

Usage:
    python3 changelog.py                      # since the latest tag, version "Unreleased"
    python3 changelog.py --version auto       # suggest next SemVer from commit types
    python3 changelog.py --from v1.2.0 --to HEAD --version 1.3.0 --repo-url https://github.com/o/r
"""
from __future__ import annotations

import argparse
import datetime as _dt
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional

CC_RE = re.compile(r"^(?P<type>[a-zA-Z]+)(?:\((?P<scope>[^)]+)\))?(?P<bang>!)?:\s*(?P<desc>.+)$")
REF_RE = re.compile(r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)", re.IGNORECASE)

SECTION_FOR_TYPE = {
    "feat": "Added",
    "fix": "Fixed",
    "perf": "Changed",
    "refactor": "Changed",
    "revert": "Removed",
    "security": "Security",
    "deprecate": "Deprecated",
}
SECTION_ORDER = ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]
INTERNAL_TYPES = {"docs", "test", "ci", "build", "chore", "style"}


@dataclass
class Commit:
    sha: str
    type: str
    scope: Optional[str]
    description: str
    breaking: bool
    breaking_note: Optional[str] = None
    refs: List[str] = field(default_factory=list)


def parse_commit(sha: str, subject: str, body: str = "") -> Optional[Commit]:
    """Parse one commit. Returns None for non-conventional subjects."""
    m = CC_RE.match(subject.strip())
    if not m:
        return None
    note = None
    for marker in ("BREAKING CHANGE:", "BREAKING-CHANGE:"):
        if marker in body:
            note = body.split(marker, 1)[1].strip().split("\n\n", 1)[0].replace("\n", " ")
    ctype = m.group("type").lower()
    desc = m.group("desc").strip()
    if "security" in (m.group("scope") or "").lower():
        ctype = "security" if ctype == "fix" else ctype
    return Commit(
        sha=sha,
        type=ctype,
        scope=m.group("scope"),
        description=desc[0].upper() + desc[1:] if desc else desc,
        breaking=bool(m.group("bang")) or note is not None,
        breaking_note=note,
        refs=REF_RE.findall(body + " " + subject),
    )


def suggest_bump(current: str, commits: List[Commit]) -> str:
    """Return the next SemVer given the current version and parsed commits."""
    m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)", current or "0.0.0")
    major, minor, patch = (int(x) for x in m.groups()) if m else (0, 0, 0)
    if any(c.breaking for c in commits):
        return f"{major + 1}.0.0" if major > 0 else f"0.{minor + 1}.0"
    if any(c.type == "feat" for c in commits):
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def render(version: str, date: str, commits: List[Commit], repo_url: Optional[str] = None,
           include_internal: bool = False) -> str:
    sections: Dict[str, List[str]] = {}
    breaking: List[str] = []

    def line_for(c: Commit) -> str:
        scope = f"**{c.scope}:** " if c.scope else ""
        link = f" ([{c.sha[:7]}]({repo_url.rstrip('/')}/commit/{c.sha}))" if repo_url else f" ({c.sha[:7]})"
        refs = "".join(
            f", [#{r}]({repo_url.rstrip('/')}/issues/{r})" if repo_url else f", #{r}" for r in c.refs
        )
        return f"- {scope}{c.description}{link}{refs}"

    for c in commits:
        if c.breaking:
            breaking.append(f"- {c.breaking_note or c.description}")
        section = SECTION_FOR_TYPE.get(c.type)
        if section is None:
            if c.type in INTERNAL_TYPES and not include_internal:
                continue
            section = "Changed"
        sections.setdefault(section, []).append(line_for(c))

    out = [f"## [{version}] - {date}" if version != "Unreleased" else "## [Unreleased]", ""]
    if breaking:
        out += ["### ⚠ BREAKING CHANGES", "", *breaking, ""]
    for name in SECTION_ORDER:
        if name in sections:
            out += [f"### {name}", "", *sections[name], ""]
    if len(out) == 2:
        out += ["_No user-facing changes._", ""]
    return "\n".join(out)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def latest_tag() -> Optional[str]:
    try:
        return git("describe", "--tags", "--abbrev=0").strip() or None
    except subprocess.CalledProcessError:
        return None


def read_commits(rev_range: str) -> List[Commit]:
    raw = git("log", "--no-merges", "--format=%H%x1f%s%x1f%b%x1e", rev_range)
    commits: List[Commit] = []
    for record in raw.split("\x1e"):
        record = record.strip("\n")
        if not record:
            continue
        parts = record.split("\x1f")
        sha, subject, body = (parts + ["", ""])[:3]
        parsed = parse_commit(sha, subject, body)
        if parsed:
            commits.append(parsed)
    return commits


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Generate a Keep a Changelog section from Conventional Commits.")
    ap.add_argument("--from", dest="from_ref", help="start ref (default: latest tag)")
    ap.add_argument("--to", dest="to_ref", default="HEAD")
    ap.add_argument("--version", default="Unreleased", help='version label, or "auto" to compute SemVer bump')
    ap.add_argument("--date", default=_dt.date.today().isoformat())
    ap.add_argument("--repo-url", help="e.g. https://github.com/owner/repo, enables links")
    ap.add_argument("--all", action="store_true", help="include docs/test/ci/chore commits")
    args = ap.parse_args(argv)

    try:
        start = args.from_ref or latest_tag()
        rev_range = f"{start}..{args.to_ref}" if start else args.to_ref
        commits = read_commits(rev_range)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"error: git failed: {exc}", file=sys.stderr)
        return 2

    version = args.version
    if version == "auto":
        version = suggest_bump(start or "0.0.0", commits)
    print(render(version, args.date, commits, args.repo_url, args.all))
    return 0


if __name__ == "__main__":
    sys.exit(main())
