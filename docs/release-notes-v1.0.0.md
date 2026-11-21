# Quán Ăn Chợ Nổi v1.0.0 — Bàn 6

Bản phát hành tổng hợp bốn phase của lab, Test Contract1.3. Tag `phase-4` và `v1.0.0` dùng cùng commit bàn giao trên main.

Bản cập nhật cuối sửa sai số uy tín gây thiếu điểm, bổ sung player.vel, siết kiểm đầu vào/ID và đổi HUD sang sans-serif18px. ZIP hiện hành thay bản dbe6d20; các asset archive-* chỉ giữ để đối chiếu. Giữ nguyên phần cá nhân của Duy/Đức theo yêu cầu chủ repo.

## Điểm mới

- Một lượt5ngày liên tục: lặn hái/bắt cá → mở quán → kết quả → Shop nâng cấp → ngày tiếp. Có pause và HUD.
- Oxy/ngạt/ngất, Cá Sấu Năm Chèo, cá bơi/sinh; bếp, giữ nguyên liệu, phục vụ, boa và uy tín.
- Kho cá thể `{id,kind,fresh}`, hao độ tươi, hàng ươn và giá nấu theo độ tươi; ID nối qua pha/ngày. Luật headless giữ theo contract.
- Cảnh báo chữ/biểu tượng cho thủy quái gần, oxy thấp, khách sắp giận; tương phản cao.
- Giao diện pixel miền Tây, thẻ truyền thuyết; phần sáng tạo bật riêng qua `--creative`. Bể cá chỉ thuộc bản chơi live.
- Benchmark có render, soak10ngày một Session, công cụ tạo/kiểm ZIP độc lập.

## Chạy từ ZIP

Giải nén asset `chonoi-v1.0.0.zip`, vào thư mục `chonoi-v1.0.0`, rồi chạy:

```bash
python3 -m chonoi.live --mode day --days 5
```

Cần Python3.10+ và trình duyệt hiện đại; không cần pip/npm để chơi. Mở URL localhost được in ra. WASD/mũi tên: di chuyển; E: tương tác; Space: bắt cá; P/Esc: pause; Enter: qua intro; R: chơi lại. Shop dùng nút trên màn hình.

Từ clone sạch trên macOS/Linux, tối đa3lệnh:

```bash
git clone --branch v1.0.0 https://github.com/hoangan06/K5-L3B-LAB-Day12-AI-SDLC-Ban6.git
cd K5-L3B-LAB-Day12-AI-SDLC-Ban6
python3 -m chonoi.live --mode day --days 5
```

## Kiểm chứng

Lệnh test: `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`.

Bench: `node tools/bench.mjs --seed 42 --duration 30 --out bench.json` — cần Node22+ và Google Chrome; có thể đặt `CHONOI_CHROME`/`PYTHON`. Soak: `python3 -m chonoi.soak --seed 7 --days 10 --out soak.json`.

| Kiểm | Kết quả đo trên bản tích hợp |
|---|---|
| Regression | 288/288 test đạt, không skip; docs/proof/final-an/all-tests.txt; thêm 9 test hồi quy điểm/schema/ID/vel |
| Clone/ZIP | Khởi động GUI/HTTP trên Linux WSL bằng lệnh README; ZIP kiểm import độc lập và hash đạt; clean-clone.json/package-check.json |
| Bench | Đo lại sau sửa HUD: {"avg_fps": 112.06974116988413, "p1_low_fps": 58.079945336521895, "frames": 3363, "measured_s": 30.008100000000002, "load_ms": 1008.77099609375}; 1280×720, nóng3s, seed42; docs/proof/final-an/bench.json |
| Soak | 10/10ngày, 0crash; hai lần seed7 có gameplay giống nhau; đã đi qua hái/nấu/phục vụ/thu tiền |
| UI | Cả3cảnh báo hiện ở tương phản cao, input browser thật trên fixture engine, không thay snapshot; console0exception |

Bench/UI dùng Chrome trên Windows; test/soak và kiểm gói dùng Python trong WSL Linux. Đây là số đo theo môi trường ghi trong proof, không hứa FPS trên mọi máy. Ma trận: `docs/verification/phase-4.md`.

## Giới hạn và giấy phép

- **Chưa công bố giấy phép**, theo xác nhận của chủ repo. Repo không có LICENSE cấp quyền chung; xem `docs/licensing-status.md` và `CREDITS.md`.
- Sáng tạo chỉ ở live; hệ số buff và các tình huống Mãng Xà chưa được chơi tay đầy đủ. Leaderboard/phụ đề SFX không triển khai.
- Kiểm UI tự động dùng scenario hợp lệ để tái hiện cảnh báo, không thay cho một buổi chơi tay dài.
- Phản tư cá nhân của Duy chưa có trong `docs/members/` lúc chốt; bằng chứng code/test của Duy có trong lịch sử và proof. Không viết thay phản tư của thành viên.

Gói ZIP có BUILD-INFO.json với SHA nguồn/hash từng file. Đối chiếu SHA256SUMS.txt của Release trước khi dùng.
