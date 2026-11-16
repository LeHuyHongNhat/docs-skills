# Cắt theo heading ngang semantic chunking, index nhanh gần 4 lần; 50 câu chưa đủ xếp hạng

Team mình thử 3 cách cắt tài liệu cho bot hỏi đáp wiki nội bộ. Cắt theo heading đạt số câu đúng ngang semantic chunking với khoảng một phần tư thời gian index. Nhưng với 50 câu hỏi, mình chưa phân biệt được cách nào chính xác hơn.

Bài này dành cho bạn mới làm bot hỏi đáp trên tài liệu (RAG, giải thích ở mục 1) và đang phân vân nên cắt tài liệu thế nào. Mình kể cách đo, kết quả kèm độ bất định, và những gì thử nghiệm này chưa cho thấy.

## 1. Bối cảnh: bot hỏi đáp và bước "cắt tài liệu"

RAG (Retrieval-Augmented Generation) là cách cho mô hình ngôn ngữ trả lời dựa trên tài liệu của bạn: hệ thống tìm vài đoạn tài liệu liên quan nhất, rồi đưa chúng cho mô hình đọc trước khi trả lời.

Muốn tìm được "đoạn liên quan", tài liệu dài phải được chia thành các đoạn nhỏ trước. Bước này gọi là **chunking**. Mỗi đoạn sau đó được đổi thành một **embedding** — một dãy số biểu diễn ý nghĩa của đoạn văn, để máy so sánh được đoạn nào gần với câu hỏi nhất.

Nếu cắt dở, đoạn đúng có thể bị chia đôi, và bot có thể không tìm thấy đủ thông tin để trả lời.

Hệ thống của team mình:
- Khoảng 1.200 trang Confluence, phần lớn có heading H2/H3 rõ ràng.
- Embedding bằng bge-m3, lưu trong pgvector, mô hình trả lời là GPT-4o-mini, mỗi câu hỏi lấy 5 đoạn gần nhất.

## 2. Cách đo: 50 câu hỏi thật, chấm tay, mỗi cấu hình chạy 1 lần

| Thành phần | Giá trị |
|---|---|
| Thiết kế | So sánh 3 cấu hình trên cùng một bộ câu hỏi; mỗi cấu hình chạy 1 lần |
| Mẫu | 50 câu hỏi thật từ kênh hỏi đáp nội bộ, tháng 9/2026 |
| Thước đo | Câu trả lời đúng hay sai, do 2 người chấm tay; bất đồng thì thảo luận để chốt |
| Độ bất định | Khoảng tin cậy 95% (Wilson) cho từng tỉ lệ; khoảng Newcombe cho chênh lệch |

Ba cách cắt được so sánh:

| Cách cắt | Mô tả ngắn |
|---|---|
| Cố định 500 token | Cứ 500 token cắt một lần, hai đoạn liền nhau chồng lên nhau 50 token |
| Theo heading | Mỗi mục H2/H3 là một đoạn; mục nào dài hơn 800 token thì cắt tiếp |
| Semantic chunking | Gộp các câu liền nhau khi độ giống nhau về nghĩa (cosine) ≥ 0,75 |

Token là đơn vị mà mô hình dùng để đếm chữ; với tiếng Việt, một từ thường tương ứng 1–3 token.

## 3. Trên 50 câu, chưa phân biệt được ba cách cắt về độ chính xác

Số câu đúng: cắt theo heading 38/50, semantic chunking 37/50, cắt cố định 31/50. Câu hỏi cần trả lời là các chênh lệch này có đủ lớn so với độ nhiễu của một bộ 50 câu hay không.

```chart
type: interval
title: Cả ba chênh lệch đều có khoảng tin cậy chứa 0
subtitle: Chênh lệch tỉ lệ câu đúng giữa hai cách cắt (điểm phần trăm), ước lượng và khoảng tin cậy 95%
categories: ["Heading trừ cố định (38 so với 31)", "Semantic trừ cố định (37 so với 31)", "Heading trừ semantic (38 so với 37)"]
values: [14, 12, 2]
low: [-4.1, -6.2, -14.8]
high: [30.9, 29.2, 18.7]
decimals: 1
source: Thử nghiệm nội bộ team Platform, tháng 9/2026, 1 lần chạy, n = 50 câu; khoảng Newcombe cho hai tỉ lệ độc lập
```

Khoảng tin cậy 95% là khoảng các giá trị của chênh lệch thật mà dữ liệu này chưa loại trừ được. Chấm rỗng nghĩa là khoảng đó có chứa 0.

- **Heading so với cố định**: chênh 14 điểm, khoảng tin cậy 95% từ −4 đến +31 điểm. Khoảng này chứa 0, tức chưa phân biệt được hai cách.
- **Heading so với semantic**: chênh 1 câu.
- Phép so chặt hơn là so theo từng câu hỏi, vì cả ba cách chạy trên cùng 50 câu. Team mình không lưu kết quả từng câu, nên chưa làm được. Các khoảng ở trên vì vậy được tính như hai mẫu độc lập và chưa hiệu chỉnh cho việc so 3 cặp cùng lúc.
- Để phát hiện một chênh lệch cỡ 14 điểm, cần khoảng 170 câu cho mỗi cách nếu so như hai mẫu độc lập. So theo từng câu sẽ cần ít hơn.

## 4. Semantic chunking index lâu gần gấp 4 lần

Thời gian index khác nhau nhiều, dù cũng mới là một lần đo trong thử nghiệm này:

```chart
type: hbar
title: Semantic chunking mất 26 phút để index, so với 7 phút của cắt theo heading
subtitle: Thời gian index toàn bộ wiki (phút), 1 lần đo
categories: [Cố định 500 token, Theo heading, Semantic chunking]
values: [6, 7, 26]
highlight: Semantic chunking
source: Thử nghiệm nội bộ team Platform, tháng 9/2026, 1 lần chạy
```

Hai quan sát khi đọc từng câu sai (đây là mô tả, chưa phải kết luận về nguyên nhân):

- 9 trong 19 câu sai của cách cắt cố định là câu cần đọc một bảng, và bảng đó bị cắt làm đôi.
- Semantic chunking đôi lúc gộp hai mục khác chủ đề nhưng viết cùng văn phong vào một đoạn.

Semantic chunking index chậm hơn vì phải tạo embedding cho từng câu trước khi quyết định gộp.

## 5. Thử nghiệm này chưa cho thấy gì

- Mỗi cấu hình mới chạy **1 lần** trên **50 câu**, nên không có ước lượng dao động giữa các lần chạy.
- Wiki của team mình **có heading rõ ràng**. Với tài liệu không có cấu trúc (email, transcript cuộc họp), cắt theo heading có thể không dùng được.
- Khoảng 5% wiki là **PDF scan**, mình chưa test phần này.
- Mình chưa thử late chunking, và chưa thử nhiều ngưỡng cho semantic chunking. Một cấu hình semantic được chỉnh kỹ hơn có thể cho kết quả khác.
- Bộ câu hỏi và wiki là dữ liệu nội bộ, không công bố được. Mình có thể chia sẻ script chấm và cấu hình.

## 6. Nếu bạn đang chọn cách cắt

Phần này là ý kiến của mình.

1. Nếu tài liệu có heading rõ ràng, bắt đầu bằng cắt theo heading: rẻ hơn, và trong thử nghiệm này không thấy kém hơn.
2. Dựng bộ câu hỏi thật trước khi đổi sang cách phức tạp hơn, và **lưu kết quả từng câu** để so theo cặp. Với 50 câu, chỉ những chênh lệch rất lớn mới lộ ra.
3. Kiểm tra riêng các câu hỏi cần đọc bảng.

Bạn đang cắt tài liệu theo cách nào, và bộ câu hỏi đánh giá của bạn có bao nhiêu câu?
