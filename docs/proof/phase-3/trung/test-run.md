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
