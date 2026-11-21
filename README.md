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

Cần **Python 3.10+**, Git để clone và một trình duyệt hiện đại. Game chỉ dùng thư viện chuẩn Python; không cần pip/npm để chơi. Từ repo sạch, chạy đúng ba lệnh sau rồi mở địa chỉ localhost in trong terminal:

```bash
git clone https://github.com/hoangan06/K5-L3B-LAB-Day12-AI-SDLC-Ban6.git
cd K5-L3B-LAB-Day12-AI-SDLC-Ban6
python3 -m chonoi.live --mode day --days 5
```

Luồng chơi liên tục: mở đầu ngày → lặn/hái → mở quán → kết quả ngày → Shop → ngày tiếp, đến hết Ngày5. Dừng server bằng `Ctrl+C`. Với bản ZIP, giải nén, vào thư mục `chonoi-v1.0.0` rồi chạy cùng lệnh Python ở trên; không cần Git để chơi.

- **WASD hoặc phím mũi tên** để di chuyển. **E** để hái, cập bến hoặc tương tác với bếp và bàn. **Space** để bắt cá dưới nước. **R** để chơi lại chế độ hiện tại.
- Bản chơi trên trình duyệt giảm độ tươi với nửa tốc độ mặc định: giỏ giảm 0,25 điểm/giây, rau trong kho giảm 0,125 điểm/giây. Cá trong kho quán tự ở **bể cá** và giữ nguyên độ tươi khi vào bể; cá đã ươn không tự tươi lại. Cá vẫn có thể được giữ cho đơn và đem nấu như bình thường.
- **P/Esc** tạm dừng; **Enter** bỏ qua giới thiệu. Bấm nút trong Shop để mua nâng cấp/kết thúc Shop. Bật **Tương phản cao** bằng nút trên giao diện; các cảnh báo có chữ/biểu tượng.
- Giỏ và kho dùng cá thể `{id,kind,fresh}`; dưới30 là hàng ươn, vẫn chiếm chỗ nhưng không dùng nấu. Hàng hao độ tươi trong sáng/quán, dừng hao khi pause hoặc ở Shop.
- **Điểm** bằng tiền kiếm được cộng `100 × floor(uy tín)` theo preset của dự án. Tiền kiếm được bao gồm boa.
- **Chạy test** bằng `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`.

## Test, headless và đo đạc

Từ gốc repo/gói, trên macOS/Linux:

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
python3 -m chonoi.headless --mode day --days 5 --seed 7 --ticks 111000 --out day.jsonl
python3 tools/smoke_inventory.py
python3 tools/check_determinism.py
```

Headless chạy theo tick, không cần browser; `--ticks` là giới hạn bước, chưa đủ để hết lượt thì kết quả là `tick_limit`. Để kết thúc Shop cần input `shop_done` hoặc chờ thời gian của Shop theo tuning. CLI chuẩn giữ giới hạn1–5ngày; soak dùng lệnh riêng.

Benchmark cần thêm **Node.js22+ và Google Chrome**. Trên Linux cần môi trường hỗ trợ Chrome; trên macOS mặc định dùng Chrome trong Applications. Đặt `CHONOI_CHROME` nếu binary ở nơi khác; đặt `PYTHON` nếu Python không có tên `python3`:

```bash
node tools/bench.mjs --seed 42 --duration 30 --out bench.json
python3 -m chonoi.soak --seed 7 --days 10 --out soak.json
```

Bench render gather1280×720, làm nóng3giây rồi đo30giây. Báo cáo gồm `avg_fps`, `p1_low_fps`, `frames`, `measured_s`, `load_ms`; FPS thực tế tùy máy. Soak là một tiến trình qua10ngày, lặp kế hoạch D1–D5 và giữ trạng thái/ID liên tục. Kết quả soak cần `days_completed == days`, `crashes == 0`.

## Đóng gói

```bash
python3 tools/package_release.py --out dist/chonoi-v1.0.0.zip
```

Script không ghi đè ZIP đã có. Gói có `BUILD-INFO.json` ghi commit nguồn và hash từng file; chỉ lấy source/docs, bỏ cache và môi trường cục bộ. Nếu còn thiếu đầu vào phát hành, script ghi rõ và gói chỉ là **ứng viên**, chưa phải Release hoàn chỉnh.

Kiểm chứng phát hành v1.0.0: `docs/verification/phase-4.md` và `docs/proof/phase-4/release/`. Bench đo lại trên giao diện cuối; `load_ms` tính từ khởi chạy đến frame gather đầu tiên. **Chưa công bố giấy phép**, theo xác nhận của chủ repo; xem `docs/licensing-status.md` và `CREDITS.md`.

Bật cả phần sáng tạo (đền Bà Thủy, Mãng Xà Vương, miếu Cá Ông; chỉ ở live, headless không đổi): `python3 -m chonoi.live --mode day --days 5 --creative`. Trên macOS có thể bấm đúp `tools/choi-game.command` (mở trình duyệt ở cổng 8800). Icon pixel cho launcher: `python3 tools/icon/make_icon.py`.

Game cần chế độ **headless** theo Test Contract (`python3 -m chonoi.headless --mode gather|quan …`) để được chạy và chấm tự động. **Công nghệ không ràng buộc**: khung Python trong `chonoi/` chỉ là gợi ý, chi tiết ở [`docs/STARTER.md`](docs/STARTER.md).

## Tự do sáng tạo

Ngoài phần đề yêu cầu, nhóm được **thêm** nhân vật, loài cá/cây, sinh vật, món, bản đồ, cơ chế, câu chuyện, đồ họa, âm nhạc… với ba điều kiện: **không phá phần cố định** (tắt ở headless), ghi mục **"Sáng tạo của nhóm"** trong README của nhóm, và **làm lõi đúng trước**.

## Sáng tạo của nhóm

Phần sáng tạo đã được nhóm nối vào live với cờ `--creative`, mặc định tắt; headless giữ phần lõi. Trạng thái kiểm và giới hạn: `docs/ideas/creative-impl-notes.md`. Các ý tưởng chưa triển khai vẫn là đề xuất.

- Ý tưởng và nguồn tham khảo: [`docs/ideas/sang-tao-trung.md`](docs/ideas/sang-tao-trung.md).
  - Thẻ truyền thuyết: dấu **?** trên vật, món, quái; bấm để đọc chuyện kể kèm nguồn; mở thẻ dùng nút `pause` lõi.
  - Bảng "ngất vì…" theo nguyên nhân (ngạt hoặc Cá Sấu).
  - Đền Bà Thủy, Cá Ông; quái sáng tạo Mãng Xà Vương với chuỗi mũi tên để thoát. Chỉ ở bản chơi live.
- Điều kiện khi cài: tắt ở headless, luồng RNG riêng, không đổi số liệu và sự kiện của Test Contract.
- Bằng chứng lõi vẫn đúng (main `59319e9`): `tests/test_creative_trung.py::test_headless_does_not_load_creative` (headless không import `chonoi.creative`); `python3 tools/check_determinism.py` PASS; toàn bộ 266 test OK; JSONL headless gather/quan/day 5 ngày giống từng byte với bản không có phần sáng tạo (ghi trong commit `651d5ba`).
- Giao diện pixel miền Tây, đồng hồ trong ngày, mặt trăng đổi pha: chỉ ở lớp hình (`chonoi/web/`), không đổi snapshot.

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
