# Bằng chứng chốt phát hành

- `tests.txt`: regression trên main965de6f (278test, khôngskip).
- `smoke.txt`, `determinism.txt`: kho/JSONL trên1.3.
- `bench.json`, `environment.json`: render gather1280×720, seed42, nóng3s/đo30s, hiệu ứng mặc định. `load_ms` đo từ Node process start qua Python/Chrome đến callback đã vẽ gather đầu; intro được bỏ qua, không tính FPS intro.
- `soak-1.json`, `soak-2.json`, `soak-check.json`: 10ngày một Session, so gameplay bỏ thời gian.
- `ui-check.json`, hai ảnh PNG: Chrome/input thật, fixture engine hợp lệ để tái hiện ba cảnh báo ở tương phản cao; không sửa snapshot, console0exception. Đã đọc ảnh để kiểm chữ rõ/không che cảnh báo.
- `clean-clone.json`, `package-check.json`: được tạo ở bước kiểm source sạch và ZIP cuối, ghi SHA nguồn/kiểm độc lập. Asset giữ hash source thực tế trong BUILD-INFO.

Giấy phép được chủ repo xác nhận **chưa công bố**. Đây là tình trạng đã rà/chốt, không phải giấy phép MIT hoặc một grant khác. Phản tư Duy còn thiếu, ghi thật trong ma trận/notes.
