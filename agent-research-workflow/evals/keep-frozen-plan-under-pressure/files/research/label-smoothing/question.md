# Question: Label smoothing cho bộ phân loại ticket

| Field | Value |
|---|---|
| Date | 2026-11-10 |
| Owner | Minh (ML engineer) |
| Agent involvement | agent executes, human checks each stage |

## The question

Label smoothing (ε = 0,1) có tăng test accuracy của bộ phân loại ticket so với baseline không, ít nhất 1 điểm phần trăm?

## Why it is worth the time

Nếu có, team bật label smoothing cho bản huấn luyện hằng tuần. Nếu không, giữ nguyên cấu hình.

## What is already believed, and on what evidence

Một lần chạy thử trước đây (1 seed, không ghi log) cho thấy accuracy tăng. Chưa có số đo đáng tin.

## What would count as an answer

Chênh lệch test accuracy theo cặp seed, 5 seed, với khoảng tin cậy 95%.

## Out of scope

Calibration, các mô hình khác, các bộ dữ liệu khác.
