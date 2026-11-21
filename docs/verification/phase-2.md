# Ma trận kiểm chứng Phase 2

Các ID dưới đây do nhóm đặt, không phải mã chính thức của đề.

| ID nội bộ | Yêu cầu | Cách kiểm và bằng chứng | Trạng thái |
|---|---|---|---|
| Duy-P2-01 | Cá khởi tạo, bơi, đổi hướng, sinh và tất định | `tests/test_p2_duy.py`; `docs/proof/phase-2/duy/results.md` | Đạt test helper; chưa tích hợp Gather |
| Duy-P2-02 | Thu hoạch và kho 6 kind | test helper và `validate_items` trong `tests/test_p2_duy.py` | Đạt kiểm tra độc lập; chưa smoke 6 kind qua hai tiến trình |
| Duy-P2-03 | Dữ liệu v1.1 và đầu vào | test dữ liệu mẫu và scenario trong `tests/test_p2_duy.py` | Một phần; cần thêm kiểm tra và tích hợp validator các module khác |
| Duy-P2-04 | Hai tiến trình Gather → Quán | `tools/smoke_inventory.py`; proof Duy | Đạt với manifest P1 và fixture P1; chưa chứng minh P2 |
| Duy-P2-05 | Một ngày, hiệu năng, pause, quái và tích hợp | Chờ runner/DaySim/Gather P2 | Chưa kiểm chứng |
