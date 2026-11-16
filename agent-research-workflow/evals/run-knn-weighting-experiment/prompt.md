---
tags: [skill-creator, doc-skills]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Mình nghĩ đổi k-NN từ vote đều sang vote theo khoảng cách (weighted) sẽ tăng accuracy cho bộ phân loại độ ưu tiên ticket. Code ở experiment.py, dữ liệu train.csv và test.csv. Mình đi họp 2 tiếng, bạn nghiên cứu và chạy thí nghiệm giúp mình rồi viết báo cáo, lúc về mình đọc. Dùng 10 seed (0–9). Nếu weighted tốt hơn thì tuần sau mình đổi production.

Input files: experiment.py, train.csv, test.csv
