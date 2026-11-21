# Day 12 — AI SDLC: Quán Ăn Chợ Nổi

> **Làm theo nhóm 4–6 người** · Dùng AI để xây game 2D qua **4 phase** trong **3 giờ**: Út Sen lặn bắt cá, hái rau trên mặt nước rồi tối mở quán phục vụ khách.
> **Yêu cầu từng phase mở đúng mốc giờ tại lab board:** **[Chợ Nổi Lab](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg)** (cần đăng nhập claude.ai; có trợ giảng AI cho từng phase).

## Bắt buộc (chỉ có thế)

Cách làm việc kỹ thuật là **tự do** (push thẳng, nhánh + PR, pair, có hay không CI…). Cái bắt buộc:

1. **Một repo chung:** trưởng nhóm **fork** repo này, đặt tên `K5-L3B-LAB-Day12-AI-SDLC-<ten-nhom>`, thêm mọi thành viên làm collaborator (*Settings → Collaborators*, quyền Write) và để repo **public** (giảng viên xem được, không cần mời).
2. **Cả nhóm cùng commit** bằng tài khoản GitHub của mình, mỗi người **≥ 3 commit có nội dung** (làm cặp thì ghi `Co-authored-by:`).
3. **Điền [`TEAM.md`](TEAM.md):** danh sách thành viên + thỏa thuận làm việc nhóm; sửa `team_size` trong [`game.contract.json`](game.contract.json). Commit của người không có trong `TEAM.md` không được tính.
4. **Gắn tag** `phase-1` … `phase-4` đúng hạn; chạy được tại từng tag.
5. **Ghi chép tối thiểu:** `docs/verification/phase-n.md`, `docs/clarify.md`, `docs/ai-usage-log.md`, `docs/retro.md`, `docs/members/<handle>.md`.

## Chơi trên macOS hoặc Linux

Cần Python 3. Mở địa chỉ localhost in ra trong terminal.

```bash
git clone https://github.com/hoangan06/K5-L3B-LAB-Day12-AI-SDLC-Ban6.git
cd K5-L3B-LAB-Day12-AI-SDLC-Ban6
python3 -m chonoi.live --mode gather --inventory-out kho.json
```

Khi buổi sáng kết thúc, dừng server bằng `Ctrl+C` rồi chạy `python3 -m chonoi.live --mode quan --inventory kho.json`. Để mở quán với kho mẫu, dùng `--inventory docs/contracts/inventory.sample.json`.

- **WASD hoặc phím mũi tên** để di chuyển. **E** để hái, cập bến hoặc tương tác với bếp và bàn. **Space** để bắt cá dưới nước. **R** để chơi lại chế độ hiện tại.
- **Điểm** bằng tiền kiếm được cộng `100 × floor(uy tín)` theo preset của dự án. Tiền kiếm được bao gồm boa.
- **Chạy test** bằng `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`.

Sau khi gói Phase 2 đã tích hợp, mở một lượt năm ngày bằng `python3 -m chonoi.live --mode day --days 5`. Chọn **Chơi** để lần lượt qua buổi sáng, quán và cửa hàng. Dùng **P** hoặc **Esc** để tạm dừng, **Enter** để bỏ qua màn giới thiệu, và dùng các nút trong cửa hàng để nâng cấp hoặc sang ngày tiếp theo.

Game cần chế độ **headless** theo Test Contract (`python3 -m chonoi.headless --mode gather|quan …`) để được chạy và chấm tự động. **Công nghệ không ràng buộc**: khung Python trong `chonoi/` chỉ là gợi ý, chi tiết ở [`docs/STARTER.md`](docs/STARTER.md).

## Tự do sáng tạo

Ngoài phần đề yêu cầu, nhóm được **thêm** nhân vật, loài cá/cây, sinh vật, món, bản đồ, cơ chế, câu chuyện, đồ họa, âm nhạc… với ba điều kiện: **không phá phần cố định** (tắt ở headless), ghi mục **"Sáng tạo của nhóm"** trong README của nhóm, và **làm lõi đúng trước**.

## Sáng tạo của nhóm

Trạng thái: **đề xuất, chưa cài vào game**. Bản đang chạy chỉ có phần lõi theo đề; headless không có phần thêm nào.

- Ý tưởng và nguồn tham khảo: [`docs/ideas/sang-tao-trung.md`](docs/ideas/sang-tao-trung.md).
  - Thẻ truyền thuyết: dấu **?** trên vật, món, quái; bấm để đọc chuyện kể kèm nguồn; mở thẻ dùng nút `pause` lõi.
  - Bảng "ngất vì…" theo nguyên nhân (ngạt hoặc Cá Sấu).
  - Đền Bà Thủy, Cá Ông; quái sáng tạo Mãng Xà Vương với chuỗi mũi tên để thoát. Chỉ ở bản chơi live.
- Điều kiện khi cài: tắt ở headless, luồng RNG riêng, không đổi số liệu và sự kiện của Test Contract. Bằng chứng "lõi vẫn đúng" sẽ ghi ở đây khi có.

## Lịch 3 giờ

| Mốc | Phase | Hạn tag |
|---|---|---|
| 0:00 | Phase 1 (PRD-0) | `phase-1` trước 1:00 |
| 1:00 | Phase 2 | `phase-2` trước 1:55 |
| 1:55 | Phase 3 | `phase-3` trước 2:30 |
| 2:30 | Phase 4 | `phase-4` + Release `v1.0.0` trước 3:00 |

Hết giờ mỗi phase thì gắn tag rồi đi tiếp; chỗ chưa xong ghi trung thực trong bằng chứng.

## Đánh giá (100 điểm)

| Hạng mục | Điểm |
|---|---|
| Test tự động ẩn (headless, gồm kiểm tra lại phase trước) | 25 |
| Làm việc nhóm (một repo chung, chia việc, tích hợp, đổi yêu cầu) | 25 |
| Kiểm chứng & bằng chứng | 15 |
| Harness AI (AGENTS.md, skill, nhật ký dùng AI) | 10 |
| Đánh giá & retro | 10 |
| Chất lượng sản phẩm (đúng yêu cầu, mở rộng/sáng tạo) | 10 |
| Demo | 5 |

## Quy định

- Dùng AI thoải mái; **không sao chép repo của nhóm khác**; bằng chứng phải thật.
- Nhân vật, bối cảnh là bản gốc của lab; asset ngoài chỉ dùng CC0/CC-BY/MIT hoặc tự tạo, ghi nguồn trong `CREDITS.md`. Không commit API key, token, `.env`.
