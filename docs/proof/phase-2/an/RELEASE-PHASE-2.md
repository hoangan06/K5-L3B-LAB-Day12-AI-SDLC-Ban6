# Chốt manifest Phase 2 — 21/11/2026

Base main 26e481a, nhánh p2/an được fast-forward tới main sau git fetch. Giữ nguyên các tài liệu P3 untracked, không ghi đè hay gộp vào code P2. Kết quả dưới đây trên working tree sửa manifest, chưa commit/tag.

## Sửa lỗi thực tế

- Manifest từ1.0 lên1.1, tuning lấy nguyên mẫu phase-2-tuning.sample.json; giữ team/team_size/build/headless metadata, run_cmd mở live day5. Có6 món,6 cây, cá8→trần12, quái,2bếp/4bàn,5kế hoạch,Shop.
- headless nhận phiên bản1.1 hoặc1.2 cho giao thức day; không còn chặn1.2 chỉ vì so sánh bằng1.1. Điều này không tự bật hay xác nhận runtime1.2.
- GatherSim trước đó chưa nối module cá của Duy dù module đã merge: fish_initial số8 không thể lặp như list. Đã nối init_fish/snapshot_fish và update_fish sau action/hết giờ đúng TICKET-02; giữ nhánh list6 cũ nếu chạy fixture cấu hình P1.

## Kết quả

-192/192 test PASS: release-tests.txt. Có HTTP localhost ngoài sandbox; PYTHONUTF8=1, Python3.12 bundled. Harness chỉ thay python3 executable sang sys.executable như các lượt kiểm trước, không sửa assertions trong lúc chạy.
- Headless thật `--mode day --days 5 --seed 1 --ticks 111000 --snapshot-every 600`: days_complete, days_completed5, đủ5 day_start/Shop đóng, khoảng3.153s. End/hash lưu day-five-summary.json; JSONL local day-five.jsonl bị gitignore, không phải file đã commit.
- Live thật5 ngày qua LiveGame/HTTP; pump cùng _tick_once nhanh hơn đồng hồ thật, bỏ intro bằng /ui, không đổi timer/luật. Đã quan sát trang localhost hiển thị Tổng kết và5 dòng ngày trong browser. live-five-summary.json ghi state, end, các chuyển pha. Không nói đây là5 ngày chơi tay hoặc đoFPS; không input thì doanh thu/phục vụ0.
- Smoke CLI kho6 kind chính xác: release-six-kind.txt. Smoke gốc: release-inventory.txt. Tất định standalone: release-determinism.txt.
- Server kiểm live đã dừng sau quan sát, không để process chạy ngầm.

## Vì sao sửa test P1?

Lần đầu khi bật manifest1.1 có5 fail do kỳ vọng cũ; giữ log release-tests-initial.txt.

1. Smoke mặc định6 cá → theo version, P2 là8 đúng TICKET-02.
2. attack trước là field chưa hỗ trợ → P2 nhận đúng kiểu rồi bỏ qua khi extension tắt; vẫn kiểm field lạ bằng jump/teleport.
3. day trước bị từ chối → P2 phải dựng được day tick0; vẫn kiểm mode lạ, versionP1 còn rejectday.
4. Unit Trung giả thiết một bàn → cố định fixture unit đó với1bàn/1bếp/3món P1 để tiếp tục kiểm luật bàn bận bỏ lượt, không đổi assertion thành chấp nhận thêm khách.
5. Unit kho khả dụng4 kind → cùng fixture3món P1 giữ kỳ vọng4kind, không thay runtimeP2 hoặc bỏ assertion.

Không xóa test luật để báo xanh. Các test P2 nhiều bàn/6món giữ nguyên.

## Chạy lại

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
python3 tools/check_determinism.py
python3 tools/smoke_inventory.py
python3 -m chonoi.headless --mode day --days 5 --seed 1 --ticks 111000 --snapshot-every 600 --out /tmp/ban6-day5.jsonl
python3 tools/check_phase2_live_release.py
python3 -m chonoi.live --mode day --days 5
```

Lệnh cuối dùng chơi tay; kiểm live tăng tốc tự động là command trước nó. Nếu muốn xem summary sau kiểm tăng tốc: `python3 tools/check_phase2_live_release.py --port 8765 --keep-open`, mở URL được in ra, Ctrl+C khi xong.

## Bước 1.2 chưa bật

Không thêm freshness vào manifest đang cần tagP2: quán Trung dùng sự hiện diện tuning.freshness để bật kho cá thể ngay, trong khi gather/actions/inventory/scenario/runner/Shop hiện còn kho đếm. Bật riêng khối này sẽ làm day mở quán lỗi thay vì hoàn thànhP3.

Migration cần gói đồng bộ: schema cá thể + precision/read/write, gather/hold/thu hoạch và LIFO, scenario, runner/live callsite version, day/Shop bảo toàn list/ID, rồi mới bật version1.2 và freshness100/0.5/0.25/30. Tài liệu phân công/giao diện P3 đã chuẩn bị riêng nhưng phải đối chiếu quan_fresh.py thật của Trung để tái dùng thay vì viết utility trùng. Chưa có bằng chứng kho file/day1.2 trong lượt này.

Trước tag: commit bản thay đổi, tích hợp/push main, ghi hash commit bàn giao vào verification và gắn phase-2 trên main đó; không gắn tag lên main cũ26e481a vẫn mang manifest1.0. Không tự coi tag đã được tạo/push.
