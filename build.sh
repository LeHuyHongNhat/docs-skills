#!/usr/bin/env bash
# Đồng bộ tài nguyên dùng chung (_shared) vào từng skill, validate và đóng gói.
# Single source of truth là _shared/: không sửa trực tiếp bản copy trong từng skill.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
SC=/mnt/skills/examples/skill-creator
DOC_SKILLS=(product-spec-writer codebase-doc-writer diagram-to-doc doc-clarity-review)
POST_SKILLS=(community-post-writer)
RESEARCH_SKILLS=(agent-research-workflow)
SKILLS=("${DOC_SKILLS[@]}" "${POST_SKILLS[@]}" "${RESEARCH_SKILLS[@]}")
mkdir -p "$ROOT/dist"

sync_common() {  # renderer, charts, stats, presentation + rigor guides, theme — every skill
  local s=$1
  mkdir -p "$ROOT/$s/scripts" "$ROOT/$s/references" "$ROOT/$s/assets"
  cp "$ROOT/_shared/scripts/render_doc.py" "$ROOT/_shared/scripts/charts.py" "$ROOT/_shared/scripts/stats_check.py" "$ROOT/$s/scripts/"
  cp "$ROOT/_shared/references/visual-style.md" "$ROOT/_shared/references/presentation-and-charts.md" \
     "$ROOT/_shared/references/research-rigor.md" "$ROOT/_shared/references/reader-test.md" \
     "$ROOT/_shared/references/agent-assisted-research.md" "$ROOT/$s/references/"
  cp "$ROOT/_shared/assets/doc-theme.css" "$ROOT/_shared/assets/reference.docx" "$ROOT/$s/assets/"
}

for s in "${DOC_SKILLS[@]}"; do
  sync_common "$s"
  cp "$ROOT/_shared/scripts/lint_doc.py" "$ROOT/$s/scripts/"
  cp "$ROOT/_shared/references/writing-standards.md" "$ROOT/$s/references/"
done
for s in "${POST_SKILLS[@]}" "${RESEARCH_SKILLS[@]}"; do
  sync_common "$s"
  cp "$ROOT/_shared/assets/experiment-plan-template.md" "$ROOT/$s/assets/"
done
for s in "${SKILLS[@]}"; do
  (cd "$SC" && python3 -m scripts.quick_validate "$ROOT/$s")
done
if [[ "${1:-}" == "--package" ]]; then
  for s in "${SKILLS[@]}"; do
    (cd "$SC" && python3 -m scripts.package_skill "$ROOT/$s" "$ROOT/dist")
  done
fi
