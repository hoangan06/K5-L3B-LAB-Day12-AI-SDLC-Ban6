# Phase 3 — Phân tích và phân công Ân, Duy, Trung, Đức

Nguồn: [TICKET-03 — Mùa Nước Nổi, Test Contract v1.2](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg#phase-3). Phase dài 35 phút, từ mốc 1:55 đến 2:30; đẩy tag phase-3 trên main trước 2:30. Nhóm 4 người chỉ làm lõi độ tươi, chưa làm current/reservations hoặc mở rộng mới.

Đọc [giao diện P3 bản 1.0](contracts/phase-3-interfaces.md) trước khi code. Đây là kế hoạch triển khai, chưa phải bằng chứng đã hoàn thành. Tài liệu thay quyền sở hữu P2 cho các file được nêu, từ khi nhóm bắt đầu P3.

## 1. Phase 3 thay đổi gì?

| Trước | Phase 3 | Phần bị ảnh hưởng |
|---|---|---|
| Kho map kind → count | Kho mảng `{id,kind,fresh}` | File, scenario, hai sim, day, Shop, HUD, test |
| Giỏ list kind | Mỗi ô là một cá thể có ID và độ tươi | Hái/bắt, snapshot, mất hàng |
| Hàng không hỏng | Giỏ −0.5/s, kho quán −0.25/s, pause dừng hao | Tick, spoiled, giữ chỗ |
| Giữ theo lượng | Giữ theo ID, chọn tươi nhất rồi ID | Gọi món, fixture, giữ lại khi vừa ươn |
| Giá menu | floor(menu_price × mean_fresh / 100) lúc nấu | Bếp, payload món, boa và tiền |

Hàng fresh < 30 là ươn nhưng vẫn tồn tại và chiếm ô, không dùng nấu. spoiled chỉ phát khi chuyển từ ≥30 xuống <30, theo ID. Hàng mới fresh 100, hao từ bước sau. Shop không hao hàng. Mất hàng vẫn theo thứ tự vào giỏ: vào sau mất trước.

## 2. Phân công và chủ file

| Người | Việc chính | File sở hữu P3 |
|---|---|---|
| **Ân — lead/contract/gather** | Contract 1.2, giỏ cá thể, hao giỏ, spoiled/hold, LIFO, chọn version trong CLI/runner | game.contract.json, contract.py, __init__.py nếu cần; sim/gather.py, gather_actions.py, gather_monsters.py; headless.py, runner.py; AGENTS và tài liệu giao diện |
| **Duy — adapter/độ chính xác/QA** | Đọc/ghi/validate kho, primitive độ tươi, scenario, JSONL, smoke migration | inventory.py, module mới freshness.py, scenario.py, jsonl.py; tools smoke/determinism; verification P3 |
| **Trung — quán** | Stock cá thể, reserved ID, giữ lại khi ươn, tiêu ID, giá theo fresh, validation | sim/quan.py, quan_customers.py, quan_kitchen.py, quan_validation.py; clarify/retro |
| **Đức — day/Shop/HUD** | Chuyển kho giữ nguyên ID/fresh, ID xuyên ngày, Shop không hao, HUD | sim/day.py, sim/shop.py, live.py, web/index.html; README/CREDITS/CHANGELOG |

**Đổi chủ ở P3:** Ân nhận manifest và gather_actions từ Duy để sửa giỏ/hái/bắt cùng một phía. Duy giữ module cá bơi nếu cần sửa hồi quy; API cá không đổi vì độ tươi. Không có hai người cùng sửa gather.py hoặc scenario.py.

Test riêng: tests/test_p3_an.py, test_p3_duy.py, test_p3_trung.py, test_p3_duc.py. Fixture và proof đặt trong thư mục tên người dưới phase-3. Duy giữ verification và proof tích hợp; Trung tập hợp clarify/ai-log; Đức ghi CHANGELOG. Sửa test công khai gửi patch và lý do cho Ân tích hợp một lần.

## 3. Ân làm gì?

1. Chuẩn bị patch version 1.2 và tuning.freshness: initial 100, gather_decay_per_s 0.5, quan_decay_per_s 0.25, spoiled_below 30. Chưa bật trên main trước khi adapter và hai sim tương thích.
2. Hái/bắt tạo từng cá thể qua cùng sim.ids; đàn cá linh cho 3 ID khác nhau, không nhân bản cùng một dict.
3. Đầu bước decay hàng đã có, phát spoiled trước di chuyển/hit/hái. Hàng mới không hao trong bước nhặt.
4. Hit bỏ floor(n/2) món cuối giỏ; faint bỏ phần còn lại. lost là mảng cá thể với độ tươi tại lúc mất, giữ thứ tự pop, không sort.
5. inventory_items và gather_end trả list cá thể; ngất trả items: []. CLI/runner truyền version đúng cho adapter, nhận cả 1.1 và 1.2 cho day.
6. Điều phối gói merge, kiểm chứng bản chung và gắn tag.

Test: fresh đúng 30 → spoiled tick 1; không lặp; nhiều crossing sort ID; sau 60 bước mất đúng 0.5; hàng mới 100; hàng ươn chiếm ô; lost LIFO; pause; tick_limit không ghi kho.

## 4. Duy làm gì?

1. Bàn giao sớm nhất ở phút 0–7: primitive/schema/serialization có test và fixture mẫu. Các bên dùng đúng API, không tự viết thêm một phép tính fresh khác.
2. Reader chọn schema theo version; 1.2 từ chối count map, ID trùng, kind lạ, NaN/Inf/bool hoặc fresh ngoài 0..100. Không tự chuyển file cũ trong lúc chạy 1.2.
3. Writer atomic, sort ID, giữ đủ chính xác. jsonl.py hiện round mọi float về 3 chữ số: phải đổi để fresh không bị làm tròn như tọa độ.
4. scenario nhận hold/stock list và reserved list ID. Giữ raw template của day để quán kiểm liên kết trên kho thực khi mở ca.
5. Helper init nhận allocator để reserve ID; reader chỉ đọc, không tự cấp ID cho hàng đã có ID.
6. Chạy smoke file và day với Trung/Đức, determinism và regression còn hiệu lực; tổng hợp verification.

Test: schema 1.2 từ chối count map; roundtrip ngay dưới/trên 30; decay chính xác; fresh 0 còn tồn tại; không ghi đè trước gather_end; kho quán vượt 12 món vẫn hợp lệ.

## 5. Trung làm gì?

1. stock chuyển thành list cá thể, reserved thành list ID. Chọn mỗi kind theo độ tươi giảm dần rồi id_key; đủ cả recipe mới giữ, không giữ một phần.
2. Đầu tick quán giảm độ tươi cả hàng đang giữ, phát hết spoiled theo ID rồi xử lý đơn bị ảnh hưởng theo order_tick/id bàn.
3. Nhả toàn bộ phần giữ của từng đơn bị ảnh hưởng và thử giữ lại đúng một lần. Thiếu thì unfulfillable, khách tiếp tục chờ; không retry mọi đơn unfulfillable mỗi tick.
4. Khi nấu, tiêu đúng ID và tính giá từ mean fresh tại thời điểm đó. cook_started.items là cá thể; món đã nấu không hao; boa tính trên giá đã chốt.
5. Fixture reserved sai/không đủ vẫn mã 2; không dùng runtime repair để che fixture lỗi. Giữ luật deadline, thanh toán và đóng ca cũ.

Test: ưu tiên tươi/ID, giữ trùng, thay toàn bộ phần giữ đủ/thiếu, nhiều đơn tranh hàng, không dùng hàng ươn, floor giá, boa và closing.

## 6. Đức làm gì?

1. Day truyền list từ gather sang quán, giữ đúng ID/fresh và không hao thêm lúc chuyển. Quán bắt đầu decay từ bước sau.
2. D1 giữ ID mẫu; D2 trở đi cấp ID mới theo thứ tự template, giữ kind/fresh ban đầu. Dùng chung allocator xuyên pha/ngày, không tái dùng ID đã tiêu hoặc bỏ.
3. Shop stock là list và không decay; kho dư vẫn bỏ khi dựng ngày mới theo P2. Không thêm vendor nếu chưa bật.
4. HUD đọc cá thể, nhóm theo kind để hiển thị lượng và độ tươi/hàng ươn; không mutate state để đếm. Live truyền version cho reader.
5. CHANGELOG ghi breaking schema và cách đổi fixture; ghi bằng chứng UI và hỗ trợ smoke day.

Test: chuyển pha giữ đúng fresh, không hao hai lần, template ngày sau không tái dùng ID, Shop không hao, HUD không crash khi hold không còn là string.

## 7. Lịch và gate tích hợp

| Phút | Mục tiêu | Phụ thuộc |
|---|---|---|
| 0–7 | Chốt schema/API/chủ file; adapter bản đầu | Duy bàn giao primitive; mọi người bắt đầu với fixture mẫu |
| 7–15 | Bốn lát viết và test riêng | Chưa cần module khác xong toàn bộ |
| 15–20 | Ghép gói migration trên nhánh tích hợp | Adapter + gather + quán + day/runner/writer đồng bộ |
| 20 | Smoke file kho, standup | So ID/kind/fresh file và snapshot quán tick 0 |
| 20–25 | Sửa giữ/giá/HUD, smoke day | Người xong hỗ trợ lát chậm |
| 25–32 | Bật 1.2 trên bản chung; regression, proof, CHANGELOG | Hai đầu đã tương thích |
| 32–35 | Dự phòng và tag phase-3 trên main | Ghi trung thực phần đạt/chưa đạt |

**Không merge riêng manifest 1.2 khi code còn count map.** Gói bật version cần loader cá thể, hành động tạo cá thể, gather xuất list, writer/reader và quán nhận list. Có thể giữ đường 1.1 tạm thời để main chạy trong lúc chuyển.

## 8. Nhánh và việc bắt đầu ngay

Mỗi người dùng p3/an, p3/duy, p3/trung, p3/duc từ main/base tích hợp đã thống nhất. Commit/bàn giao P2 trước, không reset hoặc ghi đè việc chưa commit.

Main hiện đã tích hợp nền P2: Session, cá, quái, DaySim/ShopSim và manifest 1.1; bản ghép vừa kiểm 199/199 test trong WSL. Các thành viên lấy main mới trước khi tạo nhánh P3; không dùng base P2 cũ thiếu các module đó. Gói kho cá thể chưa được bật trên manifest runtime.

Quán P3 của Trung đã có `chonoi/sim/quan_fresh.py`, dùng Fraction cho độ tươi. Duy cần tái dùng hoặc bọc qua adapter chung theo giao diện, phối hợp Trung trước khi đổi kiểu nội bộ; không viết một phép tính độ tươi thứ hai rồi để hai đầu lệch nhau. Các API primitive trong tài liệu là giao diện bàn giao mục tiêu, không phải lời khẳng định module mới đã tồn tại.

Mỗi lần bàn giao gửi nhánh, commit, file/API, lệnh test/kết quả và phần còn thiếu. Duy đọc lại phần gather của Ân; Ân đọc adapter; Trung và Đức kiểm chéo quán/day. Cả nhóm kiểm gói migration trước tag.
