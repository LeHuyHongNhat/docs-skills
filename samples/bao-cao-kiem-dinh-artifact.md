# Báo cáo: Kiểm định bộ skill viết tài liệu (bản trình bày)

| Phiên bản | Ngày | Owner | Trạng thái |
|---|---|---|---|
| 1.0 | 2026-11-16 | Le Nhat | Mẫu minh họa |

> **Tóm tắt:** Có skill, agent đạt 92,5% assertion so với 72,0% khi không có skill (10 case). Chênh lệch đến chủ yếu từ việc không bịa giá trị và tách đề xuất khỏi đặc tả. Rủi ro còn lại: case ERD → PDF mobile thua 2 lần chấm blind và bản sửa v2.2 chưa được chấm lại.

::: {.kpis}
- **92,5%** tỉ lệ đạt assertion khi có skill (không skill: 72,0%)
- **8/8** case nội dung thắng blind A/B ở vòng 1
- **52/52** lượt routing chọn đúng skill
- **−32%** độ dài tài liệu v2 so với v1
:::

## 1. Kết quả chính

Chỉ số chính là tỉ lệ assertion đạt: mỗi case có 7–13 câu kiểm tra khách quan, chấm bởi LLM grader và script.

```chart
type: hbar
title: Có skill, tỉ lệ đạt assertion cao hơn 20,5 điểm phần trăm
subtitle: Tỉ lệ đạt assertion, 10 case, vòng 2 (%)
categories: [Có skill (v2), Không skill]
values: [92.5, 72.0]
unit: "%"
max: 100
highlight: Có skill (v2)
source: docs/bao-cao-kiem-dinh-doc-skills.md §3.2
```

Cách đọc: thanh dài hơn là tốt hơn; trục bắt đầu từ 0 nên độ dài thanh tỉ lệ thuận với giá trị.

## 2. So sánh giữa hai vòng

Vòng 2 dùng bộ assertion chặt hơn, nên tỉ lệ đạt của *cả hai* cấu hình đều giảm. Khoảng cách giữa hai cấu hình mới là điều đáng xem.

```chart
type: slope
title: Assertion chặt hơn kéo cả hai xuống, nhưng khoảng cách nới rộng từ 12 lên 20,5 điểm
subtitle: Tỉ lệ đạt assertion (%)
categories: [Vòng 1 (8 case), Vòng 2 (10 case)]
series:
  - name: Có skill
    values: [97.5, 92.5]
  - name: Không skill
    values: [85.5, 72.0]
unit: "%"
source: docs/bao-cao-kiem-dinh-doc-skills.md §3.1–3.2
note: Bộ assertion và số case khác nhau giữa hai vòng; không so sánh trực tiếp giá trị tuyệt đối giữa hai vòng.
```

## 3. Thẩm mỹ & định dạng

```chart
type: dumbbell
title: Case ERD → PDF mobile vẫn thua; case PRD → Word thắng ở cả hai lần chạy
subtitle: Điểm blind A/B (thang 10)
categories: [PRD → Word v2, PRD → Word v2.1, ERD → mobile v2, ERD → mobile v2.1]
series:
  - name: Không skill
    values: [6.5, 6.3, 9.0, 9.0]
  - name: Có skill
    values: [9.0, 8.5, 7.7, 6.0]
max: 10
source: docs/bao-cao-kiem-dinh-doc-skills.md §3.3
```

| Tiêu chí | Không skill | Có skill v2.2 ★ |
|---|---|---|
| Không bịa giá trị vào AC | ✗ bịa enum, ngưỡng | ✓ đánh dấu [CẦN XÁC NHẬN] |
| Tách đề xuất khỏi đặc tả | ✗ trộn lẫn | ✓ mục riêng |
| PDF đọc trên điện thoại | ✓ chữ ≥ 9pt | ◐ đã sửa (16,9pt), chưa chấm lại |
| Thời gian chạy | ✓ 1× | ✗ 2–2,5× |

::: {.compare}
::: {}
#### Trước (v2.1)
- PDF mobile: chữ thực tế 5–6pt
- Không có cảnh báo tự động
:::
::: {.rec}
#### Sau (v2.2)
- Chữ đo được [16,9pt]{.good}
- Cảnh báo khi chữ < 7,5pt
:::
:::

## 4. Độ tin cậy của đánh giá

Ba kiểm tra đều đạt tối đa, nên bảng đủ rõ — biểu đồ không thêm thông tin khi mọi giá trị bằng nhau.

| Kiểm tra | Phát hiện đúng | Tổng có đáp án |
|---|---|---|
| Flowchart (cạnh) | 16 | 16 |
| ERD (cột) | 25 | 25 |
| Review (lỗi cài sẵn) | 13 | 13 |

> **Lưu ý:** mỗi cấu hình mới chạy 1 lần cho mỗi case; chênh 1–2 điểm ở judge nằm trong biên nhiễu.
