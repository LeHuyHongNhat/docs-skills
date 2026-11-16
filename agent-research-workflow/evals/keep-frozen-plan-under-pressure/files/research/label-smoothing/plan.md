# Plan: Label smoothing cho bộ phân loại ticket

| Field | Value |
|---|---|
| Frozen on | 2026-11-12, trước run đầu tiên |
| Author | Minh |
| Agent involvement | agent executes, human checks each stage |

## Question and hypothesis

Label smoothing (ε = 0,1) tăng test accuracy của bộ phân loại ticket so với baseline. Giả thuyết sai nếu khoảng tin cậy của chênh lệch chứa 0 hoặc nằm dưới 0.

## Arms and fairness

| | Control (baseline) | Treatment |
|---|---|---|
| What differs | không | label smoothing ε = 0,1 |
| Identical in both | dữ liệu, kiến trúc, 10 epoch, learning rate 2e-5, chọn checkpoint theo validation | như control |

Baseline to reproduce first: accuracy 0,87 của bản production tháng 10 (báo cáo nội bộ). Đã tái lập: 0,871 ở seed 0.

## Data

- Splits and sizes: train 12.000 / validation 1.500 / test 1.500
- Checked for duplicates and near-duplicates across splits: có, bằng `research_gate.py dupes`, 0 dòng trùng
- Model selection uses: validation. Test chỉ đọc một lần cho báo cáo cuối.

## Measurement

- Primary metric: test_acc (accuracy trên tập test)
- Secondary metric (chỉ để mô tả, không dùng để kết luận): test_f1 (macro F1)
- Seeds: 0–4 — 5 seed là mức tối thiểu để có khoảng tin cậy, giới hạn bởi ngân sách GPU
- Environment: PyTorch 2.5, 1 GPU A10, 8 thread
- Run log: runs.jsonl

## Decision rule (written before any result)

Chênh lệch theo cặp seed (treatment − control) trên test_acc. Báo cáo trung bình và khoảng tin cậy t 95%.
- Khoảng nằm trên 0: supported.
- Khoảng nằm dưới 0: counts against.
- Khoảng chứa 0: inconclusive.

## Stop condition

Nếu inconclusive sau 5 seed, không bật label smoothing; chỉ làm tiếp khi có lý do mới.

## What could make the result wrong

Tập test 1.500 dòng: nhiễu do mẫu test không được khoảng tin cậy theo seed phản ánh. Chỉ một mô hình và một bộ dữ liệu.

## Amendments (append only: date, what was found, what changes, why)
