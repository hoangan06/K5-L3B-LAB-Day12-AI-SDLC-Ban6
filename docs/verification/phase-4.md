# Ma trận kiểm chứng Phase 4

Cập nhật rà cuối của Ân: [docs/proof/final-an](../proof/final-an/README.md) có288test đạt, replay sai điểm đã hết, schema/ID/HUD và TEAM/phản tư Ân được sửa. Bảng dưới giữ bằng chứng lịch sử bản dbe6d20; bản nộp cuối thay thế được kiểm lại tại docs/proof/final-an/. Bench đo lại sau đổi HUD, soak chạy hai lần cho gameplay giống nhau. Gói mới có package-check.json riêng trên Release với SHA nguồn sạch trùng tag. Phản tư/AI log của thành viên khác vẫn do từng người bổ sung.

AC-P4-xx là mã nội bộ của nhóm. Nền gameplay kiểm: main `965de6f`; kiểm chốt trên clone GitHub sạch `9d4b639` (279test). Thay đổi sau đó chỉ tài liệu/bằng chứng, không sửa code. Bằng chứng mới ở `docs/proof/phase-4/release/`, thay cho báo cáo nhánh cũ. Asset cuối dựng lại từ SHA gắn tag, kèm package-check.json riêng trên Release.

| Mã | Bằng chứng / cách kiểm | Kết quả |
|---|---|---|
| AC-P4-01 | game.contract.json1.3; bench_cmd và soak_cmd chạy thật | Đạt; bench.json, soak-1.json |
| AC-P4-02 | node tools/bench.mjs --seed42 --duration30; 1280×720, nóng3s; tính load từ khởi chạy đến frame gather đầu; bỏ intro | Đạt từ clone9d4b639; bench.json, environment.json; avg119.94FPS, low95.21FPS, load701.6ms. Lượt trước ~60FPS giữ ở bench-initial.json; không cam kết FPS mọi máy |
| AC-P4-03 | tools/verify_release_ui.mjs; engine fixture hợp lệ, mouse/key thật; không thay snapshot | Đạt; ui-check.json, gather-warnings.png, customer-warning.png; tương phản cao, 3cảnh báo, 0exception |
| AC-P4-04 | README3lệnh; clone sạch, kiểm ZIP giải nén độc lập, GUI/HTTP và Chrome | Đạt trên Linux WSL; clean-clone.json/package-check.json: source sạch9d4b639, import độc lập, canvas/menu HTTP. Clone tạo bởi Git Windows rồi đọc bằng WSL, đã đồng bộ core.autocrlf; không sửa source |
| AC-P4-05 | python3 -m chonoi.soak --seed7 --days10 chạy2lần, so gameplay bỏ duration_s | Đạt; soak-check.json; 10/10ngày, 0crash, 10results, gameplay giống nhau |
| AC-P4-06 | unittest discover; smoke_inventory --require-v12; check_determinism | Đạt: 279test không skip trên clone9d4b639 (final-tests.txt); 278test trước thêm ca giấy phép trên965de6f (tests.txt); smoke.txt/determinism.txt |
| AC-P4-07 | ZIP + hash; release notes, CHANGELOG/CREDITS; chủ repo xác nhận giấy phép chưa công bố; tag/Release cùngmainSHA | Gói nguồn sạch đạt kiểm (package-check.json); tag phase-4/v1.0.0 cùng SHA main, asset cuối kiểm lại trước công bố. Giấy phép chưa công bố là quyết định đã ghi nhận, không giả có LICENSE |
| AC-P4-08 | docs/retro.md đã rà hành động P2, AI log và clarify cập nhật; phản tư cá nhân | Đạt phần retro/log; phản tư có Ân/Đức/Trung, còn thiếu file tự phản tư của Duy. Không kết luận đầy đủ phần phản tư |

Lệnh trong bảng viết gọn; cú pháp có khoảng trắng đầy đủ nằm trong release notes/README và log. Kiểm UI là kiểm tự động bằng scenario, không nhận là chơi tay. Các mục quy trình còn thiếu được ghi trong release notes, không đổi thành PASS giả.
