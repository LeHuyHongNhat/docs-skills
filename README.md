# doc-skills — Bộ skill giúp AI agent viết tài liệu sản phẩm chuẩn chuyên nghiệp

Bộ 4 [Claude skill](https://docs.claude.com) hỗ trợ BA, PM, PO, DA và dev viết tài liệu **chặt chẽ, không mơ hồ, không bịa**, và xuất ra định dạng trình bày đẹp (PDF A4 / PDF điện thoại / Word / Excel).

| Skill | Dùng khi |
|---|---|
| [`product-spec-writer`](product-spec-writer/) | BRD, PRD, SRS, user story + acceptance criteria (Gherkin), use case, định nghĩa metric/KPI |
| [`codebase-doc-writer`](codebase-doc-writer/) | README, API reference, architecture overview, ADR, runbook — viết từ source code, mọi fact truy được về `file:line` |
| [`diagram-to-doc`](diagram-to-doc/) | Ảnh flowchart / BPMN / sequence / ERD / state / wireframe → đặc tả, data dictionary |
| [`doc-clarity-review`](doc-clarity-review/) | Review và viết lại tài liệu có sẵn: từ mơ hồ, mâu thuẫn, yêu cầu không kiểm thử được |

## Nguyên tắc

- **Không tự quyết thay stakeholder:** mâu thuẫn và thông tin thiếu được đánh dấu `[CẦN XÁC NHẬN]` và gom vào Open Questions, không lấp bằng số "nghe hợp lý".
- **Đề xuất tách khỏi đặc tả:** những gì agent tự đề xuất nằm ở mục riêng, không lẫn vào requirement/AC.
- **Kiểm chứng bằng công cụ:** linter câu chữ (VI + EN), kiểm inventory diagram, render + xem ảnh từng trang trước khi bàn giao.

## Cài đặt

Tải file `.skill` trong [`dist/`](dist/) và cài vào Claude (claude.ai → Settings → Skills), hoặc copy thư mục skill vào `~/.claude/skills/` cho Claude Code.

Xuất PDF/DOCX cần `pandoc`, Chrome/Chromium (qua Playwright) và `@mermaid-js/mermaid-cli`. Thiếu công cụ nào thì skill vẫn giao `.md` và báo rõ định dạng nào chưa xuất được.

## Cấu trúc repo

```
_shared/            nguồn dùng chung (single source of truth)
  references/       writing-standards.md, visual-style.md
  scripts/          lint_doc.py, render_doc.py
  assets/           doc-theme.css, reference.docx
  tests/            48 unit test (pytest)
<skill>/            4 skill; scripts/references/assets được đồng bộ từ _shared bằng build.sh
  evals/            test case theo format `claude plugin eval`
_eval_tools/        công cụ kiểm định: auto checks, blind A/B, routing eval bằng `claude -p`
dist/               file .skill đã đóng gói
docs/               báo cáo kiểm định + benchmark
samples/            file mẫu do skill tạo (Word, PDF A4/mobile, Excel)
```

## Phát triển

```bash
./build.sh              # đồng bộ _shared → 4 skill + validate
./build.sh --package    # + đóng gói vào dist/
cd _shared && python -m pytest -q tests
```

Sửa script/reference **trong `_shared/`**, không sửa bản copy trong từng skill.

## Kết quả kiểm định (tóm tắt)

| Chỉ số | Có skill | Không skill |
|---|---|---|
| Assertion pass rate (10 case) | **92,5%** | 72,0% |
| Blind A/B (8 case nội dung, vòng 1) | **thắng 8/8** | – |
| Routing đúng skill (`claude -p`, 52 lượt) | **100%** | – |

Chi tiết, phương pháp và hạn chế: [`docs/bao-cao-kiem-dinh-doc-skills.md`](docs/bao-cao-kiem-dinh-doc-skills.md).
