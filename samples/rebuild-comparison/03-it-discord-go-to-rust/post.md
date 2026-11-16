# Discord chuyển Read States từ Go sang Rust: đọc lại như một case study

Bài "Why Discord is switching from Go to Rust" (2020) hay được trích như bằng chứng rằng Rust nhanh hơn Go. Đọc kỹ thì đó là câu chuyện của một service, không có con số trước và sau trong phần chữ, và lần viết lại đã thay đổi nhiều thứ cùng lúc.

Bài này dành cho bạn đang cân nhắc viết lại một service và muốn biết bài của Discord cho phép kết luận đến đâu.

## 1. Bối cảnh

Read States là service ghi nhận bạn đã đọc kênh nào, tin nhắn nào. Nó được gọi mỗi khi bạn kết nối, gửi hoặc đọc tin nhắn, nên nằm trên đường xử lý nóng của hệ thống.

Theo bài gốc:
- Mỗi máy chủ giữ một cache LRU (bộ nhớ đệm loại bỏ mục lâu không dùng nhất) chứa hàng chục triệu mục.
- Cache nhận hàng trăm nghìn lượt cập nhật mỗi giây.
- Dữ liệu được ghi xuống cơ sở dữ liệu Cassandra, hàng chục nghìn lượt ghi mỗi giây.

Các con số này đều là ước lượng theo bậc độ lớn, không phải số đo chính xác.

## 2. Bài gốc quan sát được gì

**Với bản Go.** Độ trễ và CPU tăng vọt khoảng 2 phút một lần. Bài gốc giải thích bằng garbage collector (GC), bộ phận tự thu hồi bộ nhớ không còn dùng. Go buộc GC chạy ít nhất 2 phút một lần, và mỗi lần chạy phải quét cả cache lớn dù lượng rác rất ít.

Đội Discord đã thử chỉnh tham số GC và đổi kích thước cache. Họ đo trên Go 1.9.2, và thử thêm các bản 1.8, 1.9, 1.10 mà không cải thiện.

**Với bản Rust.** Rust không có GC: bộ nhớ được giải phóng ngay khi một mục bị loại khỏi cache. Bản chuyển đổi đầu tiên xong vào tháng 5/2019. Khi thử tải, độ trễ ngang bản Go và không còn các đợt tăng vọt.

Sau đó đội tối ưu thêm, nâng thư viện tokio lên 0.2 và tăng cache lên 8 triệu mục.

## 3. Mỗi nhận định dựa trên bằng chứng gì

| Nhận định | Bằng chứng trong bài gốc | Mức bằng chứng |
|---|---|---|
| Bản Go có đợt tăng vọt mỗi khoảng 2 phút | Biểu đồ production; không có số trong phần chữ | Quan sát, chưa định lượng |
| Nguyên nhân là GC quét cache lớn | Cơ chế (GC bị ép chạy mỗi 2 phút) và các lần chỉnh tham số | Giải thích hợp lý, chưa có so sánh có kiểm soát |
| Bản Rust hết tăng vọt; độ trễ, CPU, bộ nhớ thấp hơn | Biểu đồ trước và sau | Quan sát trên một service, chưa định lượng |
| Cải thiện đến từ ngôn ngữ Rust | Không có phép đo tách riêng | Chưa tách được |

Không nhận định nào đi kèm số mẫu, số lần đo lặp lại hay độ dao động. Vì vậy không tính được khoảng tin cậy cho bất kỳ so sánh nào trong bài.

## 4. Vì sao chưa kết luận được "Rust nhanh hơn Go"

- **Nhiều thứ đổi cùng lúc.** Bản Rust dùng cấu trúc dữ liệu khác (BTreeMap thay cho HashMap), thư viện metrics khác, giảm sao chép bộ nhớ, và sau đó nâng phiên bản tokio. Kích thước cache cũng được tăng lên. Bài gốc không đo riêng đóng góp của từng thay đổi.
- **Không có số trước và sau.** Độ trễ, CPU, bộ nhớ chỉ xuất hiện trên biểu đồ. Bài không nêu phần cứng hai bản có giống nhau không, tải lúc đo ra sao, đo trong bao lâu.
- **Một service, một lần triển khai.** Đây là n = 1. Chính bài gốc cũng nói họ chỉ dùng Rust ở nơi phù hợp.
- **Phiên bản Go đã cũ.** Các bản được thử là 1.8 đến 1.10. Bài không đo bản mới hơn, nên không nói được Go hiện nay còn hiện tượng này hay không.
- **Tiêu đề rộng hơn nội dung.** Tiêu đề gợi ý cả công ty đổi ngôn ngữ; nội dung chỉ nói về một service.

Điều đứng vững hơn là cơ chế: một bộ GC phải quét toàn bộ vùng nhớ đang sống sẽ tốn thời gian theo kích thước vùng nhớ đó, kể cả khi rác ít. Một cache lớn sống lâu là đúng trường hợp này.

## 5. Một phép so sánh đạt chuẩn sẽ cần gì

Nếu bạn định tự đo trước khi viết lại một service:

1. Cùng phần cứng, cùng dữ liệu, cùng tải (phát lại traffic thật nếu được), bỏ giai đoạn khởi động.
2. Báo cáo p50, p99 và giá trị lớn nhất theo từng cửa sổ thời gian, không chỉ trung bình.
3. Chạy lặp lại ít nhất 5 lần mỗi cấu hình và báo cáo độ dao động giữa các lần.
4. Đo tách từng thay đổi: chỉ đổi cấu trúc dữ liệu, chỉ đổi runtime, rồi mới đổi ngôn ngữ.
5. Ghi phiên bản của mọi thành phần và ngày đo.

Riêng mục 4 là ý của mình; bài gốc không đề cập.

## 6. Nên dùng bài của Discord thế nào

Phần này là ý kiến của mình. Hãy trích bài như một ví dụ thực tế về độ trễ do GC khi vùng nhớ sống lớn, và về cách một đội chẩn đoán vấn đề đó. Đừng trích nó như bằng chứng chung về tốc độ của hai ngôn ngữ.

## Giới hạn của bài này

- Mình không đo lại bất cứ điều gì; mọi dữ kiện lấy từ bài gốc của Discord.
- Mình đọc bài gốc ở dạng văn bản nên không đọc được giá trị trên các biểu đồ.
- Mình không kiểm tra hành vi GC của các phiên bản Go mới hơn.
- Discord không công bố code, cấu hình thử tải hay thông số phần cứng, nên kết quả không tái lập được từ bên ngoài.

## Nguồn

- Jesse Howarth, Discord Engineering (04/02/2020), ["Why Discord is switching from Go to Rust"](https://discord.com/blog/why-discord-is-switching-from-go-to-rust).

Bạn có số liệu trước và sau, đo cùng tải và cùng phần cứng, cho một lần viết lại service nào không? Mình muốn biết phần cải thiện đến từ ngôn ngữ hay từ thiết kế lại.
