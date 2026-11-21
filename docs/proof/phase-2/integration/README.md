# Kiểm chứng vòng chơi Phase 2

Gói review ghép manifest 1.1, GatherSim nhận context, cá/quái, kho sáu loại, input và Session cùng với UI của Đức. Runtime đọc dữ liệu trong bản mẫu Phase 2 nhóm đã chốt. Bản ghép để ở `p2/integration-duc`.

- `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v` đạt 127/127. Các test P1 giữ cấu hình 1.0 cho kiểm thử quán cũ. Smoke chạy theo phiên bản manifest với ba điểm đổi theo phase gồm số cá, mode `day` và input `attack`.
- `python3 tools/smoke_inventory.py` và `python3 tools/check_determinism.py` đạt. Smoke mới xác nhận sáu loại nguyên liệu truyền giữa hai tiến trình.
- Headless thực chạy đủ 5 ngày trên preset với `--ticks 111000`, kết thúc `days_complete`, `days_completed: 5`. Lượt fixture mua oxy và pause cũng kết thúc sau Shop ngày 5, xuất JSONL giống từng byte khi chạy lại.
- Chrome chạy từ menu đến tổng kết ngày 5 qua `python3 -m chonoi.live --mode day --days 5 --scenario <fixture>`. Fixture rút ngắn ca tối và có tiền ban đầu để kiểm cửa hàng. Dùng Session/Input thật, pause giữ nguyên timer, nâng cấp Oxy áp dụng từ ngày sau, HUD 18 px tại 1280 × 720. Console có 0 lỗi và 0 cảnh báo.

Ảnh kiểm [buổi sáng](hud-day.png), [Shop](hud-shop.png) và [tổng kết ngày 5](hud-summary.png).
