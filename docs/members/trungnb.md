# trungnb — phản tư cá nhân (≤ 200 từ)

- Tôi đã làm (kèm link commit):
  - Lát 3 P1: khách, giữ chỗ, kiên nhẫn, validation quán ([ef7fe51](https://github.com/hoangan06/K5-L3B-LAB-Day12-AI-SDLC-Ban6/commit/ef7fe51), [f00cb9d](https://github.com/hoangan06/K5-L3B-LAB-Day12-AI-SDLC-Ban6/commit/f00cb9d)).
  - P2 quán: kế hoạch ngày, lọc món, `QuanSim(context)` ([8e9daa2](https://github.com/hoangan06/K5-L3B-LAB-Day12-AI-SDLC-Ban6/commit/8e9daa2), [e658975](https://github.com/hoangan06/K5-L3B-LAB-Day12-AI-SDLC-Ban6/commit/e658975)).
  - PO: `docs/clarify.md` Q1–Q8; gộp nhánh vào main ([885a5d8](https://github.com/hoangan06/K5-L3B-LAB-Day12-AI-SDLC-Ban6/commit/885a5d8)); chơi thử hai buổi headless và trình duyệt ([5f6c05a](https://github.com/hoangan06/K5-L3B-LAB-Day12-AI-SDLC-Ban6/commit/5f6c05a), [81c7e5c](https://github.com/hoangan06/K5-L3B-LAB-Day12-AI-SDLC-Ban6/commit/81c7e5c)); ý tưởng sáng tạo có nguồn ([a5246c4](https://github.com/hoangan06/K5-L3B-LAB-Day12-AI-SDLC-Ban6/commit/a5246c4)).
- Tôi đã review (kèm link): đọc sửa của Đức trong `quan_validation.py` ([120ceda](https://github.com/hoangan06/K5-L3B-LAB-Day12-AI-SDLC-Ban6/commit/120ceda)), giữ nguyên khi gộp; chạy lại test, tất định và smoke kho sau mỗi lần gộp.
- AI sai ở đâu và tôi phát hiện thế nào: test đầu bỏ sót lỗi (lịch khách vòng hai, `ready_ticks`, sửa nhầm fixture), mutation test bắt được. AI đề xuất câu hỏi P2 không có mâu thuẫn thật trong đề, tôi bỏ.
- Điều tôi học được: chỉ hỏi khi trích được hai câu đề mâu thuẫn; phá luật có chủ ý để biết test có thật sự bảo vệ luật không.
