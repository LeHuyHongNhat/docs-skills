# Review rubric

## 1. Taxonomy mã lỗi

| Mã | Tên | Dấu hiệu | Ví dụ |
|---|---|---|---|
| AMB-LEX | Từ mơ hồ | tính từ/trạng từ không đo được | "nhanh", "thân thiện", "phù hợp" |
| AMB-REF | Tham chiếu mơ hồ | đại từ/cụm chỉ định không rõ đối tượng | "Sau đó nó sẽ gửi email" (nó = ai?) |
| AMB-SCOPE | Phạm vi mở | danh sách mở, "và/hoặc", "các loại khác" | "hỗ trợ PDF, Word, v.v." |
| AMB-BOUND | Biên không rõ | ngưỡng không nói có bao gồm biên; thời gian không rõ mốc/múi giờ/ngày làm việc | "đơn trên 50 triệu", "trong 3 ngày" |
| TEST | Không kiểm thử được | không có tiêu chí pass/fail | "hệ thống phải ổn định" |
| INC-NUM | Mâu thuẫn số liệu | cùng một tham số có hai giá trị | "OTP 5 phút" vs "OTP 3 phút" |
| INC-TERM | Thuật ngữ không nhất quán | một khái niệm nhiều tên, hoặc một tên nhiều khái niệm | "khách hàng" / "người dùng" / "user" |
| INC-LOGIC | Mâu thuẫn logic | hai rule không thể cùng đúng | "chỉ admin được xóa" vs "người tạo được xóa" |
| MISS-ACTOR | Thiếu chủ thể | bị động không chủ thể, không rõ ai làm | "dữ liệu được đồng bộ" |
| MISS-ERR | Thiếu xử lý lỗi/ngoại lệ | chỉ có happy path | không nói gì khi thanh toán thất bại |
| MISS-COND | Thiếu điều kiện/tiền điều kiện | "khi cần", "nếu phù hợp" | "gửi nhắc nhở khi cần" |
| STRUCT-COMPOUND | Gộp nhiều requirement | một câu nhiều hành vi độc lập | "phải lưu đơn, gửi email và cập nhật tồn kho" |
| STRUCT-ID | ID thiếu/trùng | requirement không ID, ID dùng hai lần | hai dòng `FR-005` |
| MODAL | Modal sai/yếu | "có thể", "sẽ", "should" trong requirement bắt buộc | "Người dùng có thể đổi mật khẩu" (bắt buộc hay tùy chọn?) |
| PH | Placeholder | TBD, TODO, ??? | "Ngưỡng: TBD" |
| UNSOURCED | Khẳng định không nguồn | số liệu/hiệu quả không dẫn nguồn | "giúp tăng 30% doanh thu" |
| STYLE | Văn phong | marketing, cảm thán, dài dòng, sai chính tả, trộn ngôn ngữ không cần thiết | "tính năng siêu xịn" |

## 2. Severity

| Mức | Định nghĩa | Ví dụ |
|---|---|---|
| **Critical** | Dẫn tới hành vi hệ thống khác nhau giữa các cách hiểu, hoặc mâu thuẫn trực tiếp; sẽ gây bug/tranh cãi nghiệm thu | INC-NUM, INC-LOGIC, AMB-BOUND ở rule tiền/thời hạn, STRUCT-ID trùng |
| **Major** | Không kiểm thử được, hoặc thiếu nhánh xử lý quan trọng | TEST, MISS-ERR, AMB-LEX trong requirement, PH |
| **Minor** | Ảnh hưởng độ rõ/chuyên nghiệp nhưng ít rủi ro hiểu sai | STYLE, AMB-LEX trong phần mô tả bối cảnh, INC-TERM nhẹ |

Một vấn đề lặp ở nhiều chỗ → **một finding**, liệt kê mọi vị trí; không tách thành N finding.

## 3. Format báo cáo

```markdown
# Review: <tên tài liệu>
Ngày review: YYYY-MM-DD · Phạm vi: <toàn bộ / mục x–y>

## Tóm tắt
- Tổng: N finding — Critical: a · Major: b · Minor: c
- Ưu tiên sửa:
  1. <vấn đề lớn nhất, 1 dòng>
  2. ...
  3. ...

## Findings
| # | Vị trí | Trích đoạn gốc | Mã | Mức | Vấn đề | Đề xuất viết lại |
|---|---|---|---|---|---|---|
| F01 | FR-003 | "phản hồi nhanh" | AMB-LEX | Major | Không có ngưỡng → QA không viết được test | "Hệ thống phải trả kết quả trong ≤ [CẦN XÁC NHẬN: N] giây (p95)." |

## Bản đã chỉnh sửa
<!-- lint-disable -->  ← chỉ dùng nếu bản sửa có trích nguyên văn bản cũ
...

## Câu hỏi mở
| ID | Câu hỏi | Liên quan | Người cần trả lời |
```

Trích đoạn gốc ≤ 15 từ, đủ để định vị. Đề xuất viết lại phải là câu hoàn chỉnh, dán thẳng vào tài liệu được.

## 4. Ví dụ

**Gốc:** "Khi khách hàng đặt đơn trên 2 triệu, hệ thống sẽ miễn phí ship và gửi thông báo phù hợp. Người dùng có thể hủy đơn trong 24h."

| # | Trích | Mã | Mức | Vấn đề | Đề xuất |
|---|---|---|---|---|---|
| F01 | "trên 2 triệu" | AMB-BOUND | Critical | Đơn đúng 2.000.000 VND có được miễn phí? Tính trước hay sau giảm giá? | "BR-010. Đơn có tổng giá trị sau giảm giá ≥ [CẦN XÁC NHẬN: > hay ≥] 2.000.000 VND được miễn phí vận chuyển." |
| F02 | "khách hàng" / "Người dùng" | INC-TERM | Minor | Hai tên cho cùng actor? | Dùng "người dùng" nhất quán. |
| F03 | "sẽ miễn phí ship và gửi thông báo" | STRUCT-COMPOUND | Major | Hai hành vi độc lập trong một câu | Tách FR-010 (phí ship = 0) và FR-011 (thông báo). |
| F04 | "thông báo phù hợp" | AMB-LEX | Major | Kênh, nội dung, thời điểm? | "FR-011. Khi đơn đủ điều kiện BR-010, hệ thống phải hiển thị tại bước Thanh toán dòng 'Phí vận chuyển: 0 ₫'." [CẦN XÁC NHẬN: có gửi thêm push/email không] |
| F05 | "có thể hủy đơn trong 24h" | MODAL, AMB-BOUND | Major | Bắt buộc hệ thống hỗ trợ? 24h tính từ lúc đặt hay lúc thanh toán? Sau khi đã giao cho đơn vị vận chuyển? | "FR-012. Hệ thống phải cho phép người dùng hủy đơn trong vòng 24 giờ kể từ thời điểm đặt đơn [CẦN XÁC NHẬN: mốc tính], nếu đơn chưa chuyển trạng thái 'Đang giao'." |
