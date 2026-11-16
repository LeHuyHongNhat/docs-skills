# Báo cáo: Dựng lại 3 bài viết thật bằng skill và so sánh với bản gốc

| Phiên bản | Ngày | Owner | Trạng thái |
|---|---|---|---|
| 1.1 | 2026-11-16 | Claude cho Le Nhat | Tự chấm, chưa có người chấm độc lập |

> **Tóm tắt:** Ba bài thật về AI, quant và IT được dựng lại bằng `community-post-writer` có lớp research rigor. Theo rubric 12 tiêu chí (tối đa 24 điểm), bản dựng lại đạt 22–23 điểm, bản gốc đạt 10–16 điểm. Phép so sánh này **chưa đủ để kết luận skill viết tốt hơn**: chỉ có 3 cặp bài, người chấm cũng là người viết, và rubric đo cách trình bày bằng chứng chứ không đo độ hữu ích. Giá trị chính của đợt này là 8 lỗi thật mà quy trình bắt được, kể cả lỗi trong bài mẫu và trong chính các bản dựng lại.

::: {.kpis}
- **3** cặp bài (AI, quant, IT), mỗi cặp dùng chung một nguồn sơ cấp
- **+10 điểm** chênh lệch trung bình trên thang 24 (từ 6 đến 12)
- **p = 0,25** với n = 3: chưa kết luận được theo chính `stats_check.py`
- **8** lỗi thật được phát hiện trong quá trình dựng lại
:::

## 1. Cách làm

1. Chọn một bài thật đang lưu hành cho mỗi lĩnh vực và tìm nguồn sơ cấp của nó (paper, hoặc chính bài kỹ thuật).
2. Lập claim ledger từ nguồn sơ cấp, chạy `stats_check.py claims` để có verdict cho từng claim.
3. Viết lại bằng tiếng Việt cho diễn đàn kiểu Viblo, theo `research-rigor.md`.
4. Chạy `post_check.py --rigor` trên bản dựng lại.
5. Chấm cả hai bản theo rubric R1–R12 (mỗi tiêu chí 0, 1 hoặc 2 điểm).

| # | Lĩnh vực | Bài gốc | Nguồn sơ cấp | Bản dựng lại |
|---|---|---|---|---|
| 1 | AI | Medium, 08/2025: ["Its official: Developers are slower with AI"](https://medium.com/@benratcliffe_/its-official-developers-are-slower-with-ai-a7a1ccd2952e) | Paper METR, [arXiv:2507.09089](https://arxiv.org/abs/2507.09089), và bài cập nhật 02/2026 | [`01-…/post.md`](01-ai-metr-developer-productivity/post.md) |
| 2 | Quant | CXO Advisory, 10/2016: ["Effects of In-sample Bias and Market Adaptation on Stock Anomalies"](https://www.cxoadvisory.com/big-ideas/effects-of-market-adaptation) | McLean & Pontiff (2016), Journal of Finance | [`02-…/post.md`](02-quant-anomaly-decay/post.md) |
| 3 | IT | Discord Engineering, 02/2020: ["Why Discord is switching from Go to Rust"](https://discord.com/blog/why-discord-is-switching-from-go-to-rust) | Chính bài này (số liệu tự đo của Discord) | [`03-…/post.md`](03-it-discord-go-to-rust/post.md) |

Bài gốc không được sao chép vào repo. Mỗi thư mục chỉ chứa claim ledger (`claims.yaml`), bản dựng lại và ảnh biểu đồ.

## 2. Kết quả chấm rubric

```chart
type: dumbbell
title: Bản dựng lại đạt 22–23 trên 24 điểm; bản gốc đạt 10–16
subtitle: Tổng điểm rubric R1–R12 (thang 0–24), tự chấm
categories: ["1. AI: nghiên cứu METR", "2. Quant: anomaly sau công bố", "3. IT: Discord Go sang Rust"]
series:
  - name: Bài gốc
    values: [10, 16, 11]
  - name: Bản dựng lại
    values: [22, 22, 23]
min: 0
max: 24
source: Bảng điểm ở mục 2 của báo cáo này
note: Người chấm cũng là người viết bản dựng lại. Bài gốc được đọc qua công cụ trích văn bản, không đọc trực tiếp từng dòng.
```

```chart
type: heatmap
title: Khoảng cách lớn nhất nằm ở độ bất định, giới hạn và tiêu đề
subtitle: Điểm từng tiêu chí (0 = thiếu, 1 = một phần, 2 = đạt)
categories: [R1 Đúng số liệu, R2 Thiết kế và mẫu, R3 Độ bất định, R4 Mức khẳng định, R5 Phạm vi, R6 Giới hạn, R7 Giải thích thay thế, R8 Truy vết nguồn, R9 Tái lập, R10 Tách đo đạc và ý kiến, R11 Tiêu đề, R12 Tính cập nhật]
columns: [Gốc 1, Dựng lại 1, Gốc 2, Dựng lại 2, Gốc 3, Dựng lại 3]
series:
  - {name: R1, values: [2, 1, 2, 1, 2, 1]}
  - {name: R2, values: [2, 2, 2, 2, 1, 2]}
  - {name: R3, values: [0, 2, 1, 2, 1, 2]}
  - {name: R4, values: [1, 2, 1, 2, 1, 2]}
  - {name: R5, values: [1, 2, 1, 2, 1, 2]}
  - {name: R6, values: [0, 2, 2, 2, 1, 2]}
  - {name: R7, values: [1, 2, 2, 2, 1, 2]}
  - {name: R8, values: [1, 2, 1, 2, 1, 2]}
  - {name: R9, values: [0, 1, 0, 1, 0, 2]}
  - {name: R10, values: [1, 2, 1, 2, 1, 2]}
  - {name: R11, values: [0, 2, 1, 2, 0, 2]}
  - {name: R12, values: [1, 2, 2, 2, 1, 2]}
min: 0
max: 2
source: Tự chấm theo research-rigor.md mục 7
```

Lý do cho các điểm thấp của bài gốc:

| Bài gốc | Điểm 0 | Điểm 1 đáng chú ý |
|---|---|---|
| 1. Medium (METR) | Không nêu khoảng tin cậy; không nêu giới hạn nào; tiêu đề khẳng định chung cho mọi lập trình viên; không nói về dữ liệu, code | Phạm vi chỉ nêu một phần; ý kiến người viết lẫn với kết quả đo |
| 2. CXO Advisory | Không nói về dữ liệu, code | Không có sai số chuẩn cho con số chính; "32% do giao dịch" được nêu như tác động đo được; không nêu thị trường |
| 3. Discord | Không có code, cấu hình thử tải, phần cứng; tiêu đề rộng hơn nội dung | Số trước và sau chỉ nằm trên biểu đồ; nhiều thay đổi gộp chung; phiên bản Go đã cũ |

Bản dựng lại mất điểm ở hai chỗ. R1 ở cả ba cặp: số liệu được đọc qua công cụ trích văn bản, chưa đối chiếu từng dòng với nguồn sơ cấp, nên theo quy tắc "evidence state" của bản 1.1 chỉ được 1 điểm. R9 ở cặp 1 và 2: chưa xác minh được tác giả có công bố dữ liệu và code hay không.

## 3. Phép so sánh này cho phép kết luận gì

Dùng chính công cụ của skill cho ba cặp điểm:

```bash
python scripts/stats_check.py paired --a 22,22,23 --b 10,16,11
# chênh lệch trung bình 10 điểm; p = 0,25 (hoán vị chính xác, n = 3) → INCONCLUSIVE
```

Với 3 cặp, phép kiểm định hoán vị không thể cho p nhỏ hơn 0,25 dù chênh lệch lớn đến đâu. Vì vậy câu được phép viết là: "trên 3 cặp bài tự chấm, bản dựng lại có điểm rubric cao hơn ở cả 3 cặp". Câu "skill viết chặt chẽ hơn tác giả người thật" thì **chưa được phép viết**.

Các mối đe dọa đối với kết luận:

| Mối đe dọa | Trạng thái |
|---|---|
| Người chấm là người viết, cùng một model | Chưa xử lý. Cần người chấm độc lập, không biết bài nào là bản dựng lại |
| Rubric do chính tác giả skill viết, nên bản dựng lại được viết để đạt rubric | Chưa xử lý. Điểm cao một phần là do vòng lặp này |
| Bài gốc do mình chọn; bài 1 được chọn vì có tiêu đề nói quá | Chưa xử lý. Cần chọn bài theo quy tắc định trước |
| Bài gốc được đọc qua công cụ trích văn bản | Xử lý một phần: các điểm chính được đối chiếu với nguồn sơ cấp |
| Khác thể loại và mục đích: bài Discord là bài kể chuyện kỹ thuật, không phải báo cáo đo lường | Không xử lý được; cần đọc điểm của cặp 3 với lưu ý này |
| Rubric đo cách trình bày bằng chứng, không đo độ hữu ích, độ dễ đọc hay mức thu hút | Ngoài phạm vi; xem mục 4 |

## 4. Bản gốc làm tốt hơn ở đâu

- **Bài Medium** ngắn hơn và có hướng dẫn hành động cụ thể cho team muốn tự đo. Bản dựng lại dài khoảng 1.000 âm tiết và chỉ có 3 gạch đầu dòng về hành động.
- **Bài CXO Advisory** cô đọng cho người đã biết nền, và đã nêu khá đủ cảnh báo (lợi nhuận gộp, dựng lại không hoàn hảo). Đây là bài gốc có điểm cao nhất.
- **Bài Discord** có biểu đồ production và chi tiết kỹ thuật trực tiếp mà bản dựng lại không thể có. Bản dựng lại không thêm bằng chứng nào; nó chỉ nói rõ bằng chứng hiện có cho phép kết luận đến đâu.

Điểm rubric cao hơn không có nghĩa là bài có thêm bằng chứng. Với cặp 3, cả bốn claim đều có verdict UNQUANTIFIED ở cả hai bản.

## 5. Tám lỗi thật mà quy trình bắt được

1. **Chiều của dấu trong bài cập nhật của METR.** Bài viết "speedup −18%" mà không định nghĩa dấu. Các bài viết lại đọc theo hai hướng ngược nhau: có bài ghi "nhanh hơn 18%", có bài ghi "vẫn chậm 18%". Bản dựng lại trích nguyên văn và chỉ kết luận rằng khoảng tin cậy chứa 0.
2. **Con số 26% của McLean & Pontiff nằm sát ngưỡng.** Hệ số 0,150 với sai số chuẩn 0,077 cho t ≈ 1,95; khoảng tin cậy 95% tự tính chạm 0. Các bản tóm tắt thường trích 26% như một con số chắc chắn.
3. **Phần trăm không khớp trong bài CXO.** Bài ghi lợi nhuận 0,58% rồi 0,40% và gọi là "thấp hơn 26%", trong khi 0,40 so với 0,58 là thấp hơn 31%. Nguồn sơ cấp cho thấy 26% đến từ hệ số hồi quy (0,150 chia 0,582), không phải từ tỉ số hai trung bình.
4. **Phiên bản working paper khác nhau.** Bản nháp 2013 dùng 82 đặc trưng và ước lượng mức giảm ngoài mẫu khoảng 10%, không khác 0; bản đăng 2016 dùng 97 biến và ra 26%.
5. **Bài mẫu của chính skill nói quá.** Bài Viblo mẫu ở bản 2.3 viết "cắt theo heading thắng" dựa trên 38/50 so với 31/50. Khoảng tin cậy của chênh lệch là −4 đến +31 điểm. Bài đã được viết lại.
6. **Checker báo nhầm.** `post_check.py` coi METR là chữ viết hoa giật tít, coi "AI cũng" là "ai cũng", coi tên riêng trong mục Nguồn là từ viết tắt chưa giải thích, và coi chữ "Evaluation" trong tên tổ chức là dấu hiệu bài về đánh giá model. Cả bốn đã được sửa và có test.
7. **Biểu đồ không vẽ được vì YAML.** Một `subtitle` bắt đầu bằng dấu ngoặc kép làm block chart không đọc được. Renderer báo cảnh báo đúng; hướng dẫn đã bổ sung quy tắc đặt ngoặc.

8. **Hai lỗi diễn giải khoảng tin cậy trong chính các bản dựng lại** (bắt được ở bản 1.1, nhờ đối chiếu với danh sách lỗi thống kê của một skill trên GitHub). Bài Viblo mẫu kết luận từ việc ba khoảng tin cậy "chồng lên nhau", trong khi phép so đúng là khoảng tin cậy của chính chênh lệch. Hai bài giải thích khoảng tin cậy là vùng mà giá trị thật "nhiều khả năng nằm trong", một cách nói sai về mặt thống kê. Cả hai đã sửa, và `post_check.py --rigor` nay báo hai lỗi này.

## 6. Lớp rigor chưa làm được gì

- **Không tự đảm bảo đọc đúng nguồn.** Độ chính xác vẫn phụ thuộc vào việc agent đọc nguồn sơ cấp. Paper METR chỉ được đọc đến hết phần đầu Phụ lục E.
- **`stats_check.py` chỉ phủ các trường hợp phổ biến**: tỉ lệ, so sánh cặp nhị phân, nhiều seed, Sharpe. Chưa có hồi quy, sai số chuẩn theo cụm, tự tương quan chuỗi thời gian, hay mô hình Bayes.
- **`post_check.py --rigor` là kiểm tra theo từ khóa.** Một bài có thể qua bằng cách nhắc đủ từ mà vẫn sai về nội dung. Rubric vẫn cần người đọc.
- **Không biến dữ liệu yếu thành bằng chứng mạnh.** Thứ skill làm được là bắt bài viết nói đúng mức dữ liệu cho phép và nêu cần đo thêm gì.

## 7. Việc nên làm tiếp

1. Nhờ 1–2 người làm nghiên cứu (quant, data science) chấm mù 3 cặp bài theo rubric, không biết bài nào là bản dựng lại.
2. Chạy eval có skill và không có skill trên cùng nguồn, chấm bằng một model khác họ. Ba eval case đã sẵn trong `community-post-writer/evals/`, gồm case backtest mới.
3. Mở rộng lên ít nhất 10 cặp bài chọn theo quy tắc định trước, để phép so sánh có đủ mẫu.
