# Ma trận kiểm chứng Phase 2

Các ID dưới đây do nhóm đặt, không phải mã chính thức của đề.

| ID nội bộ | Yêu cầu | Cách kiểm và bằng chứng | Trạng thái |
|---|---|---|---|
| Duy-P2-01 | Cá khởi tạo, bơi, đổi hướng, sinh và tất định | `tests/test_p2_duy.py`; `docs/proof/phase-2/duy/results.md` | Đạt test helper; chưa tích hợp Gather |
| Duy-P2-02 | Thu hoạch và kho 6 kind | test helper và `validate_items` trong `tests/test_p2_duy.py` | Đạt kiểm tra độc lập; chưa smoke 6 kind qua hai tiến trình |
| Duy-P2-03 | Dữ liệu v1.1 và đầu vào | test dữ liệu mẫu và scenario trong `tests/test_p2_duy.py` | Một phần; cần thêm kiểm tra và tích hợp validator các module khác |
| Duy-P2-04 | Hai tiến trình Gather → Quán | `tools/smoke_inventory.py`; proof Duy | Đạt với manifest P1 và fixture P1; chưa chứng minh P2 |
| Duy-P2-05 | Một ngày, hiệu năng, pause, quái và tích hợp | Chờ runner/DaySim/Gather P2 | Chưa kiểm chứng |
| Trung-P2-01 | Kế hoạch ngày D1–D5: ingredients = dishes × công thức, override theo ngày, sai → mã 2 | `tests/test_p2_trung.py` lớp `DayPlan` (6 test, đối chiếu bảng TICKET-02 §2); `docs/proof/phase-2/trung/test-run.md` | Đạt test với tuning mẫu P2; chưa chạy qua manifest runtime (còn v1.0) |
| Trung-P2-02 | Quán 2 bếp, 4 bàn, 6 món; khách vào bàn theo id; lọc món theo kế hoạch trước khi xét kho | `tests/test_p2_trung.py` lớp `QuanP2`, `TwoStoves` (2 bếp lấy 2 đơn cũ nhất, khác nhau; test đỏ khi bỏ sắp theo order_tick) | Đạt test với tuning mẫu P2 |
| Trung-P2-03 | `QuanSim(context)`: tiền/earned/uy tín lấy từ context, không sửa context, cấm `quan.stock`/`reputation` trong scenario khi chạy day | `tests/test_p2_trung.py` lớp `QuanSimContext`; mutation `docs/proof/phase-2/trung/mutate.py` 16/16 | Đạt test riêng; Đức đã gọi từ `DaySim` (`tests/test_p2_duc.py`); chưa chạy `--mode day` thật vì manifest còn v1.0 (mã 2) |
