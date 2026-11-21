#!/bin/bash
# Mở game Quán Ăn Chợ Nổi (Bàn 6) trên trình duyệt: vòng 5 ngày, bật phần sáng tạo.
# Chạy: bấm đúp file này (macOS) hoặc `bash tools/choi-game.command`. Đóng cửa sổ Terminal để tắt game.
cd "$(dirname "$0")/.." || exit 1
PORT=${PORT:-8800}
# Lần mở trước chưa tắt: dừng server game cũ trên cổng này (chỉ tiến trình chonoi.live) để chạy bản code mới nhất.
for pid in $(lsof -t -iTCP:"$PORT" -sTCP:LISTEN 2>/dev/null); do
  if ps -o command= -p "$pid" | grep -q "chonoi.live"; then kill "$pid"; sleep 0.5; else
    echo "Cổng $PORT đang bị chương trình khác dùng. Chạy: PORT=8801 bash tools/choi-game.command"; exit 1; fi
done
# ?v= chống trình duyệt dùng lại trang cũ trong cache
(sleep 1.5; open "http://localhost:$PORT/?v=$(date +%s)") &
exec python3 -m chonoi.live --mode day --days 5 --creative --port "$PORT"
