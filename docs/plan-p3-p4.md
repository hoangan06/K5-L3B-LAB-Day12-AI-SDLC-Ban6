# Chia việc Phase 3 và Phase 4 (PO Trung đề xuất, nhóm sửa nếu cần)

Hạn: tag `phase-3` 2:30 (TICKET-03, Test Contract v1.2). Tag `phase-4` và GitHub Release `v1.0.0` 3:00, cùng một commit trên main (TICKET-04, Test Contract v1.3).
Chia theo file mỗi người đang giữ. Ai xong sớm báo trong nhóm để nhận lát đang trễ.

## Phase 3 — Độ tươi, kho cá thể

| Người | Việc | File chính | Xong khi |
|---|---|---|---|
| Trung | Đã xong quán P3 (giữ theo id, ươn, giá theo tươi). Đang làm: manifest 1.2 + `freshness`, module kho cá thể `chonoi/items.py`, đọc/ghi file kho `{"items":[...]}`, scenario v1.2, giỏ gather cá thể + hao 0.5/s + `spoiled` hold, `lost` LIFO dạng cá thể, bàn giao day, Shop giữ kho cá thể. Chuyển test P1–P2 kho đếm sang fixture manifest cũ (ghi lý do). | `chonoi/items.py`, `inventory.py`, `scenario.py`, `contract.py`, `sim/gather*.py`, `sim/day.py`, `sim/shop.py`, `game.contract.json` | Push lên main kèm test; báo nhóm review |
| Ân | Review phần gather/runner Trung đổi. Test gather v1.2: scenario mẫu trong đề (`hold` I1 fresh 30 → `spoiled` tick 1), `monster_hit.lost`/`faint.lost` là mảng cá thể LIFO, `gather_end.data.inventory` đúng schema. Gắn tag `phase-3`. | `tests/test_p3_an.py`, `docs/proof/phase-3/an/` | Test xanh, tag đẩy trước 2:30 |
| Duy | Test kho/scenario v1.2: file kho đếm → mã 2, id trùng/rỗng, kind lạ, fresh ngoài [0,100], id trùng giữa hold và stock. Cập nhật `tools/smoke_inventory.py` cho kho cá thể: gather ghi file → quan `--inventory --ticks 0` so đúng id/kind/fresh. Dòng QA trong `docs/verification/phase-3.md`. | `tests/test_p3_duy.py`, `tools/smoke_inventory.py`, `docs/proof/phase-3/duy/` | Smoke PASS trên v1.2 |
| Đức | HUD cho thấy độ tươi hoặc hàng ươn (giỏ, kho quán, Shop) trên nền UI của Đức. Review nhánh giao diện pixel `p3/ui-pixel-trung` khi có (chỉ đổi lớp hình, giữ luồng UI của Đức) rồi merge. Chơi thử day trên trình duyệt với v1.2, chụp ảnh. | `chonoi/web/`, `docs/proof/phase-3/duc/` | Ảnh HUD có độ tươi, console 0 lỗi |

Chung trước tag phase-3: `CHANGELOG.md` ghi breaking change kho đếm → kho cá thể; `docs/verification/phase-3.md` đủ dòng; `docs/ai-usage-log.md`; retro nhanh về lần đổi kho trong `docs/retro.md`.

## Phase 4 — Phát hành v1.0.0

| Người | Vai | Việc | Xong khi |
|---|---|---|---|
| Ân | Release / Integrator | `contract_version:"1.3"`, khai `bench_cmd`, `soak_cmd` ở gốc `game.contract.json`. README: yêu cầu môi trường, điều khiển, lệnh test/headless/bench, chạy từ clone sạch ≤ 3 lệnh (macOS/Linux). Đóng gói, GitHub Release `v1.0.0` + tag `phase-4` cùng commit main. | Release có bản đóng gói, trước 3:00 |
| Đức | Bench + UI | `bench_cmd --seed 42 --duration 30 --out bench.json`: cảnh sáng lõi 1280×720, làm nóng 3 s, đo 30 s, 5 trường `avg_fps`, `p1_low_fps`, `frames`, `measured_s`, `load_ms`. Ba cảnh báo có chữ/biểu tượng: thủy quái gần, oxy sắp hết, khách sắp giận. Chế độ tương phản cao, chơi thử cả ba cảnh báo ở chế độ đó. | `bench.json` lưu trong `docs/proof/phase-4/` |
| Duy | Bench/QA | `soak_cmd --seed 7 --days 10 --out soak.json`: 10 Ngày một tiến trình, D1–D5 lặp ở Ngày 6–10, tiền/uy tín/nâng cấp/id cá thể nối tiếp; trường `days`, `days_completed`, `crashes`, `results[] {day, earned, reputation, score}`, `duration_s`. Chạy regression P1–P3, thử clone sạch, ma trận `docs/verification/phase-4.md`. | `days_completed = 10`, `crashes = 0` |
| Trung | PO / điều phối retro | Release notes (điểm mới, cách chạy, giới hạn), `CHANGELOG.md` theo phase, rà `CREDITS.md`/`LICENSE`, `docs/clarify.md`, `docs/ai-usage-log.md`, `docs/retro.md` (mở đầu bằng rà hành động P2). Chuẩn bị checklist demo. | Các file có trên main trước 3:00 |

Mỗi người: `docs/members/<handle>.md` (≤ 200 từ: phần mình làm, đã giúp ai, AI sai ở đâu, bài học, dẫn commit). Commit bằng tài khoản của mình; làm chung thì ghi `Co-authored-by:`.

Mở rộng (leaderboard, phụ đề SFX): nhóm 4 người không bắt buộc, chỉ làm khi lõi đã xong.
