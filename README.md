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

Bốn skill theo chuẩn mở **Agent Skills** (`SKILL.md` + `scripts/` + `references/` + `assets/`). Cùng một thư mục skill chạy được trên nhiều agent; chỉ khác nơi đặt file.

| Nền tảng | Cách cài | Ghi chú |
|---|---|---|
| **Claude Code** (khuyên dùng) | Trong Claude Code: `/plugin marketplace add LeHuyHongNhat/docs-skills` rồi `/plugin install docs-skills@docs-skills` | Cập nhật bằng `/plugin marketplace update`. Skill hiện với tên `docs-skills:<tên>` |
| **Claude Code** (thủ công) | `./install.sh claude` → copy vào `~/.claude/skills/` (thêm `--project` để cài vào `./.claude/skills/` của repo hiện tại) | Dùng khi không muốn qua plugin |
| **claude.ai / Claude Desktop** | Settings → Customize → **Skills** → upload từng file trong [`dist/`](dist/) (`*.skill` là file zip chứa thư mục skill) | Phải bật code execution & file creation để chạy linter/render |
| **Claude API** | Upload qua Skills API, gọi trong Messages API bằng `container.skills` kèm tool code execution — xem [Agent Skills quickstart](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart) | Dùng khi tích hợp vào sản phẩm/agent riêng |
| **OpenAI Codex CLI** | `./install.sh codex` → `~/.agents/skills/` | Đọc chuẩn SKILL.md |
| **Cursor** | `./install.sh cursor` → `~/.cursor/skills/` | Cursor cũng đọc `.claude/skills/` |
| **Gemini CLI** | `./install.sh gemini` → `~/.gemini/skills/` | Gemini CLI ≥ 0.26 |
| **ChatGPT** | Skills đang ở dạng beta cho gói Business/Enterprise — xem hướng dẫn upload của OpenAI | Gói cá nhân: dùng Custom GPT, dán `SKILL.md` vào Instructions và đính `references/*.md` làm Knowledge (mất phần script render) |

Repo đang **private**: lệnh `/plugin marketplace add` và `git clone` cần máy đã đăng nhập GitHub (`gh auth login` hoặc git credential) với quyền đọc repo. Người không có quyền dùng file `.skill` trong `dist/`.

Cài nhiều đích một lần: `./install.sh claude codex cursor`. Đang sửa skill thì dùng `--link` để symlink thay vì copy.

**Công cụ cho phần xuất định dạng** (không bắt buộc — thiếu thì skill vẫn giao `.md` và báo rõ định dạng nào chưa xuất được):

```bash
pip install python-docx openpyxl beautifulsoup4 pyyaml playwright
npm i -g @mermaid-js/mermaid-cli
# + pandoc và Chrome/Chromium
```

## Cấu trúc repo

```
.claude-plugin/     marketplace.json — cài cả bộ qua Claude Code plugin
_shared/            nguồn dùng chung (single source of truth)
  references/       writing-standards.md, visual-style.md
  scripts/          lint_doc.py, render_doc.py
  assets/           doc-theme.css, reference.docx
  tests/            48 unit test (pytest)
<skill>/            4 skill; scripts/references/assets được đồng bộ từ _shared bằng build.sh
  evals/            test case theo format `claude plugin eval`
_eval_tools/        công cụ kiểm định: auto checks, blind A/B, routing eval bằng `claude -p`
dist/               file .skill đã đóng gói (upload lên claude.ai)
install.sh          cài vào Claude Code / Codex / Cursor / Gemini CLI
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
