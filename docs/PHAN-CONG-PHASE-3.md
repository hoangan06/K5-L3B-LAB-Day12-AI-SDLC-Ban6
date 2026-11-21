# Phase 3 — Phân công hiện hành cho Ân, Duy, Trung, Đức

Theo TICKET-03, Test Contract 1.2, thời lượng 35 phút, hạn tag phase-3 ở mốc 2:30. Nhóm 4 người chỉ ưu tiên lõi độ tươi, chưa làm current/reservations.

**Cập nhật theo điều phối mới nhất của PO Trung:** Trung đã nhận gói migration để rút ngắn thời gian. Phân công dưới đây đồng bộ với [kế hoạch P3/P4 trên main](plan-p3-p4.md). Bản chia bốn lát trước đây được thay thế; Ân không cùng sửa gather/manifest khi Trung đang làm migration.

## 1. Yêu cầu lõi

Kho đếm chuyển thành `{"items":[{"id":"I1","kind":"ca_linh","fresh":100}]}`. ID nối tiếp xuyên pha/ngày, không tái dùng. Giỏ hao 0.5/s, kho quán hao 0.25/s; pause dừng hao, Shop không hao. Hàng fresh < 30 là ươn nhưng vẫn chiếm ô; spoiled phát đúng một lần lúc đi từ ≥30 xuống <30 theo ID. Giữ theo ID, chọn tươi nhất rồi ID; nhả toàn bộ và giữ lại một lần khi phần giữ vừa ươn. Giá chốt lúc nấu bằng floor(giá menu × trung bình fresh / 100). Mất hàng theo thứ tự vào giỏ, vào sau mất trước.

## 2. Phân công hiện hành và quyền sửa

| Người | Công việc | File chính |
|---|---|---|
| **Trung — migration và quán** | Manifest 1.2/freshness; kho cá thể; adapter, scenario; gather cá thể/hao/LIFO; day/Shop truyền list; quán giữ ID/giá | items.py, inventory.py, scenario.py, contract.py, game.contract.json, sim/gather*.py, sim/day.py, sim/shop.py, quan*.py |
| **Ân — review gather/runner và chốt tag** | Kiểm fresh30→spoiled tick1; lost cá thể LIFO; gather_end inventory; review caller version/runner; tích hợp và tag phase-3 | tests/test_p3_an.py, docs/proof/phase-3/an/; đề xuất sửa runtime gửi Trung trước |
| **Duy — QA adapter và smoke** | Test schema lỗi, ID trùng/rỗng, kind/fresh sai; smoke gather file→quan tick0; dòng verification | tests/test_p3_duy.py, tools/smoke_inventory.py, docs/proof/phase-3/duy/, docs/verification/phase-3.md |
| **Đức — HUD/live và chơi thử** | Hiện fresh/hàng ươn ở giỏ/quán/Shop, review lớp hình, chạy day trên browser, chụp bằng chứng | chonoi/web/, live.py khi cần; docs/proof/phase-3/duc/ |

Mỗi file runtime chỉ một người sửa. Nếu review phát hiện lỗi, Ân/Duy gửi case đỏ hoặc patch cho Trung nhận, không cùng sửa một file trên hai nhánh. Đức chốt JSON snapshot thực tế với Trung, không thay schema để tiện HUD.

## 3. Làm song song ngay

- Trung triển khai migration và gửi schema/API/commit đầu tiên sớm; tái dùng quan_fresh.py/Fraction đang có, không tạo hai phép tính fresh khác nhau.
- Ân viết test gather độc lập bằng fixture mẫu, gồm ID xáo trộn để kiểm LIFO. Có thể bắt đầu trước khi migration xong; chỉ kết luận pass khi chạy code thật.
- Duy viết test file/scenario và command smoke trên schema mới; không tự viết lại items.py hoặc adapter Trung đang giữ.
- Đức làm HUD với snapshot mẫu rồi ghép JSON thực tế; mọi logic freshness ở sim, không ở UI.

[Giao diện và schema tham khảo](contracts/phase-3-interfaces.md) mô tả các ràng buộc cần giữ. Tên module/helper trong phần thiết kế ban đầu là đề xuất; Trung đã chọn items.py và quan_fresh.py thì các bên dùng API được Trung bàn giao, không yêu cầu đổi tên chỉ để khớp bản nháp.

## 4. Mốc tích hợp

| Phút | Mục tiêu |
|---|---|
| 0–7 | Chốt schema, chủ file và fixture; bàn giao adapter bản đầu |
| 7–20 | Trung code migration, Ân/Duy viết test, Đức làm HUD song song |
| 20 | Smoke hai tiến trình, so ID/kind/fresh file với snapshot quán tick0; standup |
| 20–25 | Smoke day, sửa giữ/giá/HUD; người xong hỗ trợ lát chậm |
| 25–32 | Bật 1.2 khi cả hai đầu tương thích, regression, CHANGELOG/proof |
| 32–35 | Dự phòng và tag phase-3 trên main; ghi thật phần đạt/chưa đạt |

Không merge riêng manifest 1.2 khi gather/adapter/day vẫn dùng count map. Gói đổi schema cần đồng bộ; có thể giữ đường 1.1 để main chạy trong lúc chuyển. Không round fresh về 3 chữ số như tọa độ, vì có thể đổi phía ngưỡng30.

## 5. Nhánh và bằng chứng

Lấy main mới trước khi tạo p3/an, p3/duy, p3/trung, p3/duc. Nhánh đã tồn tại thì cập nhật theo quy trình nhóm, không reset hoặc force-push. Mỗi người giữ test/fixture/proof riêng, gửi nhánh+commit+lệnh/kết quả+phần chưa đạt.

Trước tag: CHANGELOG ghi breaking change, verification đủ dòng, AI log và retro được cập nhật. Tag phải trỏ commit bàn giao thật trên main. Tài liệu/fixture đã có không có nghĩa runtime 1.2 đã hoàn thành.
