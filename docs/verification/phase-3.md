# Ma trận kiểm chứng Phase 3

Các ID dưới đây do nhóm đặt, không phải mã chính thức của đề. Nguồn yêu cầu: TICKET-03 §1, Test Contract v1.2.
Test phần quán (`test_p3_trung.py`) dùng `docs/contracts/phase-2-tuning.sample.json` + `freshness`; test tích hợp (`test_p3_integration.py`) dùng manifest runtime v1.2.

| ID nội bộ | Yêu cầu | Cách kiểm và bằng chứng | Trạng thái |
|---|---|---|---|
| Trung-P3-01 | Kho quán là mảng cá thể `{id,kind,fresh}`; kho đếm dưới v1.2 → mã 2; snapshot `stock` gồm cả hàng ươn/đang giữ, sắp theo id | `tests/test_p3_trung.py` lớp `Snapshot`, `BadFixtures` | Đạt test; qua CLI v1.2: xem Chung-P3-02 |
| Trung-P3-02 | Hao 0.25/s ở kho quán kể cả hàng đang giữ, chặn ở 0; so ngưỡng chính xác (240 tick = −1) | lớp `Decay` (`test_exact_quarter_point_per_second`, `test_threshold_exact_no_float_drift`, `test_clamp_at_zero`) | Đạt test |
| Trung-P3-03 | `spoiled {item_id,kind,location:"stock"}` đúng một lần khi từ ≥ 30 xuống < 30, theo id | `test_spoiled_once_on_crossing_by_id` | Đạt test |
| Trung-P3-04 | Giữ theo id: tươi nhất, hòa id nhỏ; đơn thiếu `reserved` cấp theo (order_tick, id bàn); không giữ hàng ươn | lớp `Reserve` | Đạt test |
| Trung-P3-05 | Hàng giữ vừa ươn: nhả cả phần giữ, giữ lại đúng một lần theo (order_tick, id bàn); thiếu → `unfulfillable`, khách vẫn chờ | `test_spoiled_reservation_*`, `test_affected_orders_by_order_tick_then_table` | Đạt test |
| Trung-P3-06 | Bắt đầu nấu tiêu đúng id đã giữ; `base_price = floor(giá × fresh TB / 100)`; `cook_started.items` sắp kind rồi id | lớp `CookPrice` | Đạt test; tip tính trên giá đã chốt theo code P1 (`_serve` dùng `base_price` của món), chưa có test riêng cho tip P3 |
| Trung-P3-07 | Fixture `reserved` sai id / ươn / dùng chung / lệch công thức → mã 2 | `test_reserved_errors`, `test_missing_reserved_not_enough` | Đạt test |
| Trung-P3-08 | Kho đếm P1–P2 không đổi hành vi khi không có `freshness` | toàn bộ test cũ vẫn xanh | Đạt (193 test trên main `26e481a` + test 2 bếp, lúc ghi) |
| Chung-P3-01 | Gather: hold cá thể, hao 0.5/s, `spoiled` location `hold`, `lost` LIFO | `tests/test_p3_integration.py` lớp `GatherFresh`; fixture của Ân `docs/contracts/phase-3-fixtures/gather-threshold.json` (spoiled I1 tick 1), `gather-lifo.json` (lost I7, I2, I10) chạy headless | Đạt test; test riêng của Ân (`test_p3_an.py`) chưa có |
| Chung-P3-02 | Manifest `contract_version 1.2`, scenario/inventory/runner đọc kho cá thể, id I1… tăng qua pha và ngày | lớp `Manifest`, `FileHandoff` (kho đếm/schema sai → mã 2, ngưỡng qua file), `DayHandoff` (cùng tick không hao thêm, Ngày 2 id I3/I4); `gather-dock.json`+`dock-inputs.json` → quán tick 0 khớp; `tools/smoke_inventory.py` PASS; day 5 ngày headless ×2 giống từng byte | Đạt; live day trên trình duyệt với v1.2 chưa chạy (UNVERIFIED) |
| Chung-P3-03 | HUD hiện độ tươi hoặc hàng ươn | — | Chưa kiểm chứng (đang làm giao diện) |

Mutation (quán + migration v1.2): `python3 docs/proof/phase-3/trung/mutate.py` bắt 33/37; 4 mutant lọt là tương đương (`docs/proof/phase-3/trung/test-run.md`).
