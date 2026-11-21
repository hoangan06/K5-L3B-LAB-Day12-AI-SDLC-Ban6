# Ma trận kiểm chứng Phase 3

Các ID dưới đây do nhóm đặt, không phải mã chính thức của đề. Nguồn yêu cầu: TICKET-03 §1, Test Contract v1.2.
Tuning dùng để test phần quán: `docs/contracts/phase-2-tuning.sample.json` + `freshness {100, 0.5, 0.25, 30}`, vì manifest runtime còn v1.0.

| ID nội bộ | Yêu cầu | Cách kiểm và bằng chứng | Trạng thái |
|---|---|---|---|
| Trung-P3-01 | Kho quán là mảng cá thể `{id,kind,fresh}`; kho đếm dưới v1.2 → mã 2; snapshot `stock` gồm cả hàng ươn/đang giữ, sắp theo id | `tests/test_p3_trung.py` lớp `Snapshot`, `BadFixtures` | Đạt test với tuning mẫu; chưa chạy qua CLI (scenario/inventory/runner chưa nhận v1.2) |
| Trung-P3-02 | Hao 0.25/s ở kho quán kể cả hàng đang giữ, chặn ở 0; so ngưỡng chính xác (240 tick = −1) | lớp `Decay` (`test_exact_quarter_point_per_second`, `test_threshold_exact_no_float_drift`, `test_clamp_at_zero`) | Đạt test |
| Trung-P3-03 | `spoiled {item_id,kind,location:"stock"}` đúng một lần khi từ ≥ 30 xuống < 30, theo id | `test_spoiled_once_on_crossing_by_id` | Đạt test |
| Trung-P3-04 | Giữ theo id: tươi nhất, hòa id nhỏ; đơn thiếu `reserved` cấp theo (order_tick, id bàn); không giữ hàng ươn | lớp `Reserve` | Đạt test |
| Trung-P3-05 | Hàng giữ vừa ươn: nhả cả phần giữ, giữ lại đúng một lần theo (order_tick, id bàn); thiếu → `unfulfillable`, khách vẫn chờ | `test_spoiled_reservation_*`, `test_affected_orders_by_order_tick_then_table` | Đạt test |
| Trung-P3-06 | Bắt đầu nấu tiêu đúng id đã giữ; `base_price = floor(giá × fresh TB / 100)`; `cook_started.items` sắp kind rồi id | lớp `CookPrice` | Đạt test; tip tính trên giá đã chốt theo code P1 (`_serve` dùng `base_price` của món), chưa có test riêng cho tip P3 |
| Trung-P3-07 | Fixture `reserved` sai id / ươn / dùng chung / lệch công thức → mã 2 | `test_reserved_errors`, `test_missing_reserved_not_enough` | Đạt test |
| Trung-P3-08 | Kho đếm P1–P2 không đổi hành vi khi không có `freshness` | toàn bộ test cũ vẫn xanh | Đạt (193 test trên main `26e481a` + test 2 bếp, lúc ghi) |
| Chung-P3-01 | Gather: hold cá thể, hao 0.5/s, `spoiled` location `hold`, `lost` LIFO | — | Chưa kiểm chứng (chưa có code) |
| Chung-P3-02 | Manifest `contract_version 1.2`, scenario/inventory/runner đọc kho cá thể, id I1… tăng qua pha và ngày | — | Chưa kiểm chứng (chưa có code) |
| Chung-P3-03 | HUD hiện độ tươi hoặc hàng ươn | — | Chưa kiểm chứng (đang làm giao diện) |
| Duy-P3-01 | File kho, hold và stock từ chối schema sai, ID trùng/rỗng, kind/fresh sai trước output; chấp nhận kho rỗng và giữ precision | `tests/test_p3_duy.py`; `docs/proof/phase-3/duy/results.md` | Đã viết test; 4 test bỏ qua vì runtime còn 1.1, chưa xác nhận 1.2 |
| Duy-P3-02 | Gather → file → quán tick 0 giữ ID/kind/fresh | `python3 tools/smoke_inventory.py --require-v12`; proof Duy | Chưa đạt: manifest hiện 1.1; smoke 1.1 đạt |
| Duy-P3-03 | ID vật lý trùng giữa hold và stock | Cần fixture tích hợp với migration Day thực tế | Chưa kiểm chứng; scenario day không cho quan.stock riêng |

Mutation phần quán: `python3 docs/proof/phase-3/trung/mutate.py` bắt 24/26; 2 mutant lọt là tương đương (`docs/proof/phase-3/trung/test-run.md`).
