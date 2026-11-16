# Notes thử nghiệm chunking cho bot hỏi đáp wiki nội bộ (team Platform)

## Bối cảnh
- Bot RAG trả lời câu hỏi về wiki nội bộ (~1.200 trang Confluence, phần lớn có heading H2/H3 rõ ràng).
- Embedding: bge-m3. Vector store: pgvector. LLM trả lời: GPT-4o-mini. Top-k = 5.
- Bộ test: 50 câu hỏi thật lấy từ kênh #ask-platform (tháng 9/2026). Chấm đúng/sai bằng tay, 2 người chấm, bất đồng thì thảo luận chốt.
- Mỗi cấu hình chạy 1 lần.

## Kết quả
| Cách chunk | Đúng / 50 | Thời gian index toàn bộ wiki |
|---|---|---|
| Fixed 500 token, overlap 50 | 31 | 6 phút |
| Theo heading (H2/H3), đoạn > 800 token thì cắt tiếp | 38 | 7 phút |
| Semantic chunking (ngưỡng cosine 0.75) | 37 | 26 phút |

- Fixed sai nhiều ở câu hỏi cần bảng (bảng bị cắt đôi): 9/19 câu sai thuộc loại này.
- Semantic chunking đôi khi gộp 2 mục khác chủ đề vì văn phong giống nhau.
- Chi phí embedding của semantic cao hơn vì phải embed từng câu trước khi gộp.

## Ghi chú riêng (chưa kiểm chứng)
- Anh Tuấn bảo "semantic chunking chắc chắn là tốt nhất cho mọi loại tài liệu, chỉ là mình tune chưa tới".
- Có thể thử thêm late chunking nhưng chưa làm.
- Tài liệu PDF scan (khoảng 5% wiki) chưa test.
