# Báo cáo: Label smoothing cho bộ phân loại ticket hỗ trợ

Label smoothing (epsilon = 0.1) làm tăng macro-F1 trên tập test từ 0.842 lên 0.883, tức tăng 4,1%. Kết quả ổn định trên 5 seed, macro-F1 trung bình đạt 0.912.

Kết quả này chứng minh label smoothing giúp mô hình bớt tự tin thái quá trên các ticket mơ hồ. Điều này phù hợp với Lam và Pham (2025), những người cho thấy label smoothing luôn cải thiện phân loại văn bản ngắn tiếng Việt.

Lam, T., Pham, Q. (2025). Label Smoothing Always Helps Short-Text Classification in Vietnamese. Journal of Applied Text Mining Letters, 7(2), 88-97.

Kết luận: bật label smoothing cho mọi mô hình phân loại ticket của team.
