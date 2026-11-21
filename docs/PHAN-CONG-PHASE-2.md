# Phân công Phase 2 — Ân, Duy, Trung, Đức

Chuẩn áp dụng: [TICKET-02/Test Contract v1.1](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg#phase-2). Thời lượng 55 phút, tag phase-2 trên main trước mốc 1:55. Nhóm 4 người: chỉ làm lõi, chưa làm weapon/net/snake/burn/vendor/ca_ho/settings. API nội bộ theo [giao diện P2 bản 1.0](contracts/phase-2-interfaces.md), không nhầm với phiên bản Test Contract 1.1.

Đây là kế hoạch và hợp đồng để triển khai, chưa có code P2 hay kết quả kiểm thử P2. Không thay file contract/game đang chạy chỉ vì đã có tài liệu.

## 1. Các quyết định đã chốt

- Giữ Python/starter, nâng cấp contract lên 1.1 với số chuẩn sau khi chốt mốc P1. Mỗi file chỉ có một chủ sửa ở P2.
- Chốt tag phase-1 trước khi đổi dữ liệu/validator sang P2; ghi thật phần chưa đạt. Không đợi P1 hoàn hảo rồi bỏ lỡ mốc P2.
- P1 chưa tích hợp: viết helper P2 và test riêng bằng state mẫu trước; không viết lại phần P1 của người khác.
- Các module giữ API P1 trừ thay đổi được ghi tường minh trong giao diện P2. Chốt thêm context, ShopSim/DaySim và sự kiện chuyển pha trước khi code.
- Dùng `docs/contracts/phase-2-tuning.sample.json` để test helper độc lập trong lúc chưa đổi manifest P1; file có dữ liệu chuẩn6 món/6 cây/5 kế hoạch/Shop/quái/cá.
- Không thêm tính năng mở rộng. Không sửa số liệu chuẩn. Mọi điều chưa rõ được ghi là quy ước nhóm/giả định, không tự nhận đã hỏi giảng viên.

## 2. Quyền sở hữu file — thay cho phân công P1 từ mốc bắt đầu P2

| Người | Công việc | File sở hữu P2 |
|---|---|---|
| **Ân** | Quái, hit/ngất/bất tử; tích hợp gather; runner/pause/tick; CLI/input | `chonoi/sim/gather.py`, module mới `gather_monsters.py`; `chonoi/runner.py`, `chonoi/headless.py`, `chonoi/inputs.py`; `AGENTS.md`; test_p2_an.py |
| **Duy** | Cá bơi/sinh, thu hoạch 6 kind; cấu hình chuẩn và kiểm input scenario/kho | `gather_fish.py`, `gather_actions.py`; `game.contract.json`, `chonoi/contract.py`, `chonoi/inventory.py`, `chonoi/scenario.py`; test_p2_duy.py; verification/proof tích hợp |
| **Trung** | Toàn bộ quán 2 bếp/4 bàn, 6 món, lọc món theo ngày, fixture quán; trợ giúp dữ liệu kế hoạch | `chonoi/sim/quan.py`, `quan_customers.py`, `quan_kitchen.py`, `quan_validation.py`; `day_plan.py`; test_p2_trung.py; clarify/retro |
| **Đức** | Điều phối nhiều ngày, Shop/nâng cấp, menu/pause/HUD và thống kê | `chonoi/sim/day.py`, `shop.py`; `chonoi/live.py`, `chonoi/web/index.html`; README/CREDITS; test_p2_duc.py |

**Đổi chủ file bếp:** Đức bàn giao commit P1 của quan.py/quan_kitchen.py cho Trung. Từ P2 chỉ Trung sửa toàn bộ quán. Đức gọi qua API, không sửa quán để tích hợp day. Duy sở hữu toàn bộ scenario.py/contract.py: Ân/Trung/Đức gửi helper validation hoặc đề xuất, không cùng sửa các file này.

Đức viết validator day/shop trong day.py/shop.py; Trung viết validator quán trong quan_validation.py; Ân viết validator monster trong gather_monsters.py; Duy gọi/import validation tương ứng khi cần, kiểm thứ tự trước output theo giao diện. Tránh import vòng: scenario.py chỉ kiểm cú pháp/phạm vi top-level và trả dữ liệu, không import runner/day.

Mỗi người giữ `tests/test_p2_<an|duy|trung|duc>.py`, fixtures `tests/fixtures/phase-2/<tên>/`, proof `docs/proof/phase-2/<tên>/`. Duy giữ `docs/verification/phase-2.md`, bằng chứng tích hợp tại `docs/proof/phase-2/integration.*`. Trung tập hợp clarify/retro/ai-usage-log từ ghi chép riêng; Ân giữ tài liệu giao diện/phân công. Không cùng sửa file test công khai: người cần đổi gửi patch và lý do cho Ân tích hợp.

## 3. Ân — quái và nền tảng mô phỏng

1. Đọc giao diện P2; bàn giao sớm API Session/input hỗ trợ buy/pause và giao thức gọi DaySim, chưa cần quái hoàn chỉnh.
2. Implement init/update monster theo data: patrol/chase/recoil; M1 từ D1, M2 từ D3. Giữ ngưỡng phát hiện/chạm/depth đúng PRD.
3. Hit tối đa một con/bước, gần nhất rồi id; trừ máu, mất floor(hold/2) LIFO, invuln=90, recoil=60. Ngạt xuyên invuln và không rơi hàng.
4. Gather tích hợp cá Duy và quái Ân đúng thứ tự; mọi bước dừng ngay khi ngất. Cấp oxy/máu lấy context ngày, không sửa tuning gốc.
5. Session tách tick/sim_tick/phase_tick, xử lý pause trước action. CLI nhận day/days; giữ độc lập gather/quan và lỗi mode/cờ đúng.
6. Ghép main và tag. Bảo đảm event chuyển pha còn phase/day cũ, snapshot là pha mới tick 0.

Test: hit tie/id, hit ở mép radius/depth, invuln 90 tick, recoil 60 bước, ngạt+hit cùng bước, ngất bỏ hết hàng, pause cả 3 mode, resume chạy ngay, giữ phím qua đổi pha, days/file flags sai.

## 4. Duy — cá, dữ liệu chuẩn và validation đầu vào

1. Chuẩn bị patch data đầy đủ v1.1 và thay đổi validator; không merge manifest fish_initial=8 khi GatherSim chưa đọc được số đó.
2. Thêm ca_keo/keo_neo vào kho/thu hoạch và cập nhật nodes N5/N6. Schema kho giữ nguyên, chỉ mở rộng miền kind.
3. Bàn giao init_fish/update_fish/snapshot_fish; dùng RNG stream riêng. Cá fixture random_fish=false đứng yên, không sinh; cá mặc định đủ 8 điểm phân biệt, trần12; đổi hướng trước bơi mỗi 120 bước, phản xạ mép giữ phần đường dư.
4. Sinh theo phase_tick 360k sau bơi, lọc clearance >1, trọng số loài rồi chọn đều điểm, không dùng RNG khi không có lựa chọn hợp lệ.
5. scenario.py nhận day templates, trả nguyên khối cho DaySim; không lấy tuning["day"] hoặc áp kiểm kho quán trước khi có hàng thực. Giữ kiểm dữ liệu tĩnh trước output.
6. Smoke hai tiến trình ở phút20; tập hợp proof và verification P2. Kiểm performance headless <=20s/ngày trên máy chấm nếu có điều kiện; nêu môi trường đo thực tế.

Test: reflection góc/mép, age120 trước move, random_fish=false, 8 đàn/không trùng điểm, sinh360/cap/clearance, seed deterministic, 6 kind kho, dữ liệu chuẩn đủ khóa, input fixture sai.

## 5. Trung — quán và kế hoạch

1. Nhận bàn giao P1 bếp từ Đức, tiếp quản toàn bộ quan*.py. Bàn giao sớm QuanSim(context=...) và day_plan helpers.
2. 2 bếp/4 bàn theo data, menu6 món. Quan độc lập cho cả menu; day lọc allowed_dishes trước lọc stock khả dụng. Không giới hạn suất bán theo mục tiêu kế hoạch.
3. Giữ thứ tự timer → chín → move/interact → trả/rời/closing → sinh khách. Giữ quy ước giá/ID/fixture trong giao diện P1 bản1.2, trừ khi có xác nhận mới từ PO.
4. Chuẩn hóa/validate khách/bếp/tay trên kho thực tại thời điểm mở quán. Không cho scene template day cung cấp stock/reputation riêng.
5. Viết day_plan.py: tính ingredients từ dishes×recipe, hợp nhất override theo day, so ingredients nếu khai. Chuẩn D1–D5 đúng đề, không mutate manifest.
6. Thu thập câu hỏi và retro 45–50 phút; ghi một hành động cụ thể có người nhận.

Test: B2/T4, đủ6 món, menu ngày khác menu độc lập, reserved không âm, nhiều bếp chọn đơn cũ không trùng, đóng ca/boa, kế hoạch đúng recipe, fixture quán chỉ hợp lệ sau khi biết kho bàn giao.

## 6. Đức — vòng ngày/Shop/live/UI

1. Viết ShopSim và DaySim theo API, có thể test với phase factory giả trong test riêng khi gather/quan P1 chưa xong; không đưa phase giả vào sản phẩm.
2. DaySim điều phối đúng 5 ngày, chuyển pha cùng tick, ngày hoàn tất chỉ khi Shop đóng. Mỗi pha mới chỉ chạy từ bước sau.
3. Shop mua cấp kế, đúng giá vẫn mua được, tiền giảm/earned giữ, bought/failed; buy trước shop_done và trước xét hết giờ. Khác upgrades/active_upgrades, bỏ kho dư khi dựng ngày mới.
4. Live/HTTP dùng cùng Session như headless, hỗ trợ day, buy/pause/shop_done/days; không tự chạy DaySim trực tiếp bỏ qua Session.
5. UI menu Chơi/Thoát, intro/result/summary, pause/resume/về menu; HUD theo yêu cầu đề, font >=18px ở1280×720. Menu màn hình không tạo phase headless mới.
6. Thống kê từ event thật, không suy số served=paid vì có khách đang ăn. README nêu cách chạy/test6 món/vòng ngày.

Test: bought áp dụng ngày sau, đủ đúng giá, max/funds/unknown, ngày cuối vẫn Shop, buy+done cùng frame cuối, multi-day giữ money/earned/reputation, kho dư bị bỏ, headless1ngày<=22200 tick không pause, HUD/pause thực tế.

## 7. Nhịp bàn giao và điều kiện phải có trước

| Mốc trong P2 | Mục tiêu | Phụ thuộc thật |
|---|---|---|
| 0–5 | Chốt file này; chuyển chủ quán; chốt base P1 | Không đổi dữ liệu P1 trước tag |
| 5–10 | Duy gửi data patch; Trung gửi plan/context; Đức gửi Shop/Day API; Ân gửi Session/input API | Chốt tên hàm không đợi viết xong logic |
| 10–20 | Test riêng bằng fixture, ghép các helper thật đầu tiên | Import thật phải tồn tại trước caller |
| Phút20 | Smoke gather→file kho→quan; standup2–3phút | Gather/Quan + data/validator đồng bộ |
| 20–35 | Day chuyển gather→quan→shop; quái/cá ghép hoàn chỉnh | Session + DaySim + hai sim chuẩn |
| 35–45 | Smoke1ngày, nhiều ngày nâng cấp, pause, regression P1 còn hiệu lực | Các pipeline đã ghép; log trên commit bàn giao |
| 45–50 | Retro có hành động và người nhận | Không cần dừng người đang sửa lỗi |
| 50–55 | Dự phòng, push tag phase-2 trên main | Ghi thật phần chưa đạt, không dời hạn để chờ hoàn hảo |

Gói ghép nguyên tử cần Ân điều phối: manifest mới + loader/validator mới + init_fish mới + GatherSim gọi init_fish. Đừng merge riêng JSON khiến main không khởi tạo được. Day hỗ trợ có thể ghép sau, không chặn test helper/quán độc lập.

## 8. Nhánh và báo bàn giao

Sau khi chốt P1 và có main/base chung đã thống nhất, tạo một nhánh/người: `p2/an`, `p2/duy`, `p2/trung`, `p2/duc`. Người đang còn code P1 chưa commit phải lưu/bàn giao trước; không switch/reset cưỡng bức để tạo P2. Chưa có base tích hợp thì chỉ chuẩn bị helper và test độc lập, ghi rõ base tạm khi bàn giao.

Mỗi lần gửi: tên nhánh + commit SHA + file/API + test/lệnh/kết quả + phụ thuộc/chưa đạt. Merge sớm theo gói chạy được; không force-push main, không formatter toàn repo, không tự đổi API. Review: Ân↔Duy, Trung↔Đức; cả nhóm cùng kiểm phần Session/Day trước tag.

## 9. Các việc có thể làm ngay khi P1 chưa xong

- Ân: unit state quái, thiết kế Session/input, test pause bằng sim nhỏ trong test.
- Duy: module cá và data draft/validator tests; chưa ghi đè manifest local đang có thay đổi của người dùng.
- Trung: day_plan và test lọc6 món; tiếp nhận phần bếp P1 ngay khi Đức bàn giao.
- Đức: ShopSim và DaySim với fake factory trong test riêng, màn hình/HUD dựa trên snapshot mẫu.

Các phần trên không cần sửa file của người khác. Không cam kết tuyệt đối không có xung đột Git; cả nhóm tuân thủ chủ file/API và base chung để giảm xung đột chủ động.
