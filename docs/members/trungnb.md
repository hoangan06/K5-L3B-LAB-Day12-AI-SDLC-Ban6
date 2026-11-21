# trungnb — phản tư cá nhân (≤ 200 từ)

Commit: `https://github.com/hoangan06/K5-L3B-LAB-Day12-AI-SDLC-Ban6/commit/<mã>`

- Tôi đã làm:
  - P1 quán: khách, giữ chỗ, kiên nhẫn, validation (ef7fe51, f00cb9d).
  - P2 quán: kế hoạch ngày, lọc món, `QuanSim(context)` (8e9daa2, e658975).
  - P3: độ tươi kho quán (736d9c8); migration Contract v1.2 (5f9a0aa, 04cd262).
  - P4: giao diện pixel, HUD theo TICKET-02 (18549be, f437a3a); sáng tạo chỉ chạy live (651d5ba, 69933fa); launcher (438b3ad); nháp release notes, retro (2ff2be1).
  - PO: `docs/clarify.md` Q1–Q8, chia việc P3–P4 (fea4df4), gộp nhánh.
- Tôi đã review: sửa `quan_validation.py` của Đức (120ceda); bể cá của Duy (đổi luật độ tươi live, headless giữ nguyên byte) trước khi gộp. Sau mỗi lần gộp chạy test, tất định, smoke kho.
- AI sai ở đâu, tôi phát hiện thế nào: test sót lỗi (lịch khách vòng hai, `ready_ticks`), mutation test bắt được; JSONL làm tròn `fresh`, test file kho của Ân báo đỏ; AI hỏi PO chỗ đề không mâu thuẫn, tôi bỏ.
- Điều tôi học được: chỉ hỏi khi trích được hai câu đề mâu thuẫn; phá luật có chủ ý để biết test có bảo vệ luật không; phần sáng tạo phải tắt ở headless.
