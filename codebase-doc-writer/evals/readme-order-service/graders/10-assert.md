---
type: llm
focus: trace
weight: 1
---

README nêu ít nhất một lỗi phát hiện từ logic code (không chỉ chép TODO/FIXME): ghi DB và push Redis không atomic, race giữa cancel và worker confirm, worker mất message khi crash (BRPOP), hoặc lỗi kết nối SMTP (OSError) không được retry
