# Bàn giao Phase 2 của Đức

Nhánh `p2/duc` bắt đầu từ `a813811`, dùng giao diện Phase 2 và tuning mẫu của nhóm. `DaySim` điều phối ba pha qua `resolve_day_plans` và truyền `allowed_dishes` cho `QuanSim`. `ShopSim` xử lý tiền, cấp nâng cấp và thời điểm đóng cửa hàng. `live.py` gọi `Session(..., days=N)` và xử lý màn trình bày; pause đi qua input của Session.

- `PYTHONPATH=tests:. python3 -m unittest discover -s tests -p test_p2_duc.py -v` đạt 9/9. Test bao gồm mua vừa đủ giá, lỗi mua, ưu tiên mua trước đóng cửa, chuyển pha cùng tick, áp cấp từ ngày sau và kết thúc sau Shop ngày 5.
- `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v` đạt 121/121 trong checkout bàn giao.
- Chrome ở 1280 × 720 đã kiểm từ menu tới tổng kết 5 ngày, pause giữ nguyên timer, HUD 18 px và mua Oxy áp dụng ở ngày sau. Lượt chơi dùng máy chủ live thật và DaySim, QuanSim, ShopSim thật. Session, input và phần context của GatherSim được thay bằng bộ hỗ trợ kiểm thử tạm để thử giao diện trong khi chờ API của Ân.
- Ảnh kiểm [HUD buổi sáng](hud-day.png), [cửa hàng](hud-shop.png) và [tổng kết ngày 5](hud-summary.png).

Còn cần chạy `python3 -m chonoi.live --mode day --days 5` và headless qua Session/Inputs Phase 2 thật, sau khi manifest và GatherSim nhận context được ghép đồng bộ. Checkout hiện tại vẫn dùng manifest v1.0.
