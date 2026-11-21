# Bằng chứng P3 quán — Trung (nhánh `p3/trung`)

Ngày chạy: 2026-11-21. Tuning test = `docs/contracts/phase-2-tuning.sample.json` + `freshness {100, 0.5, 0.25, 30}` (TICKET-03).

| Lệnh | Kết quả |
|---|---|
| `PYTHONPATH=tests:. python3 -m unittest tests.test_p3_trung -v` | 25 test OK |
| `PYTHONPATH=tests:. python3 -m unittest discover -s tests` | 137 test OK (112 cũ + 25 mới) |
| `python3 docs/proof/phase-3/trung/mutate.py` | 24/26 CAUGHT |
| `python3 tools/check_determinism.py` | PASS (chạy kho đếm, chưa chạy v1.2) |
| `python3 tools/smoke_inventory.py` | PASS (kho đếm) |

Hai mutant lọt là tương đương: bỏ `raise` khi cấp `reserved` thiếu kho, hoặc bỏ kiểm dạng mảng `reserved` ở fixture, thì
`validate_quan_state` vẫn báo mã 2 (đơn reserved không khớp công thức / id không có trong kho).

Ghi chú trung thực:
- Test viết sau khi nối code; bằng chứng "đỏ" là mutation ở trên, không phải chạy test trước khi có code.
- Chưa chạy headless/CLI với contract v1.2: `scenario.py`, `inventory.py`, `runner.py`, manifest chưa lên v1.2 (không phải file của Trung).
- Chưa có HUD độ tươi (`chonoi/web/`). Chưa làm phần gather (decay 0.5/s, hold, LIFO).

## Migration v1.2 (cập nhật)

| Lệnh | Kết quả |
|---|---|
| `PYTHONPATH=tests:. python3 -m unittest discover -s tests` | 210 test OK |
| `python3 docs/proof/phase-3/trung/mutate.py` | 33/37 CAUGHT |
| `python3 tools/check_determinism.py` | PASS (v1.2) |
| `python3 tools/smoke_inventory.py` | PASS (v1.2, so id/kind/fresh) |
| `python3 -m chonoi.headless --mode day --days 5 --seed 1 --ticks 111000` ×2 | exit 0, `days_complete` 5, hai file giống từng byte (không input nên giỏ rỗng, không có `spoiled`) |
| Fixture `docs/contracts/phase-3-fixtures/*` của Ân | threshold: spoiled I1 tick 1; lifo: lost I7,I2,I10; dock: file kho → quán tick 0 khớp; sample: exit 0 |

Mutant lọt mới (tương đương):
- `items.py` bỏ kiểm `raw` là list: dict/số vẫn bị từ chối mã 2 ở bước kiểm từng cá thể.
- `day.py` bàn giao bằng `inventory_items()` (float sắp id) thay vì cá thể Fraction: `QuanSim` sắp theo id và `exact()` khôi phục đúng phân số k/240, nên kết quả như nhau.
Đã bỏ `_unique_item_ids` trong `scenario.py` vì không chạy tới được: scenario day đã từ chối `quan.stock`.
Test v1.2 cũng viết sau code; bằng chứng đỏ là mutation.
