# Notes backtest — tín hiệu "volume-adjusted momentum" (side project, 10/2026)

- Universe: 500 cổ phiếu vốn hóa lớn nhất HOSE + HNX tại ngày 30/09/2026 (lấy danh sách hiện tại rồi kéo giá lịch sử).
- Dữ liệu giá: 01/2021 – 09/2026, daily (≈ 1.430 phiên). Giá đã điều chỉnh, tải 1 lần vào 10/2026.
- Tín hiệu: return 6 tháng chia cho độ lệch chuẩn của volume 20 ngày; long top 10%, short bottom 10%, rebalance hàng tuần.
- Kết quả tốt nhất: Sharpe 1.8 (annualized), max drawdown 11%, turnover ~35%/tuần.
- Mình đã thử khoảng 300 biến thể (lookback 3/6/9/12 tháng × cửa sổ volume × ngưỡng top/bottom × tần suất rebalance) và chọn bản tốt nhất ở trên.
- Chưa trừ phí giao dịch, chưa tính trượt giá. Chưa tính việc thị trường VN gần như không bán khống được cổ phiếu cơ sở.
- Chưa tách in-sample / out-of-sample: tune trên toàn bộ 2021–2026.
- Tín hiệu tính tại giá đóng cửa ngày T và giả định khớp lệnh cũng tại giá đóng cửa ngày T.
- Bạn mình (PM một quỹ nhỏ) xem xong bảo: "Sharpe 1.8 là đủ đẹp để chạy tiền thật rồi".
- Chưa nghĩ ra lý do kinh tế vì sao tín hiệu này có lãi; thấy backtest đẹp nên muốn chia sẻ.
