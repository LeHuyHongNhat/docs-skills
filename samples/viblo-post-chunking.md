# Cắt tài liệu theo heading thắng semantic chunking trên wiki nội bộ của team mình

Team mình thử 3 cách cắt tài liệu cho bot hỏi đáp wiki nội bộ. Cách đơn giản nhất — cắt theo heading — trả lời đúng nhiều câu nhất, còn semantic chunking tốn gấp gần 4 lần thời gian mà không hơn.

Bài này dành cho bạn mới làm bot hỏi đáp trên tài liệu (RAG, giải thích ở mục 1) và đang phân vân nên cắt tài liệu thế nào. Mình kể cách đo, kết quả, và những gì thử nghiệm này *chưa* chứng minh được.

## 1. Bối cảnh: bot hỏi đáp và bước "cắt tài liệu"

RAG (Retrieval-Augmented Generation) là cách cho mô hình ngôn ngữ trả lời dựa trên tài liệu của bạn: hệ thống tìm vài đoạn tài liệu liên quan nhất, rồi đưa chúng cho mô hình đọc trước khi trả lời.

Muốn tìm được "đoạn liên quan", tài liệu dài phải được chia thành các đoạn nhỏ trước. Bước này gọi là **chunking**. Mỗi đoạn sau đó được đổi thành một **embedding** — một dãy số biểu diễn ý nghĩa của đoạn văn, để máy so sánh được đoạn nào gần với câu hỏi nhất.

Nếu cắt dở, đoạn đúng có thể bị chia đôi, và bot không bao giờ tìm thấy đủ thông tin để trả lời.

Hệ thống của team mình:
- Khoảng 1.200 trang Confluence, phần lớn có heading H2/H3 rõ ràng.
- Embedding bằng bge-m3, lưu trong pgvector, mô hình trả lời là GPT-4o-mini, mỗi câu hỏi lấy 5 đoạn gần nhất.

## 2. Cách đo

Mình lấy 50 câu hỏi thật từ kênh hỏi đáp nội bộ của team trong tháng 9/2026. Hai người chấm từng câu trả lời là đúng hay sai bằng tay; câu nào hai người chấm khác nhau thì thảo luận để chốt.

Ba cách cắt được so sánh:

| Cách cắt | Mô tả ngắn |
|---|---|
| Cố định 500 token | Cứ 500 token cắt một lần, hai đoạn liền nhau chồng lên nhau 50 token |
| Theo heading | Mỗi mục H2/H3 là một đoạn; mục nào dài hơn 800 token thì cắt tiếp |
| Semantic chunking | Gộp các câu liền nhau khi độ giống nhau về nghĩa (cosine) ≥ 0,75 |

Token là đơn vị mà mô hình dùng để đếm chữ; với tiếng Việt, một từ thường tương ứng 1–3 token.

## 3. Kết quả

```chart
type: hbar
title: Cắt theo heading trả lời đúng nhiều câu nhất, hơn cắt cố định 7 câu
subtitle: Số câu trả lời đúng trên 50 câu hỏi thật
categories: [Theo heading, Semantic chunking, Cố định 500 token]
values: [38, 37, 31]
max: 50
highlight: Theo heading
source: Thử nghiệm nội bộ team Platform, tháng 9/2026, 1 lần chạy
```

```chart
type: hbar
title: Semantic chunking cần 26 phút để index, gấp gần 4 lần cắt theo heading
subtitle: Thời gian index toàn bộ wiki (phút)
categories: [Cố định 500 token, Theo heading, Semantic chunking]
values: [6, 7, 26]
highlight: Semantic chunking
source: Thử nghiệm nội bộ team Platform, tháng 9/2026, 1 lần chạy
```

Ba điều mình rút ra từ số liệu và từ việc đọc từng câu sai:

- **Cắt cố định làm vỡ bảng.** 9 trong 19 câu sai của cách cắt cố định là câu cần đọc một bảng, và bảng đó bị cắt làm đôi.
- **Semantic chunking đôi khi gộp nhầm.** Hai mục khác chủ đề nhưng viết cùng văn phong bị gộp thành một đoạn, khiến đoạn tìm được chứa cả thông tin không liên quan.
- **Semantic chunking tốn hơn.** Nó phải tạo embedding cho từng câu trước khi quyết định gộp, nên thời gian index và chi phí embedding đều cao hơn.

Với 38 so với 37 câu, khác biệt giữa cắt theo heading và semantic chunking chỉ là 1 câu — quá nhỏ để nói cách nào chính xác hơn. Điều chắc hơn là: cắt theo heading đạt mức tương đương với chi phí thấp hơn nhiều.

## 4. Thử nghiệm này chưa chứng minh được gì

- Mỗi cấu hình mới chạy **1 lần** trên **50 câu**. Kết quả có thể dao động nếu chạy lại hoặc đổi bộ câu hỏi.
- Wiki của team mình **có heading rõ ràng**. Với tài liệu không có cấu trúc (email, transcript cuộc họp), cắt theo heading có thể không dùng được.
- Khoảng 5% wiki là **PDF scan**, mình chưa test phần này.
- Mình chưa thử các cách khác như late chunking, và chưa tune nhiều ngưỡng cho semantic chunking.

Nói cách khác: kết luận chỉ đúng cho tài liệu giống wiki của team mình.

## 5. Nếu bạn đang chọn cách cắt

1. Xem tài liệu của bạn có heading rõ ràng không. Nếu có, bắt đầu bằng cắt theo heading — đơn giản và rẻ.
2. Dựng một bộ 30–50 câu hỏi thật và chấm tay trước khi đổi sang cách phức tạp hơn. Không có bộ đo, rất khó biết thay đổi có thật sự tốt hơn không.
3. Kiểm tra riêng các câu hỏi cần đọc bảng: đây là chỗ cách cắt cố định yếu nhất trong thử nghiệm của mình.

Bạn đang cắt tài liệu theo cách nào, và đo chất lượng bot bằng gì? Nếu bạn từng thử semantic chunking trên tài liệu không có heading, mình rất muốn biết kết quả.
