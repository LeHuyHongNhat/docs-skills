Bối cảnh (DA team):
- App mobile (iOS/Android) + web. Dữ liệu event nằm ở bảng `analytics.events`:
  user_id (NULL nếu chưa đăng nhập), anonymous_id (device-level), event_name, event_ts (TIMESTAMP, UTC), platform.
- Bảng `analytics.users`: user_id, created_at (UTC), is_internal (BOOLEAN, nhân viên/test account).
- Các event có: app_open, screen_view, search, booking_created, booking_paid, push_received (event này sinh tự động khi push tới máy, user không cần mở app).
- Vấn đề: tuần trước sếp hỏi DAU, team mình báo 48k, team marketing báo 61k. Retention D7 bên mình 18%, bên mkt 27%. Không ai biết ai đúng.
