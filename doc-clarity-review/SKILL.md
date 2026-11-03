---
name: doc-clarity-review
description: Review và viết lại tài liệu sản phẩm/kỹ thuật có sẵn cho chặt chẽ, rõ ràng, không mơ hồ, dùng từ chuẩn chuyên nghiệp — phát hiện từ mơ hồ, yêu cầu không kiểm thử được, số liệu/thuật ngữ mâu thuẫn, biên ngưỡng không rõ, thiếu actor/điều kiện/xử lý lỗi, requirement gộp nhiều ý, ID trùng, placeholder TBD; xuất báo cáo finding có mức độ + đề xuất câu viết lại, và bản tài liệu đã sửa. Dùng skill này khi người dùng đưa một PRD, SRS, BRD, user story, spec, README, release note, email yêu cầu... và nói "review giúp", "soát lỗi tài liệu", "viết lại cho chuyên nghiệp/chặt chẽ", "chỗ nào mơ hồ", "chuẩn hóa câu chữ", "polish this spec", "is this requirement testable", kể cả khi họ chỉ dán một đoạn văn và hỏi "viết vậy ổn chưa". Không dùng để viết tài liệu mới từ đầu (dùng product-spec-writer / codebase-doc-writer / diagram-to-doc).
---

# Doc Clarity Review

Mục tiêu: sau review, hai người đọc độc lập (dev và QA) hiểu tài liệu **giống hệt nhau**, và mọi chỗ tác giả *chưa quyết* được đưa ra ánh sáng thành câu hỏi — thay vì bị reviewer lặng lẽ quyết thay.

## Quy trình

### 1. Đọc trọn và nắm ý định

Đọc toàn bộ tài liệu trước khi bắt lỗi. Xác định: loại tài liệu, người đọc đích, ngôn ngữ, thuật ngữ chủ đạo. Một câu "mơ hồ" trong vision statement có thể chấp nhận được; cùng câu đó trong acceptance criteria thì không. Mức nghiêm trọng phụ thuộc vị trí.

Đọc `references/review-rubric.md` (taxonomy lỗi + định nghĩa severity + format báo cáo) và `references/writing-standards.md` (chuẩn câu chữ).

### 2. Quét tự động bằng linter

```bash
python <skill-dir>/scripts/lint_doc.py <input.md> --format json > /tmp/lint.json
```
Input không phải Markdown (docx, pdf, text dán vào chat) → lưu nội dung thành `.md` trước. Linter bắt nhanh lớp lỗi bề mặt (từ mơ hồ, TBD, "v.v.", "và/hoặc", ID trùng, thuật ngữ lệch). Nó **không** bắt được lớp lỗi ngữ nghĩa — phần quan trọng hơn, làm ở bước 3. Không chép nguyên output linter thành báo cáo: lọc false positive (vd "đơn giản" là tên gói cước) và gộp finding cùng gốc.

### 3. Review ngữ nghĩa (thủ công)

Đi qua từng requirement/đoạn và hỏi:
- **Hai cách hiểu?** Nếu dev A và dev B code theo câu này, kết quả có khác nhau không?
- **Kiểm thử được?** QA viết được test pass/fail từ câu này không? Ngưỡng nằm ở đâu?
- **Biên ngưỡng**: "trên 50 triệu", "trong 7 ngày", "từ 1/1 đến 31/1" — có bao gồm biên không, tính theo múi giờ nào, ngày làm việc hay ngày lịch?
- **Mâu thuẫn chéo**: cùng một rule/số liệu ở hai mục khác nhau có khớp không (vd mục 3 nói OTP hết hạn sau 5 phút, AC nói 3 phút). So mọi con số xuất hiện > 1 lần.
- **Thiếu**: actor nào làm? lỗi/timeout thì sao? dữ liệu rỗng thì sao? quyền không đủ thì sao?
- **Gộp ý**: một câu chứa nhiều requirement độc lập → tách.
- **Khẳng định không nguồn**: "giúp tăng 30% conversion" — số liệu từ đâu?

### 4. Viết đề xuất sửa — giữ nguyên ý, không bịa

Đây là ranh giới quan trọng nhất của reviewer:
- Sửa **cách diễn đạt** thoải mái (cấu trúc câu, thuật ngữ, modal, tách ý, thêm ID).
- **Không tự quyết nội dung nghiệp vụ** tác giả chưa quyết. Khi câu "phản hồi nhanh" cần một con số mà tài liệu không có → viết lại thành `phải phản hồi trong ≤ [CẦN XÁC NHẬN: N] giây (p95)` và có thể gợi ý giá trị tham khảo *trong cột ghi chú*, không đưa vào câu requirement.
- Mâu thuẫn → không chọn bên; nêu cả hai vị trí và đưa vào câu hỏi mở. Trong bản sửa, viết tham số dạng ký hiệu (T, N) + [CẦN XÁC NHẬN] để AC đúng với mọi lựa chọn — không xây AC trên con số reviewer tự chọn.
- **Vị trí finding = chỗ cần sửa.** Khi hai đoạn mâu thuẫn mà chỉ một đoạn sai/mơ hồ, gắn finding vào đoạn đó và nhắc đoạn kia như ngữ cảnh — đừng đánh dấu đoạn viết đúng là có lỗi.
- Bản sửa giữ độ dài tương xứng bản gốc (writing-standards §7b): làm rõ cái đã có, không mở rộng phạm vi tài liệu. Đề xuất phạm vi mới (bảo mật, NFR bổ sung) → để ở câu hỏi mở/ghi chú, không chèn vào thân tài liệu.
- Giữ ngôn ngữ, thuật ngữ đã chọn của tài liệu gốc (trừ khi chính thuật ngữ là vấn đề — khi đó đề xuất một thuật ngữ và áp dụng nhất quán).

### 5. Xuất kết quả

Theo format trong `references/review-rubric.md`:
1. **Tóm tắt**: số finding theo severity, 3 vấn đề ảnh hưởng lớn nhất.
2. **Bảng finding**: ID · vị trí (mục/dòng/ID requirement) · trích đoạn gốc ngắn · mã lỗi · severity · vì sao là vấn đề · đề xuất viết lại.
3. **Bản đã sửa** của tài liệu (mặc định khi tài liệu ≤ ~3 trang hoặc người dùng yêu cầu "viết lại"); đánh dấu chỗ thay đổi lớn nếu hữu ích. Với tài liệu dài chỉ xuất bảng finding trừ khi được yêu cầu.
4. **Câu hỏi mở** cho tác giả/stakeholder.

Chạy lại linter trên **bản đã sửa** (không chạy trên báo cáo — báo cáo chứa trích đoạn gốc nên linter sẽ báo lại chính các lỗi đó):
```bash
python <skill-dir>/scripts/lint_doc.py <revised.md>
```
Bản sửa không được còn finding `high` ngoài các vị trí [CẦN XÁC NHẬN] có chủ đích.


### Xuất định dạng (bản đã sửa) & kiểm tra thẩm mỹ

Markdown là nguồn. Khi người dùng cần PDF/DOCX/XLSX (gửi sếp/khách, in, "file Word", "Excel để lọc"), hoặc nói tài liệu sẽ được chia sẻ, đọc `references/visual-style.md` rồi render:
```bash
python <skill-dir>/scripts/render_doc.py <file.md> --to pdf,docx,xlsx --out-dir <thư mục output> --qa
```
Người dùng nói đọc trên điện thoại/mobile → thêm `--page mobile` (khổ hẹp, bảng thành thẻ); cần cả bản in thì render thêm bản A4. Xem warnings và các ảnh trang trong `qa.preview_pages` (ít nhất trang đầu, trang có bảng lớn nhất, trang có diagram); sửa `.md` rồi render lại nếu bảng tràn, diagram không hiện, chữ lỗi dấu. Không nói định dạng nào là "đã xuất" nếu script báo bỏ qua nó. Người dùng không nhắc định dạng → chỉ giao `.md` và nhắc một dòng rằng có thể xuất PDF/DOCX/XLSX.

Nếu tài liệu đã tốt: nói thẳng là tốt, liệt kê ít finding thật sự đáng sửa. Không tạo finding cho đủ số lượng — finding giả làm người dùng mất niềm tin vào cả báo cáo.

## Tài nguyên

- `references/review-rubric.md` — taxonomy mã lỗi, định nghĩa severity, format báo cáo, ví dụ.
- `references/writing-standards.md` — chuẩn câu chữ dùng chung.
- `scripts/render_doc.py` + `assets/` + `references/visual-style.md` — xuất bản đã sửa ra PDF/DOCX, bảng finding ra XLSX.
- `scripts/lint_doc.py` — linter bề mặt (`--format json` để xử lý tiếp; `--terms` để truyền nhóm từ đồng nghĩa riêng của dự án).
