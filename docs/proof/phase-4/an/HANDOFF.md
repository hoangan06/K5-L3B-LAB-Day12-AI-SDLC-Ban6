# Phase 4 — Ân: contract, Session và đóng gói

Nhánh `p4/an`. Phân công: `docs/PHAN-CONG-PHASE-4.md`.

## Thay đổi

- Loader nhận1.3, giữ validation freshness/P2 cho1.3 và kiểm bench_cmd/soak_cmd khác rỗng. Manifest khai `node tools/bench.mjs` và `python3 -m chonoi.soak`, giữ tuning P3.
- Headless day nhận1.3. Session/build_sim nhận `soak=False`; khi True chỉ cho day, days nguyên dương, truyền `soak=True` vào DaySim của Duy. Không tăng giới hạn CLI chơi chuẩn1–5ngày.
- Gate fixture/test/smoke/tất định nhận cả1.2/1.3. Đây là sửa tương thích version theo TICKET-04, không bỏ test/luật P3. Test P3 riêng của Ân cũng bật ở1.3.
- 9 test P4: loader và command thiếu/sai; freshness còn bắt buộc; loader1.2 không cần lệnh P4; CLI day/quan thật1.3; CLI chuẩn chặn10ngày trước output; adapter soak và tham số sai; đóng gói bỏ file môi trường/cache và không ghi đè ZIP.
- README: clone sạch3lệnh GUI, Python3.10+, điều khiển, test/headless/bench/soak, môi trường bench riêng Node22+/Chrome, dùng ZIP không cần Git.
- Script `tools/package_release.py`: allowlist source/docs, không lấy symlink/cache/dist/.env; ZIP có BUILD-INFO.json chứa commit nguồn và hash file. File còn thiếu được liệt kê, không giả là Release đầy đủ. ZIP nằm trong dist/ đã gitignore.
- Đã gộp nhánh bench/UI `origin/p4/duc` hiện có để kiểm tích hợp; không sửa đè tools/bench.mjs hoặc UI của Đức.

## Kiểm tra

Các log trong thư mục này là kết quả chạy, không dùng số liệu mẫu. `acceptance.txt` là test riêng; `regression.txt` là lần regression cuối; đọc kết luận cuối log. Khi có kết quả mới sẽ cập nhật phần bàn giao.

Lần đầu test CLI của AI đọc dòng đầu JSONL như snapshot, nhưng day có event khởi tạo trước snapshot; đã sửa test chọn đúng type=snapshot. Không đổi thứ tự output để phục vụ test.

Test P3 của Ân từng phát hiện JSONL khác file kho vì làm tròn fresh. Trong lúc review, đã thử phép so dung sai theo contract; sau khi Trung sửa precision ở main `04cd262`, giữ lại phép so bằng tuyệt đối gốc của test để bảo vệ bàn giao ID/kind/fresh. Không còn nới assertion này trong bản cuối.

## Bàn giao cho Duy

```python
session = Session("day", tuning, {}, seed, days=10, soak=True)
```

Adapter của Ân đã sẵn sàng. DaySim cần nhận keyword soak=True, cho N ngày, chọn kế hoạch modulo5 và giữ một allocator/Streams. Duy giữ `completed_results` lấy lúc Shop đóng và module `chonoi.soak`; xem API đã chốt trong phân công. Unit test adapter dùng mock constructor để kiểm truyền tham số, **không dùng nó làm bằng chứng đã chạy đủ10ngày**.

## Còn phải chốt trước phase-4 / Release

- Tích hợp module soak/DaySim10ngày của Duy, chạy lệnh manifest thật và kiểm cùng seed hai lần.
- Đức kiểm lại load_ms tính từ lúc khởi chạy và chơi thật ba cảnh báo ở tương phản cao trên bản tích hợp. Kết quả nhánh cũ không thay nghiệm thu cuối.
- Trung bàn giao LICENSE/release notes, retro/AI log, và các file dùng chung. Ân không tự đoán license cho source/tài sản.
- Duy cập nhật ma trận P4 và clone sạch; cả nhóm tự điền phản tư. Ân có file `docs/members/hoangan06.md`.
- Tạo lại gói từ code bàn giao, kiểm GUI trong gói, rồi tag phase-4 và Release v1.0.0 cùng SHA main. Chưa tạo tag/Release P4 khi các bước này còn thiếu.

## Dòng AI log gửi Trung tổng hợp

Ân — OpenAI Codex — P4 loader1.3/Session soak, version gates, CLI tests, README và packaging. Chưa đo token/chi phí. AI từng đọc event đầu JSONL thành snapshot và viết phép so fresh quá chặt; phát hiện bằng chạy CLI thật, sửa test theo contract, không đổi runtime để né test.
