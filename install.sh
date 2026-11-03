#!/usr/bin/env bash
# install.sh — cài 4 skill vào thư mục skill của các agent hỗ trợ chuẩn Agent Skills (SKILL.md).
#
# Usage:
#   ./install.sh                      # mặc định: Claude Code, cấp user (~/.claude/skills)
#   ./install.sh claude codex cursor  # nhiều đích cùng lúc
#   ./install.sh --project claude     # cấp project (./.claude/skills) thay vì user
#   ./install.sh --link claude        # symlink thay vì copy (tiện khi đang phát triển skill)
#
# Đích hỗ trợ: claude | codex | cursor | gemini | agents (thư mục chung .agents/skills)
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
    *) echo "Đích không hỗ trợ: $1" >&2; exit 2 ;;
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
      # không copy evals/ (test case, có file input lớn) vào máy người dùng
      mkdir -p "$dest/$s"
      (cd "$ROOT/$s" && tar --exclude=evals --exclude=__pycache__ -cf - .) | (cd "$dest/$s" && tar -xf -)
    fi
  done
  echo "✓ $t ($SCOPE): ${#SKILLS[@]} skill → $dest"
done

cat <<'EOF'

Công cụ ngoài để xuất PDF/DOCX (không bắt buộc — thiếu thì skill vẫn giao .md):
  pandoc · Chrome/Chromium + `pip install playwright` · `npm i -g @mermaid-js/mermaid-cli`
  pip install python-docx openpyxl beautifulsoup4 pyyaml
EOF
