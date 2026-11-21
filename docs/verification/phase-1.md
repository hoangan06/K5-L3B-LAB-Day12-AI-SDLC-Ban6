# Ma trận truy vết Phase 1

| AC | Cách kiểm chứng | Bằng chứng (link `docs/proof/phase-1/...`) | Kết quả (đạt / chưa đạt — ghi trung thực) |
|---|---|---|---|
| Nội bộ DUY-01: hái/bắt và các biên | `tests/test_p1_duy.py`; test tích hợp sau khi nối helper | `docs/proof/phase-1/duy/results.md` | Test helper đạt; tích hợp chưa kiểm chứng |
| Nội bộ DUY-02: kho gather → quán | `python3 tools/smoke_inventory.py` | `docs/proof/phase-1/duy/results.md` | Đạt smoke với fixture cập bến |
| Nội bộ DUY-03: hồi cây, giữ phím, bến, ngất và tick limit | Test tích hợp sau khi phần Ân hoàn thành | `docs/proof/phase-1/duy/results.md` | Chưa đạt bằng chứng; phụ thuộc tích hợp và runtime |
| Nội bộ TRUNG-01: khách đến theo lịch, giữ chỗ, kiên nhẫn, rời bàn, đóng ca | `PYTHONPATH=tests:. python3 -m unittest tests.test_p1_trung -v` (18 test) + `python3 docs/proof/phase-1/trung/mutate.py` | `docs/proof/phase-1/trung/test-run.md` | Đạt trên commit P1 (13/13 mutation bị bắt) |
| Nội bộ TRUNG-02: kiểm fixture quán (mã 2 trước output), theo chốt Q1–Q8 | như trên | `docs/proof/phase-1/trung/test-run.md`, `docs/clarify.md` | Đạt; Q1–Q8 là quy ước nhóm, chưa có xác nhận giảng viên |
| Tích hợp hai buổi (headless): hái → cập bến → file kho → nấu → phục vụ → thu tiền | 2 lệnh headless trong README của thư mục bằng chứng | `docs/proof/phase-1/trung/e2e/` | Đạt; chưa kiểm ngạt/ngất trong luồng hai buổi |
| Chơi thử trình duyệt hai buổi, HUD | `chonoi.live` gather → kho.json → quan | `docs/proof/phase-1/trung/live/` | Đạt; phím gửi bằng sự kiện bàn phím (không phải người chơi tay), chưa kiểm ngạt/ngất |

## Đánh giá ngắn
- Các ID DUY là ID nội bộ, không phải mã chính thức của đề. Test helper và smoke kho đạt; các tình huống tích hợp còn thiếu như ghi ở trên.
- Kiểm lại trên `main` `d77aecb` (2026-11-21): `PYTHONPATH=tests:. python3 -m unittest discover -s tests` → 112 OK; `tools/check_determinism.py` PASS; `tools/smoke_inventory.py` PASS. Các dòng TRUNG do Trung thêm.
- Chưa đủ lúc gắn tag: TEAM.md còn thiếu dòng của Duy và phần thỏa thuận nhóm; nhật ký AI và `docs/members/` chưa có Ân, Duy; dòng DUY-01/DUY-03 chưa cập nhật theo bản đã tích hợp.
- Điều cần chỉnh cho phase sau:
