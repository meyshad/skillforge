#!/usr/bin/env bash
# SkillForge installer: copies Agent Skills (SKILL.md folders) into your agent's skills directory.
#
#   curl -fsSL https://raw.githubusercontent.com/meyshad/skillforge/main/scripts/install.sh | bash
#   ./scripts/install.sh --target codex --plugin security
#   ./scripts/install.sh --project --skill commit-craft --skill code-review
set -euo pipefail

REPO_URL="${SKILLFORGE_REPO:-https://github.com/meyshad/skillforge.git}"
TARGET="claude"
SCOPE="user"
DEST=""
PLUGINS=""
SKILLS=""
MODE="install"
FORCE=0

c_green=$'\033[32m'; c_yellow=$'\033[33m'; c_red=$'\033[31m'; c_dim=$'\033[2m'; c_off=$'\033[0m'
if [ ! -t 1 ]; then c_green=""; c_yellow=""; c_red=""; c_dim=""; c_off=""; fi

usage() {
  cat <<'EOF'
SkillForge installer

Usage: install.sh [options]

Targets (where skills are installed):
  -t, --target NAME   claude (default) -> ~/.claude/skills
                      codex            -> ~/.codex/skills
  -p, --project       install into ./.claude/skills (or ./.codex/skills) of the current directory
  -d, --dir PATH      install into a custom directory (any agent that reads SKILL.md folders)

Selection (default: everything):
      --plugin NAME   only skills from this plugin (repeatable): dev-workflow, security, docs, devops, frontend
      --skill NAME    only this skill (repeatable)

Actions:
  -l, --list          list available plugins and skills
  -u, --uninstall     remove the selected skills from the target
  -f, --force         overwrite skills that already exist
  -h, --help          show this help
EOF
}

die() { printf '%serror:%s %s\n' "$c_red" "$c_off" "$*" >&2; exit 1; }

while [ $# -gt 0 ]; do
  case "$1" in
    -t|--target)  [ $# -ge 2 ] || die "$1 needs a value"; TARGET="$2"; shift 2 ;;
    -p|--project) SCOPE="project"; shift ;;
    -d|--dir)     [ $# -ge 2 ] || die "$1 needs a value"; DEST="$2"; shift 2 ;;
    --plugin)     [ $# -ge 2 ] || die "$1 needs a value"; PLUGINS="$PLUGINS $2"; shift 2 ;;
    --skill)      [ $# -ge 2 ] || die "$1 needs a value"; SKILLS="$SKILLS $2"; shift 2 ;;
    -l|--list)    MODE="list"; shift ;;
    -u|--uninstall) MODE="uninstall"; shift ;;
    -f|--force)   FORCE=1; shift ;;
    -h|--help)    usage; exit 0 ;;
    *) die "unknown option: $1 (see --help)" ;;
  esac
done

# Locate the repository: use the local checkout when run from it, otherwise clone a shallow copy.
SRC=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
  candidate="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  [ -d "$candidate/plugins" ] && SRC="$candidate"
fi
if [ -z "$SRC" ]; then
  command -v git >/dev/null 2>&1 || die "git is required"
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT
  printf '%sFetching SkillForge...%s\n' "$c_dim" "$c_off"
  git clone --quiet --depth 1 "$REPO_URL" "$TMP/skillforge" || die "could not clone $REPO_URL"
  SRC="$TMP/skillforge"
fi

if [ -z "$DEST" ]; then
  case "$TARGET" in
    claude) base=".claude" ;;
    codex)  base=".codex" ;;
    *) die "unknown target '$TARGET' (use claude, codex, or --dir PATH)" ;;
  esac
  if [ "$SCOPE" = "project" ]; then DEST="$PWD/$base/skills"; else DEST="$HOME/$base/skills"; fi
fi

contains() { case " $1 " in *" $2 "*) return 0 ;; *) return 1 ;; esac; }

description_of() {
  sed -n 's/^description:[[:space:]]*//p' "$1/SKILL.md" | head -n 1 | cut -c1-90
}

selected=0; done_count=0; skipped=0
for plugin_dir in "$SRC"/plugins/*/; do
  plugin="$(basename "$plugin_dir")"
  if [ -n "$PLUGINS" ] && ! contains "$PLUGINS" "$plugin"; then continue; fi
  [ "$MODE" = "list" ] && printf '\n%s%s%s\n' "$c_green" "$plugin" "$c_off"
  for skill_dir in "$plugin_dir"skills/*/; do
    [ -f "$skill_dir/SKILL.md" ] || continue
    skill="$(basename "$skill_dir")"
    if [ -n "$SKILLS" ] && ! contains "$SKILLS" "$skill"; then continue; fi
    selected=$((selected + 1))
    case "$MODE" in
      list)
        printf '  %-22s %s%s...%s\n' "$skill" "$c_dim" "$(description_of "$skill_dir")" "$c_off" ;;
      uninstall)
        if [ -f "$DEST/$skill/SKILL.md" ]; then
          rm -rf "${DEST:?}/$skill"; done_count=$((done_count + 1))
          printf '  %s-%s %s\n' "$c_red" "$c_off" "$skill"
        fi ;;
      install)
        mkdir -p "$DEST"
        if [ -e "$DEST/$skill" ] && [ "$FORCE" -ne 1 ]; then
          skipped=$((skipped + 1))
          printf '  %s=%s %s %s(exists, use --force to update)%s\n' "$c_yellow" "$c_off" "$skill" "$c_dim" "$c_off"
          continue
        fi
        rm -rf "${DEST:?}/$skill"
        cp -R "$skill_dir" "$DEST/$skill"
        find "$DEST/$skill" -name '*.py' -exec chmod +x {} +
        done_count=$((done_count + 1))
        printf '  %s+%s %s\n' "$c_green" "$c_off" "$skill" ;;
    esac
  done
done

[ "$selected" -gt 0 ] || die "no skills matched your selection (try --list)"

case "$MODE" in
  install)
    printf '\n%sInstalled %d skill(s)%s into %s' "$c_green" "$done_count" "$c_off" "$DEST"
    [ "$skipped" -gt 0 ] && printf ' (%d skipped)' "$skipped"
    printf '\nRestart your agent session to load them.\n' ;;
  uninstall)
    printf '\nRemoved %d skill(s) from %s\n' "$done_count" "$DEST" ;;
esac
