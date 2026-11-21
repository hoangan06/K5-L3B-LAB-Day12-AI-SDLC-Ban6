# Dòng đề xuất cho `docs/verification/phase-1.md` (Duy chép sang nếu đồng ý)

Kiểm lại trên `main` `4229ebf` (2026-11-21): `PYTHONPATH=tests:. python3 -m unittest discover -s tests` → 112 OK; `tools/check_determinism.py` PASS; `tools/smoke_inventory.py` PASS.

| AC | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| Nội bộ TRUNG-01: khách đến theo lịch, giữ chỗ, kiên nhẫn, rời bàn, đóng ca | `PYTHONPATH=tests:. python3 -m unittest tests.test_p1_trung -v` (18 test) + `python3 docs/proof/phase-1/trung/mutate.py` | `docs/proof/phase-1/trung/test-run.md` | Đạt trên commit P1 (13/13 mutation bị bắt) |
| Nội bộ TRUNG-02: kiểm fixture quán (mã 2 trước output), theo chốt Q1–Q8 | như trên | `docs/proof/phase-1/trung/test-run.md`, `docs/clarify.md` | Đạt; Q1–Q8 là quy ước nhóm, chưa có xác nhận giảng viên |
| Tích hợp hai buổi (headless): hái → cập bến → file kho → nấu → phục vụ → thu tiền | 2 lệnh headless trong README của thư mục bằng chứng | `docs/proof/phase-1/trung/e2e/` | Đạt; chưa kiểm ngạt/ngất trong luồng hai buổi |
| Chơi thử trình duyệt hai buổi, HUD | `chonoi.live` gather → kho.json → quan | `docs/proof/phase-1/trung/live/` | Đạt; phím gửi bằng sự kiện bàn phím (không phải người chơi tay), chưa kiểm ngạt/ngất |
