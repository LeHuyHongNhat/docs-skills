#!/usr/bin/env bash
# install.sh — install the 4 skills into the skill directory of agents that support Agent Skills (SKILL.md).
#
# Usage:
#   ./install.sh                      # default: Claude Code, user scope (~/.claude/skills)
#   ./install.sh claude codex cursor  # several targets at once
#   ./install.sh --project claude     # project scope (./.claude/skills) instead of user
#   ./install.sh --link claude        # symlink instead of copy (handy while developing)
#
# Targets: claude | codex | cursor | gemini | agents (shared .agents/skills directory)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SKILLS=(product-spec-writer codebase-doc-writer diagram-to-doc doc-clarity-review)
SCOPE=user
MODE=copy
TARGETS=()

for arg in "$@"; do
  case "$arg" in
    --project) SCOPE=project ;;
    --user) SCOPE=user ;;
    --link) MODE=link ;;
    -h|--help) sed -n '2,11p' "$0"; exit 0 ;;
    *) TARGETS+=("$arg") ;;
  esac
done
[[ ${#TARGETS[@]} -eq 0 ]] && TARGETS=(claude)

dir_for() {
  local base
  if [[ $SCOPE == user ]]; then base="$HOME"; else base="$PWD"; fi
  case "$1" in
    claude) echo "$base/.claude/skills" ;;
    codex|agents) echo "$base/.agents/skills" ;;
    cursor) echo "$base/.cursor/skills" ;;
    gemini) echo "$base/.gemini/skills" ;;
    *) echo "Unsupported target: $1" >&2; exit 2 ;;
  esac
}

for t in "${TARGETS[@]}"; do
  dest="$(dir_for "$t")"
  mkdir -p "$dest"
  for s in "${SKILLS[@]}"; do
    rm -rf "${dest:?}/$s"
    if [[ $MODE == link ]]; then
      ln -s "$ROOT/$s" "$dest/$s"
    else
      # skip evals/ (test cases with large input fixtures)
      mkdir -p "$dest/$s"
      (cd "$ROOT/$s" && tar --exclude=evals --exclude=__pycache__ -cf - .) | (cd "$dest/$s" && tar -xf -)
    fi
  done
  echo "✓ $t ($SCOPE): ${#SKILLS[@]} skills → $dest"
done

cat <<'EOF'

Optional tools for PDF/DOCX export (without them the skills still deliver Markdown):
  pandoc · Chrome/Chromium + `pip install playwright` · `npm i -g @mermaid-js/mermaid-cli`
  pip install python-docx openpyxl beautifulsoup4 pyyaml
EOF
