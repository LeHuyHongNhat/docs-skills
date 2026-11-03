# Visual Style — trình bày & xuất định dạng (MD → HTML/PDF/DOCX/XLSX)

Nội dung đúng mà trình bày rối thì người đọc vẫn bỏ qua. File này quy định cách *viết Markdown sao cho render ra đẹp*, và cách xuất/kiểm tra bản cuối.

## 1. Khi nào xuất định dạng nào

| Người dùng nói / ngữ cảnh | Xuất |
|---|---|
| Không nói gì về định dạng | Chỉ `.md` (nguồn). Trong câu trả lời, nhắc một dòng có thể xuất PDF/DOCX/XLSX. |
| "gửi sếp", "gửi khách", "in", "PDF" | `.md` + `.pdf` (A4) |
| "đọc trên điện thoại", "xem trên mobile" | `.md` + `.pdf` với `--page mobile`: khổ ~108×192 mm, bảng ≥ 4 cột tự chuyển thành thẻ "nhãn: giá trị" |
| "Word", "docx", "để team sửa tiếp" | `.md` + `.docx` |
| Data dictionary, ma trận truy vết, danh sách finding, bảng metric — "Excel", "để lọc/sort" | `.md` + `.xlsx` (mỗi bảng một sheet) |
| Nhiều đối tượng đọc | kết hợp, vd `--to pdf,xlsx` |

Markdown luôn là nguồn gốc duy nhất: sửa nội dung trong `.md` rồi render lại, không sửa tay file PDF/DOCX.

## 2. Viết Markdown để render đẹp

**Đầu tài liệu**
```markdown
# <Loại tài liệu>: <Tên>
| Phiên bản | Ngày | Owner | Trạng thái |
|---|---|---|---|
| 0.1 | 2026-11-03 | <tên> | Draft |
```
Bảng metadata đặt **ngay sau H1** — theme render nó thành dải thông tin gọn. Mục lục do script tự sinh khi có ≥ 6 mục H2; không tự viết mục lục bằng tay.

**Mở đầu cho người duyệt**: tài liệu gửi sếp/khách/stakeholder → ngay sau bảng metadata đặt khối `> **Tóm tắt:**` 3–5 dòng: tài liệu là gì, điều cần họ quyết, 1–3 rủi ro/vấn đề lớn nhất (trỏ ID). Người duyệt thường chỉ đọc trang đầu.

**Heading**: viết cho người đọc, không cho người viết — "Sơ đồ quan hệ dữ liệu", không phải "Diagram (Mermaid)". Một H1 duy nhất; H2 đánh số `## 1. Tổng quan`; H3 `### 1.1 ...`. Không nhảy cấp (H2 → H4).

**Bảng**
- Tối đa **6 cột**. Bảng 7+ cột sẽ chật trên A4 dọc và vỡ trên mobile → tách thành 2 bảng, hoặc chuyển cột mô tả dài thành danh sách bên dưới.
- Cột đầu là ID/tên ngắn; cột mô tả dài đặt cuối.
- Không nhân bản nội dung chỉ để phục vụ định dạng khác (vd phụ lục lặp lại mọi cột chỉ để có sheet Excel phẳng) — trừ khi người dùng cần Excel để lọc; khi đó đặt phụ lục đó ở cuối và ghi rõ mục đích.
- Mỗi ô ≤ ~40 từ. Nội dung dài hơn → bullet dưới bảng, tham chiếu bằng ID.
- Không xuống dòng trong ô bằng `<br>` quá 2 lần.
- Tên cột, tên bảng, endpoint, env var trong ô: bọc `backtick`.

**Marker và callout**
- [CẦN XÁC NHẬN: ...] viết như văn bản thường, *không* bọc backtick — renderer tô nền vàng để người đọc quét nhanh.
- Ghi chú quan trọng dùng blockquote (`> **Lưu ý:** ...`) — render thành khối nền xanh nhạt. Tối đa 1–2 khối mỗi mục, nhiều hơn thì mất tác dụng nhấn.
- Không dùng emoji trang trí trong tài liệu nghiệp vụ.

**Diagram Mermaid**
- ≤ 15 node mỗi diagram; diagram lớn hơn → tách theo luồng.
- Nhãn ngắn (≤ 5 từ), tránh ký tự `;` `"` `{}` trong nhãn — chúng làm vỡ cú pháp (lỗi hay gặp nhất: `BEGIN; INSERT...` trong sequence diagram).
- Mỗi diagram có một câu dẫn ngay trước nó nói diagram thể hiện gì.

**Code block**: luôn ghi ngôn ngữ (```` ```bash ````, ```` ```sql ````). Dòng code ≤ 100 ký tự để không bị cắt trong PDF.

## 3. Render & kiểm tra (visual QA)

```bash
python <skill-dir>/scripts/render_doc.py <doc.md> --to pdf,docx,xlsx --out-dir <thư mục output> --qa
# đọc trên điện thoại:
python <skill-dir>/scripts/render_doc.py <doc.md> --to pdf --page mobile --out-dir <thư mục output> --qa
```
Cần cả A4 (in/duyệt) và bản mobile: render hai lần vào hai thư mục, hoặc đổi tên file mobile thành `<tên>-mobile.pdf`.

Script in ra JSON gồm `outputs`, `warnings`, `qa`. Sau đó:

1. **Đọc warnings**: Mermaid không render được, bảng ≥ 7 cột, thiếu công cụ (pandoc/Chrome/mmdc). Sửa nguồn `.md` rồi render lại.
2. **Xem ảnh trang** trong `qa.preview_pages` (Read tool hiển thị ảnh). Tối thiểu xem trang 1, trang có bảng lớn nhất và trang có diagram. Kiểm:
   - chữ có dấu hiển thị đúng (không ra ô vuông);
   - bảng không tràn lề, cột ID không gãy giữa chừng;
   - diagram hiện thành hình, đọc được nhãn;
   - không có trang gần trống do ngắt trang xấu.
3. **DOCX**: nếu cần xem, chuyển sang PDF để xem ảnh: `soffice --headless --convert-to pdf <file.docx>` rồi `pdftoppm -r 60 -png`.
4. **XLSX**: mỗi bảng một sheet có header cố định và filter; sheet "Tổng quan" liệt kê các sheet. Kiểm tên sheet có nghĩa (lấy từ heading gần nhất — đặt heading rõ ràng trước mỗi bảng).

Môi trường thiếu công cụ → script bỏ qua định dạng đó và báo warning; khi đó nói rõ với người dùng định dạng nào chưa xuất được, không giả vờ đã xuất.

## 4. Thiết kế mặc định (để hiểu, không cần sửa)

- Font: Inter (PDF/HTML), Arial (DOCX — có sẵn trên mọi máy, đủ dấu tiếng Việt). Số dạng tabular trong bảng.
- Một màu nhấn (xanh `#2A4FB8`) cho link/ghi chú; vàng chỉ cho [CẦN XÁC NHẬN]; đỏ chỉ cho rủi ro. Màu mang nghĩa, không trang trí.
- A4, lề 16–20 mm, footer: tên tài liệu + số trang `x / y`. Header bảng lặp lại khi bảng sang trang.
