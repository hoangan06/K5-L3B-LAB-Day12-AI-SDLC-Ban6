# Giao diện Phase 3 — bản nội bộ 1.0, Test Contract 1.2

[Phân công và chủ file](../PHAN-CONG-PHASE-3.md). Theo TICKET-03 đã đọc trên board. Các API bên dưới là mục tiêu cần triển khai, chưa phải code có sẵn. Chỉ làm lõi freshness, không current/reservations.

## 1. Schema và thứ tự

```json
{"items":[{"id":"I1","kind":"ca_linh","fresh":100},{"id":"I2","kind":"ca_loc","fresh":97.5}]}
```

- File đúng khóa items, giá trị list; mỗi item có đúng id/kind/fresh. ID string duy nhất, không rỗng; kind trong 6 nguyên liệu; fresh hữu hạn 0..100, bool không phải số. items: [] hợp lệ. Contract 1.2 từ chối items: {} hoặc count map bằng mã 2.
- Internal hold giữ thứ tự vào giỏ. Không sort hold tại chỗ. lost theo thứ tự pop LIFO; file/stock và spoiled theo id_key; cook_started.items theo (kind,id_key).
- Snapshot hold giữ thứ tự giỏ. ID fixture có thể xáo trộn; không đoán LIFO theo ID lớn nhất.
- inventory_items() giữ tên để runner tương thích nhưng trả list ở 1.2. gather_end.inventory là {items:list}. Không đếm rồi tái tạo cá thể vì mất ID/fresh.
- I1,I2… được cấp bằng sim.ids hiện có; reserve mọi ID fixture/file trước khi cấp. Không tái dùng ID đã dùng/bỏ. yield 3 tạo ba object với ba ID khác nhau.

## 2. Config và version

Ân chuẩn bị contract_version: "1.2" và tuning.freshness:

```json
{"initial":100,"gather_decay_per_s":0.5,"quan_decay_per_s":0.25,"spoiled_below":30}
```

Loader chọn schema theo version tường minh, không tự nhận schema cũ khi chạy 1.2. Có thể giữ đường 1.0/1.1 trong migration nhưng phải tách test. CLI cho day ở cả 1.1 và 1.2, không chỉ so version == "1.1".

## 3. Primitive chung — Duy giữ freshness.py

Main đã có `sim/quan_fresh.py` của Trung. Duy và Trung thống nhất tái dùng nguồn Fraction hiện có qua facade/helper dưới đây, không tạo hai cách decay khác nhau. Không tự sửa file Trung: gửi patch hoặc bàn giao adapter để Trung cập nhật callsite quán. Các chữ ký dưới là mục tiêu thống nhất, chưa có đầy đủ trong repo.

```python
validate_individuals(items, kinds) -> list
init_individuals(items, kinds, ids) -> list
make_individuals(kind, amount, ids, config) -> list
decay_individuals(items, config, *, location, events) -> None
fresh_value(item)  # số chính xác dùng tính toán
serialize_individuals(items, *, sort_by_id=False) -> list
```

- validate_individuals kiểm raw schema/miền/trùng ID, trả bản sao mới giữ thứ tự, không cấp ID hoặc bỏ hàng ươn.
- init_individuals validate, chuẩn hóa giá trị exact nội bộ, reserve ID qua allocator truyền vào; không sinh ID thay thế.
- make_individuals tạo list object độc lập, cấp ID qua ids.new("I"), fresh=config.initial. Caller extend hold; helper không tự thêm/decay/phát event.
- fresh_value trả nguồn giá trị exact để so ngưỡng, chọn tươi nhất, tính mean/giá. Không dùng giá trị đã làm tròn của snapshot.
- decay_individuals nhận location hold/stock, lấy rate tương ứng chia 60, trừ trên toàn bộ hàng có sẵn và clamp 0. Giữ thứ tự và số món, không xóa hàng ươn. Append spoiled theo ID khi before >= threshold và after < threshold. Không tăng tick, giảm timer hoặc sửa reserved.
- serialize_individuals trả deep-copy/project đúng 3 field, fresh là số JSON. sort_by_id=False giữ thứ tự; True dùng id_key. Không làm tròn fresh về 3 chữ số hoặc rò field private/Decimal/Fraction ra JSON.

**Độ chính xác:** một nguồn giá trị exact qua fresh_value, ví dụ Fraction từ giá trị thập phân đầu vào. Bước giỏ = 1/120 điểm, quán = 1/240 điểm. Không trừ float rồi round mỗi tick; không ép fixture 29.9999 lên lưới 240 bằng round. Kiểu nội bộ do Duy đóng gói; caller dùng helper, không tự cast float trước so ngưỡng/floor.

Duy gửi code primitive và cách dựng item test sớm. Các bên có thể dùng test double đúng API trong test riêng trước đó, không tạo các freshness.py khác nhau hoặc stub sản phẩm.

## 4. Adapter kho và callsite

Duy triển khai chữ ký mục tiêu:

```python
read_inventory(path, kinds=..., *, contract_version="1.2") -> list
write_inventory(path, items, *, contract_version="1.2") -> None
```

Return list ở 1.2; đường compatibility cũ có thể trả map khi version cũ. Mọi callsite sản phẩm truyền contract_version rõ ràng. Reader không có allocator: sim/controller nhận list rồi init/reserve. Writer atomic, sort ID, giữ precision, không decay hoặc đếm lại.

Ân giữ headless/runner, Đức giữ live. Chốt thêm keyword-only contract_version=None cho Session và run nếu cần truyền version từ manifest; positional API P2 giữ nguyên. Production truyền rõ version, default None chỉ dành cho caller cũ và phải được chuẩn hóa nhất quán. Ân bàn giao thay đổi chữ ký trước khi Đức sửa caller.

Duy giữ scenario: hold/stock list, reserved list ID; không kiểm kho tương lai của day bằng count map hiện tại. Kiểm lỗi tĩnh trước output, ngữ nghĩa kho quán tại lúc mở ca bằng hàng thực.

## 5. Gather — Ân

- Normalize hold bằng init_individuals, không mutate fixture. Snapshot serialize hold giữ thứ tự; hold_count=len(hold), hàng ươn vẫn chiếm ô.
- Đầu step xử lý timer/cooldown/invuln/hồi cây và decay hold trước move/oxy/hit/action. Có thể giữ node_regrown trước spoiled theo pipeline hiện có; các spoiled phải theo ID.
- Hái/bắt dùng make_individuals, fresh 100, chỉ hao từ bước sau. Không nhân cùng một dict bằng list multiplication.
- Quái pop floor(n/2) món cuối; faint pop phần còn lại. lost là cá thể với fresh sau hao đầu bước, serialize theo thứ tự pop, không sort.
- docked/time: inventory_items trả list sort ID, event/file giữ đúng số lượng/ID/fresh; không hao thêm lúc ghi. Fainted items: []; tick_limit không ghi đè file.

## 6. Quán — Trung

stock là list cá thể; reserved là list ID. available_stock(sim) đổi thành list cá thể chưa ươn/chưa giữ, không mutate nguồn. Đây là breaking type so với P2; Trung cập nhật tất cả caller quán trong cùng commit.

Trung giữ helper chọn recipe trong module quán:

```python
select_recipe_items(stock, recipe, reserved_ids, threshold) -> list | None
```

Trả list ID nếu đủ toàn recipe, None nếu thiếu; không giữ một phần. Chọn từng kind theo (-fresh_value,item_id_key). reserved_ids là ID thuộc các đơn khác; nhả phần giữ của đơn đang chọn lại trước khi gọi.

Thứ tự tick: timer → decay stock/phát hết spoiled → xử lý đơn giữ bị ảnh hưởng theo (order_tick,id bàn) → chín/cháy → move/interact → trả tiền/rời/closing → khách mới.

Đơn giữ có món vừa ươn: nhả toàn bộ, thử giữ lại đúng một lần. Thiếu thì unfulfillable và tiếp tục chờ. Không retry mọi unfulfillable mỗi tick. Fixture sai vẫn mã 2; không dùng runtime repair để hợp thức hóa fixture lỗi.

Nấu: tiêu đúng ID giữ, chốt floor(menu_price × mean fresh_value / 100), cook_started.items theo (kind,id). Payload món giữ giá đã chốt; món nấu xong không decay. Boa/thu tiền không tra lại fresh/menu price.

Fixture reserved phải tồn tại, chưa ươn, đúng recipe và không giữ chung giữa hai đơn. Bỏ reserved ở đơn reserved thì cấp theo order_tick rồi ID bàn, chọn tươi nhất/ID; sai hoặc thiếu kho là mã 2 như PRD v1.2.

## 7. Day/Shop/UI — Đức

- Context/constructor P2 giữ nguyên; inventory của QuanSim ở 1.2 là list, không object bọc items. Freshness config từ tuning.
- gather → quan cùng tick giữ nguyên ID/fresh, không cấp lại ID hoặc hao thêm; quán decay từ step sau.
- D1 giữ ID template; D2… copy template, cấp ID mới theo thứ tự mảng, giữ kind/fresh ban đầu. Dùng chung allocator xuyên pha/ngày.
- ID vật lý duy nhất giữa các nơi chứa. reserved là tham chiếu ID stock, không phải cá thể vật lý thứ hai.
- Shop giữ stock list, không hao; kho dư bỏ khi dựng ngày mới theo P2, ID không tái dùng. Không triển khai vendor nếu chưa bật.
- HUD đọc cá thể rồi nhóm theo kind để đếm/hiển thị độ tươi hoặc hàng ươn. Không mutate state và không tự đổi schema để tiện UI.

## 8. Event và precision output

```json
{"type":"event","tick":1,"phase":"gather","name":"spoiled","data":{"item_id":"I1","kind":"ca_linh","location":"hold"}}
```

Quán dùng location stock. Không tự thêm payload khác. Hàng bắt đầu dưới 30 không phát spoiled khi init hoặc lặp mỗi tick; chỉ crossing. Fresh đúng 30 chưa ươn, bước hao kế tiếp mới phát spoiled. Hàng ươn vẫn có trong kho/snapshot.

jsonl._clean hiện round mọi float về 3 digits là điểm phải đổi. Tọa độ vẫn theo quy định, fresh phải đủ chính xác để roundtrip không đổi nhánh ngưỡng. Tất cả snapshot/file/lost dùng serialize_individuals để không json.dump kiểu exact nội bộ trực tiếp.

## 9. Fixture chung

Trong [phase-3-fixtures](phase-3-fixtures/inventory.sample.json):

- inventory.sample.json: có fresh 30, 29.9999 và 100 để kiểm schema/roundtrip.
- gather-threshold.json: không input, một bước phải spoiled I1/hold.
- gather-dock.json + dock-inputs.json: cập bến tick 1 sau khi hao một bước; kho file và snapshot quán tick 0 phải khớp.
- gather-lifo.json: hold theo thứ tự I10,I2,I7; ngất lost I7,I2,I10, không sort ID để đoán LIFO.

Đây là fixture contract 1.2 sau migration. Loader P1/P2 hiện tại sẽ từ chối; JSON parse được không có nghĩa gameplay test đã pass.

## 10. Gate merge và kiểm chứng

Chốt primitive/precision trước để không có bốn phép tính fresh khác nhau. Gói adapter + gather + quán + day/writer + manifest phải kiểm trên nhánh tích hợp trước main. Helper độc lập có thể merge sớm nếu không làm hỏng đường runtime cũ; không optional-import rồi âm thầm bỏ tính năng.

Phút 20 smoke file; sau đó smoke day/pause/Shop. Regression P1/P2 giữ luật còn hiệu lực, thay fixture/count map có ghi lý do. Duy tập hợp verification; Ân chốt tag đúng hạn và ghi thật phần chưa đạt.
