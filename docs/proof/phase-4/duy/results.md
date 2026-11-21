# Bàn giao Duy Phase 4

Nền `04cd262` (có migration `5f9a0aa`); các thay đổi Duy chưa commit. Kiểm trên Windows, Python `.venv` 3.11.9, chạy ngoài sandbox.

- `$env:PYTHONPATH='tests;.'; .\.venv\Scripts\python.exe -m unittest discover -s tests`: 236 test đạt, 18.536 giây, manifest 1.2.
- `.\.venv\Scripts\python.exe tools/smoke_inventory.py --require-v12`: PASS, Gather → file → stock quán tick 0.
- `.\.venv\Scripts\python.exe -m chonoi.soak --seed 7 --days 10 --out docs/proof/phase-4/soak.json`: exit 1, `Session soak adapter is not integrated`; không tạo báo cáo giả.
- `test_p4_duy.py`: kiểm DaySim 10 ngày bằng fixture rút ngắn, kế hoạch D1–D5 lặp, ID mới, tiền/điểm và kết quả lúc đóng Shop. Test harness dùng adapter giả chỉ trong test và fixture rút ngắn; hai lượt cùng seed khớp gameplay. Đây không phải soak 10 ngày trên runtime tích hợp.
- `DaySim(..., soak=True)` cho phép ngày nguyên dương; mặc định vẫn giới hạn 5. `completed_results` lưu điểm tại Shop trước chuyển ngày. Cần Ân nối `Session(..., soak=True)` và `build_sim` vào DaySim, chỉ bật ở mode day; sau đó chạy lệnh soak thật hai lần và so toàn bộ trường gameplay trừ `duration_s`.
- WSL liệt kê duy nhất `docker-desktop`; chưa xác nhận môi trường Linux có GUI/browser và chưa có gói release ứng viên. Chưa kết luận clone sạch GUI.
- Bot dùng input hợp lệ: đi tới nút mặt nước đầu tiên, hái, về bến; chờ quán kết thúc và đóng Shop. Không rút ngắn tuning trong lệnh thật. Bot không kiểm chứng đầy đủ gameplay nấu/phục vụ hoặc mua nâng cấp.
