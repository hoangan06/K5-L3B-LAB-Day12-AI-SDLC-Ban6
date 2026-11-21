# QA Phase 3 — Duy

Base `feb93a2`; thay đổi chưa commit. Kiểm trên Windows, Python `.venv` 3.11.9 ngoài sandbox.

- `$env:PYTHONPATH='tests;.'; .\.venv\Scripts\python.exe -m unittest discover -s tests`: 203 test, OK, **4 skipped** (test mới chờ manifest/runtime 1.2), 9.365 giây.
- `.\.venv\Scripts\python.exe tools/smoke_inventory.py`: PASS, contract 1.1, kho đếm từ gather đến stock quán tick 0.
- `.\.venv\Scripts\python.exe tools/smoke_inventory.py --require-v12`: exit 1, `FAIL: contract 1.2 required; current version is '1.1'`. Đây là kiểm tra điều kiện, không phải smoke P3 đạt.
- Test 1.2 kiểm file kho sai schema, ID trùng/rỗng, kind/fresh sai, hold/stock scenario sai, kho rỗng và precision 29.9999. Khi migration được tích hợp, chạy lại test và smoke; sửa lỗi runtime do Trung phụ trách.
- Chưa kiểm chứng ID trùng giữa hold và stock qua Day: theo giao diện P2/P3, day không nhận `quan.stock` trực tiếp; cần fixture/API migration thực tế để tạo hai vật chứa cùng tồn tại và phân biệt lỗi ID với lỗi trường cấm.
- Smoke 1.2 kiểm ID sort số, kind, fresh sau đúng một tick hao, event và stock tick 0 khớp file. Chưa thể xác nhận smoke 1.2 trước khi gói migration được tích hợp.
