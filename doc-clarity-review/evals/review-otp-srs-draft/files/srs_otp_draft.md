# SRS – Xác thực OTP khi đăng nhập (draft v0.3)

## 1. Mục tiêu
Tính năng này giúp giảm 40% số tài khoản bị chiếm đoạt và mang lại trải nghiệm liền mạch cho khách hàng.

## 2. Quy tắc chung
- OTP gồm 6 chữ số, có hiệu lực trong 5 phút kể từ khi gửi.
- Người dùng nhập sai OTP quá nhiều lần sẽ bị khóa.
- Ngưỡng rate limit gửi OTP: TBD.

## 3. Yêu cầu chức năng
- FR-001. Khi người dùng nhấn **Gửi mã**, hệ thống phải gửi OTP 6 chữ số tới số điện thoại đã đăng ký của tài khoản.
- FR-002. Hệ thống phải gửi OTP nhanh chóng.
- FR-003. Hệ thống hỗ trợ gửi OTP qua SMS, Email, Zalo, v.v.
- FR-004. Người dùng có thể yêu cầu gửi lại OTP.
- FR-004. Dữ liệu OTP được lưu và mã hóa.
- FR-005. Khi user nhập OTP sai, nó sẽ hiển thị thông báo lỗi phù hợp.
- FR-006. Hệ thống phải ghi log mỗi lần xác thực OTP gồm các trường user_id, kết quả (thành công/thất bại), thời điểm (ISO 8601, UTC).

## 4. Acceptance Criteria
- AC-001: Given khách hàng đã nhận OTP, When nhập đúng OTP trong vòng 3 phút, Then đăng nhập thành công.
- AC-002: Given OTP đã được gửi quá 3 phút, When người dùng nhập OTP đó, Then hệ thống từ chối.
