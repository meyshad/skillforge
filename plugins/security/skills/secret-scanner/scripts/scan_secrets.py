#!/usr/bin/env python3
"""Scan a directory (and optionally git history) for hard-coded secrets.

Zero dependencies: Python 3.8+ standard library only.

Usage:
    python3 scan_secrets.py [PATH] [--history] [--json] [--no-generic]

Exit codes: 0 = clean, 1 = findings, 2 = usage error.
Suppress a known false positive by adding `secretscan:ignore` to the line.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from typing import Iterable, Iterator, List, Optional, Tuple

SKIP_DIRS = {
    ".git", "node_modules", "vendor", "dist", "build", "out", "target",
    ".venv", "venv", "env", "__pycache__", ".next", ".nuxt", ".cache",
    ".idea", ".vscode", "coverage", ".terraform", ".gradle", "Pods",
}
SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz",
    ".tar", ".tgz", ".7z", ".jar", ".class", ".so", ".dylib", ".dll", ".exe",
    ".woff", ".woff2", ".ttf", ".otf", ".mp3", ".mp4", ".mov", ".lock",
}
SKIP_FILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Cargo.lock", "go.sum"}
MAX_FILE_BYTES = 2 * 1024 * 1024
IGNORE_MARKERS = ("secretscan:ignore", "pragma: allowlist secret")

# (rule id, regex, severity)
RULES: List[Tuple[str, "re.Pattern[str]", str]] = [
    ("aws-access-key-id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"), "critical"),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"), "critical"),
    ("github-fine-grained-pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{60,}\b"), "critical"),
    ("gitlab-token", re.compile(r"\bglpat-[A-Za-z0-9_\-]{20,}\b"), "critical"),
    ("slack-token", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}\b"), "high"),
    ("slack-webhook", re.compile(r"https://hooks\.slack\.com/services/[A-Za-z0-9/]{20,}"), "high"),
    ("stripe-live-key", re.compile(r"\b[sr]k_live_[A-Za-z0-9]{20,}\b"), "critical"),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b"), "high"),
    ("sk-style-api-key", re.compile(r"\bsk-(?:proj-|ant-)?[A-Za-z0-9_\-]{32,}\b"), "high"),
    ("sendgrid-key", re.compile(r"\bSG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}\b"), "high"),
    ("npm-token", re.compile(r"\bnpm_[A-Za-z0-9]{36}\b"), "high"),
    ("private-key-block", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY-----"), "critical"),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"), "medium"),
    ("credentials-in-url", re.compile(r"\b[a-zA-Z][a-zA-Z0-9+.\-]*://[^/\s:@\"']+:[^/\s:@\"']{3,}@[^\s/\"']+"), "high"),
]

GENERIC_ASSIGNMENT = re.compile(
    r"""(?ix)
    (?P<key>[a-z0-9_.\-]*(?:api[_\-]?key|secret|token|passwd|password|private[_\-]?key|access[_\-]?key|auth)[a-z0-9_.\-]*)
    ["']?\s*(?::|=|:=|=>)\s*
    ["'](?P<value>[^"'\s]{12,})["']
    """
)
PLACEHOLDER_HINTS = (
    "example", "sample", "dummy", "placeholder", "changeme", "change_me", "your_", "your-",
    "xxxx", "****", "<", "${", "{{", "process.env", "os.environ", "getenv", "redacted", "test",
)


@dataclass
class Finding:
    rule: str
    severity: str
    file: str
    line: int
    preview: str
    commit: Optional[str] = None


def shannon_entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = {ch: value.count(ch) for ch in set(value)}
    length = len(value)
    return -sum((c / length) * math.log2(c / length) for c in counts.values())


def mask(secret: str) -> str:
    if len(secret) <= 8:
        return "*" * len(secret)
    return f"{secret[:4]}{'*' * min(len(secret) - 4, 16)}"


def looks_like_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(hint in lowered for hint in PLACEHOLDER_HINTS) or len(set(value)) <= 3


def scan_line(text: str, use_generic: bool = True) -> Iterator[Tuple[str, str, str]]:
    """Yield (rule, severity, masked_match) for every secret found in one line."""
    if any(marker in text for marker in IGNORE_MARKERS):
        return
    matched_spans: List[Tuple[int, int]] = []
    for rule, pattern, severity in RULES:
        for m in pattern.finditer(text):
            matched_spans.append(m.span())
            yield rule, severity, mask(m.group(0))
    if not use_generic:
        return
    for m in GENERIC_ASSIGNMENT.finditer(text):
        value = m.group("value")
        start = m.start("value")
        if any(s <= start < e for s, e in matched_spans):
            continue
        if looks_like_placeholder(value) or shannon_entropy(value) < 3.5:
            continue
        yield "generic-secret-assignment", "medium", f"{m.group('key')}={mask(value)}"


def iter_files(root: str) -> Iterator[str]:
    if os.path.isfile(root):
        yield root
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name in SKIP_FILES or os.path.splitext(name)[1].lower() in SKIP_EXTENSIONS:
                continue
            path = os.path.join(dirpath, name)
            try:
                if os.path.getsize(path) > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            yield path


def read_text(path: str) -> Optional[str]:
    try:
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError:
        return None
    if b"\x00" in data[:8192]:
        return None
    return data.decode("utf-8", errors="replace")


def scan_tree(root: str, use_generic: bool = True) -> List[Finding]:
    findings: List[Finding] = []
    for path in iter_files(root):
        text = read_text(path)
        if text is None:
            continue
        rel = os.path.relpath(path, root) if os.path.isdir(root) else path
        for lineno, line in enumerate(text.splitlines(), start=1):
            for rule, severity, preview in scan_line(line, use_generic):
                findings.append(Finding(rule, severity, rel, lineno, preview))
    return findings


def scan_history(root: str, use_generic: bool = True) -> List[Finding]:
    """Scan every added line in every commit reachable from any ref."""
    try:
        proc = subprocess.run(
            ["git", "-C", root, "log", "--all", "-p", "--no-color", "--unified=0", "--format=commit %H"],
            capture_output=True, text=True, errors="replace", check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"warning: could not read git history: {exc}", file=sys.stderr)
        return []
    findings: List[Finding] = []
    commit, current_file, new_lineno = None, None, 0
    hunk = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)")
    for raw in proc.stdout.splitlines():
        if raw.startswith("commit "):
            commit = raw.split()[1][:12]
        elif raw.startswith("+++ "):
            current_file = raw[6:] if raw.startswith("+++ b/") else None
        elif raw.startswith("@@"):
            m = hunk.match(raw)
            new_lineno = int(m.group(1)) if m else 0
        elif raw.startswith("+") and current_file:
            for rule, severity, preview in scan_line(raw[1:], use_generic):
                findings.append(Finding(rule, severity, current_file, new_lineno, preview, commit))
            new_lineno += 1
    return findings


def dedupe(findings: Iterable[Finding]) -> List[Finding]:
    seen, out = set(), []
    for f in findings:
        key = (f.rule, f.file, f.preview)
        if key not in seen:
            seen.add(key)
            out.append(f)
    return out


SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Find hard-coded secrets in files and git history.")
    parser.add_argument("path", nargs="?", default=".", help="file or directory to scan (default: .)")
    parser.add_argument("--history", action="store_true", help="also scan all git history")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--no-generic", action="store_true", help="disable entropy-based generic rule")
    args = parser.parse_args(argv)

    if not os.path.exists(args.path):
        print(f"error: {args.path} does not exist", file=sys.stderr)
        return 2

    use_generic = not args.no_generic
    findings = scan_tree(args.path, use_generic)
    if args.history:
        findings += scan_history(args.path if os.path.isdir(args.path) else ".", use_generic)
    findings = sorted(dedupe(findings), key=lambda f: (SEVERITY_ORDER.get(f.severity, 9), f.file, f.line))

    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2))
    elif not findings:
        print("No secrets found.")
    else:
        for f in findings:
            where = f"{f.file}:{f.line}" + (f" @ {f.commit}" if f.commit else "")
            print(f"[{f.severity.upper():8}] {f.rule:28} {where}  {f.preview}")
        print(f"\n{len(findings)} potential secret(s) found. Rotate real credentials before cleaning history.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
