---
name: product-spec-writer
description: Viết tài liệu đặc tả sản phẩm chuẩn chuyên nghiệp cho BA/PM/PO/DA — BRD, PRD, SRS/FRD, user story + acceptance criteria (Gherkin), use case specification, business rules, non-functional requirements, metric/KPI definition, data dictionary nghiệp vụ. Dùng skill này bất cứ khi nào người dùng muốn biến meeting notes, ý tưởng, ticket, email, yêu cầu rời rạc thành tài liệu đặc tả chặt chẽ, có ID, kiểm thử được — kể cả khi họ chỉ nói "viết PRD", "viết spec", "viết user story", "viết tài liệu yêu cầu", "định nghĩa metric", "write requirements", "draft a PRD/BRD/SRS", hoặc "chuẩn hóa yêu cầu này". Không dùng cho tài liệu sinh từ source code (dùng codebase-doc-writer), đặc tả từ ảnh biểu đồ (dùng diagram-to-doc), hay chỉ review/sửa câu chữ tài liệu có sẵn (dùng doc-clarity-review).
---

# Product Spec Writer

Mục tiêu: tạo tài liệu đặc tả mà dev, QA và stakeholder đọc xong **hiểu giống nhau**, QA viết được test case trực tiếp từ đó, và mọi chỗ chưa chắc chắn đều hiện rõ thay vì bị lấp bằng phỏng đoán.

## Quy trình

### 1. Xác định loại tài liệu và người đọc

| Người dùng cần | Loại tài liệu | Template |
|---|---|---|
| Lý do kinh doanh, phạm vi dự án, stakeholder, lợi ích | BRD | `references/templates.md#brd` |
| Một tính năng/sản phẩm: vấn đề, mục tiêu, scope, user story, AC, metric | PRD | `references/templates.md#prd` |
| Đặc tả hệ thống chi tiết để dev/QA thực thi | SRS / FRD | `references/templates.md#srs` |
| Backlog item cho sprint | User story + AC | `references/templates.md#user-story` |
| Tương tác actor–hệ thống theo luồng | Use case spec | `references/templates.md#use-case` |
| Định nghĩa KPI/metric cho dashboard, tracking | Metric definition | `references/templates.md#metric` |

Nếu người dùng không nói rõ loại: chọn loại khớp nhất với input và nói một dòng ở đầu câu trả lời là đã chọn loại nào, vì sao. Chỉ hỏi lại khi hai loại dẫn tới cấu trúc khác hẳn nhau *và* sai thì tốn công làm lại.

Đọc `references/writing-standards.md` (chuẩn câu chữ dùng chung) trước khi viết. Đọc phần template tương ứng trong `references/templates.md`.

### 2. Bóc tách input thành inventory trước khi viết

Input thường là meeting notes lộn xộn, chat, email. Trước khi viết văn bản, liệt kê (có thể chỉ trong suy nghĩ hoặc file nháp):

- **Actors** và vai trò của họ.
- **Facts**: mọi con số, ngưỡng, quy tắc, ràng buộc — kèm nguồn (ai nói, ở đâu).
- **Mâu thuẫn**: hai nguồn nói khác nhau về cùng một điều (vd hạn điểm 6 tháng vs 12 tháng). Đây là phát hiện có giá trị nhất của BA — không được âm thầm chọn một bên.
- **Khoảng trống**: điều tài liệu loại này bắt buộc phải có nhưng input không nói (vd không ai nói chuyện gì xảy ra khi thanh toán thất bại).
- **Out of scope** được nhắc đến hoặc ngầm hiểu.

Lý do: viết thẳng từ input lộn xộn dễ làm mất fact và che giấu mâu thuẫn; inventory giúp kiểm soát độ phủ.

### 3. Viết theo template

Nguyên tắc khi điền template:

- **Mỗi requirement có ID** (`BR-`, `FR-`, `NFR-`, `US-`, `AC-`, `UC-`, `DR-`) và dùng modal chuẩn (phải / không được / nên / được phép). Không dùng "có thể" trong câu requirement.
- **Viết theo EARS** cho functional requirement: "Khi <sự kiện>, hệ thống phải <hành vi>"; "Nếu <lỗi>, thì hệ thống phải <xử lý>".
- **Acceptance criteria dạng Gherkin** (Given/When/Then hoặc Cho/Khi/Thì — giữ nhất quán một kiểu trong tài liệu). Mỗi user story phải có ít nhất: 1 happy path, các nhánh lỗi/biên mà input nhắc tới, và kiểm tra ranh giới của mọi ngưỡng số (đúng ngưỡng, dưới ngưỡng, trên ngưỡng).
- **NFR phải đo được**: metric + ngưỡng + điều kiện đo (vd "p95 ≤ 300 ms ở 200 RPS", "uptime ≥ 99,9%/tháng"). Nếu input không có số: viết khung NFR với [CẦN XÁC NHẬN: ngưỡng] thay vì tự bịa số.
- **Business rule tách riêng khỏi UI**: rule (vd "điểm hết hạn sau N tháng") đặt trong bảng BR, các FR/AC tham chiếu ID rule đó. Khi rule đổi chỉ sửa một chỗ.
- **Biên ngưỡng tường minh**: "≥ 50.000.000 VND" khác "> 50.000.000 VND". Nếu input nói "trên 50 triệu" mà không rõ có bao gồm 50 triệu hay không, ghi [CẦN XÁC NHẬN].
- **Mọi mâu thuẫn và khoảng trống** từ bước 2 vào mục Open Questions (ID `OQ-`, ảnh hưởng, người trả lời). Giả định buộc phải đặt để viết tiếp → mục Assumptions (`AS-`).
- Giữ đúng ngôn ngữ người dùng dùng; tiếng Việt giữ thuật ngữ kỹ thuật tiếng Anh thông dụng.
- **Không đưa giá trị tự đề xuất vào requirement/AC.** Input nói "tầm 2-3s" → requirement ghi ngưỡng có trong input (≤ 3 giây) và đưa percentile/điều kiện tải vào Open Questions; không tự chế "p95 ≤ 2s". Giá trị gợi ý (nếu muốn giúp stakeholder quyết nhanh) để ở cột ghi chú của Open Questions.
- **Độ dài tương xứng input** (writing-standards §7b): chỉ thêm quy ước RFC 2119, Glossary, ma trận truy vết khi là SRS/tài liệu lớn; mỗi câu hỏi mở chỉ xuất hiện một lần trong bảng Open Questions.

### 4. Tự kiểm

1. Chạy linter trên file kết quả:
   ```bash
   python <skill-dir>/scripts/lint_doc.py <output.md>
   ```
   Sửa mọi finding `high`. Finding `medium` còn lại phải có lý do giữ (vd từ "đơn giản" nằm trong tên tính năng).
2. Đối chiếu inventory: mọi fact trong input xuất hiện trong tài liệu hoặc được ghi rõ là out of scope; mọi mâu thuẫn có trong Open Questions.
3. Đọc lại với vai QA: với mỗi AC, có viết được test case pass/fail rõ ràng không? Nếu không — AC chưa đạt.

### 5. Bàn giao

### Xuất định dạng & kiểm tra thẩm mỹ

Markdown là nguồn. Khi người dùng cần PDF/DOCX/XLSX (gửi sếp/khách, in, "file Word", "Excel để lọc"), hoặc nói tài liệu sẽ được chia sẻ, đọc `references/visual-style.md` rồi render:
```bash
python <skill-dir>/scripts/render_doc.py <file.md> --to pdf,docx,xlsx --out-dir <thư mục output> --qa
```
Người dùng nói đọc trên điện thoại/mobile → thêm `--page mobile` (khổ hẹp, bảng thành thẻ); cần cả bản in thì render thêm bản A4. Xem warnings và các ảnh trang trong `qa.preview_pages` (ít nhất trang đầu, trang có bảng lớn nhất, trang có diagram); sửa `.md` rồi render lại nếu bảng tràn, diagram không hiện, chữ lỗi dấu. Không nói định dạng nào là "đã xuất" nếu script báo bỏ qua nó. Người dùng không nhắc định dạng → chỉ giao `.md` và nhắc một dòng rằng có thể xuất PDF/DOCX/XLSX.

- Lưu tài liệu Markdown (và các định dạng đã render).
- Trong câu trả lời: 2–4 dòng tóm tắt + số Open Questions cần stakeholder trả lời. Không dán lại toàn bộ tài liệu vào chat nếu đã có file.

## Mẫu ngắn (để định hướng văn phong)

❌ "Người dùng có thể đổi điểm lấy voucher nhanh chóng, hệ thống sẽ xử lý phù hợp nếu điểm không đủ."

✅
```
BR-003. 100 điểm = 10.000 VND giá trị voucher. Chỉ đổi theo bội số 100 điểm.
FR-007. Khi người dùng xác nhận đổi điểm, hệ thống phải trừ điểm và phát hành voucher trong ≤ 3 giây (p95).
FR-008. Nếu số điểm khả dụng < số điểm cần đổi, thì hệ thống phải chặn giao dịch và hiển thị "Bạn chưa đủ điểm để đổi voucher này".

AC-007.1  Given người dùng có 500 điểm khả dụng
          When đổi voucher 50.000 VND (500 điểm)
          Then số điểm khả dụng = 0 và voucher có trạng thái "Chưa sử dụng"
AC-007.2  Given người dùng có 499 điểm khả dụng
          When đổi voucher 50.000 VND
          Then giao dịch bị chặn, điểm không đổi, hiển thị thông báo theo FR-008
```

## Tài nguyên

- `references/writing-standards.md` — chuẩn câu chữ, modal, EARS, danh sách từ mơ hồ, xử lý thiếu/mâu thuẫn.
- `references/templates.md` — template BRD, PRD, SRS, user story, use case, metric definition.
- `scripts/lint_doc.py` — linter phát hiện từ mơ hồ, placeholder, ID trùng, thuật ngữ không nhất quán.
- `scripts/render_doc.py` + `assets/` — xuất HTML/PDF/DOCX/XLSX có thiết kế, `--qa` render ảnh trang để kiểm tra.
- `references/visual-style.md` — quy tắc viết Markdown để render đẹp và quy trình visual QA.
