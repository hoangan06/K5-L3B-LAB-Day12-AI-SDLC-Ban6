# Bằng chứng chốt phát hành

- `tests.txt`: regression trên main965de6f (278test, khôngskip).
- `final-tests.txt`: regression trên clone GitHub sạch9d4b639, 279test đạt, khôngskip (có thêm kiểm không tự tạo LICENSE).
- `smoke.txt`, `determinism.txt`: kho/JSONL trên1.3.
- `bench.json`, `environment.json`: render gather1280×720, seed42, nóng3s/đo30s, hiệu ứng mặc định. `load_ms` đo từ Node process start qua Python/Chrome đến callback đã vẽ gather đầu; intro được bỏ qua, không tính FPS intro.
- Bench cuối chạy lại từ clone sạch9d4b639: 3599frame/30.0078s, avg119.94FPS; lượt đầu khoảng60FPS được giữ ở bench-initial.json. Số đo RAF phụ thuộc lịch trình/thiết bị host, không sửa kết quả để đạt mốc.
- `soak-1.json`, `soak-2.json`, `soak-check.json`: 10ngày một Session, so gameplay bỏ thời gian.
- `ui-check.json`, hai ảnh PNG: Chrome/input thật, fixture engine hợp lệ để tái hiện ba cảnh báo ở tương phản cao; không sửa snapshot, console0exception. Đã đọc ảnh để kiểm chữ rõ/không che cảnh báo.
- `clean-clone.json`, `package-check.json`: kiểm clone/ZIP nguồn sạch9d4b639, GUI/HTTP Linux WSL, không cần cài package. Git Windows tạo clone CRLF, đặt core.autocrlf=true trong clone để WSL đọc đúng, không thay source. Asset phát hành dựng lại từ SHA tag và có package-check.json riêng; BUILD-INFO giữ hash thực tế.

Giấy phép được chủ repo xác nhận **chưa công bố**. Đây là tình trạng đã rà/chốt, không phải giấy phép MIT hoặc một grant khác. Phản tư Duy còn thiếu, ghi thật trong ma trận/notes.
