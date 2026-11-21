# Giao diện dùng chung Phase 1 — bản chốt 1.2

Áp dụng cho Ân, Duy, Trung, Đức. Đọc file này trước khi code. Tài liệu chốt cách chia module nội bộ dựa trên PRD-0/Test Contract v1.0 đã đọc trên lab board; không thay thế đề. **Các API mới bên dưới chưa được triển khai trong starter.** Không hiểu chữ “chốt” là game đã đáp ứng contract.

Nếu phần mô tả giao diện trong `docs/PHAN-CONG-PHASE-1.md` chưa đủ chi tiết, dùng file này làm chuẩn kỹ thuật. Thay đổi giao diện cần báo Ân và người gọi hàm, cập nhật tài liệu cùng thay đổi code. Không tự đổi tên/kiểu trả về trên nhánh riêng.

## 1. Quyền sở hữu và chiều phụ thuộc

| Người | Module chính | Trách nhiệm tích hợp |
|---|---|---|
| Ân | `chonoi/sim/gather.py` | Constructor, step, oxy/máu/ngất, snapshot gather; gọi helper Duy |
| Duy | `chonoi/sim/gather_actions.py` | Hái/bắt; kiểm chứng kho và hai tiến trình |
| Trung | `chonoi/sim/quan_customers.py`, `chonoi/sim/quan_validation.py` | Khách, giữ chỗ, timer quán, khách rời, validation |
| Đức | `chonoi/sim/quan.py`, `chonoi/sim/quan_kitchen.py`, `chonoi/web/index.html` | Constructor/step/snapshot quán, bếp/phục vụ/thu tiền, UI |

Chiều import: `gather → gather_actions`; `quan → quan_customers, quan_kitchen, quan_validation`; `quan_customers → quan_kitchen` để gọi pay/discard. Kitchen **không import customers hoặc quan**; actions không import gather. Validation không import QuanSim. Dùng helper ids/rng/errors của starter.

Để Trung có thể import/test init, timer, spawn trước khi Đức bàn giao kitchen, đặt import `pay_customer, discard_order` **bên trong `resolve_departures`**, không ở đầu quan_customers.py. Test resolve_departures cần hai helper thật của Đức hoặc patch trong test riêng. Không tạo quan_kitchen.py thay Đức chỉ để vượt lỗi import. Test helper độc lập dùng `types.SimpleNamespace` hoặc fixture state trong file test của người làm; chưa cần import QuanSim đã tích hợp.

Không tạo class sim thứ hai, không đổi constructor/public API runner. Khung dùng chung do Ân nhận sửa nếu phát hiện cần thiết; báo nhóm trước. Hai phía có thể test helper với đối tượng trạng thái nhỏ trong test riêng, nhưng không đưa mock/stub vào sản phẩm bàn giao.

## 2. Quy ước mọi hàm

- `sim`: chính đối tượng GatherSim/QuanSim đang chạy, không phải snapshot copy. Hành động sửa trực tiếp trạng thái được cho phép bên dưới.
- `events`: list dùng chung cho một bước; append tuple `(name: str, data: dict)`. Không replace list, không tự ghi tick/type/phase/JSONL.
- Hàm hành động trả `None`. Hàm truy vấn `available_stock` trả dict mới. Validation thành công trả None; sai ném `chonoi.errors.BadInput`.
- Không có mục tiêu/không đủ điều kiện gameplay: không ném lỗi; không làm gì hoặc phát event thất bại theo PRD. Fixture sai: BadInput trước khi mở output.
- Mỗi event dùng payload mới; sao chép list/dict sẽ còn bị sửa, tránh event lịch sử thay đổi theo state.
- Thời gian trong state là số tick nguyên không âm; quy đổi giây bằng `int(round(value * 60))`, giống starter. Chỉ định dạng tọa độ ở writer, không làm tròn trước xét bán kính.
- So id dùng `id_key`/`sort_by_id`, không so chuỗi trực tiếp với id thực thể. Dish id/kind dùng thứ tự Unicode. Cùng seed/inputs phải cho đầu ra giống byte.
- Helper không xử lý cạnh phím. Hai hàm step là nơi duy nhất kiểm `inp.pressed(...)` và gọi action đúng một lần/cạnh. Helper vẫn kiểm điều kiện trạng thái như tay đầy/cooldown.
- Hai bộ đếm có vai trò khác nhau: Session tăng tick output sau sim.step; Đức tăng `sim.phase_tick` đúng một lần đầu step để helper biết lịch hiện tại. Trong Phase 1 sau mỗi bước chúng bằng nhau; không sửa runner để tăng phase_tick lần nữa.

## 3. Dữ liệu gather — Ân và Duy

| Thuộc tính | Kiểu/ý nghĩa | Bên được sửa |
|---|---|---|
| `t` | `tuning["gather"]`, chỉ đọc | Không sửa tuning |
| `pos`, `vel`, `heading` | `[x,d]`, vận tốc, góc | Ân |
| `oxygen_ticks`, `oxygen_max`, `hp`, `zero_oxy_ticks` | Oxy/máu/ngạt | Ân |
| `hold` | `list[str]` kind, mới nhất cuối | Duy thêm; Ân xóa khi ngất |
| `nodes` | `{id,kind,pos,regrow_ticks}` | Duy đặt hồi khi hái; Ân giảm hồi |
| `fish` | `{id,kind,pos,heading_deg}` | Duy xóa đàn khi bắt thành công |
| `catch_cd_ticks` | Hồi bắt | Duy đặt; Ân giảm |
| `time_left_ticks`, `done`, `reason` | Ca và kết thúc | Ân |

Không thêm `hold_count` như biến riêng; snapshot tính bằng len(hold). `_at_surface()`, `_in_dock()`, `_finish(reason, events)`, `inventory_items()` giữ giao diện starter.

```python
# chonoi/sim/gather_actions.py — Duy
def gather_node(sim, events: list) -> None: ...
def catch_fish(sim, events: list) -> None: ...
```

`gather_node`: chỉ mặt nước, chọn nút ready gần nhất trong bán kính (kể cả mép), hòa theo id. Đủ chỗ: thêm node_yield, đặt regrow_ticks, phát gather. Thiếu chỗ: hold_full; không sửa cây/giỏ.

`catch_fish`: chỉ dưới nước và catch_cd_ticks=0; chọn đúng đàn gần nhất, hòa theo id. Đủ chỗ nhận toàn bộ fish_yield[kind], xóa đàn, đặt cooldown và phát fish_caught. Thiếu chỗ phát hold_full, giữ đàn/cooldown; không thử đàn khác. Không có cá thì không đặt cooldown.

Hai hàm không giảm timer, không kiểm bến, không kết thúc ca, không ghi kho. Ân gọi sau di chuyển/oxy. Khi ngất, Ân lấy `lost = list(reversed(hold))`, xóa hold, phát faint rồi `_finish("fainted", events)` và return.

## 4. Dữ liệu quán — Trung và Đức

Đức giữ constructor như starter: `(tuning, scenario, streams, ids, inventory=None)`. Thêm các thuộc tính nội bộ sau trước khi gọi helper Trung:

```python
self.phase_tick = 0
self.random_customers = scenario.get("random_customers", True)
# Các thuộc tính còn lại giữ tên starter:
# t, menu, rng, ids, pos, vel, stock, hand, stoves, tables,
# time_left_ticks, reputation, money, earned, shift_earned, done, reason
```

`phase_tick` là số bước gameplay đã chạy, không tính từ thời gian ca còn lại. Runner vẫn sở hữu tick output. Không thêm counter độc lập trong module khách.

Không cần thêm thuộc tính `patience_max_ticks`: khi tính boa dùng `int(round(sim.t["patience_s"] * 60))`. Thuộc tính helper cần được liệt kê ở đây trước khi thêm phụ thuộc mới; không tự dùng tên như sim.tick, sim.tuning hoặc sim.orders vì starter không có chúng.

### 4.1. Khách/đơn

```python
{
    "id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
    "order_tick": 0,
    "state": "waiting",                  # waiting | eating
    "patience_ticks_left": 3600,         # lấy tuning, số ở đây minh họa preset
    "eat_ticks_left": 0,
    "order_status": "reserved",         # reserved | assigned | unfulfillable | served
    "reserved": {"ca_loc": 1}
}
```

- Không có collection orders riêng; `customer.id` chính là `order_id`. `tables[].customer_id` suy từ khách khi snapshot.
- waiting/reserved: giữ đúng công thức, chưa có món vật lý.
- waiting/assigned: reserved rỗng, đúng một payload món ở bếp hoặc tay khớp khách/đơn/món.
- waiting/unfulfillable: reserved rỗng, không có món. Không tự đổi sang reserved mỗi bước; Phase 1 không có luật tự nhận lại đơn.
- eating/served: reserved rỗng, không còn payload bếp/tay của đơn, có eat_ticks_left dương lúc khởi tạo; `base_price` và `tip` được chốt khi phục vụ.
- Khi vừa trả tiền/rời, xóa khách khỏi list; không lưu state left trong snapshot.

Vòng đời chính: reserved → assigned (bắt đầu nấu) → served/eating (phục vụ) → rời (trả tiền). Khách waiting có thể rời từ mọi order_status nếu hết kiên nhẫn/đóng ca.

Default khi fixture bỏ trường: state=waiting, order_tick=0, order_status=reserved, patience_ticks_left=patience_s quy đổi tick, eat_ticks_left=0. Reserved thiếu chỉ được suy theo recipe khi order_status=reserved; trạng thái khác mặc định reserved rỗng. Không mặc định base_price/tip cho khách eating để che việc fixture thiếu giá đã chốt. Trường đã khai sai không được thay bằng default. ID khách, table_id và dish_id phải có và hợp lệ.

### 4.2. Bếp và món

```python
# Payload món trên bếp hoặc tay
{"order_id":"C1", "dish_id":"ca_loc_nuong_trui", "base_price":60}

# Bếp
{"id":"B1", "pos":[2,8], "state":"idle", "dish":None,
 "cook_ticks_left":0, "ready_ticks":0}
```

Idle: dish=None, timer bằng 0. Cooking: có payload, cook_ticks_left dương. Ready: có payload, cook_ticks_left=0, ready_ticks không âm. Tay là None hoặc một payload. `base_price` là int tiền món trước boa, chốt từ menu khi bắt đầu nấu; không tra lại giá lúc thu tiền. Không thêm tip vào payload món.

### 4.3. Kho và ai được sửa

- stock là tồn vật lý. reserved trong mỗi khách là phần đã giữ nhưng chưa dùng. Chỉ khách reserved giữ nguyên liệu.
- Trung thêm reserved khi nhận đơn, nhả khi khách rời. Đức trừ stock và xóa reserved khi bắt đầu nấu.
- available_stock tính stock trừ tổng reserved, không sửa nguồn; trả đủ 4 kind, kể cả 0, để gọi `.get` hay indexing đều nhất quán.
- Không clamp kho khả dụng âm để giấu lỗi. Fixture quá giữ phải BadInput; runtime âm là lỗi cần sửa.
- Đức sửa bếp/tay/order_status khi nấu/phục vụ; Trung sửa customers khi init/sinh/rời và timer qua advance_timers.
- Đức sửa tiền và uy tín do boa trong pay_customer; Trung sửa uy tín khi khách rời vì patience. Cả hai kẹp theo reputation_min/max.

## 5. API quán đã chốt

### 5.1. Trung: quan_customers.py

```python
def init_customers(sim, scenario: dict) -> None: ...
def available_stock(sim) -> dict: ...
def advance_timers(sim) -> None: ...
def resolve_departures(sim, events: list) -> None: ...
def spawn_customer(sim, events: list) -> None: ...
```

| Hàm | Điều kiện và tác động |
|---|---|
| init_customers | Mọi kho/bếp/tay/bàn/tuning/ids đã dựng. Hàm tự gán sim.customers=[] trước khi deep-copy và chuẩn hóa khách từ scenario.get("customers", []); caller không cần dựng customers. Thiếu reserved ở đơn reserved thì cấp đúng recipe theo order_tick rồi id bàn, không cấp một phần khi thiếu kho. Giữ nguyên giá trị khai sai để validation báo lỗi; không sửa fixture sai thành đúng. Reserve mọi id khách. Không event, không sinh khách ngẫu nhiên |
| available_stock | Trả map mới 4 kind; không đổi stock/reserved, không RNG |
| advance_timers | Giảm time_left_ticks đúng một lần; giảm cook của bếp cooking; tăng ready_ticks chỉ với bếp đã ready ở đầu bước; giảm patience khách waiting, eat khách eating. Không chuyển ready, không trả tiền, không xóa khách, không tăng phase_tick |
| resolve_departures | Duyệt theo id bàn. Khách eating timer 0 trả finished_eating; nếu đóng ca, eating còn lại trả closing. Gọi pay_customer rồi xóa khách. Waiting: đóng ca rời closing không phạt; nếu chưa đóng ca và patience=0 rời patience có phạt. Khi rời nhả reserved, gọi discard_order, xóa khách. Không quan_end, không sinh khách |
| spawn_customer | Chỉ khi random_customers=true, ca còn giờ và phase_tick đến lịch. Điều kiện chính xác: phase_tick >= first_customer_tick VÀ (phase_tick−first_customer_tick) % interval_ticks == 0, interval_ticks quy đổi từ customer_interval_s. Không bàn: im lặng. Có bàn nhưng không món: no_dish. Có món: chọn bàn id nhỏ nhất, dish từ danh sách sorted đủ nguyên liệu bằng `sim.rng.get("customer_orders").choice(candidates)`, cấp `sim.ids.new("C")`, giữ recipe, timer đầy, phát customer_arrived. Không RNG khi không bàn/không món; không giữ hàng đợi hay sinh bù lượt đã bỏ |

Chỉ gọi pay_customer một lần cho mỗi khách; dùng nhánh/continue để khách ăn xong đúng lúc đóng ca không bị trả hai lần. Sau khi rời, món cũ không còn ở bếp/tay. Nếu ca còn giờ và đúng lịch, có thể sinh khách mới vào bàn vừa trống ở cuối bước.

### 5.2. Đức: quan_kitchen.py

```python
def finish_cooking(sim, events: list) -> None: ...
def interact(sim, events: list) -> None: ...
def pay_customer(sim, customer: dict, reason: str, events: list) -> None: ...
def discard_order(sim, order_id: str) -> None: ...
```

| Hàm | Điều kiện và tác động |
|---|---|
| finish_cooking | Duyệt bếp theo id; cooking có cook_ticks_left=0 → ready, ready_ticks=0, phát dish_ready. Không giảm timer |
| interact | Gọi một lần khi cạnh E, sau di chuyển. Chọn đối tượng trong radius theo (khoảng cách, bếp trước bàn, id_key). Chọn trước rồi xét có thực hiện được không; không dùng được thì bỏ lượt. Mỗi lần chỉ nấu HOẶC lấy HOẶC phục vụ |
| pay_customer | reason chỉ finished_eating/closing, customer đã served/eating. Cộng amount=base_price+tip vào money/earned/shift_earned. Tip dương mới tăng uy tín. Phát paid với uy tín cập nhật nội bộ; payload paid đúng mục 7. Không xóa khách/giữ chỗ/món, không giảm timer. Caller bảo đảm không gọi lại |
| discard_order | Xóa payload đúng order khỏi tay/bếp; bếp tương ứng về idle, dish=None, cook/ready timer=0. Không hoàn stock, không xóa khách, không event tự thêm |

Trong interact:

- Bếp idle: chọn waiting/reserved cũ nhất `(order_tick, id_key(table_id))`. Trừ stock đúng reserved, xóa reserved, đặt assigned; tạo payload, cooking với timer đầy, phát cook_started. Không tự tạo đơn mới. Không thêm điều kiện tay trống cho bắt đầu nấu vì PRD chỉ yêu cầu tay trống khi lấy món.
- Bếp ready: chỉ tay trống mới lấy payload, đưa bếp về idle, phát dish_picked. Không tiếp tục nấu trong cùng lần nhấn.
- Bàn: tay chứa đúng order_id của khách waiting/assigned mới phục vụ; xóa hand, chuyển served/eating, timer ăn đầy, chốt base_price/tip trên customer. Dùng patience còn lại sau advance_timers chia `int(round(sim.t["patience_s"] * 60))`; đạt ngưỡng kể cả bằng thì tip=floor(base_price×tip_rate), còn lại 0. Phát served; chưa thu tiền.

### 5.3. Trung: quan_validation.py

```python
def validate_quan_fixture(scenario: dict, tuning: dict) -> None: ...
def validate_quan_state(sim) -> None: ...
```

`validate_quan_fixture` là **bổ sung đã chốt** so với file phân công: kiểm raw field/kiểu dữ liệu/enum của customer, hand, stove/table override, random_customers, reputation trước khi chuẩn hóa có thể làm mất dấu trường sai. Có thể dựa vào kiểm tra cấu trúc có sẵn trong scenario.py nhưng phải bổ sung phần thiếu. Không sửa scenario.py để tránh xung đột.

`validate_quan_state` kiểm sau chuẩn hóa: bàn/id/liên kết có thật, trạng thái/timer phù hợp, giữ đúng công thức và không quá stock, một món/đơn assigned, không trùng bếp/tay, món khớp đơn, eating có giá/tip/timer đúng, unfulfillable không có món. Từ chối fixture mâu thuẫn bằng BadInput trước output; không phát event, không tiêu RNG, không sửa gameplay.

Phạm vi của cả hai hàm là đầu vào/quá trình dựng fixture, không gọi lại full validation giữa từng helper runtime: cooking có cook_ticks_left=0 ngay sau advance_timers và trước finish_cooking là trạng thái chuyển tiếp hợp lệ; eating có timer=0 trước resolve_departures cũng vậy. Nếu cần assertion nội bộ sau toàn bước thì viết riêng, không dùng validator fixture để bác trạng thái chuyển tiếp.

## 6. Thứ tự gọi bắt buộc

### Constructor quán — Đức tích hợp

1. `validate_quan_fixture(scenario, tuning)`.
2. Dựng t/menu/rng/ids/player/stock/hand/timers/reputation/stoves/tables/tiền/done như starter; thêm phase_tick/random_customers.
3. `init_customers(self, scenario)` thay đoạn dựng customers thô hiện có, không chạy cả hai.
4. `validate_quan_state(self)` rồi constructor trả về. Runner mới ghi snapshot tick 0 sau đó.

### Gather step — Ân tích hợp

```python
# Đây là pseudocode thứ tự; không copy nguyên như mã hoàn chỉnh.
events = []
# giảm time_left, cooldown, hồi cây; node_regrown theo id
# di chuyển, dive/surface, oxy, choke/faint
if self.done:  # ngất: đã phát faint rồi gather_end, giỏ rỗng
    return events
if inp.pressed("interact"):
    if self._in_dock():
        self._finish("docked", events)
        return events
    gather_node(self, events)
if inp.pressed("catch"):
    catch_fish(self, events)
if self.time_left_ticks == 0:
    self._finish("time", events)
return events
```

### Quán step — Đức tích hợp

```python
events = []
self.phase_tick += 1
advance_timers(self)              # xóa dòng giảm time_left cũ trong step
finish_cooking(self, events)
self._move(inp)
if inp.pressed("interact"):
    interact(self, events)
resolve_departures(self, events)
if self.time_left_ticks == 0:
    self.done, self.reason = True, "time"
    events.append(("quan_end", {
        "reason": "time", "money": self.money, "earned": self.earned,
        "shift_earned": self.shift_earned, "reputation": self.reputation,
    }))
    return events
spawn_customer(self, events)
return events
```

Step không gọi lại khi done (Session đã dừng). Cooldown đặt tại t dùng lại t+L. Action diễn ra sau giảm timer; món mới nấu/khách mới ăn không giảm timer lần nữa trong cùng bước. Món vừa chín có thể lấy trong cùng bước nếu có cạnh E. Khách mới chỉ tham gia bước sau. Hết giờ gather xét sau action; quán phục vụ trước khách rời, vì vậy deadline bằng nhau vẫn phục vụ được.

## 7. Event và kho — không tự đổi payload

| Event | Data bắt buộc | Bên append |
|---|---|---|
| dive / surface | pos | Ân |
| oxygen_empty | oxygen_ticks: 0 | Ân |
| choke | hp sau trừ | Ân |
| faint | cause: choke, lost: list kind theo LIFO, hp: 0 | Ân |
| node_regrown | node_id | Ân |
| gather | node_id, kind, amount | Duy |
| fish_caught | fish_id, kind, yield | Duy |
| hold_full | action: gather/catch, node_id hoặc fish_id, required, free | Duy |
| gather_end | reason: time/docked/fainted, inventory: object kho | Ân |
| customer_arrived | order_id, table_id, dish_id | Trung |
| no_dish | object rỗng | Trung |
| cook_started | stove_id, order_id, dish_id, items: list kind, base_price | Đức |
| dish_ready / dish_picked | stove_id, order_id, dish_id | Đức |
| served | order_id, table_id, dish_id, patience_ticks_left, base_price, tip | Đức |
| paid | order_id, table_id, base_price, tip, amount, reason | Đức |
| customer_left | order_id, table_id, reason: patience/closing, reputation sau đổi | Trung |
| quan_end | reason: time, money, earned, shift_earned, reputation | Đức |

`cook_started.items` là mảng nguyên liệu lặp theo lượng, sort kind, ví dụ `["bong_dien_dien","ca_linh","ca_linh","ca_linh"]`. `lost` giữ LIFO, không sort. paid không tự thêm reputation vào payload. Không event tùy tiện như order_reserved hoặc dish_discarded trong headless.

Kho file `{"items":{"bong_sung":2,"ca_loc":1}}`: chỉ items, lượng nguyên không âm, bool không tính là int hợp lệ, chỉ 4 kind. Bỏ lượng 0 khi ghi. Không chứa tiền/uy tín. Runner ghi một lần khi gather_end, khớp inventory trong event, atomic replace. Tick_limit chưa kết thúc không tạo/ghi đè file, ngất ghi items rỗng. Không thêm đường ghi từ gather_actions.

## 8. UI và snapshot

- Giữ snapshot theo mục D/E của PRD và cấu trúc starter: player/nodes/fish/hold cho gather; player/stock/hand/stoves/tables/customers cho quan; trường chung do runner cấp.
- snapshot.stock vẫn là **tồn vật lý**. Không đổi nghĩa thành khả dụng. UI tính khả dụng từ stock trừ reserved để hiển thị; không ghi ngược state và không bổ sung field headless chỉ để tiện UI.
- UI dùng `/state`, `/input`, `/restart` hiện có. Input HTTP là trạng thái phím; LiveInputs chuyển thành cạnh. File inputs headless theo Test Contract, không phải gửi nguyên JSON HTTP vào file.
- Không thêm endpoint để bypass luật. Cả live/headless dùng Session/Sim; helper không biết cửa sổ hoặc đồng hồ thực.

## 9. Dữ liệu mẫu và bàn giao tối thiểu

Trong `docs/contracts/phase-1-fixtures/` có 4 file: dock.json, dock-inputs.json, quan-reserved.json, quan-ready.json. Đây là đầu vào phát triển độc lập, không phải bằng chứng test đã pass.

- Ân test oxy/ngất bằng scenario riêng trong test của Ân.
- Duy dùng dock + input để kiểm kho; không cần chờ thu hoạch hoàn chỉnh.
- Trung dùng quan-reserved; random_customers=false giúp kiểm fixture không bị sinh thêm.
- Đức dùng quan-reserved để nấu; quan-ready để lấy món rồi đi tới bàn phục vụ. Nhấn true rồi false rồi true cho hai lần tương tác.
- Fixture quán đã đặt người chơi tại bếp, không phải tại bàn; muốn test phục vụ tức thì, tạo fixture hợp lệ đặt player tại bàn, bếp idle, payload trên hand, khách assigned.

Nhịp bàn giao: Trung gửi init/validation/khách mẫu sớm; Đức gửi pay/discard sớm; Duy gửi hai action sớm. Người tích hợp không merge import thiếu. Kiểm chức năng riêng trước, rồi kiểm cả pipeline và JSONL/byte determinism trên main. Không giữ stub trên main để báo xanh giả.

## 10. Chống xung đột Git và điều kiện tích hợp

1. Cả bốn lấy cùng commit chứa **giao diện 1.2** trước khi code. Người đã bắt đầu nhánh cần cập nhật tài liệu mới và rà tên hàm, không ghi đè code đang làm để quay lại starter.
2. Chỉ chủ file sửa file sản phẩm theo mục 1. Muốn sửa file người khác: gửi patch hoặc mô tả cho chủ file tích hợp. Không chạy formatter toàn repo, đổi tên file hay sửa tuning trên nhánh tính năng.
3. Test tách thành test_p1_an/duy/trung/duc.py, bằng chứng vào thư mục riêng. Không cùng thêm test vào test_smoke_p1.py hoặc sửa helpers.py. Test cần thêm fixture thì đặt trong thư mục riêng theo tên người, không sửa mẫu contract chung.
4. TEAM/AGENTS/contract và khung chung: Ân giữ; verification: Duy; clarify và nhật ký AI chung: Trung; README/CREDITS/UI: Đức. Mỗi người gửi dòng nhật ký AI cho Trung và tự giữ bản ghi gốc trong proof riêng. Retro nhóm do Trung tập hợp khi đến mốc; members mỗi người một file.
5. Hai file phân công/giao diện và fixtures chung do Ân giữ sau khi phát hành. Người khác báo đề xuất thay vì tự sửa; thay đổi giao diện tăng số phiên bản và báo các bên gọi.
6. Người làm bàn giao commit SHA, file, API, lệnh test và kết quả. Ân tích hợp từng nhánh trên main và chạy kiểm tra; Đức hỗ trợ ghép pipeline quán. Không merge nhánh chứa import module chưa có. Có thể tích hợp helper chưa được gọi vào main trước, sau đó mới merge code caller.
7. Thứ tự merge khả thi: helper Duy → gather caller Ân; kitchen Đức (chưa nối caller mới) và customers/validation Trung → quan caller Đức. Nếu Đức muốn bàn giao kitchen trước, tạo commit riêng chỉ chứa kitchen/test tương ứng, chưa sửa quan.py import customers còn thiếu.
8. Trước main/tag: chạy test công khai + test các lát, smoke kho, vòng đời khách/bếp, kiểm tính tất định và chơi HUD. Test helper pass chưa đủ kết luận pipeline pass.

Không thể bảo đảm tuyệt đối không xung đột Git; các quy tắc trên loại phần sửa chồng chủ động và làm rõ phụ thuộc. Không còn yêu cầu phải chờ cả module khác xong mới bắt đầu viết/test helper riêng.

## 11. Quyết định bổ sung cho câu hỏi của Trung — bản 1.2

Mục này chốt cách triển khai nội bộ, không phải câu trả lời chính thức của giảng viên. Các điểm suy luận/PRD chưa rõ được đánh dấu; PO cần xác nhận điểm thiếu kho và cặp state/status nếu có kênh hỏi. Trong lúc chờ, code theo quyết định dưới đây, không để mỗi module chọn một cách.

| # | Vấn đề | Quyết định dùng chung | Cơ sở / mức độ chắc chắn |
|---|---|---|---|
| 1 | ID khách tự sinh | Dùng C1, C2… qua sim.ids.new("C"). Reserve mọi ID khách fixture trước khi sinh; có C10 thì khách tự sinh tiếp là C11. Không tái dùng ID khi khách rời; không cấp ID cho lượt bỏ vì bàn bận/không món | Prefix C là quy ước nhóm; nối tiếp hậu tố lớn nhất là contract |
| 2 | Giá/boa trên customer trước phục vụ | Không có khóa base_price/tip trong customer snapshot cho đến khi phục vụ. Không null, không mặc định 0. Đơn assigned vẫn có base_price đã chốt trong payload món bếp/tay, không có tip ở payload đó. Khi served/eating, customer có cả base_price và tip; tip=0 khi không được boa | Quy ước serialize, phù hợp vòng đời dữ liệu |
| 3 | Khách eating lúc đóng ca | Chỉ paid, rồi xóa khách; không customer_left cho cùng khách. Timer ăn vừa về 0: reason=finished_eating; timer còn dương: reason=closing. Khách vừa được phục vụ trong bước đóng ca cũng paid/closing. quan_end phát sau mọi xử lý khách | Suy luận từ thứ tự luật F; tránh hai event rời cho một người |
| 4 | Fixture reserved thiếu trường reserved và không đủ kho | BadInput → mã 2, trước output; không cấp một phần, không tự chuyển unfulfillable. Dựng các phần giữ khai rõ trước để biết tổng cam kết; suy phần thiếu theo (order_tick, id bàn), rồi kiểm tổng không vượt tồn. Nếu muốn dựng khách không thể phục vụ, fixture phải khai order_status=unfulfillable và reserved={} ngay | Chốt bảo thủ theo câu “giữ … quá tồn → mã 2”; thứ tự cấp chưa đủ để suy ra cơ chế tự đổi trạng thái. PRD chưa rõ, cần PO xác nhận |
| 5 | Fixture waiting + served | Không hợp lệ: BadInput/mã 2. served đi cùng eating; eating phải có served. Không tự chuyển waiting thành eating hay đoán timer/giá/boa | Quy ước nhóm dựa trên vòng đời ở F; PRD chỉ ghi rõ một chiều nên cần PO xác nhận |
| 6a | order_tick dương khi phase_tick=0 | Cho phép số nguyên không âm, không bool; chưa áp điều kiện order_tick <= phase_tick vì PRD không ghi trần này. Khách fixture đã hiện diện từ tick 0, order_tick dùng để xếp ưu tiên, không hẹn giờ sinh/không làm bước đầu chờ đến order_tick | Quy ước fixture theo miền đã nêu; gameplay tự sinh luôn ghi phase_tick hiện tại. Nếu PO yêu cầu cấm tương lai, sửa validator và test đồng bộ |
| 6b | waiting có patience_ticks_left=0 | Cho phép tại fixture. Snapshot tick 0 giữ 0; bước đầu vẫn xử lý interact trước rời, phục vụ đúng đơn được tính, nếu không thì rời vì patience (hoặc closing nếu hết ca). Không đuổi/xử lý tiền ngay trong constructor | Phù hợp timer không âm và thứ tự F. eating vẫn cần eat_ticks_left dương lúc dựng |
| 7 | Uy tín giảm do khách bỏ đi | Kẹp trong [reputation_min,reputation_max], giống đường cộng boa; customer_left.reputation là giá trị sau kẹp. closing không trừ. Ví dụ preset: uy tín 0.2 giảm 0.5 → 0 | Quy ước nhóm theo miền uy tín; PRD nêu kẹp tường minh ở boa |
| 8 | Giá payload khác menu hoặc timer nấu lớn hơn thời gian chuẩn | Không bác fixture chỉ vì khác menu/timer chuẩn: base_price phải int dương, cook_ticks_left của cooking phải int dương, không bool. Món/đơn/liên kết phải khớp. Ready vẫn cook_ticks_left=0. Giữ giá payload khi phục vụ/thu tiền; không ép lại menu. Gameplay bắt đầu nấu luôn lấy giá/thời gian từ tuning | PRD không ghi ràng buộc bằng giá hiện tại hoặc trần timer nấu; không thêm điều kiện từ chối ngoài đề |

Điểm 4 không có nghĩa chấp nhận reserved khai rõ khác recipe hoặc quá tồn: những trường hợp đó luôn mã 2 theo contract. Việc cấp theo thứ tự chỉ quy định thứ tự xử lý xác định; hiện không dùng thứ tự đó để tự hạ đơn sang unfulfillable.

Các quy tắc này áp dụng cho cả validator của Trung lẫn serializer/thu tiền của Đức. Đức phải bỏ qua hoặc không serialize các trường giá/boa customer chưa phục vụ; fixture có giá payload khác menu vẫn dùng giá payload khi chuyển lên customer lúc phục vụ. Không sửa payload giá trong quá trình chuẩn hóa.

Test liên module cần có: C10 → C11; assigned không có giá/boa trên customer nhưng món có giá; closing eating chỉ một paid; finished_eating ưu tiên closing khi timer vừa 0; thiếu kho suy giữ → mã 2 và chưa ghi output; waiting/served → mã 2; order_tick dương vẫn hiện ngay; patience=0 được phục vụ bước đầu; uy tín không âm; payload giá 75/menu 60 được thu theo 75; cooking timer lớn hơn chuẩn vẫn được nạp. Đây là danh sách test cần triển khai, không phải kết quả đã chạy.

Sau khi dùng file này, mỗi người chỉ cần báo: “Đã đọc giao diện 1.2; đang làm phần <tên>; thay đổi API cần báo trước”. Đây là trao đổi nội bộ nhóm tự thực hiện, tài liệu không tự gửi thông báo cho ai.
