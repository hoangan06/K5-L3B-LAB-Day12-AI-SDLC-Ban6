# Phân công và hướng dẫn Phase 1 — Ân, Duy, Trung, Đức

Tài liệu phối hợp của nhóm 4 người, lập từ PRD-0 / Test Contract v1.0 trên [lab board](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg#phase-1) và starter trong repo. Đây là quyết định triển khai của nhóm; tiêu chí nghiệm thu vẫn theo PRD. Tên hàm và file mới bên dưới là giao diện bàn giao đã chốt, **chưa được triển khai trong starter**.

## 1. Các quyết định đã chốt

1. Dùng Python 3 và thư viện chuẩn, giữ starter; không đổi engine trong Phase 1. Dùng cùng phiên bản Python 3.12 nếu có thể.
2. Giữ nguyên toàn bộ preset gameplay trong `game.contract.json`. Chỉ điền mã nhóm và `team_size: 4`; không tự thêm luật Phase 2, không làm cá bơi, cháy món hoặc mode `day`.
3. Mục tiêu: chơi được `gather` và `quan`, nối qua file kho bằng hai tiến trình; HUD đủ đọc. Dùng hình khối có sẵn, chưa ưu tiên trang trí.
4. Ân giữ `gather.py` và tích hợp chung; Đức giữ `quan.py` và UI. Duy và Trung viết module riêng để giảm xung đột.
5. Luật chỉ chạy trong sim; UI đọc snapshot, gửi input. Không viết bản luật riêng cho headless và live.
6. Dùng nhánh ngắn `p1/an`, `p1/duy`, `p1/trung`, `p1/duc` từ cùng một commit xuất phát. Ân tích hợp vào `main` sau khi người làm kiểm tra phần mình. Có thể merge hoặc dùng PR ngắn; không bắt buộc chờ approval trên GitHub. Không force-push nhánh chung.
7. Người làm tự viết test luật và lưu bằng chứng. Duy tập hợp ma trận kiểm chứng, không kiểm thử thay cả nhóm. Không sửa test công khai để che lỗi.
8. Đề nghị trao đổi tối đa 2 phút khi bất đồng, sau đó Ân chốt kỹ thuật; Trung ghi quyết định. Vướng hơn 10 phút phải báo cả nhóm và kích hoạt người dự phòng.
9. Mỗi người tự ghi nhật ký AI và phản tư cá nhân; không bịa token, kết quả test hoặc đóng góp. Tối thiểu 3 commit có nội dung/người tính cho **cả buổi lab**, không riêng Phase 1.
10. Không tự đổi kho, snapshot, event, input hoặc tuning. Người muốn đổi báo Ân và các bên bị ảnh hưởng, Trung ghi lý do trước khi tích hợp.

Chỉ còn thông tin hành chính cần nhóm điền: tên/mã nhóm, GitHub handle thật của 4 người, URL fork public, kênh liên lạc và giờ bắt đầu thực tế. Không đoán GitHub handle từ tên. Ân thu thập để điền `TEAM.md`; thời hạn trong tài liệu tính từ lúc bắt đầu phase.

## 2. Bảng sở hữu và người dự phòng

| Người | Việc chính | File được chủ động sửa/tạo | Vai quy trình | Dự phòng |
|---|---|---|---|---|
| Ân | Oxy/máu/ngất, điều phối gather, tích hợp | `chonoi/sim/gather.py`, `TEAM.md`, `AGENTS.md`, `game.contract.json`; `tests/test_p1_an.py` | Integrator / Release | Duy hỗ trợ gather |
| Duy | Hái/bắt, kho, smoke tích hợp | `chonoi/sim/gather_actions.py`; `tests/test_p1_duy.py`; `docs/verification/phase-1.md`; `docs/proof/phase-1/duy/` | QA lead | Ân hỗ trợ |
| Trung | Khách, giữ nguyên liệu, fixture quán | `chonoi/sim/quan_customers.py`, `chonoi/sim/quan_validation.py`; `tests/test_p1_trung.py`; `docs/clarify.md` | PO | Đức hỗ trợ |
| Đức | Bếp, phục vụ, thanh toán, HUD | `chonoi/sim/quan.py`, `chonoi/sim/quan_kitchen.py`, `chonoi/web/index.html`; `tests/test_p1_duc.py`; `README.md`, `CREDITS.md` | Điều phối quán / sản phẩm | Trung hỗ trợ |

`chonoi/{headless,inputs,contract,rng,ids,jsonl,inventory,runner,live,scenario}.py` là khung dùng chung: không đổi nếu chưa báo cả nhóm. Nếu thật sự cần, Ân nhận sửa và tích hợp. Trung đặt kiểm tra mức luật trong `quan_validation.py`, gọi từ constructor quán trước khi runner mở JSONL; không cần cùng sửa `scenario.py`.

Mọi người tạo bằng chứng riêng tại `docs/proof/phase-1/<an|duy|trung|duc>/` và phản tư `docs/members/<github-handle>.md`. Nhật ký `docs/ai-usage-log.md` là file chung: báo trước khi sửa hoặc gửi dòng ghi cho Trung tập hợp.

## 3. Hợp đồng kỹ thuật chung

**Chuẩn triển khai chi tiết:** đọc [Giao diện dùng chung Phase 1 — bản chốt 1.2](contracts/phase-1-interfaces.md). File đó chốt kiểu dữ liệu, tác động từng hàm, thứ tự constructor/step, RNG, event, dữ liệu mẫu và thứ tự merge. Chi tiết mục 3 dưới đây là tóm tắt; dùng bản 1.2 khi cần quy tắc đầy đủ, nhất là mục 11 trả lời các câu hỏi của Trung. Bổ sung API Trung phụ trách: `validate_quan_fixture(scenario, tuning)` để kiểm raw fixture trước chuẩn hóa; Đức gọi trước khi dựng state. Các helper chưa được triển khai chỉ bằng việc có tài liệu này.

### 3.1. Dữ liệu và sự kiện

- Giữ tên trường snapshot và payload event theo mục D/E/F của PRD, không dịch ID sang tiếng Việt có dấu.
- Event nội bộ là tuple `(name, data_dict)`, các hàm bên dưới nhận cùng `events: list` và **append trực tiếp**, trả `None` trừ khi có ghi khác. Hàm con không tự ghi JSONL, không gắn tick vào event.
- Runner giữ quyền tăng tick và ghi output. Các hàm luật không tự tăng tick hoặc giảm timer ngoài phần được giao.
- Số liệu đọc tuning, khoảng cách Euclid tính cả đúng mép. Dùng `ids.sort_by_id`, `IdAllocator`, `Streams`; không dùng random toàn cục/đồng hồ thực.
- Input dùng `inp.pressed("interact")` và `inp.pressed("catch")`; giữ nút không tạo thêm cạnh lên.

### 3.2. Kho và giỏ — Ân/Duy/Trung/Đức dùng chung

```json
{"items":{"bong_sung":2,"ca_loc":1}}
```

- File chỉ có `items`; 4 kind hợp lệ: `ca_loc`, `ca_linh`, `bong_dien_dien`, `bong_sung`. Số lượng nguyên không âm; bên ghi bỏ lượng 0. Kho rỗng: `{"items":{}}`.
- `sim.hold` là list kind theo thứ tự nhặt, mới nhất cuối; ngất bỏ theo LIFO. Không tự chuyển giỏ thành map vì mất thứ tự.
- `sim.stock` của quán là map **tồn vật lý**, gồm cả phần đang giữ chỗ. Kho khả dụng = stock trừ tổng `reserved` của các đơn còn giữ chỗ.
- Giữ chỗ chưa trừ stock. Bắt đầu nấu mới trừ stock đúng công thức và xóa phần giữ chỗ của đơn.
- Runner đã hỗ trợ ghi kho khi gather kết thúc. Duy kiểm tra lại; không thêm đường ghi kho thứ hai trong hàm hái/bắt.
- Chạm tick limit trước `gather_end` không tạo/ghi đè kho. Ngất ghi rỗng. Quán không áp trần giỏ lên kho.

### 3.3. Giao diện gather — Duy bàn giao cho Ân

File mới `chonoi/sim/gather_actions.py` xuất:

```python
def gather_node(sim, events): ...
def catch_fish(sim, events): ...
```

Hai hàm chỉ xử lý hành động tại trạng thái **sau di chuyển và oxy**. Dùng `sim.t`, `sim.pos`, `sim.hold`, `sim.nodes`, `sim.fish`, `sim.catch_cd_ticks`, `sim._at_surface()` có sẵn. Không giảm timer, không đọc input, không xét bến, không kết thúc ca. `catch_fish` tự kiểm tra dưới nước và cooldown; `gather_node` tự kiểm tra mặt nước.

Ân giữ thứ tự `GatherSim.step()`:

1. Giảm timer ca/cooldown/hồi cây; phát `node_regrown` theo id.
2. Di chuyển, phát dive/surface, cập nhật oxy và ngạt. Ngất: mất giỏ LIFO, phát faint rồi gather_end và return.
3. Nếu cạnh interact: xét bến trước; cập bến thì kết thúc và return; nếu không thì gọi `gather_node`.
4. Nếu cạnh catch: gọi `catch_fish`.
5. Hết giờ thì kết thúc `time`, giữ thành quả hành động vừa xử lý.

### 3.4. Giao diện quán — Trung và Đức

Giữ `sim.customers`, `sim.stock`, `sim.stoves`, `sim.tables`, `sim.hand`, `sim.menu`, `sim.t` theo starter. Đức thêm `sim.phase_tick = 0`, tăng đúng một lần đầu mỗi `step`; không giảm time_left ở nơi khác.

Khách dùng các trường PRD: `id`, `table_id`, `dish_id`, `order_tick`, `state`, `patience_ticks_left`, `eat_ticks_left`, `order_status`, `reserved`, và `base_price`, `tip` khi đã phục vụ. `state` là waiting/eating; `order_status` là reserved/assigned/unfulfillable/served. Món trên bếp/tay có `{order_id,dish_id,base_price}`; order_id bằng id khách.

Trung xuất từ `quan_customers.py`:

```python
def init_customers(sim, scenario): ...
def available_stock(sim): ...  # trả map khả dụng mới, không sửa stock
def advance_timers(sim): ...
def resolve_departures(sim, events): ...
def spawn_customer(sim, events): ...
```

- `init_customers`: chuẩn hóa defaults, suy giữ chỗ theo `(order_tick, id bàn)` khi thiếu, reserve id; thay phần dựng customers thô của starter để không khởi tạo hai lần.
- `advance_timers`: giảm timer ca, nấu, ăn, kiên nhẫn; chỉ tăng ready_ticks của món đã ready đầu bước. Bộ đếm không âm; timer ăn chỉ giảm khi eating, kiên nhẫn chỉ giảm khi waiting.
- `resolve_departures`: xử lý theo id bàn; thu tiền khách ăn xong trước, rồi xử lý khách waiting; đóng ca theo PRD. Gọi helper của Đức để thu tiền/bỏ món, rồi nhả giữ chỗ và xóa khách. Không tự phát quan_end.
- `spawn_customer`: tôn trọng random_customers, lịch phase_tick, bàn trống và kho khả dụng; sinh cuối bước. Chọn ngẫu nhiên bằng Streams trên tập món sắp cố định.

Đức xuất từ `quan_kitchen.py`:

```python
def finish_cooking(sim, events): ...
def interact(sim, events): ...
def pay_customer(sim, customer, reason, events): ...
def discard_order(sim, order_id): ...
```

- `pay_customer`: chỉ tính/cộng tiền, earned, shift_earned, uy tín do boa và phát paid; không xóa khách.
- `discard_order`: xóa món thuộc order khỏi bếp/tay, đưa bếp về idle; không hoàn nguyên liệu, không xóa khách, không phát event ngoài contract.
- `quan_customers.py` được import `pay_customer`, `discard_order` từ `quan_kitchen.py`; chiều ngược lại **không import customers** để tránh vòng import. `interact` chọn đơn reserved trực tiếp từ `sim.customers`.

Trung xuất `validate_quan_state(sim)` trong `quan_validation.py`; Đức gọi sau khi init_customers xong, trước khi constructor trả về. Kiểm toàn bộ liên kết, trạng thái và timer theo mục D; sai dùng `BadInput`, không dùng assert làm kiểm tra dữ liệu đầu vào.

Đức giữ thứ tự `QuanSim.step()`:

1. Tăng phase_tick, gọi `advance_timers` của Trung.
2. Gọi `finish_cooking` của Đức.
3. Di chuyển, nếu cạnh interact thì gọi `interact` của Đức.
4. Gọi `resolve_departures` của Trung. Nếu hết ca thì phát quan_end, đặt done/reason, return.
5. Nếu còn giờ gọi `spawn_customer` của Trung.

Phục vụ đúng tick kiên nhẫn về 0 vẫn hợp lệ. Đóng ca: khách eating trả ngay, khách waiting rời với closing và không trừ uy tín. Khách vừa phục vụ ở tick đóng ca vẫn trả tiền. Không cho khách mới sinh tương tác ngay trong bước sinh.

## 4. Hướng dẫn riêng cho Ân

**Đầu vào đọc:** `AGENTS.md`, PRD mục F/G, `gather.py`, `runner.py`, giao diện ở mục 3.3.

**Làm theo thứ tự:**

1. Tập hợp GitHub handle, fork URL, kênh trao đổi; điền TEAM và mã nhóm/team_size. Báo cả nhóm về chỉnh contract hành chính.
2. Viết oxy theo độ sâu cuối bước, dive/surface, oxygen_empty, choke và faint. Đếm ngạt gồm cả bước vừa hết oxy: hết oxy ở t thì lần ngạt đầu ở t+59 nếu liên tục dưới nước.
3. Ngất: ghi lost theo LIFO trước khi xóa giỏ, phát faint rồi kết thúc một lần với kho rỗng.
4. Gắn hai helper Duy bàn giao vào step đúng thứ tự. Nếu chưa có helper, chạy test oxy độc lập; không tích hợp import chưa tồn tại vào main.
5. Sở hữu mọi chỉnh sửa cần thiết vào khung chung sau khi báo nhóm. Tích hợp sớm các nhánh; kiểm test trước khi đẩy main.
6. Cập nhật AGENTS với lệnh thật và hai command nhóm tự viết: Ân làm command kiểm tra tính tất định; Duy làm command smoke kho. Ghi cách dùng và phạm vi, không chỉ đặt tên.
7. Chốt commit main bàn giao, chạy kiểm chứng, bảo đảm proof khớp commit rồi tạo/đẩy phase-1. Không dời tag đã công bố nếu chưa thống nhất.

**Test phải có:** oxy dưới nước/mặt nước; ngạt đúng tick; nổi lên đúng bước ngạt; máu 0 mất giỏ đúng LIFO; ngất ưu tiên trước interact; di chuyển/biên không hồi quy; hai lần chạy cùng seed giống byte.

**Bàn giao:** file luật, test, kết quả thật trong proof/an và hướng dẫn chạy command tính tất định. Tạo command riêng ở `tools/check_determinism.py` (không sửa helper test chung).

**Prompt có thể giao AI:** “Đọc AGENTS.md và docs/PHAN-CONG-PHASE-1.md, làm phần Ân. Chỉ sửa file thuộc Ân; giữ contract v1.0, tập trung oxy/máu/ngất và điều phối gather. Không viết thay helper Duy. Viết test các mốc biên, chạy kiểm chứng thật và báo phần chưa đạt.”

## 5. Hướng dẫn riêng cho Duy

**Đầu vào đọc:** PRD mục E/F Gather/G, `gather.py`, `inventory.py`, `tests/test_smoke_p1.py`, mục 3.2/3.3.

**Làm theo thứ tự:**

1. Viết gather_actions với đúng hai hàm đã chốt; bàn giao tên hàm sớm cho Ân.
2. Hái nút ready gần nhất, hòa theo id, chỉ mặt nước; đủ chỗ mới thêm nguyên liệu và đặt hồi cây. Đầy thì phát hold_full, giữ cây.
3. Bắt đàn gần nhất, hòa theo id, chỉ dưới nước và hết cooldown. Nhận đủ yield mới xóa đàn/đặt cooldown; không đủ thì giữ đàn/cooldown, không thử đàn khác. Không có cá trong tầm thì không phát bắt/hồi chiêu.
4. Kiểm đường ghi kho có sẵn; phát hiện lỗi khung thì báo Ân thay vì viết lại runner.
5. Viết `tools/smoke_inventory.py`: tự tạo fixture tạm, chạy hai tiến trình theo headless_cmd, đối chiếu JSON kho và stock tick 0, báo pass/fail và exit code. Lưu đầu ra thật; tạo hướng dẫn command trong `.agents/skills/` hoặc tài liệu command tương đương.
6. Tập hợp ma trận verification: yêu cầu → cách kiểm → đường dẫn proof → đạt/chưa đạt. ID yêu cầu do nhóm đặt phải ghi là ID nội bộ, không giả nhận là mã chính thức của đề.

**Test phải có:** đúng mép bán kính; hòa khoảng cách theo id; cây hồi đúng tick; giữ phím chỉ một lần; cá linh cần đủ 3 ô; đầy không tiêu cá/cooldown; E ở bến ưu tiên hái; kho ngất rỗng; tick_limit không ghi đè file có sẵn; smoke hai tiến trình.

**Bàn giao:** module, test, command smoke, proof/duy; gửi Ân lệnh tích hợp và các test đã chạy. Có thể kiểm kho bằng fixture ngay, không chờ oxy hoàn thành.

**Prompt AI:** “Đọc AGENTS.md và docs/PHAN-CONG-PHASE-1.md, làm phần Duy. Tạo gather_actions.py theo giao diện mục 3.3; không sửa gather.py/runner.py. Dùng fixture kiểm thu hoạch và hai tiến trình kho, giữ luật v1.0, lưu bằng chứng thật.”

## 6. Hướng dẫn riêng cho Trung

**Đầu vào đọc:** PRD mục D/E/F Quán, `quan.py`, `scenario.py`, `rng.py`, `ids.py`, mục 3.4.

**Làm theo thứ tự:**

1. Chốt fields khách/đơn với Đức; viết init_customers và validate_quan_state trước để cả hai dùng fixture đúng.
2. Viết available_stock không làm đổi tồn vật lý. Khách mới giữ nguyên liệu theo công thức ngay khi gọi món.
3. Viết timer và lịch khách bằng phase_tick; tôn trọng random_customers=false, không suy lịch từ time_left khi fixture rút ngắn ca.
4. Viết resolve_departures với helper Đức: ăn xong trả tiền; khách chờ hết kiên nhẫn rời; đóng ca không trừ uy tín vì chờ. Nhả giữ chỗ, bỏ món cũ, không hoàn nguyên liệu đã nấu.
5. Dùng stock mẫu để làm ngay; không chờ gather. Dùng fixture một món đủ để kiểm nhánh cụ thể, tránh phụ thuộc kết quả chọn ngẫu nhiên.
6. Giữ docs/clarify.md. Chỗ đề đã quy định thì làm theo; phần chưa rõ ghi câu hỏi và hỏi trợ giảng/giảng viên, phân biệt giả định nhóm với câu trả lời chính thức.

**Test phải có:** không đủ món phát no_dish khi có bàn; bàn bận bỏ lượt; giữ chỗ không làm âm khả dụng; timer khách mới giảm từ bước sau; khách hết kiên nhẫn; đóng ca; fixture mặc định reserved; assigned thiếu/trùng món; món không khớp đơn; giữ quá kho; eating thiếu base_price/tip; trường lạ/bộ đếm mâu thuẫn phải bị từ chối trước output.

**Bàn giao:** hai module, test, proof/trung và danh sách câu hỏi đã chốt. Gửi Đức ví dụ khách fixture hợp lệ và cách gọi helper.

**Prompt AI:** “Đọc AGENTS.md và docs/PHAN-CONG-PHASE-1.md, làm phần Trung. Chỉ sửa module khách/validation, test và clarify. Giữ giao diện mục 3.4, không sửa quan.py hay viết lại tính tiền. Dùng fixture để làm độc lập, kiểm rõ reserved/assigned/served và lỗi đầu vào.”

## 7. Hướng dẫn riêng cho Đức

**Đầu vào đọc:** PRD mục D/E/F Quán, `quan.py`, `web/index.html`, `live.py`, mục 3.4.

**Làm theo thứ tự:**

1. Tạo quan_kitchen với bốn helper đã chốt; bàn giao pay_customer/discard_order sớm cho Trung.
2. Interact chọn đúng một đối tượng theo (khoảng cách, bếp trước bàn, id). Đối tượng gần nhất không dùng được thì bỏ lượt, không tự tìm đối tượng khác.
3. Bếp idle lấy đơn reserved cũ nhất theo order_tick rồi id bàn; trừ đúng phần giữ, chốt giá, chuyển assigned. Nấu xong ready; tay trống mới lấy được món. Phase 1 không cháy món.
4. Phục vụ chỉ đúng order_id. Chốt boa bằng floor(base_price × tip_rate) nếu tỷ lệ kiên nhẫn sau giảm timer đạt ngưỡng. Phục vụ chuyển served/eating, timer ăn đầy; chưa cộng tiền lúc phục vụ.
5. Thu tiền cập nhật money/earned/shift_earned và uy tín do boa đúng một lần, kẹp uy tín theo tuning. Không tự xóa khách trong pay_customer.
6. Ghép helpers Trung vào constructor/step theo mục 3.4. Phải bỏ phần giảm timer cũ để không giảm hai lần. Cùng Trung rà fixture trước output.
7. Kiểm HUD cả hai mode. UI hiển thị đủ oxy/máu/giỏ và kho khả dụng/đơn/kiên nhẫn/bếp/tay/tiền/uy tín. Kho khả dụng tính để hiển thị từ snapshot, không thay đổi luật.
8. README ghi chạy từ clone sạch trên macOS/Linux tối đa 3 lệnh, điều khiển, công thức điểm, một lệnh test; ghi nguồn asset/công cụ trong CREDITS. Hình khối có sẵn đủ nếu đọc rõ.

**Test phải có:** nguyên liệu trừ đúng lúc nấu; chín đúng tick; một tương tác mỗi cạnh; tay đầy; phục vụ sai đơn; phục vụ đúng tick kiên nhẫn 0; boa đúng ngưỡng và làm tròn; trả tiền đúng một lần; khách vừa ăn lúc đóng ca vẫn trả; khách rời làm mất món đúng đơn. Chơi thử UI thật, lưu ảnh có thể đọc HUD.

**Bàn giao:** quan.py, kitchen, UI, test, README/CREDITS và proof/duc. Dùng khách fixture hợp lệ để làm bếp ngay trong lúc Trung viết sinh khách.

**Prompt AI:** “Đọc AGENTS.md và docs/PHAN-CONG-PHASE-1.md, làm phần Đức. Giữ giao diện mục 3.4, sở hữu quan.py/quan_kitchen.py và UI. Không sửa module khách của Trung. Hoàn thiện bếp/phục vụ/thu tiền, tích hợp đúng thứ tự, kiểm các deadline và HUD; không đưa luật vào UI.”

## 8. Lịch tích hợp 60 phút

| Mốc | Ân | Duy | Trung | Đức |
|---|---|---|---|---|
| 0–10 | TEAM, preset, nhánh xuất phát | Chốt gather helper, chạy kho fixture | Chốt schema khách, fixture hợp lệ | Chốt kitchen helper, đọc UI |
| 10–20 | Oxy/máu, test độc lập | Hái/bắt, smoke kho | Init/validation, khả dụng | Bếp/phục vụ, fixture |
| Phút 20 | Tích hợp đầu, điều người hỗ trợ | Bàn giao helper | Bàn giao helper/fixture | Ghép quán phiên bản đầu |
| Trước 25 | Ghép gather | Chứng minh kho thật → quán | Sửa tích hợp khách | Kiểm stock tick 0 |
| 25–45 | Sửa biên gather, command tất định | Hoàn thiện test/proof | Khách/lịch/rời/validation | Đóng ca, tiền, HUD |
| 45–55 | Test toàn bộ trên main | Verification và smoke | Rà hồi quy, clarify | Chơi thử, README |
| 55–60 | Chốt commit và đẩy phase-1 | Kiểm proof/commit | Hoàn tất nhật ký | Xác nhận chạy sạch |

Đừng đợi mọi lát hoàn thiện mới ghép. Chỉ merge phần chạy được; helper chưa có thì bên gọi chờ trên nhánh riêng, không đẩy import lỗi lên main. Phần chưa đạt ghi trung thực, vẫn chốt tag trước hạn.

## 9. Lệnh chung và checklist bàn giao

Chạy tại gốc repo. Trên macOS/Linux theo starter:

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
python3 -m chonoi.live --mode gather
python3 -m chonoi.live --mode quan --inventory docs/contracts/inventory.sample.json
```

Trên PowerShell, nếu máy có lệnh python3:

```powershell
$env:PYTHONPATH = "tests;."
python3 -m unittest discover -s tests -v
```

Nếu chỉ có `python`, chạy runner bằng python chưa đủ vì test gọi headless_cmd đang khai `python3`. Báo Ân thống nhất lệnh/runtime và môi trường chấm trước khi đổi contract; không để mỗi nhánh đổi lệnh một kiểu.

Mỗi người trước khi bàn giao:

- [ ] Code trong đúng phạm vi, không đổi contract âm thầm.
- [ ] Có test luật/tình huống biên và kết quả thật; ghi rõ lệnh, commit và phần chưa đạt.
- [ ] Chạy test hiện có sau thay đổi; nếu có lỗi nền thì ghi rõ, không tuyên bố tất cả pass.
- [ ] Gửi người tích hợp danh sách file, interface và phụ thuộc.
- [ ] Nhờ người kế bên đọc thay đổi: Ân đọc Duy; Duy đọc Ân; Trung đọc Đức; Đức đọc Trung.
- [ ] Nhật ký AI và commit phản ánh đúng người làm; pair thì Co-authored-by với thông tin thật.

Trước tag, cả nhóm xác nhận: chơi được hai buổi; smoke hai tiến trình; test và tính tất định; HUD; README; TEAM/team_size; schema kho; verification/proof khớp commit; main chạy được. Bản thân file phân công này **không phải bằng chứng rằng các việc trên đã hoàn thành**.
