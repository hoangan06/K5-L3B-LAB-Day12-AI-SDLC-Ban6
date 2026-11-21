# Kiểm chứng HUD độ tươi

Phạm vi theo mục Chung-P3-03 trong ma trận nhóm, dựa trên main 4ab6aa0. HUD đọc freshness.spoiled_below từ metadata live và hiển thị độ tươi theo ID. Kho khả dụng bỏ cá thể ươn và cá thể đang giữ. Giỏ và kho dạng đếm Phase 1–2 vẫn hiển thị.

- Test riêng API live đạt 2/2. Bộ test toàn repo ghi `Ran 201 tests in 6.143s OK`.
- Chrome dùng quán thật với fixture P3. Mục 30% vẫn hợp lệ và hiện nhãn Đã giữ. Mục 29.99% được đánh dấu Ươn. Chỉ mặt hàng chưa giữ và chưa ươn được tính vào kho khả dụng.
- Giỏ Phase 3 dùng snapshot mẫu trên Chrome. Trình duyệt xác nhận đánh dấu hàng ươn và giữ tương thích giỏ dạng chuỗi. Manifest runtime chưa chuyển sang 1.2 tại mốc kiểm.

[Kho](fresh-stock.png) · [Giỏ](fresh-hold.png)
