# Quán Ăn Chợ Nổi v1.0.0 — Bàn 6 (NHÁP, Trung gom; chốt khi có kết quả cuối)

> Trạng thái: **nháp**. Các mục ghi UNVERIFIED chưa có bằng chứng trên commit phát hành; Ân điền SHA/tag/Release, Duy điền soak/clone sạch, Đức điền bench cuối.

## Điểm mới
- Vòng một Ngày: sáng lặn hái/bắt cá (oxy, ngạt, ngất, Cá Sấu Năm Chèo), tối mở quán (giữ chỗ, nấu, phục vụ, thu tiền), Shop nâng cấp; 5 Ngày liên tiếp (P2).
- Độ tươi cá thể (Contract v1.2, P3): kho `{"items":[{id,kind,fresh}]}`, giỏ hao 0.5/s, kho quán hao 0.25/s, hàng < 30 là ươn, giá món theo độ tươi trung bình lúc nấu.
- Phát hành (P4): bench 1280×720, ba cảnh báo (thủy quái gần, oxy sắp hết, khách sắp giận), chế độ tương phản cao; soak 10 Ngày (UNVERIFIED: chưa có `soak.json` trên main).
- Giao diện pixel miền Tây: xuồng ba lá, cây bẹo, nhà sàn, lục bình, nón lá; đồng hồ trong ngày, mặt trời/mặt trăng đổi pha; thẻ truyền thuyết "?" có nguồn.
- Phần sáng tạo chỉ ở live (`--creative`, headless không đổi): đền Bà Thủy (thắp hương → bơi nhanh hơn, ít gặp quái), Mãng Xà Vương (chuỗi mũi tên để thoát), miếu Cá Ông (xúc xắc hồi sinh).

## Cách chạy (macOS/Linux, Python 3 stdlib)
```bash
git clone https://github.com/hoangan06/K5-L3B-LAB-Day12-AI-SDLC-Ban6 && cd K5-L3B-LAB-Day12-AI-SDLC-Ban6
python3 -m chonoi.live --mode day --days 5 --creative
```
Test: `PYTHONPATH=tests:. python3 -m unittest discover -s tests`. Headless: `python3 -m chonoi.headless --mode day --days 5 --seed 1 --ticks 111000 --out out.jsonl`. macOS: bấm đúp `tools/choi-game.command`.
Bench/soak: lệnh chính thức theo `bench_cmd`/`soak_cmd` trong `game.contract.json` (UNVERIFIED: manifest chưa lên 1.3 lúc viết).

## Số liệu (điền từ bằng chứng)
| Mục | Giá trị | Nguồn |
|---|---|---|
| Test | 253 OK trên main `918ed67` (lúc viết) | chạy `unittest discover` |
| Bench | avg_fps 60.0, p1_low_fps 59.5, 1801 frames, 30.0 s, load_ms 162.7 (đo trên nhánh `p4/duc`, trước khi gộp giao diện pixel; cần đo lại) | `docs/proof/phase-4/bench.json` |
| Soak 10 Ngày | UNVERIFIED | `soak.json` (Duy) |
| Clone sạch ≤ 3 lệnh | UNVERIFIED | Duy |

## Giới hạn đã biết
- Bench đo trước khi gộp lớp pixel; đồ họa mới nặng hơn nên số FPS phải đo lại trên commit phát hành.
- Phần sáng tạo: hệ số buff, vị trí đền, 3 s đứng yên là số tạm (`docs/ideas/creative-impl-notes.md`); Mãng Xà chưa được chơi tay đủ một ca.
- Mở rộng (leaderboard, phụ đề SFX) không làm.

## Ghi công
Xem `CREDITS.md`, `docs/ai-usage-log.md`. Giấy phép: UNKNOWN (chưa có `LICENSE`, nhóm cần chọn).
