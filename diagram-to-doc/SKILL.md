---
name: diagram-to-doc
description: Chuyển ảnh biểu đồ thành tài liệu đặc tả chặt chẽ, không mơ hồ — flowchart, BPMN/swimlane, activity, state machine, sequence diagram, ERD, use case diagram, architecture diagram, wireframe/mockup màn hình, sơ đồ trên whiteboard chụp ảnh. Trích xuất đầy đủ mọi node, nhánh điều kiện, ngưỡng, actor, bảng/cột/khóa, rồi viết thành process specification, business rules, use case, data dictionary, API sequence spec hoặc screen spec. Dùng skill này bất cứ khi nào người dùng gửi ảnh/screenshot/PDF chứa sơ đồ và muốn "viết tài liệu từ hình này", "mô tả quy trình trong ảnh", "chuyển diagram thành spec", "viết data dictionary từ ERD", "đặc tả màn hình theo mockup", "describe this flow", kể cả khi họ chỉ gửi ảnh kèm một câu ngắn như "viết lại cái này thành tài liệu".
---

# Diagram to Doc

Rủi ro lớn nhất khi viết tài liệu từ ảnh không phải câu chữ — mà là **đọc sót hoặc đọc sai** một nhánh, một ngưỡng, một mũi tên. Một nhánh "Không" bị sót trong flowchart phê duyệt là một lỗ hổng nghiệp vụ. Vì vậy skill tách làm hai pha: **trích xuất có kiểm chứng**, rồi mới **viết**.

## Pha 1 — Trích xuất

### 1.1 Nhìn ảnh và phân loại

Xem ảnh (Read tool hiển thị ảnh). Xác định loại diagram — mỗi loại có checklist trích xuất riêng trong `references/diagram-types.md`; đọc mục tương ứng.

Nếu ảnh lớn, chữ nhỏ, hoặc có số liệu (tiền, ngưỡng, mã lỗi, thời hạn), cắt ô phóng to và xem từng ô:
```bash
python <skill-dir>/scripts/zoom_tiles.py <image> --out /tmp/tiles --grid 2x2 --scale 2
```
Chọn grid lớn hơn (3x3) khi diagram dày đặc. Đừng đoán chữ mờ — đánh dấu là không đọc được.

### 1.2 Lập inventory JSON

Ghi toàn bộ những gì nhìn thấy vào `inventory.json` theo schema trong docstring của `scripts/check_diagram.py` (flowchart/BPMN/state, ERD, sequence). Nguyên tắc:
- **Chép nguyên văn nhãn** trong ảnh (kể cả lỗi chính tả); chuẩn hóa câu chữ để sang pha 2.
- Mỗi nhánh từ decision là một cạnh có nhãn điều kiện chính xác như trong ảnh ("> 50tr", "Có", "Reject").
- Swimlane → trường `lane` của node: actor thực hiện bước đó.
- Chỗ không đọc được → mảng `unreadable`, không suy diễn.
- Wireframe, use case diagram, architecture diagram: không có checker tự động — lập bảng inventory dạng Markdown theo checklist trong `references/diagram-types.md`.

### 1.3 Kiểm inventory và round-trip

```bash
python <skill-dir>/scripts/check_diagram.py inventory.json --mermaid /tmp/roundtrip.mmd
```
Checker báo: decision thiếu nhánh hoặc nhánh không nhãn, node cụt (không có cạnh ra mà không phải end), node không tới được, vòng lặp không lối ra, FK trỏ bảng không tồn tại, cột trùng...

Mỗi ERROR/WARN → **quay lại nhìn ảnh** vùng đó trước khi kết luận:
- Nếu do trích sót → sửa inventory.
- Nếu ảnh thật sự như vậy (vd diagram gốc thiếu nhánh "Không") → đó là **lỗi của diagram gốc**, ghi vào mục "Vấn đề phát hiện trong diagram" của tài liệu. Đây là giá trị lớn mà BA mang lại, đừng âm thầm "vá" bằng cách tự thêm nhánh.

Nếu có `mmdc`, render Mermaid và so sánh bằng mắt với ảnh gốc (số node, số nhánh, hướng mũi tên):
```bash
echo '{"args":["--no-sandbox"]}' > /tmp/pp.json
mmdc -p /tmp/pp.json -i /tmp/roundtrip.mmd -o /tmp/roundtrip.png
```

## Pha 2 — Viết tài liệu

Đọc `references/writing-standards.md` (chuẩn câu chữ chung) và mục output tương ứng trong `references/diagram-types.md`. Quy tắc:

1. **Phủ 100% inventory**: mỗi node/bước, mỗi nhánh, mỗi entity/cột, mỗi message xuất hiện trong tài liệu. Cuối tài liệu có bảng truy vết ngắn (ID bước ↔ node trong ảnh) khi diagram có > 8 node.
2. **Mỗi bước một chủ thể + một hành động**, lấy actor từ swimlane. Không có swimlane → ghi [CẦN XÁC NHẬN: ai thực hiện] cho bước không rõ chủ thể.
3. **Điều kiện rẽ nhánh viết thành business rule có ID** với biên rõ ràng. Ảnh ghi "> 50tr" → "Tổng giá trị > 50.000.000 VND". Nếu ảnh có hai nhánh "> 50tr" và "< 50tr" → trường hợp *đúng bằng* 50.000.000 VND không được bao phủ: ghi rõ là khoảng trống trong mục vấn đề.
4. **Luồng ngoại lệ** (reject, timeout, lỗi) mô tả đầy đủ như luồng chính, kèm điểm quay về hoặc trạng thái kết thúc.
5. **Không thêm bước/nhánh không có trong ảnh** vào phần đặc tả. Đề xuất bổ sung (vd "nên có nhánh timeout") để riêng trong mục "Đề xuất", ghi rõ là đề xuất.
6. **Kèm Mermaid** đã round-trip trong tài liệu (người đọc sửa diagram dạng text dễ hơn ảnh).
7. **Một hệ ID xuyên suốt**: ID bước (S01...) map 1-1 với node trong inventory; bảng truy vết dùng đúng ID đó, không đặt hệ ID thứ hai.
8. **Tài liệu gửi IT để build** → thêm acceptance criteria tối thiểu: mỗi nhánh của mỗi decision một AC (Given/When/Then), và AC cho biên ngưỡng. AC chỉ kiểm hành vi có trong diagram.
9. **ERD/screen spec: không tự liệt kê giá trị enum** (trạng thái, phương thức thanh toán...) mà ảnh không ghi — kể cả trong cột "Ví dụ". Ghi [CẦN XÁC NHẬN: danh sách giá trị hợp lệ].
10. Chạy linter câu chữ:
   ```bash
   python <skill-dir>/scripts/lint_doc.py <output.md>
   ```
   Sửa finding `high`. Nhãn nguyên văn trong ảnh được trích trong ngoặc kép sẽ được linter bỏ qua.

## Cấu trúc tài liệu đầu ra (mặc định cho process diagram)

```markdown
# Đặc tả quy trình: <tên>
## 1. Tổng quan  (mục đích, phạm vi, trigger, kết quả cuối)
## 2. Actors / vai trò
## 3. Business rules  (bảng: ID | Quy tắc | Nhánh liên quan)
## 4. Luồng chính  (bước đánh số: ID | Actor | Hành động | Đầu vào/ra | Bước tiếp)
## 5. Luồng thay thế & ngoại lệ
## 6. Trạng thái kết thúc
## 7. Acceptance criteria  (khi tài liệu dùng để build: mỗi nhánh một AC, kèm AC biên ngưỡng)
## 8. Sơ đồ quy trình (vẽ lại bằng Mermaid)
## 9. Vấn đề phát hiện trong diagram gốc  (thiếu nhánh, biên chưa phủ, nhãn mâu thuẫn, vùng không đọc được)
## 10. Đề xuất (không thuộc diagram gốc)  — chỉ khi có
## 11. Câu hỏi mở
```
ERD, sequence, wireframe, state machine có cấu trúc riêng — xem `references/diagram-types.md`.


## Xuất định dạng & kiểm tra thẩm mỹ

Markdown là nguồn. Khi người dùng cần PDF/DOCX/XLSX (gửi sếp/khách, in, "file Word", "Excel để lọc"), hoặc nói tài liệu sẽ được chia sẻ, đọc `references/visual-style.md` rồi render:
```bash
python <skill-dir>/scripts/render_doc.py <file.md> --to pdf,docx,xlsx --out-dir <thư mục output> --qa
```
Người dùng nói đọc trên điện thoại/mobile → thêm `--page mobile` (khổ hẹp, bảng thành thẻ); cần cả bản in thì render thêm bản A4. Xem warnings và các ảnh trang trong `qa.preview_pages` (ít nhất trang đầu, trang có bảng lớn nhất, trang có diagram); sửa `.md` rồi render lại nếu bảng tràn, diagram không hiện, chữ lỗi dấu. Không nói định dạng nào là "đã xuất" nếu script báo bỏ qua nó. Người dùng không nhắc định dạng → chỉ giao `.md` và nhắc một dòng rằng có thể xuất PDF/DOCX/XLSX.

## Tài nguyên

- `references/diagram-types.md` — checklist trích xuất + cấu trúc output theo từng loại diagram.
- `references/writing-standards.md` — chuẩn câu chữ dùng chung.
- `scripts/zoom_tiles.py` — cắt + phóng to ảnh để đọc chữ nhỏ.
- `scripts/check_diagram.py` — kiểm inventory (thiếu nhánh, node cụt, FK sai...) và sinh Mermaid round-trip.
- `scripts/lint_doc.py` — linter câu chữ mơ hồ.
- `scripts/render_doc.py` + `assets/` + `references/visual-style.md` — xuất PDF/DOCX/XLSX có thiết kế và visual QA (data dictionary → XLSX mỗi bảng một sheet).
