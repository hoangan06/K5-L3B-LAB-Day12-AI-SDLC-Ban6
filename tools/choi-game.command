#!/bin/bash
# Mở game Quán Ăn Chợ Nổi (Bàn 6) trên trình duyệt: vòng 5 ngày, bật phần sáng tạo.
# Chạy: bấm đúp file này (macOS) hoặc `bash tools/choi-game.command`. Đóng cửa sổ Terminal để tắt game.
cd "$(dirname "$0")/.." || exit 1
PORT=${PORT:-8800}
(sleep 1.5; open "http://localhost:$PORT") &
exec python3 -m chonoi.live --mode day --days 5 --creative --port "$PORT"
