# Smoke kho Phase 1

Chạy từ gốc repo: `python3 tools/smoke_inventory.py`. Script dùng `headless_cmd` trong contract, tạo fixture tạm và chạy gather rồi quan; kiểm file kho, event kết thúc và stock ở tick 0. Exit 0 là đạt, exit 1 là lỗi. Cần runtime trong `headless_cmd` có trên PATH. Đây là smoke tích hợp kho, không kiểm toàn bộ luật thu hoạch hay ngất.
