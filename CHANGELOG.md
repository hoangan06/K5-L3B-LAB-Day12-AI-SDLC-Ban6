# Changelog
## v1.0.0 — 2026-11-21

### Phase 4 — phát hành
- Contract1.3 giữ gameplay/kho P3; khai bench_cmd và soak_cmd. Session có đường soak riêng, CLI chơi chuẩn giữ1–5ngày.
- Soak10ngày một tiến trình, kế hoạch lặp D1–D5, trạng thái/ID nối tiếp; bot thật hái/nấu/phục vụ/thu tiền.
- Bench render1280×720, nóng3s/đo30s; bỏ intro và đo load từ khởi chạy đến frame gather đầu. Cảnh báo chữ/biểu tượng và tương phản cao.
- ZIP source portable, hash nội dung, kiểm clone sạch và GUI độc lập; bằng chứng chốt tại docs/proof/phase-4/release/.
- Chủ repo xác nhận chưa công bố giấy phép; ghi nhận trong docs/licensing-status.md, không tự gán MIT.

### Phase 2 — vòng ngày
- DayIntro → gather → EveningIntro → quan → DayResult → Shop → ngày tiếp, đủ5ngày; menu6món, 2bếp/4bàn, kế hoạch ngày và nâng cấp.
- Session dùng chung live/headless, pause trước gameplay; cá bơi/sinh và Cá Sấu tuần tra/đuổi/chạm.

### Phase 1 — lõi
- Lặn/hái/bắt cá, oxy/ngạt/ngất, giỏ, cập bến và bàn giao kho; quán gọi món/giữ chỗ/nấu/phục vụ/thu tiền/uy tín.
- CLI tất định, scenario/input/JSONL, test và ma trận kiểm chứng theo phase.

### Phase 3 — migration Contract v1.2 (Trung) — BREAKING
- `game.contract.json` lên `contract_version "1.2"`, thêm `tuning.freshness {initial 100, gather_decay_per_s 0.5, quan_decay_per_s 0.25, spoiled_below 30}`. Loader nhận 1.0/1.1/1.2; 1.2 bắt buộc có `freshness`.
- **Kho đếm → kho cá thể**: file kho, `gather_end.inventory`, snapshot `hold`/`stock`, `faint.lost`, `monster_hit.lost` là mảng `{id,kind,fresh}`. File kho đếm dưới 1.2 → mã 2. Module chung `chonoi/items.py` (kiểm schema, Fraction chính xác, hao, `spoiled`); `quan_fresh.py` dùng lại cùng hàm hao.
- Gather: hàng có sẵn đầu bước hao 0.5/s (sau `node_regrown`), `spoiled` location `hold` theo id; hái/bắt tạo cá thể mới id `I…` fresh 100, hao từ bước sau; `lost` theo thứ tự LIFO của giỏ; snapshot `hold` giữ thứ tự giỏ, file/`gather_end` sắp theo id.
- Day: bàn giao gather→quán cùng tick giữ nguyên id/fresh chính xác, không hao thêm; Ngày >1 cấp id mới cho mẫu hold theo thứ tự mảng. Shop giữ kho cá thể, không hao.
- Scenario v1.2: `gather.hold`/`quan.stock` là mảng cá thể (kiểm sức chứa theo số cá thể).
- Test P1–P2 dùng kho đếm chuyển sang fixture manifest cũ (`tests/fixtures/phase-1/`, `tests/fixtures/phase-2/`) vì luật kho đếm vẫn đúng ở version đó; test CLI đọc version manifest (`helpers.v12()`). `tools/smoke_inventory.py`, `tools/check_determinism.py` nhận kho cá thể. Test mới: `tests/test_p3_integration.py`.
- Đã sửa ở `04cd262`: JSONL giữ đủ precision riêng trường fresh; tọa độ/số thực khác giữ quy tắc xuất3chữ số. File kho và JSONL không đổi phía ngưỡng30 khi bàn giao.

### Phase 3 — quán (Trung)
- Kho quán theo cá thể `{id, kind, fresh}` khi tuning có khối `freshness` (contract v1.2); không có thì giữ kho đếm P1–P2.
- Hao tươi 0.25/s ở kho quán (kể cả hàng đang giữ), chặn ở 0; event `spoiled` (location `stock`) đúng một lần khi qua ngưỡng 30, theo id.
- Giữ chỗ theo id: tươi nhất rồi id nhỏ; cá thể giữ vừa ươn → nhả và giữ lại một lần theo (order_tick, id bàn), thiếu → `unfulfillable`.
- Bắt đầu nấu tiêu đúng id đã giữ; `base_price = floor(giá × fresh trung bình / 100)`; `cook_started.items` là mảng cá thể theo kind rồi id.
- Kiểm fixture v1.2: kho đếm, id trùng/rỗng, kind lạ, fresh ngoài [0,100], `reserved` sai/ươn/dùng chung/lệch công thức → mã 2.
- Ảnh hưởng: snapshot `stock` và `customers[].reserved` đổi schema khi chạy v1.2 (scenario/inventory đã nối ở mục migration trên).
