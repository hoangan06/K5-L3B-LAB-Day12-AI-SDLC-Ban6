# laitrongduc — phản tư cá nhân

- Phase 1: ghép luồng thanh toán, dọn món, bếp và HUD. Tôi rà thứ tự phục vụ và thanh toán ở tick đóng ca để mỗi khách chỉ phát một `paid`. [Bằng chứng](../proof/phase-1/duc/quan-and-hud.md)
- Phase 2: triển khai Day, Shop và giao diện chơi liên tục năm ngày. [Bằng chứng](../proof/phase-2/duc/day-shop-live.md)
- Phase 3: hiển thị độ tươi ở giỏ, kho và Shop. [Nhánh và bằng chứng](https://github.com/hoangan06/K5-L3B-LAB-Day12-AI-SDLC-Ban6/commit/004ab0abd7d9fdbd19a53f093797eb818b0eb205)
- Phase 4: chuẩn bị lệnh benchmark để Ân khai trong manifest, thêm ba cảnh báo và chế độ tương phản cao. [Commit triển khai](https://github.com/hoangan06/K5-L3B-LAB-Day12-AI-SDLC-Ban6/commit/4c03258) · [Bằng chứng](../proof/phase-4/duc/README.md)
- Lượt kiểm Phase 1 do Codex viết đọc sự kiện nấu quá sớm. Bản sửa chờ từng sự kiện từ snapshot. Bài học là kiểm các mốc giao giữa module bằng luồng chạy thật, đồng thời ghi rõ những lần dùng snapshot kiểm thử.
