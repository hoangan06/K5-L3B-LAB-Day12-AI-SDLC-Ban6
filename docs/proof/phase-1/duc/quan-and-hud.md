# Kiểm chứng tích hợp quán và HUD

Kiểm trên `p1/duc` sau khi ghép module khách và validation từ `p1/trung` tại `e5ed072`. Luồng quán áp dụng các quyết định Phase 1 bản 1.2.

| Kiểm tra | Kết quả |
|---|---|
| `PYTHONPATH=tests:. PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` | 64/64 test đạt, gồm 14 test của Đức, 18 test của Trung và 32 test starter |
| Headless với khách chờ ở 0, giá món 77 và còn 1 tick | `served → paid (closing, 77) → quan_end`. Hai lần chạy cùng input cho JSONL giống từng byte |
| Headless với fixture chờ nhưng `served`, hoặc thiếu kho để suy phần giữ | Cả hai trả mã 2 trước khi ghi output |
| Chrome qua Playwright, `gather` với `dock.json` | HUD hiện oxy, máu và giỏ 3/12. Nhấn E ở bến phát `gather_end` |
| Chrome qua Playwright, `quan` với mẫu `quan-reserved` và thêm kho khả dụng | HUD trừ phần giữ đúng. Nhấn E tại bếp, lấy món khi chín, đi tới bàn và phục vụ. Quan sát đủ `cook_started → dish_ready → dish_picked → served → paid`, tiền 72. Console có 0 lỗi và 0 cảnh báo |

Ảnh HUD ở 1200 × 760 gồm [buổi sáng](hud-gather.png), [bếp đang nấu](hud-quan-cooking.png) và [đang cầm món](hud-quan-carry.png).

Kiểm thử hồi quy trên CLI tái hiện mã 1 với `dish_id: []` ở khách và payload món. Sau khi kiểm kiểu trước khi tra menu, cả hai vị trí trả mã 2 trước khi ghi output.

Mô phỏng ghép `p1/an` với `p1/trung` phát hiện xung đột trong `docs/clarify.md`. Hai nhánh ghi lại cùng bộ câu hỏi Phase 1. Ân và Trung có thể hợp nhất thành một bảng khi tích hợp.
