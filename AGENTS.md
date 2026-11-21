# AGENTS.md — hướng dẫn chung cho mọi agent AI của nhóm

> Cập nhật file này qua các phase (lịch sử git phải cho thấy điều đó). Ngắn gọn, có lệnh chạy thật.

## Lệnh
- Test: `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`
- Headless: `python3 -m chonoi.headless --mode gather|quan --seed 1 --ticks 600 --out out.jsonl`
- Chơi thử trên trình duyệt: `python3 -m chonoi.live --mode gather|quan` (mở địa chỉ in ra; WASD, E, Space, R)

## Cấu trúc & quy ước
- (Starter Python là TÙY CHỌN; nhóm có thể dùng ngôn ngữ khác nếu giữ Test Contract.) Khung do giảng viên cấp: `chonoi/{headless,inputs,scenario,contract,rng,ids,jsonl,inventory,runner,live}.py` và `chonoi/web/`. Hạn chế sửa; nếu phải sửa thì báo cả nhóm và ghi lại lý do.
- Luật chơi của nhóm: `chonoi/sim/gather.py`, `chonoi/sim/quan.py` (tìm `TODO(nhóm)`).
- **Số liệu chỉ đọc từ `game.contract.json` / dữ liệu**, không hard-code trong luật.
- Mọi số ngẫu nhiên đi qua `Streams` (`chonoi/rng.py`); không dùng `random` toàn cục, không dùng đồng hồ hệ thống.
- Sắp danh sách thực thể bằng `ids.sort_by_id`; cấp id bằng `IdAllocator`.

## Nên tránh
- Không sửa `docs/contracts/`, `game.contract.json` (khóa contract) hoặc schema kho khi chưa báo cả nhóm (đổi hợp đồng ảnh hưởng mọi module).
- Không làm hỏng nhánh chính: trước khi đẩy, chạy test.
- Không bịa yêu cầu: chỗ mơ hồ thì ghi `docs/clarify.md` và hỏi PO.
- Không sửa test cho xanh khi luật sai; phải sửa luật hoặc ghi lý do đổi test trong commit.

## Quy tắc làm việc với agent
- Mỗi agent một việc rõ ràng (một lát). Cho agent đọc PRD/ticket đúng phase và hợp đồng kho trước.
- Agent làm xong phải chạy test và ghi kết quả vào mô tả commit hoặc `docs/proof/`; người đọc lại thay đổi trước khi đẩy.
- Sáng tạo thêm được khuyến khích nhưng phải tắt ở headless (xem README, mục "Tự do sáng tạo").

## Skills / hooks của nhóm
- `python3 tools/check_determinism.py`: trước bàn giao, chạy lại headless gather/quan và so từng byte JSONL + kho ngất. Hướng dẫn: `docs/proof/phase-1/an/HANDOFF.md`. Chỉ kết luận tất định, không thay test đúng luật.
- `python3 tools/smoke_inventory.py`: kiểm hai tiến trình gather ghi kho → quan đọc đúng stock tick 0. Hướng dẫn: `docs/smoke-inventory.md`.

## Tích hợp Phase 1 — phần Ân
- `gather.py` đã có oxy/ngạt/ngất và đã nối helper thật `gather_node`/`catch_fish` từ module Duy. Giữ thứ tự ngất → bến/hái → bắt → hết giờ.
- Test riêng Ân: `python3 -m unittest discover -s tests -p test_p1_an.py -v`.
- Giữ thông tin TEAM/GitHub để thành viên tự điền; không tự đoán handle.

## Phase 2 — nền tảng Session/input của Ân
- Nhánh `p2/an`: Session tách tick/sim_tick, pause trước gameplay, resume chạy ngay; input hỗ trợ buy/shop_done. CLI nhận day với version1.1/1.2; manifest runtime hiện1.1 và chưa bật freshness. DaySim/ShopSim/live đã tích hợp từ Đức.
- Test: `python3 -m unittest discover -s tests -p test_p2_an.py -v`. Bàn giao và giới hạn: `docs/proof/phase-2/an/HANDOFF.md`.
- `load_frames(path)` mặc định giữ parser v1.0 để không phá kiểm P1. Headless chọn BUTTONS_V11 khi manifest1.1; caller P2 khác cần truyền `buttons=BUTTONS_V11`. LiveInputs/InputPlayer mặc định nhận nút v1.1.
- Không dùng mock DaySim trong runtime. Bản thật đã được kiểm5ngày headless/live; xem `docs/proof/phase-2/an/RELEASE-PHASE-2.md` và `tools/check_phase2_live_release.py`.
- Cá Sấu: `gather_monsters.py` đã nối vào GatherSim sau oxy/ngạt, trước interact/catch. Config P1 không có monsters thì không tự thêm quái. Test `python3 -m unittest discover -s tests -p test_p2_an_monsters.py -v`.
- GatherSim nhận keyword context, hp_max/oxygen_max_ticks/ngày/tiền theo giao diện P2; `_faint(cause, events)` dùng chung choke/monster. Đã nối init/update/snapshot_fish với fish_initial số8 của Duy, giữ nhánh list P1 khi chạy cấu hình cũ.
