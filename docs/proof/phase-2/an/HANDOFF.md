# Ân — bàn giao nền tảng Session, CLI và input P2

Ngày: 21/11/2026 Asia/Saigon. Nhánh `p2/an` tạo từ main `4229ebf` (local working tree sạch khi tạo). Các thay đổi này chưa commit/push tại thời điểm ghi biên bản.

## Kiểm tra tin của Trung

Đã xác nhận trên máy: QuanSim có keyword-only context, yêu cầu allowed_dishes là list id hợp lệ trong menu, lấy money/earned/reputation từ context; resolve_day_plans đã có. DaySim/ShopSim chưa có trong bản local. Manifest vẫn1.0, scenario loader vẫn chỉ gather/quan. live.py chưa nhận day và thuộc Đức; không sửa file Đức/Trung/Duy trong lượt làm này.

## Đã làm

- inputs.py: InputState(..., buy=None); buy chỉ trên frame khai, không kế thừa; bool chốt/cạnh giữ qua pha; LiveInputs.set nhận buy và FIFO, mỗi advance lấy tối đa một lệnh. Parse pause/shop_done/attack/photo theo BUTTONS_V11; mở rộng chưa bật không tự chạy luật.
- runner.py: Session(..., days=1); tick ngoài khác sim_tick; phase_tick lấy từ child (fallback counter cho GatherSim P1). Pause phát event trước gameplay và đóng băng child; resume chạy child ngay, không phát lại action đã bỏ lúc pause.
- Session.initial_events drain một lần; day event giữ phase/day nguồn trước chuyển pha; snapshot sau chuyển pha dùng child mới/phase_tick0, kể cả không phải mốc snapshot định kỳ. end day có days_completed.
- build_sim chọn DaySim qua import bên trong nhánh day; không ảnh hưởng standalone nếu day.py chưa có. Thiếu DaySim báo BadInput rõ, không giả hoàn thành bằng stub.
- headless.py: --days chỉ day,1..5, mặc định1; day cấm hai file kho flags; truyền nguyên day scenario/days cho runner. Chỉ bật mode day và parser input mới khi manifest contract_version1.1, giữ P1 regression khi manifest1.0.
- Giữ constructor Session cũ tương thích live; không đổi schema kho. write_inventory_if_done chống ghi lặp trong cùng Session.

## Kiểm chứng thật

-19 test P2 mới trong tests/test_p2_an.py PASS.
- Tổng131 test PASS: test-results.txt. Trong đó112 test có sẵn +19 test mới. Không sửa assertion nguồn của test P1.
- Pause gather/quán dùng sim thật; các test day dùng FakeDay **chỉ trong test** để kiểm API/provenance/tick/CLI dispatch, chưa chứng minh DaySim/ShopSim thật.
- Tính tất định standalone và kho ngất: determinism-results.txt, PASS.
- Smoke hai tiến trình kho: inventory-results.txt, PASS.
- Test live lần đầu trong sandbox bị WinError10013; test-results-sandbox.txt giữ lỗi thật. Chạy lại ngoài sandbox, HTTP localhost PASS.

Môi trường Python3.12 bundled Codex, PYTHONUTF8=1. Vì python3 WindowsApps alias không chạy, harness full suite thay duy nhất executable trong helpers.headless_cmd bằng sys.executable trong bộ nhớ, không sửa helpers.py/config. Command smoke làm tương tự với shlex.split trong harness; command determinism dùng --python. Đây không phải kiểm khả năng chạy python3 native của Windows.

## Đức cần dùng đúng các API sau

```python
session = Session("day", tuning, scenario, seed, days=days)
events = session.initial_events()  # một lần lúc reset/start
events += session.step(inputs.advance())
snapshot = session.snapshot()
```

- LiveGame reset truyền days và lấy initial_events; GET/state không drain lại.
- HTTP/input chấp nhận pause/shop_done boolean và buy string; gọi LiveInputs.set(buy=..., ...). Không bool-coerce buy. LiveInputs giữ queue; Session consume input mỗi tick ngay cả khi pause.
- Không dùng tuning["day"] để làm meta trong live, vì không có khóa đó. Chọn meta của current phase hoặc dựng object meta riêng từ tuning.
- DaySim constructor `DaySim(tuning, scenario, streams, ids, *, days=1)`.
- DaySim.step trả list dict {phase,day,name,data}, không chứa tick/type; child Gather/Quan/Shop vẫn trả tuple(name,data). Session bọc tick/type, không đoán phase cũ từ phase mới.
- DaySim.initial_events trả day_start/day_plan/phase_start D1; DaySim có phase_tick/time_left_ticks/money/earned/reputation/day/days_completed/done/reason, snapshot dữ liệu ngày.
- Khi đổi pha, dựng child mới nhưng không step ngay; giữ InputPlayer/LiveInputs và RNG/IDs xuyên pha/ngày.
- Quan context **bắt buộc allowed_dishes list**; gọi resolve_day_plans rồi lấy list(plan["dishes"]) cùng money/earned/reputation. Không sửa quan.py để bỏ validation.

## Duy cần ghép

- Manifest1.1/data chuẩn và validator đọc được, đặc biệt fish_initial số8 khác list6 cũ.
- scenario.load_scenario(path,"day",tuning) trả toàn object day/gather/quan. Không áp tuning["day"], không trả riêng block day.
- Tránh xác minh kho fixture quán trước gather; kho thực chỉ biết lúc mở quán. Các lỗi tĩnh vẫn kiểm trước output.
- API load_frames mặc định giữ v1.0; headless đã truyền BUTTONS_V11 theo manifest. Nếu code P2 khác gọi trực tiếp loader input, truyền buttons=BUTTONS_V11.

## Còn chưa xong

- Chưa có DaySim/ShopSim thật, live day/menu/HUD của Đức; chưa data/loader P2 của Duy. **Hiện chưa thể chạy trọn --mode day trên bản runtime local.** Không đổi manifest1.1 riêng để báo đã hỗ trợ.
- Lát Cá Sấu đã được bổ sung ở lần làm tiếp theo, xem mục cập nhật dưới đây; không còn là phần chưa triển khai.
- Chưa smoke day1..5/mua upgrade thật/benchmark ngày; chưa tag phase2. Sau ghép cần regression các test còn hiệu lực, cập nhật kỳ vọng P1 thay đổi do data1.1 có ghi lý do.

## Lệnh kiểm thử trên WSL/Linux của nhóm

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -p test_p2_an.py -v
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
python3 tools/check_determinism.py
python3 tools/smoke_inventory.py
```

Sau khi DaySim/data thật đã ghép, thêm `python3 -m chonoi.headless --mode day --days 1 --seed 1 --ticks 22200 --out /tmp/ban6-day.jsonl`, kiểm end.days_completed/reason và nhiều ngày; không coi lệnh này đã chạy trong lượt hiện tại.

Nhật ký AI gửi Trung tập hợp: Phase2 | Ân | Codex | Session/pause/tick/CLI/input buy và19 test/handoff | Token/chi phí chưa đo | Dùng sim thật cho pause, test double riêng cho giao thức day; log ghi rõ thiếu phụ thuộc thực tế. Người dùng cần đọc/review trước merge/push.

## Cập nhật: Cá Sấu đã triển khai, tổng150 test PASS

- Module mới `chonoi/sim/gather_monsters.py`: init/validation, patrol/chase/recoil, di chuyển trước hit, một hit gần nhất/id mỗi bước, rơi floor(n/2) LIFO, invuln90 và recoil60 bước từ bước sau.
- M1 từ D1, M2 từ D3, fixture monsters=[] tắt quái; config P1 không monsters vẫn giữ gameplay P1. Không hard-code dữ liệu Cá Sấu vào luật, dùng tuning.gather.monsters.
- GatherSim nhận context keyword để lấy day, caps oxy/máu, money/earned/reputation; snapshot hp_max theo nâng cấp. phase_tick tăng một lần mỗi gameplay step. Không sửa tuning/context gốc.
- `_faint(cause, events)` dùng chung cho ngạt/quái: hit làm rơi nửa giỏ trước, faint liệt kê phần còn lại rồi kết thúc kho rỗng. Ngạt xuyên invuln và có thể đi trước hit trong cùng bước.
-19 test Cá Sấu bổ sung; tổng38 test P2 Ân và112 test cũ =150/150 PASS, log `test-results-with-monsters.txt` (ngoài sandbox cho test_live). Log131 test trước đó là kết quả trước bổ sung quái, vẫn giữ lịch sử.
- Real runner với tuning mẫu P2 và fixture cố định random_fish=false đã kiểm hit→faint→kho rỗng, dừng tick1 và hai lần giống byte; event và hash ở `monster-pipeline-results.txt`. Kiểm này gọi runner.run trực tiếp, không tự nhận CLI/loader P2 đã ghép.

**Duy cần chú ý khi ghép:** mở scenario GATHER_KEYS để nhận monsters, fish age_ticks và6kind theo P2; hiện loader P1 vẫn từ chối fixture monsters trước khi tới sim. GatherSim gọi init_monsters sau dựng state và đã có phase_tick; không tăng phase_tick trong helper cá. Cá bơi/sinh chưa nối, đoạn fish_initial list P1 vẫn phải thay bằng init_fish của Duy trong gói data1.1 đồng bộ. Không đổi manifest riêng vì fish_initial số8 sẽ không chạy qua đường P1 hiện tại.

**Đức:** GatherSim(tuning, gather_block, streams, ids, context=context) đã có thật. Context tối thiểu gồm day/money/earned/reputation/oxygen_max_ticks/hp_max; fixture player có thể ghi đè mức refill để test và được kiểm cap. Không tự sửa caps bằng cách mutate tuning. Quái mặc định dựa context.day. Các phần này mới kiểm trong sim/runner, chưa chơi qua HUD quái hoặc day thật.

Nhật ký bổ sung gửi Trung: Ân dùng Codex triển khai Cá Sấu/context gather,19 test sát thương/tick/fixture và real-runner determinism; token/chi phí chưa đo; không sửa source test cũ, không giả runtime P2 hoàn tất.
