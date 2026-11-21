# Bàn giao Duy Phase 4

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
