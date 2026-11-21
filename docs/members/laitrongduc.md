# laitrongduc — phản tư cá nhân Phase 1

- Phần tôi phụ trách gồm [thanh toán và dọn món](https://github.com/hoangan06/K5-L3B-LAB-Day12-AI-SDLC-Ban6/commit/ca47bfc), [bếp và phục vụ](https://github.com/hoangan06/K5-L3B-LAB-Day12-AI-SDLC-Ban6/commit/c2649df), [HUD và hướng dẫn chơi](https://github.com/hoangan06/K5-L3B-LAB-Day12-AI-SDLC-Ban6/commit/0b039f4).
- Phần rà khi tích hợp là thứ tự xử lý khách ở tick đóng ca. Hai test chạy qua `Session` xác nhận khách ăn xong dùng `finished_eating`, còn khách vừa được phục vụ dùng `closing`. Mỗi khách chỉ phát một `paid`. [Bằng chứng](../proof/phase-1/duc/quan-and-hud.md)
- Lượt kiểm Playwright đầu do Codex viết đọc sự kiện quá sớm. Mô phỏng mới ghi `cook_started` khi script đã kiểm thanh toán. Lượt sau chờ từng sự kiện trong snapshot và ghi nhận đầy đủ luồng quán.
- Bài học từ lần tích hợp này là kiểm thử các mốc chung giữa module bằng luồng chạy thật. Một test helper độc lập khó phát hiện hai bước thay đổi sai thứ tự ở cùng tick.
