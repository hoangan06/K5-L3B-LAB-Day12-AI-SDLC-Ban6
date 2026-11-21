# Changelog
## Unreleased

### Phase 3 — quán (Trung)
- Kho quán theo cá thể `{id, kind, fresh}` khi tuning có khối `freshness` (contract v1.2); không có thì giữ kho đếm P1–P2.
- Hao tươi 0.25/s ở kho quán (kể cả hàng đang giữ), chặn ở 0; event `spoiled` (location `stock`) đúng một lần khi qua ngưỡng 30, theo id.
- Giữ chỗ theo id: tươi nhất rồi id nhỏ; cá thể giữ vừa ươn → nhả và giữ lại một lần theo (order_tick, id bàn), thiếu → `unfulfillable`.
- Bắt đầu nấu tiêu đúng id đã giữ; `base_price = floor(giá × fresh trung bình / 100)`; `cook_started.items` là mảng cá thể theo kind rồi id.
- Kiểm fixture v1.2: kho đếm, id trùng/rỗng, kind lạ, fresh ngoài [0,100], `reserved` sai/ươn/dùng chung/lệch công thức → mã 2.
- Ảnh hưởng: snapshot `stock` và `customers[].reserved` đổi schema khi chạy v1.2. Chưa đổi: `chonoi/scenario.py` (vẫn kiểm `quan.stock` dạng đếm), `inventory.py`/`runner.py` (đọc kho v1.2), HUD.
