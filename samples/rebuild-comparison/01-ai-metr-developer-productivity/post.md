# "AI làm lập trình viên chậm 19%": nghiên cứu METR đo gì và không đo gì

Con số "chậm hơn 19%" là kết quả đo thật, nhưng khoảng tin cậy của nó trải từ 2% đến 39%, trên 16 lập trình viên kỳ cựu vào đầu năm 2025. Đợt đo tiếp theo, công bố tháng 2/2026, không còn phân biệt được AI làm họ nhanh hơn hay chậm hơn.

Bài này đọc lại nghiên cứu từ bản gốc, dành cho bạn đang muốn trích con số này trong một cuộc tranh luận về công cụ AI cho lập trình.

## 1. Nghiên cứu làm gì

METR (Model Evaluation & Threat Research) là một tổ chức nghiên cứu phi lợi nhuận. Họ chạy một thử nghiệm ngẫu nhiên có đối chứng (RCT): mỗi đầu việc được tung đồng xu để quyết định lập trình viên **được phép** hay **không được phép** dùng AI. Vì việc chia nhóm là ngẫu nhiên, khác biệt về thời gian có thể quy cho việc được dùng AI, trong phạm vi nhóm người và loại việc này.

| Thành phần | Giá trị |
|---|---|
| Người tham gia | 16 lập trình viên, trung bình 5 năm đóng góp cho repo của mình |
| Đầu việc | 246 issue thật (136 được dùng AI, 110 không), trung bình khoảng 2 giờ mỗi issue |
| Repo | Mã nguồn mở lớn: trung bình khoảng 23.000 sao, 1,1 triệu dòng code |
| Công cụ | Chủ yếu Cursor Pro với Claude 3.5/3.7 Sonnet |
| Thời gian | Tháng 2 đến tháng 6 năm 2025 |
| Thù lao | 150 USD mỗi giờ |
| Thước đo | Thời gian hoàn thành issue do lập trình viên tự ghi |

Cách ước lượng (mục 2.3 của paper): hồi quy trên log của thời gian hoàn thành, có kiểm soát theo thời gian mà lập trình viên dự đoán cho issue đó trong trường hợp không dùng AI.

## 2. Kết quả, kèm độ bất định

Issue được phép dùng AI mất nhiều thời gian hơn **19%**, khoảng tin cậy 95% từ **+2% đến +39%**. Khoảng tin cậy là vùng giá trị mà tác động thật nhiều khả năng nằm trong. Ở đây vùng đó không chứa 0, nên *hướng* (chậm hơn) được dữ liệu ủng hộ. Nhưng *độ lớn* thì chưa chắc: tác động thật có thể gần như bằng 0, cũng có thể gấp đôi con số 19%.

Phát hiện thứ hai là khoảng cách giữa cảm nhận và đo đạc:

```chart
type: hbar
title: Mọi dự đoán đều nói AI giúp nhanh hơn; kết quả đo cho thấy chậm hơn 19%
subtitle: Thay đổi thời gian hoàn thành khi được dùng AI (%), số âm là nhanh hơn
categories: [Chuyên gia kinh tế dự đoán, Chuyên gia ML dự đoán, Lập trình viên dự đoán trước, Lập trình viên ước lượng sau, Kết quả đo]
values: [-39, -38, -24, -20, 19]
unit: "%"
highlight: Kết quả đo
source: Becker và cộng sự (2025), arXiv:2507.09089, mục 3 và 3.1
note: Kết quả đo có khoảng tin cậy 95% từ +2% đến +39%; các dự đoán là giá trị trung bình, không kèm khoảng tin cậy.
```

Sau khi làm xong, chính những người tham gia vẫn tin rằng AI đã giúp họ nhanh hơn 20%.

Các kiểm tra độ vững mà paper báo cáo (Phụ lục C.3 và E.2):
- Đổi cách ước lượng (ba mô hình hồi quy khác và tỉ số trung bình) cho kết quả cùng hướng.
- Trên phần có ghi màn hình, thời gian đo từ video cho mức chậm 25%, so với 24% từ thời gian tự ghi.
- 75% số lập trình viên bị chậm hơn khi được dùng AI; một số ít nhanh hơn.

## 3. Điều tác giả nói nghiên cứu KHÔNG cho thấy

Paper có hẳn một bảng liệt kê (Bảng 2, mục 4.1). Tóm tắt lại, kết quả không có nghĩa là:
- AI không giúp được đa số lập trình viên hay đa số loại công việc phần mềm.
- Kết quả áp dụng cho lĩnh vực khác.
- Các mô hình AI ra sau sẽ không giúp nhanh hơn trong chính bối cảnh này.
- Người dùng AI thành thạo hơn sẽ không nhanh hơn.

Vài chi tiết khác ảnh hưởng đến cách đọc kết quả:
- 93% người tham gia từng dùng công cụ LLM (mô hình ngôn ngữ lớn), nhưng chỉ 44% từng dùng Cursor.
- Nghiên cứu không "mù": người tham gia biết mình thuộc nhóm nào. Một số nói họ dùng AI nhiều hơn bình thường vì đang trong thử nghiệm.
- Tác giả nêu 5 yếu tố có thể góp phần làm chậm (Bảng 1), gồm: người tham gia quá quen repo của mình, repo lớn và phức tạp, và AI thiếu ngữ cảnh ngầm của dự án.

## 4. Cập nhật tháng 2/2026: kết quả mới không kết luận được

METR chạy tiếp từ tháng 8/2025 với 57 lập trình viên (10 người cũ, 47 người mới), hơn 800 đầu việc trên 143 repo, thù lao 50 USD mỗi giờ.

```chart
type: interval
title: Cả hai ước lượng mới đều có khoảng tin cậy chứa 0
subtitle: 'Giá trị "speedup" theo cách ghi của METR (%); bài gốc không định nghĩa chiều của dấu'
categories: [Nhóm 10 người cũ, Nhóm 47 người mới]
values: [-18, -4]
low: [-38, -15]
high: [9, 9]
unit: "%"
source: METR (24/02/2026), "We are Changing our Developer Productivity Experiment Design"
```

Hai điều cần nói rõ:

1. **Chiều của dấu không được định nghĩa.** METR viết kết quả 2025 là "mất thêm 19% thời gian", còn kết quả mới là "speedup −18%". Các bài viết lại đang đọc con số này theo hai hướng ngược nhau: có bài ghi "nhanh hơn 18%", có bài ghi "vẫn chậm 18%". Mình không chọn cách đọc nào. Điều duy nhất dữ liệu cho phép nói là cả hai khoảng tin cậy đều chứa 0.
2. **Mẫu bị chọn lọc.** Theo METR, 30% đến 50% lập trình viên đã tránh đưa vào những việc họ không muốn làm thiếu AI, và nhiều người từ chối tham gia vì lý do tương tự. METR gọi dữ liệu mới là bằng chứng rất yếu, cho rằng lập trình viên nhiều khả năng đã được tăng tốc hơn so với đầu 2025, và đang đổi thiết kế thí nghiệm.

## 5. Nên trích kết quả này thế nào

Phần này là ý kiến của mình.

- Đừng viết "AI làm lập trình viên chậm 19%". Viết: "Trong một RCT đầu năm 2025 với 16 lập trình viên kỳ cựu trên repo của chính họ, issue được phép dùng AI mất thêm 19% thời gian (khoảng tin cậy 95%: 2% đến 39%)."
- Phát hiện đáng mang về hơn là khoảng cách giữa cảm nhận và đo đạc. Nếu team bạn đánh giá công cụ AI bằng khảo sát cảm nhận, kết quả này là lý do để đo thời gian thật.
- Muốn tự đo: chia ngẫu nhiên theo từng đầu việc, ghi thời gian từng việc, và báo cáo kèm khoảng tin cậy.

## Giới hạn của bài tóm tắt này

- Mình đọc paper qua bản PDF trên arXiv; phần từ cuối Phụ lục E trở đi mình chưa đọc được. Khoảng tin cậy +2% đến +39% lấy từ bài cập nhật năm 2026 của METR.
- Mình chưa xác minh được METR có công bố dữ liệu và code phân tích hay không.
- Bài chỉ nói về hai nghiên cứu của METR, không tổng hợp các nghiên cứu khác về năng suất khi dùng AI.

## Nguồn

- Becker, Rush, Barnes, Rein (2025), "Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity", [arXiv:2507.09089](https://arxiv.org/abs/2507.09089).
- METR (24/02/2026), ["We are Changing our Developer Productivity Experiment Design"](https://metr.org/blog/2026-02-24-uplift-update/).

Team bạn đã từng đo, chứ không chỉ hỏi cảm nhận, tác động của AI lên thời gian làm việc chưa? Nếu có, bạn chia nhóm và ghi thời gian bằng cách nào?
