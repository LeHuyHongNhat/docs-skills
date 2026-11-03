#!/usr/bin/env bash
# Đồng bộ tài nguyên dùng chung (_shared) vào từng skill, validate và đóng gói.
# Single source of truth là _shared/: không sửa trực tiếp bản copy trong từng skill.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
SC=/mnt/skills/examples/skill-creator
SKILLS=(product-spec-writer codebase-doc-writer diagram-to-doc doc-clarity-review)
mkdir -p "$ROOT/dist"
for s in "${SKILLS[@]}"; do
  mkdir -p "$ROOT/$s/scripts" "$ROOT/$s/references"
  cp "$ROOT/_shared/scripts/lint_doc.py" "$ROOT/_shared/scripts/render_doc.py" "$ROOT/$s/scripts/"
  cp "$ROOT/_shared/references/writing-standards.md" "$ROOT/_shared/references/visual-style.md" "$ROOT/$s/references/"
  mkdir -p "$ROOT/$s/assets"
  cp "$ROOT/_shared/assets/doc-theme.css" "$ROOT/_shared/assets/reference.docx" "$ROOT/$s/assets/"
  (cd "$SC" && python3 -m scripts.quick_validate "$ROOT/$s")
done
if [[ "${1:-}" == "--package" ]]; then
  for s in "${SKILLS[@]}"; do
    (cd "$SC" && python3 -m scripts.package_skill "$ROOT/$s" "$ROOT/dist")
  done
fi
