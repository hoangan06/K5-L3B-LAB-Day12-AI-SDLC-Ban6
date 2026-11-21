# Giao diện nội bộ Phase 2 — bản chốt 1.0

Áp dụng TICKET-02/Test Contract **v1.1**. “1.0” trong tiêu đề là phiên bản tài liệu nội bộ P2. [Phân công/chủ file](../PHAN-CONG-PHASE-2.md). API sau là mục tiêu triển khai, **chưa có trong starter**. Không khai đã pass nếu chỉ mới tạo tài liệu.

Kế thừa giao diện P1 bản1.2 cho luật quán, event tuple, kho, giá/boa, ID; phần dưới thay thế các giới hạn4 kind/3 món/6 cá/1 bếp/1 bàn và tick đồng nhất. Mở rộng không bắt buộc được tắt, không có weapon/net/snake/burn/vendor/ca_ho.

## 1. Module và chiều phụ thuộc

- Ân: gather.py/gather_monsters.py, runner.py/headless.py/inputs.py.
- Duy: gather_fish.py/gather_actions.py, contract.py/inventory.py/scenario.py, manifest.
- Trung: quan.py/quan_customers.py/quan_kitchen.py/quan_validation.py/day_plan.py.
- Đức: day.py/shop.py/live.py/web/index.html.
- `runner → day, gather, quan`; `day → gather, quan, shop, day_plan`; `gather → gather_actions, gather_fish, gather_monsters`; `quan → quan_*`; `quan_customers → quan_kitchen` như P1.
- Không module sim nào import runner/live/scenario. day_plan chỉ xử lý dữ liệu. scenario không import day/runner. Validation ngữ nghĩa day ở DaySim, quán ở QuanSim, cá/quái ở module tương ứng.
- Dữ liệu số đọc tuning; không global random/đồng hồ thực. ID/RNG giữ trong một Session và xuyên các pha/ngày; không reseed mỗi ngày. State input cũng xuyên pha/ngày.

## 2. Context giữa bộ điều phối và sim — dùng dict, không tạo kiểu riêng trên mỗi nhánh

Giữ positional constructor của starter, thêm **keyword-only context=None** ở GatherSim/QuanSim:

```python
GatherSim(tuning, scenario, streams, ids, *, context=None)
QuanSim(tuning, scenario, streams, ids, inventory=None, *, context=None)
ShopSim(tuning, scenario, streams, ids, *, context)  # Đức, module shop.py
DaySim(tuning, scenario, streams, ids, *, days=1)   # Đức, module day.py
```

Tuning luôn là khối tuning đầy đủ, không phải manifest. scenario của GatherSim/QuanSim là **block đã tách** (không bọc gather/quan); DaySim nhận toàn bộ scenario gồm day/gather/quan. inventory của QuanSim là map kind→count, không bọc items.

```python
context = {
    "day": 1,                      # 1..5
    "money": 0, "earned": 0, "reputation": 3.0,
    "upgrades": {"oxygen": 0, "hp": 0},
    "active_upgrades": {"oxygen": 0, "hp": 0},
    "day_plan": {"day": 1, "dishes": {"ca_loc_nuong_trui": 3, "goi_bong_sung": 3},
                 "ingredients": {"ca_loc": 3, "bong_sung": 6}},
    "allowed_dishes": ["ca_loc_nuong_trui", "goi_bong_sung"],
    "oxygen_max_ticks": 1800, "hp_max": 3,
}
```

Các giá trị ví dụ là D1/preset; runtime lấy từ dữ liệu. context là **bản sao chỉ đọc của trạng thái đầu pha** do DaySim truyền, sim không sửa context/upgrades/tuning gốc. Mỗi sim giữ working money/earned/reputation của mình. DaySim sao ba giá trị từ child sau mỗi step, rồi dùng khi dựng pha sau. Mua hàng do ShopSim giữ working upgrades; DaySim đồng bộ upgrades khi Shop kết thúc. Chỉ khi dựng Ngày mới mới sao upgrades→active_upgrades. Không cần child cập nhật lại context sau mỗi tick.

Context None ở mode độc lập: day=1, money/earned=0, reputation theo tuning (scenario.quan.reputation được override), upgrades0; gather base oxy/máu và M1, quan cho toàn bộ menu. `self.allowed_dishes=None` nghĩa toàn menu; day dùng list id món trong kế hoạch. Không biến số suất thành quota bán. Gather lưu `self.day`, `self.oxygen_max`, **self.hp_max**; snapshot hp_max dùng self.hp_max thay t[hp_max].

Đầu mỗi Ngày: refill oxy/máu theo active caps rồi áp fixture player nếu được khai (để test có thể dựng hp/oxy thấp). Validate fixture theo cap hiệu lực. Đây là quy ước nhóm cho fixture; gameplay không fixture luôn hồi đầy.

## 3. Public API mọi sim và Session

GatherSim/QuanSim/ShopSim giữ:

```python
sim.step(inp) -> list[tuple[str, dict]]
sim.snapshot() -> dict                 # state gameplay riêng, không envelope output
sim.phase_tick                        # init0, tăng ở đầu mỗi child.step một lần
sim.time_left_ticks
sim.money, sim.earned, sim.reputation
sim.done, sim.reason
```

Gather thêm inventory_items()->dict và _finish(reason,events), không ghi file. Quan thêm shift_earned=0 đầu ca. Shop giữ stock dư, upgrades working; reason done/time khi kết thúc.

Session giữ API cũ để live/test không vỡ, thêm keyword-only days=1:

```python
Session(mode, tuning, scenario, seed, inventory=None, *, days=1)
session.step(inp) -> list[dict]         # event JSON hoàn chỉnh
session.snapshot() -> dict
session.end_row() -> dict
session.done -> bool
session.initial_events() -> list[dict] # Ân bổ sung: gọi một lần trước snapshot0
session.write_inventory_if_done(path)
```

initial_events ở standalone rỗng; ở day chứa day_start/day_plan/phase_start của D1, tick0, day1, phase gather. Session không tự chạy step trong constructor. run() gọi initial_events một lần rồi snapshot0, gameplay event→snapshot như P1. LiveGame reset cũng lấy initial_events để hiển thị danh sách ngày; không drain lặp trong /state.

### Tick và pause — duy nhất Session xử lý pause, child không xử lý

- tick ngoài tăng1 mỗi frame xử lý; sim_tick chỉ tăng khi chạy gameplay; child.phase_tick do child.step tăng. Các helper không tăng tick.
- Cạnh pause được xét trước: đang chơi→pause phát paused, tăng tick ngoài, **không child.step**, giữ sim_tick/phase_tick/timer.
- Đang pause: vẫn đọc/cập nhật chốt input, nhưng bỏ buy/cạnh hành động, không tăng gameplay. Cạnh pause tiếp theo phát resumed rồi child.step **ngay bước đó**, sim_tick tăng1.
- Bước resume vẫn nhận các hành động cùng frame theo input hiện tại; không phát lại hành động đã bị bỏ ở các frame pause.
- snapshot.state ưu tiên paused khi session pause; còn lại playing/finished. Child không biết pause. Tick end/ticks dùng tick ngoài, không gán sim_tick=tick nữa.
- Không reset InputPlayer/LiveInputs khi đổi pha/ngày. Bool giữ nguyên không sinh cạnh mới; buy chỉ ở frame khai.

### Input — Ân giữ, Đức dùng đúng API

Giữ InputState(move, held, edges), thêm optional keyword-only `buy=None` (str khác rỗng hoặc None), thuộc tính inp.buy. InputPlayer giữ move/bool, nhưng buy **không kế thừa**: mỗi advance mặc định None rồi lấy từ frame hiện tại. Nút lõi: interact, catch, pause, shop_done. attack/photo đúng kiểu nhưng mở rộng tắt thì bỏ qua theo đề, không chạy luật mở rộng; trường lạ/kiểu sai mã2.

LiveInputs.set(move=None, **buttons) cần nhận buy như lệnh riêng, không bool-coerce: Đức gửi buy chuỗi, Ân giữ hàng đợi FIFO mỗi yêu cầu buy; mỗi advance lấy tối đa một lệnh. Lệnh ở frame pause bị consume/bỏ, không giữ đến resume. Bool cạnh như cũ. UI giữ khóa ngoài như starter; không thêm xử lý mô phỏng ở HTTP thread.

## 4. Gather: API Duy/Ân và thứ tự xử lý

### Cá — Duy, gather_fish.py

```python
def init_fish(sim, scenario: dict) -> None: ...
def update_fish(sim, events: list) -> None: ...
def snapshot_fish(sim) -> list: ...
```

Ân dựng t/rng/ids/phase_tick=0 trước gọi init. init tự tạo self.fish và self.random_fish; thay đoạn đọc fish_initial list của P1. Fish có id/kind/pos/heading_deg/age_ticks; init reserve mọi id. random_fish=false: không mặc định, không bơi/sinh, vẫn giữ fixture và bắt được.

update gọi cuối bước nếu gather chưa done; tăng age từng cá đang có, bước age120/240… đổi heading trước move, phản xạ cả phần đường dư. Sinh sau mọi cá bơi tại phase_tick360k; cá mới age0, chưa move. init8 điểm hình học khác nhau, loại+vị trí theo data; stream `fish_spawn` cho chọn loài/điểm/hướng, `fish_turn` cho hướng đổi, hướng chọn đều [0,360). Các lựa chọn enumerate theo kind Unicode rồi x tăng/d tăng để tất định. Trọng số loài hợp lệ chuẩn hóa lại; điểm sinh phải cách mọi cá sống >clearance, sinh tối đa1. Quy tắc RNG/hướng là quy ước nhóm vì đề không chỉ định thuật toán cụ thể.

Hái/bắt giữ gather_node(sim,events), catch_fish(sim,events), nhưng6 kind/yield3 loài, không hard-code4 kind. Snapshot cá sort theo id, có age_ticks; không đưa biến nội bộ ngoài PRD.

### Quái — Ân, gather_monsters.py

```python
def init_monsters(sim, scenario: dict) -> None: ...
def update_monsters(sim, events: list) -> None: ...
def snapshot_monsters(sim) -> list: ...
```

init tạo sim.monsters: {id,kind,pos,waypoints,target_idx,state,state_ticks_left,recoil_dir}. kind=ca_sau, target_idx mặc định1, state patrol/timer0/dirNone. Bỏ mảng: lọc spawns.from_day<=sim.day; []: không quái. Validate fixture, reserve id; không event khởi tạo.

update tự di chuyển mọi quái theo id rồi xét tối đa1 hit gần nhất/id. Cập nhật patrol/chase dựa vị trí người chơi sau move. Quái ở recoil đầu bước thực hiện một bước lùi, giảm timer; kể cả vừa về0 vẫn không detect/hit đến bước sau. Hit đặt recoil60 bắt đầu bước sau, invuln90, hp−1, bỏ floor(len(hold)*loss_ratio) LIFO; phát monster_hit mới gọi sim._faint("monster",events) nếu hp0. _faint do Ân giữ trên GatherSim, bỏ **phần giỏ còn lại**, faint rồi gather_end. Ngạt gọi cùng _faint với cause choke và không rơi nửa giỏ.

Giảm invuln đầu GatherSim.step, không trong helper. Ngạt không kiểm invuln. Quái không thay time_left/phase_tick. Recoil dùng recoil_dist/recoil_ticks mỗi bước (chuẩn2/60m); hướng chốt từ người ra quái tại hit, trùng tâm+x.

### Pipeline GatherSim.step — Ân duy nhất sửa

1. phase_tick++; giảm time_left/cooldown/invuln và hồi cây.
2. Player move/biên; dive/surface; oxy/choke; hp0 faint rồi return.
3. update_monsters; hp0 faint rồi return.
4. Cạnh interact: bến trước rồi gather_node; docked thì return.
5. Cạnh catch: catch_fish, dùng vị trí cá trước khi bơi.
6. time_left0: finish time, return. Nếu còn giờ: update_fish.

snapshot thêm monsters[]/invuln theo đề. Không output attack_cd/ca_ho khi mở rộng tắt. Gather standalone vẫn giữ schema kho cũ, chỉ miền kind tăng6.

## 5. Quán và kế hoạch — Trung

Giữ toàn bộ helper P1, Trung sở hữu cả kitchen từ P2. Quan constructor nhận context; self.allowed_dishes từ context hoặc None. spawn lọc allowed trước available; reserve/tiền/boa/closing giữ luật cũ. Không tự thay tập món giữa ca. phase_tick bắt đầu0 mỗi ca.

```python
# day_plan.py, không import sim/controller
def resolve_day_plans(tuning: dict, overrides=None) -> list[dict]: ...
# trả 5 object {day,dishes,ingredients}, copy mới, theo day1..5
```

tuning.day_plan là mảng chuẩn5 mục. overrides là list cùng dạng (day,dishes,ingredients optional), thiếu ngày giữ preset; từ chối ngày trùng/ngoài1..5, món lạ, số suất không nguyên dương, ingredients khai không khớp recipe. Tính ingredients bằng toàn recipe×suất, không hard-code bảng riêng.

Chuẩn dishes:
- D1: ca_loc_nuong_trui3, goi_bong_sung3.
- D2: ca_loc_nuong_trui2, lau_ca_linh_dien_dien2.
- D3: goi_bong_sung2, canh_chua_ca_loc2, ca_keo_nuong2.
- D4: lau_mam1, ca_loc_nuong_trui2, goi_bong_sung1.
- D5: lau_mam1, lau_ca_linh_dien_dien1, ca_loc_nuong_trui1.

Thực đơn chuẩn: 3 món P1 giữ nguyên; canh_chua_ca_loc={ca_loc1,bong_dien_dien1},8s,90; ca_keo_nuong={ca_keo2},6s,70; lau_mam={ca_linh2,ca_keo1,keo_neo1,bong_dien_dien1},12s,200. 2 bếp B1[2,8]/B2[5,8], bàn T1[9,2]/T2[13,2]/T3[9,6]/T4[13,6].

Validator quán có thêm optional keyword `allowed_dishes=None` nếu cần ở raw validation; validate_quan_state đọc self.allowed_dishes. Trong day, fixture dish ngoài kế hoạch bị BadInput lúc dựng quán. Không áp trước khi biết kho thực.

## 6. DaySim/ShopSim — Đức; giao thức event cho Ân

DaySim public state: mode=day, phase thuộc gather/quan/shop, day1..5, days_completed0..days, phase_tick/time_left của child hiện tại; money/earned/reputation mirror child; upgrades/active_upgrades; done/reason. Giữ child ở `self.current_sim`. days là số ngày chạy từ D1, không phải chỉ số ngày bắt đầu.

```python
DaySim.initial_events() -> list[dict]
DaySim.step(inp) -> list[dict]
DaySim.snapshot() -> dict
# event nội bộ DaySim, CHƯA có tick/type:
{"phase": "gather", "day": 1, "name": "gather_end", "data": {...}}
```

Ngoại lệ có chủ ý: child sim vẫn tuple events như P1; **chỉ DaySim bọc dict kèm phase/day** để giữ provenance trước/sau chuyển pha. Session thêm type=event và tick ngoài hiện tại, không ghi đè phase/day. Không để helper child tự bọc vỏ JSONL. Standalone Session chụp phase trước gọi step và bọc tuple bằng phase đó.

DaySim init: validate day static, resolve_day_plans, tiền/cấp mặc định, start_day1 → dựng gather với context. initial_events: day_start → day_plan → phase_start(gather), tick0 do Session gắn. Các init khác không phát cá/quái spawn event tự thêm.

Mỗi step gọi child đúng một lần (child tự tăng phase_tick), đồng bộ tiền/uy tín. Nếu child done:
- Gather: lấy inventory_items, dựng QuanSim với kho đó + quan template deepcopy + context, phase_start(quan) cùng tick sau gather_end. Ngất vẫn mở quán kho rỗng.
- Quan: lấy stock dư, dựng ShopSim, phase_start(shop) sau quan_end cùng tick.
- Shop: đồng bộ upgrades/money, days_completed++; nếu đủ days: done/reason=days_complete; còn ngày: day++, copy upgrades→active, bỏ kho dư, dựng gather mới, phát day_start/day_plan/phase_start cùng tick.
- Không chạy step child mới trong tick chuyển; snapshot sau step lấy phase mới/phase_tick0. Event kết thúc giữ phase/day cũ. Ngày cuối vẫn phải qua Shop, không kết thúc ở quan_end.

ShopSim scenario là block nội bộ do DaySim dựng `{"stock": <map dư>}`, không thêm top-level scenario.shop vào CLI. Context truyền tiền/uy tín/upgrades. phase_tick init0; mỗi step tăng1/giảm timer max600; xử lý inp.buy trước inp.pressed(shop_done), rồi xét tự hết giờ. shop_done đúng bước cuối ưu tiên reason done. Không có command thì timeout600. Mua thành công cập nhật working upgrades ngay, không active; mua trừ money, earned giữ. unknown/funds/max_level không đổi state; chỉ trả buy_failed, không BadInput cho chuỗi lệnh không hỗ trợ. Đúng giá mua được.

upgrades/active map chuẩn có đủ oxygen/hp, cấp0..2; scenario bỏ map/khóa dùng0; khóa mở rộng tắt không tự áp dụng. Oxygen cấp1 giá200 cap45s, cấp2 giá400 cap60s; hp cấp1 giá250 cap4, cấp2 giá500 cap5. Cấp2 cần cấp1, không mua nhảy.

### UI và thống kê

DayIntro/EveningIntro/DayResult/Summary là màn trình bày UI, **không thêm phase/tick gameplay vào headless** (tối đa21600+600=22200/ngày). DayIntro có4s hoặc skip theo đề ở bản chơi; Đức dùng presentation gate ở live layer trước gọi Session.step, không giả lập bằng input pause để tạo event paused không có yêu cầu. Các màn kết quả khác chốt cách tiếp tục trong UI, không thay event headless. Pause gameplay thực sự luôn qua Session; live không tự trừ timer khi gate/pause.

Summary/DayResult tính từ event served/customer_left/paid và chênh uy tín, theo day. Không thêm keys ngoài contract vào headless để phục vụ UI; live có thể thêm meta/ui riêng như starter. Đầu ngày HUD lấy/cần từ hold và day_plan.ingredients. Không tự thưởng lấy đủ mục tiêu.

## 7. Scenario/CLI và thời điểm kiểm lỗi

Ân CLI: mode gather/quan/day; days chỉ day, int1..5 mặc định1; inventory chỉ quan, inventory-out chỉ gather; day cấm hai file kho flags. Duy loader: day cho top-level day/gather/quan, trả nguyên object; độc lập giữ block riêng như P1. Không mặc định tuning[mode] khi mode=day.

day.money/earned int không âm, khai cả hai nếu có một trong hai; money<=earned. reputation hữu hạn trong0..5. upgrades hợp lệ; day_plan override tính lại ingredients. day cấm quan.stock/quan.reputation ngay ở kiểm static. Fixture gather/quan là template khởi tạo lại mỗi ngày bằng deep copy, không dùng chung list đã mutate.

Lỗi biết lúc khởi tạo (field/kiểu/id/trần/plan) phải mã2 trước output. Tương thích giữa khách/món fixture và kho quán chỉ kiểm khi mở quán bằng hàng thực; nếu lúc đó mới lộ mâu thuẫn thì mã2, có thể đã có log gather. Không cam kết “mọi lỗi day đều phát hiện trước file” khi dữ liệu phụ thuộc tương lai.

Tắt random_fish=false không tắt quái; muốn cô lập cá/oxy thì khai monsters:[]; muốn test quán không sinh khách thì random_customers=false. Khi dùng time_left_ticks fixture rút ngắn ca, lịch cá/khách vẫn bắt đầu phase_tick0.

## 8. Event/output thay đổi — phải khớp PRD

| Event | Data | Chủ phát |
|---|---|---|
| monster_hit | monster_id,hp,lost,pos | Ân; lost chỉ nửa giỏ bị rơi |
| faint | cause choke/monster,lost,hp0 | Ân; lost phần còn lại |
| fish_spawned | id,kind,pos | Duy; chỉ lượt sinh theo lịch |
| day_start / phase_start | {} | Đức/DaySim |
| day_plan | dishes,ingredients | Đức lấy plan Trung |
| paused / resumed | {} | Ân/Session |
| bought | upgrade,level,price,money | Đức/Shop |
| buy_failed | action,reason funds/max_level/unknown | Đức/Shop |
| shop_end | reason done/time | Đức/Shop |

Các event P1 giữ nguyên, day wrapper thêm day. Snapshot day mọi pha có day,day_plan,upgrades,active_upgrades; shop có stock và time_left. end day thêm days_completed; đủ ngày reason days_complete, chưa đủ mà hết --ticks thì tick_limit. Khi gameplay kết thúc đúng bước cuối được cấp, ưu tiên days_complete. Điểm earned+100*floor(reputation), mua hàng không giảm điểm.

## 9. Data manifest và gói tương thích — Duy chuẩn bị, Ân điều phối merge

**Dữ liệu mẫu dùng ngay:** [phase-2-tuning.sample.json](phase-2-tuning.sample.json), chứa contract_version/tuning, không chứa các lệnh build/run. Đây là bản nháp chuẩn để unit test riêng, không phải manifest runtime đã được loader P1 hỗ trợ. Python đọc bằng `json.load(open(path, encoding="utf-8-sig"))["tuning"]`; không dùng load_contract() P1 để nạp vì validator hiện còn bắt fish_initial list6. Duy đối chiếu rồi chuyển dữ liệu vào manifest trong gói merge đồng bộ. Số liệu mẫu không phải bằng chứng gameplay đã đúng.

- contract_version1.1; fish_initial=8 (số, không list), fish_speed1.5, fish_turn_ticks120, fish_max12, fish_spawn_ticks360, clearance1, fish_x[4,96], fish_depths theo đề; đủ3 loài/yield và nodes6.
- monster species.ca_sau patrol1/chase3/detect10/exit16/depths[10,30]/hit1.5/recoil_ticks60/recoil_dist2; spawns M1[60,24]↔[64,24] from_day1, M2[85,18]↔[89,18] from_day3; invuln_ticks90/loss_ratio0.5. Ngưỡng player depth10 theo species.depths[0].
- menu6/quan2bếp4bàn, day_plan5, shop.max_ticks600 và upgrades data đầy đủ. Duy validate plan bằng helper Trung, không hard-code một bảng thứ hai lệch dữ liệu.
- Không merge riêng manifest mới khi GatherSim còn đọc fish_initial như list. Merge đồng bộ loader/config+init_fish+caller GatherSim; data draft có thể gửi patch để test riêng trước.

## 10. Bàn giao và kiểm chứng để làm song song

Không chờ người khác xong toàn module. Test helper với SimpleNamespace/state mẫu trong test riêng; DaySim/Session test với fake child chỉ trong test. Không đưa stub vào main, không optional-import để âm thầm bỏ tính năng chưa có.

Giao sớm: Duy init_fish/data schema; Ân Session/input contract và context GatherSim; Trung resolve_day_plans/context QuanSim; Đức ShopSim/DaySim event envelope. Các thay đổi signature ở đây cần cả caller/callee cập nhật trong cùng gói merge.

Regression P1: giữ luật còn hiệu lực, thay đúng kỳ vọng do đề đổi (6→8 cá, day không còn bị reject, kind mới hợp lệ…). Ghi lý do từng thay đổi test, không xóa assertion để giấu luật sai. Ân tích hợp sửa test dùng chung, mỗi người chỉ viết test_p2 riêng.

Các ca tích hợp bắt buộc: kho6kind hai tiến trình; faint→quán rỗng; event kết thúc pha cũ/snapshot pha mới tick0; pause cả3mode/Shop; frame buy không kế thừa; mua đủ giá/ngày sau mới active; ngày cuối Shop; multi-day M2 từD3; random_fish=false; hiệu năng/tính tất định; UI thực tế. Kết quả phải theo commit bàn giao.

## 11. Quy ước nhóm cần PO xác nhận nếu đề chưa rõ

- RNG hướng cá chọn đều0..360 và thứ tự enumerate ứng viên: quy ước nội bộ, không phải thuật toán giảng viên đã chỉ định.
- Fixture player ghi đè mức refill đầu ngày để dựng test; nâng cấp vẫn giới hạn miền hợp lệ.
- Vòng đời presentation UI không được làm tăng headless tick; chi tiết thao tác skip/result là quyết định UI theo yêu cầu màn hình đề.
- Các giả định quán P1-Q04/Q05 về reserved thiếu kho và waiting/served vẫn là giả định nhóm, không biến thành trả lời chính thức trong P2.

File này chốt đủ API để bắt đầu song song, không bảo đảm tự động hết mọi xung đột. Tuân thủ chủ file, commit base chung và gói merge là điều kiện để hợp đồng có hiệu lực thực tế.
