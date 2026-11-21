# Chơi thử bản trình duyệt đủ hai buổi (main `a813811`, 2026-11-21)

Chạy trong trình duyệt tích hợp của Claude Code. Phím được gửi bằng sự kiện `keydown`/`keyup` thật vào trang (đi qua đúng bộ xử lý phím của `chonoi/web/index.html`); trạng thái đọc từ `GET /state`.

```bash
python3 -m chonoi.live --mode gather --port 8765 --inventory-out kho.json
python3 -m chonoi.live --mode quan --port 8766 --inventory kho.json
```

**Buổi sáng** (`gather-docked.jpg`): bơi sang phải, lặn, bắt đàn F1 → `fish_caught` cá linh ×3; nổi, hái N3, N4 → bông súng ×2; về bến, E → `gather_end` `docked`. File kho ghi ra: `kho.json` = `{"items":{"bong_sung":2,"ca_linh":3}}`.

**Buổi tối** (`quan-paid.jpg`): nạp `kho.json`. Khách C1 tới tick 120 gọi gỏi bông súng → nấu ở B1 (tick 1946) → chín 2186 → bưng 2230 → phục vụ 3338 → trả 40 tick 3938 (`finished_eating`). Phục vụ muộn (còn 382 tick kiên nhẫn < 50%) nên boa 0, uy tín giữ 3.0. HUD: tiền 40k, uy tín 3.0, điểm 340 = 40 + 100 × 3.

**Ghi chú trung thực**
- Pane trình duyệt bị ẩn nên trang chạy chậm (tab nền), làm phục vụ trễ; luật boa vẫn đúng với số tick thực tế.
- Không phải người chơi bằng tay; chưa kiểm ngạt/ngất và hết giờ ca sáng trên trình duyệt.
- Sau khi xong buổi sáng phải dừng server rồi chạy lệnh quán: đúng yêu cầu Phase 1 (hai tiến trình chung file kho). Chạy một mạch là việc của Phase 2 (`--mode day`).
