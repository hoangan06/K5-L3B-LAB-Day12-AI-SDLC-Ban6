# Nhật ký dùng AI (theo phase và theo người)

| Phase | Người | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|---|
| 1 | Lại Trọng Đức (`laitrongduc`) | OpenAI Codex | Luật bếp, tích hợp khách, HUD, test và tài liệu chơi | Chưa có số đo | Lượt Playwright đầu đọc sự kiện quá sớm. Đổi sang chờ snapshot live có sự kiện, rồi chạy lại đủ nấu, lấy món, phục vụ và thu tiền. |
| 1–2 | Trung (`trungnb`) | Claude Code, Claude Opus 5.5 | Khách/giữ chỗ/validation quán P1; day_plan, lọc món theo kế hoạch, QuanSim(context) P2; clarify; ý tưởng sáng tạo và tra nguồn truyền thuyết; gộp nhánh và chơi thử headless hai buổi | UNKNOWN (chưa đo token) | Test đầu bỏ sót 3 lỗi, mutation (`docs/proof/phase-*/trung/mutate.py`) bắt được nên thêm test. Đề xuất 6 câu hỏi P2 không có mâu thuẫn thật trong đề, PO bỏ. Không hỏi được bot Anh Năm (lỗi quyền). Nguồn truyền thuyết 1–17 mới đọc trích đoạn, chưa đọc toàn văn. |
