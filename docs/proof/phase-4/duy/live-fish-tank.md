# Kiểm tra bể cá bản chơi trực tiếp

- Nền `c5de54e` và thay đổi chưa commit; Python `.venv` 3.11.9 trên Windows.
- `PYTHONPATH=tests;. python -m unittest discover -s tests`: 277 test đạt trước khi bổ sung test lấy cá từ bể.
- `python -m unittest discover -s tests -p test_live_fish_tank.py -v`: 4 test đạt, gồm hao tươi giỏ/kho, cá qua ngưỡng 30 không ươn trong bể, lấy cá ra nấu và restart.
- `python tools/smoke_inventory.py --require-v12`: PASS với contract 1.3. JavaScript nội tuyến được Node kiểm tra cú pháp; chưa kiểm tra trực quan trong trình duyệt.
- Luật bản live dùng hệ số 0.5 trong `chonoi/live_rules.json`, áp cho giỏ và kho. Cá trong kho quán tự vào bể không giới hạn và giữ nguyên mức tươi khi vào, không hồi tươi; headless giữ tuning contract.
