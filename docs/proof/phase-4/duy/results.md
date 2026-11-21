# Bàn giao Duy Phase 4

## Kiểm tra bổ sung toàn bộ món

- `test_bot_serves_each_menu_dish_from_real_stock` tạo quán thực cho từng công thức trong menu, kho cá thể đúng công thức và một khách hợp lệ; bot điều khiển bếp/bàn qua input. Cả 6 món đều đi qua nấu, chín, lấy, phục vụ và thanh toán; đối chiếu nguyên liệu tiêu thụ với công thức.
- Regression sau bổ sung: `$env:PYTHONPATH='tests;.'; .\.venv\Scripts\python.exe -m unittest discover -s tests`: 269 test đạt, 23.154 giây. Các test hiện có kiểm riêng oxy/ngất (`test_p1_an.py`), quái (`test_p2_an_monsters.py`), pause và chuyển pha (`test_p2_an.py`, `test_p2_duc.py`), độ tươi và giữ nguyên liệu (`test_p3_an.py`, `test_p3_trung.py`), cá/kho (`test_p2_integration.py`, `test_p3_integration.py`), mua nâng cấp (`test_p2_duc.py`).
- Đây là độ bao phủ bằng nhiều test và fixture, không phải bằng chứng một lượt soak tự nhiên tạo đủ 6 món hay mọi nhánh gameplay. Bot soak hiện chỉ tự thu bông súng; cần mở rộng thu cá và các loại cây nếu muốn tự tạo mọi món trong một lượt.

## Kiểm tra lại trên main `a23b947` và thay đổi bot chưa commit

- Windows, Python `.venv` 3.11.9; hai lệnh `python -m chonoi.soak --seed 7 --days 10 --out ...` tạo `soak-1.json` và `soak-2.json`: mỗi lượt đủ 10 ngày, crashes 0; các trường gameplay giống nhau khi bỏ `duration_s`. Thời gian đo 7.755 và 7.670 giây khi chạy song song với test.
- Kiểm tra độc lập một lượt 10 ngày: 20 lần hái, 6 lần nấu, lấy món, phục vụ và thanh toán; 1 lần mua nâng cấp oxy. Kết quả cuối earned 252, reputation 4.2, score 652. Bot chưa khai thác mọi món hoặc tất cả cơ chế gameplay.
- `$env:PYTHONPATH='tests;.'; .\.venv\Scripts\python.exe -m unittest discover -s tests`: 268 test đạt trong 21.636 giây. `tools/smoke_inventory.py --require-v12`: PASS với contract 1.3.
- Bot sử dụng input bình thường: hái hai bông súng, phục vụ đơn khả dụng và mua một nâng cấp nếu đủ tiền. Không thay tuning hoặc state trực tiếp. Kết quả kiểm này cần chạy lại nếu code tích hợp thay đổi.

## Lịch sử trước tích hợp

Nền `04cd262` (có migration `5f9a0aa`); các thay đổi Duy chưa commit. Kiểm trên Windows, Python `.venv` 3.11.9, chạy ngoài sandbox.

- `$env:PYTHONPATH='tests;.'; .\.venv\Scripts\python.exe -m unittest discover -s tests`: 236 test đạt, 18.536 giây, manifest 1.2.
- `.\.venv\Scripts\python.exe tools/smoke_inventory.py --require-v12`: PASS, Gather → file → stock quán tick 0.
- `.\.venv\Scripts\python.exe -m chonoi.soak --seed 7 --days 10 --out docs/proof/phase-4/soak.json`: exit 1, `Session soak adapter is not integrated`; không tạo báo cáo giả.
- `test_p4_duy.py`: kiểm DaySim 10 ngày bằng fixture rút ngắn, kế hoạch D1–D5 lặp, ID mới, tiền/điểm và kết quả lúc đóng Shop. Test harness dùng adapter giả chỉ trong test và fixture rút ngắn; hai lượt cùng seed khớp gameplay. Đây không phải soak 10 ngày trên runtime tích hợp.
- `DaySim(..., soak=True)` cho phép ngày nguyên dương; mặc định vẫn giới hạn 5. `completed_results` lưu điểm tại Shop trước chuyển ngày. Cần Ân nối `Session(..., soak=True)` và `build_sim` vào DaySim, chỉ bật ở mode day; sau đó chạy lệnh soak thật hai lần và so toàn bộ trường gameplay trừ `duration_s`.
- WSL liệt kê duy nhất `docker-desktop`; chưa xác nhận môi trường Linux có GUI/browser và chưa có gói release ứng viên. Chưa kết luận clone sạch GUI.
- Bot dùng input hợp lệ: đi tới nút mặt nước đầu tiên, hái, về bến; chờ quán kết thúc và đóng Shop. Không rút ngắn tuning trong lệnh thật. Bot không kiểm chứng đầy đủ gameplay nấu/phục vụ hoặc mua nâng cấp.
