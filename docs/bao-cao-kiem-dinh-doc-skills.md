# Báo cáo xây dựng & kiểm định bộ skill viết tài liệu sản phẩm

| Phiên bản | Ngày | Người thực hiện | Trạng thái |
|---|---|---|---|
| v2.2 | 2026-11-03 | Claude (skill-creator) cho Le Nhat | Sẵn sàng dùng thử nội bộ |

> **Tóm tắt:** Bộ 4 skill giúp agent viết tài liệu sản phẩm/kỹ thuật chặt chẽ, không bịa, trình bày chuyên nghiệp (MD → PDF/DOCX/XLSX). Kiểm định bằng 7 phương pháp qua 2 vòng lặp. So với Claude không có skill: tỉ lệ đạt assertion 92,5% vs 72,0% (10 case); blind A/B thắng 8/8 case nội dung (vòng 1) và 1/2 case định dạng (vòng 2 — case thua đã sửa, chưa chấm lại). Điểm yếu còn lại: tài liệu vẫn dài hơn mức lý tưởng với input rất ngắn, và chi phí thời gian cao hơn baseline khoảng 2–2,5 lần.

## 1. Bộ skill

| Skill | Dùng khi | Công cụ đi kèm |
|---|---|---|
| `product-spec-writer` | BRD, PRD, SRS, user story + AC Gherkin, use case, metric definition (DA) | templates, `lint_doc.py`, `render_doc.py` |
| `codebase-doc-writer` | README, API reference, architecture (C4/arc42), ADR, runbook từ source code | `scan_repo.py` (inventory file:line) |
| `diagram-to-doc` | Ảnh flowchart/BPMN/sequence/ERD/state/wireframe → đặc tả, data dictionary | `zoom_tiles.py`, `check_diagram.py` (kiểm inventory + Mermaid round-trip) |
| `doc-clarity-review` | Review/viết lại tài liệu có sẵn: mơ hồ, mâu thuẫn, không test được | rubric 17 mã lỗi, `lint_doc.py` |

Dùng chung trong cả 4 skill (nguồn duy nhất `_shared/`, đồng bộ bằng `build.sh`):
- `writing-standards.md`: modal RFC 2119, EARS, bảng từ mơ hồ VI/EN, quy tắc [CẦN XÁC NHẬN], độ dài tương xứng.
- `visual-style.md`: quy tắc trình bày và quy trình visual QA.
- `lint_doc.py`: linter.
- `render_doc.py`: xuất PDF A4 / PDF mobile / DOCX / XLSX.

**Nguyên tắc thiết kế chính:**
- Tách hai pha *thu thập fact có nguồn* và *diễn đạt*.
- Không bao giờ tự quyết thay stakeholder: mâu thuẫn và giá trị thiếu được đánh dấu [CẦN XÁC NHẬN] và đưa vào Open Questions.
- Đề xuất của agent tách riêng khỏi đặc tả.

## 2. Phương pháp kiểm định

| # | Phương pháp | Đo cái gì | Kết quả |
|---|---|---|---|
| 1 | Structural validation (`quick_validate`, package) | Frontmatter, cấu trúc skill | 4/4 hợp lệ |
| 2 | Unit test các script (48 test) | Linter (true/false positive VI+EN), scan_repo (ground truth 5 route / 6 env var), check_diagram, render_doc (end-to-end, mobile, sheet naming) | 48/48 pass |
| 3 | Eval có skill vs không skill (10 case, LLM grader + script) | Assertion khách quan theo từng case | Xem §3 |
| 4 | Blind A/B comparator | Judge không biết bên nào là skill | Xem §3 |
| 5 | Ground-truth fidelity | Diagram sinh từ DOT có đáp án: edge recall, column accuracy, planted-issue recall | Flowchart 16/16 cạnh; ERD 25/25 cột; review 13/13 lỗi cài sẵn (v2) |
| 6 | Routing eval bằng `claude -p` thật | Cả 4 skill cài cùng lúc, 26 query × 2 lượt (gồm 6 near-miss) | 52/52 (100%); vẫn 52/52 khi cài thêm 3 skill đối thủ (`docs`, `docx`, `technical-writer`) |
| 7 | Visual QA | Ảnh trang PDF/DOCX được judge xem trực tiếp; check font nhúng, chữ có dấu, Mermaid lộ mã, cỡ chữ hiệu dụng | Xem §3.3 |

## 3. Kết quả

### 3.1 Vòng 1 (v1, 8 case nội dung)
- Assertion: có skill **97,5%** vs không skill 85,5%.
- Blind A/B: có skill thắng **8/8**, điểm TB 9,1 vs 8,3.
- Chi phí: +85% thời gian, +30% token.
- Judge chê bản có skill độn nội dung (mục RFC 2119, glossary từ hiển nhiên, câu hỏi mở lặp lại).

### 3.2 Vòng 2 (v2, assertion siết lại + 2 case định dạng)

| So sánh | Assertion | Blind A/B |
|---|---|---|
| v2 vs không skill (10 case) | **92,5%** vs 72,0% | Chỉ chạy blind trên 2 case định dạng: thắng PRD→Word, thua ERD→mobile (§3.3). 8 case nội dung: xem v1 vs baseline ở §3.1 |
| v2 vs v1 (8 case chung) | **94,9%** vs 91,0% | v2 thắng 6/8; v1 thắng sát 2/8 (architecture 9,3–9,0; ERD 9,0–8,7) |

- Độ dài tài liệu v2 giảm **32%** so với v1, token giảm 7%.
- Thời gian tăng, chủ yếu do v2 chạy kiểm chứng code thật nhiều hơn.

**Khác biệt thật giữa có skill và không skill:**
- Bản không skill hay **bịa giá trị** vào requirement/AC: enum trạng thái, ngưỡng 10.000, p95 ≤ 2s, chọn 5 phút OTP.
- Bản không skill **trộn đề xuất vào đặc tả**.
- Bản không skill lint bẩn hơn.
- Bản có skill phát hiện nhiều lỗi thật trong fixture hơn: redis-py 8.x làm worker crash, `make worker` không chạy do thiếu `.PHONY`, `.env` bị pydantic từ chối biến lạ.

### 3.3 Thẩm mỹ & định dạng

| Case | Lần chạy | Kết quả blind | Ghi chú |
|---|---|---|---|
| PRD → Word | v2 | thắng 9,0–6,5 | marker vàng, bảng full ngang; thiếu số trang |
| PRD → Word | v2.1 | thắng 8,5–6,3 | |
| PRD → Word | v2.2 | — | đã thêm footer "Trang x/y", Title/Heading chuẩn Word, ID không gãy, 3.267 từ (từ 4.173) |
| ERD → Excel + PDF điện thoại | v2 | **thua** 7,7–9,0 | xuất A4, chưa có chế độ mobile |
| ERD → Excel + PDF điện thoại | v2.1 | **thua** 6,0–9,0 | chữ thực tế 5–6pt |
| ERD → Excel + PDF điện thoại | v2.2 | — | đã sửa: cỡ chữ đo được 16,9pt; thêm check tự động cảnh báo khi chữ < 7,5pt |

Bản v2.2 của case ERD/mobile **chưa được chấm lại bằng blind A/B**. Đây là việc cần làm đầu tiên ở vòng sau.

## 4. Lỗi đã phát hiện nhờ kiểm định & đã sửa

**Linter**
- Đếm `AC-001.1` / `AC-001.2` là ID trùng.
- Bắt nhầm "không được lưu" (modal cấm) là câu bị động.
- Bắt nhầm heading "User stories" là lệch thuật ngữ.
- Bảng ánh xạ/truy vết bị báo trùng ID.
- Từ "mềm" (nhiều, đầy đủ) bị xếp mức high.

**Renderer**
- Mermaid ERD làm méo `DECIMAL(12,2)`; ERD hiển thị "UK" thay cho "UQ".
- Tên sheet Excel mất dấu `_`; bảng metadata thành sheet rác.
- Mục lục DOCX tiếng Anh, trống; DOCX không có số trang.
- PDF mobile bị thu nhỏ cả trang.

**Hướng dẫn trong skill**
- Agent tự chế rule ON DELETE.
- Agent dựng AC trên giá trị tự chọn.
- Cột "Hạn" độn trong bảng câu hỏi mở.
- Bảng câu hỏi mở bị lặp lại ở phụ lục.
- Thiếu bảng 3 biến thể retention.
- "Nguyên nhân gốc là…" khẳng định khi chưa có dữ liệu.

**Bản thân bộ eval**
- Một assertion sai sự thật (khuyên đặt SMTP_HOST vào `.env`).
- Một assertion thiên vị cách làm của skill (bắt buộc mỗi bảng một sheet).
- Nhiều assertion không phân biệt được các config → đã thay bằng assertion sắc hơn.

## 5. Hạn chế & rủi ro (phản biện)

1. **Assertion chưa đủ:**
   - Ở case README, baseline đạt 10/10 assertion dù hướng dẫn của nó làm worker crash.
   - Ở case metric, cả 3 cấu hình đều 7/9.
   - Kết luận: phải đọc kết hợp với blind A/B và đọc output thật, không chỉ nhìn % pass.
2. **Mẫu nhỏ:** 1 run cho mỗi cấu hình mỗi case, chưa có variance. Chênh 1–2 điểm ở judge là trong biên nhiễu.
3. **Judge cùng họ model với executor** (Claude chấm Claude). Có thể có thiên vị phong cách; nên thêm human blind review với BA/PO thật.
4. **Linter có tính vòng tròn:** skill dặn chạy chính linter dùng để chấm. Chỉ coi là chỉ số tuân thủ quy trình.
5. **Độ dài:** input 9 dòng chat vẫn ra PRD ~3.300 từ, mục tiêu là ≤ 2.500.
6. **Chi phí:** thời gian chạy ~2–2,5 lần baseline. Đổi lại là kiểm chứng thật và ít bịa hơn.
7. **Phụ thuộc môi trường:** PDF/DOCX cần pandoc, Chrome, mmdc. Thiếu thì skill vẫn giao `.md` và báo rõ định dạng nào chưa xuất được.
8. **Sự cố quy trình:** 2 run gọi nhầm Artifact; một lần đã publish rồi xóa ngay. Prompt test sau đó đã cấm hẳn.

## 6. Việc nên làm tiếp

- Chạy lại blind A/B case ERD-mobile và PRD-docx với v2.2, mỗi cấu hình 3 run để đo variance.
- Human blind review 5–10 tài liệu với BA/PO trong team.
- Thêm fixture khó hơn:
  - ảnh chụp whiteboard nghiêng, mờ;
  - BPMN có gateway song song;
  - repo Node/Java;
  - tài liệu tiếng Anh.
- Chạy `claude plugin eval` trên các thư mục `evals/` (đã đúng format) để tích hợp CI.
