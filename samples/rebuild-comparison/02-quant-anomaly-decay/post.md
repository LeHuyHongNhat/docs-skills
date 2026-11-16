# Anomaly còn lại bao nhiêu sau khi được công bố? Đọc lại McLean & Pontiff (2016)

Trung bình, lợi nhuận của 97 anomaly đã công bố giảm 58% sau khi bài báo ra đời. Con số 26% "giảm ngoài mẫu" hay được trích kèm thì nằm sát ngưỡng thống kê: khoảng tin cậy mình tự tính có chứa 0. Cả hai là trung bình của cả nhóm, không phải dự báo cho một tín hiệu cụ thể.

Bài này dành cho bạn làm alpha research và muốn dùng paper này để ước lượng mức hao hụt của một tín hiệu khi đem ra ngoài mẫu.

## 1. Câu hỏi và ba giả thuyết kinh tế

Anomaly ở đây là một đặc trưng của cổ phiếu dự báo được lợi nhuận tương lai, ví dụ momentum hay value. Paper hỏi: lợi nhuận đó thay đổi thế nào sau khi nghiên cứu gốc kết thúc mẫu, và sau khi nó được công bố?

Ba cách giải thích cho ba dự đoán khác nhau:

| Nếu anomaly đến từ | Thì ngoài mẫu, lợi nhuận sẽ |
|---|---|
| Sai lệch thống kê (data mining, chọn lọc kết quả đẹp) | Biến mất ngay khi ra khỏi mẫu gốc |
| Phần bù rủi ro hợp lý | Không đổi, kể cả sau khi công bố |
| Định giá sai mà nhà đầu tư học được từ bài báo | Giảm sau khi công bố, nhưng không về 0 nếu việc arbitrage tốn kém |

Thiết kế của paper dùng chính sự khác nhau này để tách các giả thuyết.

## 2. Cách đo: 97 biến dự báo, ba giai đoạn, cổ phiếu Mỹ đến 2013

- **Mẫu**: 97 biến dự báo lấy từ 80 nghiên cứu đăng trên tạp chí có bình duyệt. Trong bài này, "biến dự báo", "đặc trưng", "factor" và "tín hiệu" cùng chỉ một thứ: đại lượng dùng để xếp hạng cổ phiếu. Dữ liệu cổ phiếu Mỹ lấy từ CRSP (Center for Research in Security Prices, bộ dữ liệu giá cổ phiếu chuẩn trong nghiên cứu tài chính), kéo dài đến năm 2013.
- **Danh mục**: với mỗi biến, mua nhóm 20% cổ phiếu ở một đầu và bán khống nhóm 20% ở đầu kia (long-short), phần lớn theo trọng số bằng nhau.
- **Ba giai đoạn**: trong mẫu gốc (trung bình 323 tháng), ngoài mẫu nhưng trước khi công bố (56 tháng), và sau khi công bố (156 tháng).
- **Ước lượng**: hồi quy lợi nhuận tháng của từng danh mục lên hai biến giả (nhận giá trị 0 hoặc 1) đánh dấu hai giai đoạn sau. Mô hình có fixed effect theo từng biến dự báo, tức mỗi biến được so với mức trung bình của chính nó.

Đây là so sánh quan sát, không phải thí nghiệm: không ai phân ngẫu nhiên việc một anomaly có được công bố hay không.

## 3. Sau công bố giảm 58%; ngoài mẫu giảm 26% ở mức ranh giới

Lợi nhuận long-short trung bình trong mẫu là 0,582% mỗi tháng. So với mức đó:

| Giai đoạn | Hệ số (điểm % mỗi tháng) | Sai số chuẩn | Mức giảm |
|---|---|---|---|
| Ngoài mẫu, trước công bố | −0,150 | 0,077 | 26% |
| Sau công bố | −0,337 | 0,090 | 58% |

Paper báo cáo sai số chuẩn (SE), không báo cáo khoảng tin cậy cho hai tỉ lệ 26% và 58%. Mình tự tính khoảng tin cậy 95% bằng hệ số ± 1,96 × SE rồi chia cho 0,582:

```chart
type: interval
title: Mức giảm sau công bố khác 0 rõ ràng; mức giảm ngoài mẫu có khoảng tin cậy chạm 0
subtitle: Mức giảm lợi nhuận long-short so với trong mẫu (%), ước lượng và khoảng tin cậy 95%
categories: ["Ngoài mẫu, trước công bố", "Sau công bố"]
values: [25.8, 57.9]
low: [-0.2, 27.7]
high: [51.7, 88.1]
unit: "%"
source: McLean & Pontiff (2016), Bảng II cột 1; khoảng tin cậy do người viết tính từ hệ số và sai số chuẩn
note: Phép tính xấp xỉ, bỏ qua sai số của mức nền 0,582%.
```

Cách đọc: chấm đặc nghĩa là khoảng tin cậy không chứa 0; chấm rỗng nghĩa là có chứa.

- **Sau công bố**: giảm 58%, khoảng tin cậy từ 28% đến 88%. Khoảng này không chứa 0, nhưng rất rộng, và phép tính của mình còn bỏ qua sai số của mức nền nên khoảng thật rộng hơn nữa.
- **Ngoài mẫu, trước công bố**: giảm 26%, khoảng tin cậy từ −0,2% đến 52%, tức có chứa 0; t ≈ 1,95, thấp hơn ngưỡng 1,96 của mức 5%. Kết quả nằm ngay sát ngưỡng: chưa đủ để gọi là đã xác lập, cũng không thể gọi là không có.

Các kiểm định khác trong paper:
- Bác bỏ giả thuyết "lợi nhuận biến mất hoàn toàn sau công bố" (paper ghi p = 0,000, tức p < 0,001).
- Hai mức giảm khác nhau có ý nghĩa thống kê (p = 0,024).
- Thêm fixed effect theo thời gian: hệ số còn −0,179 và −0,310, tức sau công bố giảm khoảng 53%.
- Bỏ 12 biến mà tác giả dựng lại không đạt t > 1,5: hệ số là −0,180 và −0,387.

Paper cũng báo cáo rằng biến có lợi nhuận trong mẫu càng cao thì giảm càng mạnh, và sau công bố thì khối lượng giao dịch cùng tỉ lệ bán khống ở các cổ phiếu liên quan tăng lên.

## 4. Điều paper không cho thấy

- **"32% là do nhà đầu tư giao dịch theo bài báo"** là phần dư (58% − 26%), không phải một tác động được đo riêng. Tác giả coi 26% là chặn trên của sai lệch thống kê, vì một số người đã biết tín hiệu từ bản thảo trước ngày công bố.
- **Không dự báo được cho từng tín hiệu.** 58% là trung bình của 97 biến; paper cho thấy mức giảm khác nhau nhiều giữa các biến.
- **Chi phí giao dịch.** Bản tóm tắt của CXO Advisory ghi các con số là lợi nhuận gộp, chưa trừ phí. Trong phần mình đọc được, paper không nêu rõ điểm này.
- **Phạm vi.** Cổ phiếu Mỹ, đến năm 2013, các tín hiệu từ dữ liệu công khai. Không nói gì về thị trường khác hay tín hiệu độc quyền.
- **Look-ahead và survivorship bias.** Mình không kiểm được cách từng biến được dựng lại có dùng dữ liệu point-in-time hay không. Tác giả thừa nhận việc dựng lại là không hoàn hảo.
- **Phiên bản.** Bản nháp tháng 5/2013 dùng 82 đặc trưng và ước lượng mức giảm ngoài mẫu khoảng 10%, không khác 0 về thống kê. Bản đăng năm 2016 dùng 97 biến và ra 26%. Khi trích, cần nói rõ bản nào.

## 5. Nghiên cứu sau đó nói gì

- Jensen, Kelly và Pedersen (2021) dùng mô hình Bayes trên 153 factor ở 93 nước. Theo phần tóm tắt của paper, đa số factor dựng lại được và đứng vững ngoài mẫu. Hai kết quả không nhất thiết trái nhau: lợi nhuận có thể giảm sau công bố mà vẫn khác 0. Mình chưa đọc đủ để nói hai paper khớp nhau đến đâu.
- Chen và Zimmermann (2021), theo bài tổng hợp của Larry Swedroe, cũng thấy lợi nhuận giảm sau công bố nhưng vẫn dương, và giảm mạnh hơn ở tín hiệu mạnh trong mẫu.

Mình mới đọc phần tóm tắt của hai paper này, chưa đọc bảng số liệu gốc.

## 6. Dùng kết quả này thế nào khi làm alpha

Phần này là ý kiến của mình.

- Coi lợi nhuận trong mẫu là chặn trên. Tín hiệu càng đẹp trong mẫu càng nên bị trừ hao mạnh.
- Không dùng 58% như một hệ số cố định. Khoảng tin cậy của nó trải từ 28% đến 88%, và đó là trung bình của tín hiệu học thuật trên cổ phiếu Mỹ.
- Mỗi tín hiệu cần giai đoạn ngoài mẫu của riêng nó, cần ghi lại số biến thể đã thử, và cần tính sau chi phí.
- Viết giả thuyết kinh tế trước khi nhìn backtest: ai ở phía bên kia giao dịch, và vì sao họ tiếp tục ở đó. Tín hiệu không có cơ chế là ứng viên của overfitting.

## Giới hạn của bài tóm tắt này

- Số liệu lấy từ một bản working paper có phần tóm tắt trùng với bản đăng tạp chí, đọc qua công cụ trích văn bản; mình chưa đối chiếu từng bảng với bản in.
- Khoảng tin cậy trong biểu đồ là phép tính xấp xỉ của mình, không phải của tác giả.
- Dữ liệu CRSP là dữ liệu thương mại; mình không xác minh được tác giả có công bố code hay không.
- Bài này do một AI agent soạn từ các nguồn nêu bên dưới. Chưa có người nào đối chiếu từng con số với bản gốc.

## Nguồn

- McLean, Pontiff (2016), "Does Academic Research Destroy Stock Return Predictability?", Journal of Finance 71(1), doi:10.1111/jofi.12365. [Bản working paper](https://counterpointfunds.com/wp-content/uploads/2017/07/PredictabilityMcleanPontiff.pdf).
- Jensen, Kelly, Pedersen (2021), "Is There a Replication Crisis in Finance?", [NBER Working Paper 28432](http://www.nber.org/papers/w28432).
- CXO Advisory (2016), ["Effects of In-sample Bias and Market Adaptation on Stock Anomalies"](https://www.cxoadvisory.com/big-ideas/effects-of-market-adaptation).

Bạn trừ hao lợi nhuận trong mẫu bao nhiêu khi ước lượng ngoài mẫu, và con số đó dựa trên dữ liệu nào?
