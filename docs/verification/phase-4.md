# Ma trận kiểm chứng Phase 4

AC-P4-xx là mã nội bộ của nhóm. Nền gameplay kiểm: main `965de6f`; thay đổi sau đó sửa benchmark/công cụ đóng gói và tài liệu, không sửa luật Python. Bằng chứng mới ở `docs/proof/phase-4/release/`, thay cho các báo cáo nhánh cũ. SHA clean-clone/gói được ghi trong JSON kiểm cuối và BUILD-INFO của asset.

| Mã | Bằng chứng / cách kiểm | Kết quả |
|---|---|---|
| AC-P4-01 | game.contract.json1.3; bench_cmd và soak_cmd chạy thật | Đạt; bench.json, soak-1.json |
| AC-P4-02 | node tools/bench.mjs --seed42 --duration30; 1280×720, nóng3s; tính load từ khởi chạy đến frame gather đầu; bỏ intro | Đạt; bench.json, environment.json; avg60.00FPS, low57.75FPS, load828.3ms |
| AC-P4-03 | tools/verify_release_ui.mjs; engine fixture hợp lệ, mouse/key thật; không thay snapshot | Đạt; ui-check.json, gather-warnings.png, customer-warning.png; tương phản cao, 3cảnh báo, 0exception |
| AC-P4-04 | README3lệnh; clone sạch, kiểm ZIP giải nén độc lập, GUI/HTTP và Chrome | Bước chốt: clean-clone.json/package-check.json; chỉ ghi Đạt sau khi các file kiểm được tạo |
| AC-P4-05 | python3 -m chonoi.soak --seed7 --days10 chạy2lần, so gameplay bỏ duration_s | Đạt; soak-check.json; 10/10ngày, 0crash, 10results, gameplay giống nhau |
| AC-P4-06 | unittest discover; smoke_inventory --require-v12; check_determinism | Đạt trên nền965de6f: 278test, không skip; tests.txt, smoke.txt, determinism.txt; test đóng gói chạy lại khi sửa công cụ |
| AC-P4-07 | ZIP + hash; release notes, CHANGELOG/CREDITS; chủ repo xác nhận giấy phép chưa công bố; tag/Release cùngmainSHA | Gói/tag/Release được chốt sau kiểm; trạng thái giấy phép ghi thật trong docs/licensing-status.md |
| AC-P4-08 | docs/retro.md đã rà hành động P2, AI log và clarify cập nhật; phản tư cá nhân | Đạt phần retro/log; phản tư có Ân/Đức/Trung, còn thiếu file tự phản tư của Duy. Không kết luận đầy đủ phần phản tư |

Lệnh trong bảng viết gọn; cú pháp có khoảng trắng đầy đủ nằm trong release notes/README và log. Kiểm UI là kiểm tự động bằng scenario, không nhận là chơi tay. Các mục quy trình còn thiếu được ghi trong release notes, không đổi thành PASS giả.
