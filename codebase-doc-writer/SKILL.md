---
name: codebase-doc-writer
description: Viết tài liệu kỹ thuật chuẩn chuyên nghiệp trực tiếp từ source code — README, API reference, architecture overview (C4/arc42), module/component doc, ADR, runbook vận hành, onboarding guide cho dev mới, tài liệu cấu hình/env vars. Mọi khẳng định trong tài liệu đều truy được về file:line, không bịa endpoint/biến môi trường/lệnh. Dùng skill này bất cứ khi nào người dùng muốn "viết README", "document repo này", "viết tài liệu kiến trúc", "viết API docs", "tài liệu cho dev mới", "giải thích codebase thành tài liệu", "write docs for this service", kể cả khi họ chỉ trỏ vào một thư mục code và nói "viết tài liệu cho cái này". Không dùng cho tài liệu yêu cầu nghiệp vụ (PRD/BRD/user story — dùng product-spec-writer) hoặc chỉ sửa câu chữ một tài liệu có sẵn (dùng doc-clarity-review).
---

# Codebase Doc Writer

Tài liệu kỹ thuật sai còn tệ hơn không có tài liệu: dev tin và làm theo. Vì vậy nguyên tắc số một của skill này là **mọi fact phải có nguồn trong code**, và chỗ nào code không trả lời được thì nói thẳng là chưa biết.

## Quy trình

### 1. Xác định loại tài liệu

| Người dùng cần | Loại | Template trong `references/code-doc-templates.md` |
|---|---|---|
| Ai đó mới clone repo cần chạy được | README | `#readme` |
| Client/frontend cần gọi API | API reference | `#api-reference` |
| Dev mới cần hiểu hệ thống, review kiến trúc | Architecture overview | `#architecture` |
| Ghi lại một quyết định kỹ thuật | ADR | `#adr` |
| On-call/vận hành | Runbook | `#runbook` |
| Một module/package cụ thể | Module doc | `#module` |

Yêu cầu chung chung ("viết tài liệu cho repo") → mặc định README; nếu repo có HTTP API thì thêm API reference (có thể là một mục trong README khi ≤ 10 endpoint). Nói một dòng về lựa chọn này.

### 2. Lập inventory bằng script, rồi đọc code

```bash
python <skill-dir>/scripts/scan_repo.py <repo_dir> > /tmp/inventory.md
```

Script liệt kê (kèm file:line): ngôn ngữ, cây thư mục, manifest, entrypoint, HTTP route (FastAPI/Flask/Express/Spring), env var (kể cả field của pydantic `BaseSettings`), CLI, Dockerfile, test, TODO. Đây là **bản đồ để đọc code**, không phải sự thật cuối cùng — regex có thể sót (route đăng ký động, env var đọc qua wrapper) hoặc nhầm prefix.

Sau đó đọc tối thiểu: entrypoint, file config/settings, mọi file chứa route, manifest dependency, Dockerfile/compose, và README cũ nếu có. Với mỗi route: đọc handler để biết request schema, response schema, status code, lỗi có thể trả, auth.

### 3. Lập fact sheet có trích dẫn

Trước khi viết văn, ghi fact sheet (file nháp): mỗi dòng một fact + `file:line`. Ví dụ:
```
- POST /api/v1/orders tạo đơn, trả 201 + OrderOut — app/routers/orders.py:24
- ORDER_MAX_ITEMS mặc định 50 — app/config.py:12
- Worker đọc queue "orders.created" từ Redis — worker/main.py:8
```
Lý do: fact sheet tách bước *thu thập* khỏi bước *diễn đạt*, giúp kiểm độ phủ (so với inventory) và chặn việc "nhớ nhầm" khi viết đoạn văn dài.

Những thứ **không được suy đoán** — nếu code không cho biết thì ghi [CẦN XÁC NHẬN: ...] hoặc bỏ:
- Phiên bản runtime khi không có file khai báo (`.python-version`, `engines`, `FROM python:3.x`).
- Giá trị môi trường production, URL deploy, SLA, số lượng user.
- Hành vi của dịch vụ ngoài mà repo chỉ gọi tới.
- Lệnh chạy/test không có trong Makefile/scripts/manifest — được phép đề xuất lệnh chuẩn của framework nhưng ghi rõ là đề xuất.

### 4. Viết theo template

- Đọc `references/writing-standards.md` (chuẩn câu chữ chung) và template tương ứng.
- **Trích nguồn**: trong architecture/module doc, mỗi thành phần ghi đường dẫn file/thư mục. Trong API reference, mỗi endpoint ghi handler `file:line`. README không cần trích từng dòng nhưng mọi lệnh phải chạy được với cấu hình trong repo.
- **Bảng env var** luôn có cột: tên, bắt buộc?, mặc định (đúng như code), mô tả, nơi đọc. "Bắt buộc" = không có default trong code. So sánh danh sách này với file cấu hình mẫu (`.env.example`, compose, Helm values) và **nói thẳng biến nào thiếu trong file mẫu** — đây là lỗi đầu tiên người mới gặp.
- **Diagram**: dùng Mermaid (C4-style flowchart hoặc sequence). Chỉ vẽ thành phần và luồng có trong code. Nhãn ngắn, không chứa `;` `"` `{}` (vd `BEGIN; INSERT` làm vỡ sequence diagram). Render thử **mọi** diagram nếu có `mmdc` — một diagram lỗi ở luồng chính làm hỏng cả tài liệu:
  ```bash
  echo '{"args":["--no-sandbox"]}' > /tmp/pp.json && mmdc -p /tmp/pp.json -i diagram.mmd -o /tmp/diagram.svg
  ```
- Nhắc tới marker trong code (TODO, FIXME) thì bọc backtick: `TODO` tại `app/x.py:16` — đó là trích dẫn code, không phải placeholder của tài liệu.
- **Ví dụ request/response**: dựng từ schema thật (Pydantic model, DTO, TypeScript type). Giá trị ví dụ được phép bịa nhưng tên field, kiểu, field bắt buộc phải khớp schema.
- Ghi rõ **rủi ro / nợ kỹ thuật** quan sát được trong code (TODO, secret hard-code, thiếu retry, thiếu test cho module X) trong mục riêng — đây là thông tin dev mới và reviewer cần nhất, và chỉ người đọc code mới thấy.
- Ngôn ngữ: theo ngôn ngữ người dùng yêu cầu; tên biến, endpoint, lệnh giữ nguyên trong `code`.

### 5. Kiểm chứng trước khi bàn giao

1. **Đối chiếu ngược**: mỗi endpoint/env var/lệnh trong tài liệu phải có trong fact sheet; mỗi route và env var trong inventory phải có trong tài liệu hoặc được ghi lý do loại (vd route nội bộ `/metrics`).
2. Nếu sandbox cho phép: chạy thử lệnh cài đặt/khởi động/test ghi trong README (hoặc ít nhất `python -c "import app"`/`--help`) trên **bản copy** của repo. Ghi nhận lệnh nào đã verify. Dependency không pin version (`redis>=5.0`) sẽ cài bản mới nhất — nếu chạy thử thấy lỗi do major version mới, ghi rõ version đã test và đề xuất pin.
3. Chạy linter câu chữ:
   ```bash
   python <skill-dir>/scripts/lint_doc.py <output.md>
   ```
   Code block được linter bỏ qua; sửa các finding `high` trong phần văn.
4. Trong câu trả lời bàn giao: liệt kê ngắn các mục [CẦN XÁC NHẬN] và những gì đã/chưa verify bằng cách chạy.

### Xuất định dạng & kiểm tra thẩm mỹ

Markdown là nguồn. Khi người dùng cần PDF/DOCX/XLSX (gửi sếp/khách, in, "file Word", "Excel để lọc"), hoặc nói tài liệu sẽ được chia sẻ, đọc `references/visual-style.md` rồi render:
```bash
python <skill-dir>/scripts/render_doc.py <file.md> --to pdf,docx,xlsx --out-dir <thư mục output> --qa
```
Người dùng nói đọc trên điện thoại/mobile → thêm `--page mobile` (khổ hẹp, bảng thành thẻ); cần cả bản in thì render thêm bản A4. Xem warnings và các ảnh trang trong `qa.preview_pages` (ít nhất trang đầu, trang có bảng lớn nhất, trang có diagram); sửa `.md` rồi render lại nếu bảng tràn, diagram không hiện, chữ lỗi dấu. Không nói định dạng nào là "đã xuất" nếu script báo bỏ qua nó. Người dùng không nhắc định dạng → chỉ giao `.md` và nhắc một dòng rằng có thể xuất PDF/DOCX/XLSX.


## Tài nguyên

- `scripts/scan_repo.py` — inventory repo có file:line (md hoặc `--format json`).
- `scripts/lint_doc.py` — linter câu chữ mơ hồ.
- `references/code-doc-templates.md` — template README, API reference, architecture, ADR, runbook, module doc.
- `references/writing-standards.md` — chuẩn câu chữ dùng chung (gồm §7b độ dài tương xứng).
- `scripts/render_doc.py` + `assets/` + `references/visual-style.md` — xuất PDF/DOCX/XLSX có thiết kế và visual QA.
