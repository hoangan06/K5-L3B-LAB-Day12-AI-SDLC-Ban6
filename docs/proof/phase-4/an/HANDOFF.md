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

Code gameplay kiểm trên `2f3f5b6` (đã gộp Duy `6a445b8` và main `2ff2be1`); các cập nhật sau đó thuộc tài liệu, đóng gói và test packaging, không thay gameplay.

| Kiểm tra | Kết quả / bằng chứng |
|---|---|
| Regression P1–P4 | **266/266 đạt, không skip**, `regression.txt` |
| Test riêng Ân | **9/9 đạt**, `acceptance.txt`; chạy lại sau sửa launcher/package metadata |
| Gather → file → quán | PASS contract1.3, `smoke.txt` |
| Tất định | JSONL/kho lặp từng byte, `determinism.txt` |
| LiveGame/HTTP5ngày | PASS, `live-five-days.txt` và `live-five-summary.json`; chạy engine thật nhanh hơn đồng hồ, không sửa luật |
| Soak thật10ngày ×2 | days_completed10, crashes0, đủ10results; hai lần cùngseed7 gameplay giống nhau; `soak-1.json`, `soak-2.json`, `soak-check.json` |
| ZIP trong thư mục riêng | `package-build.txt`, `package-check.json`: kiểm hash, import đúng source giải nén, headless day và GUI HTTP/canvas/menu trên Linux WSL; không tuyên bố đã chơi bằng mắt/clone sạch |

Các log là kết quả thật. Gói cuối của Ân: `dist/chonoi-v1.0.0-an-f970332.zip`, dựng từ **commit sạch f970332**; `package-check.json` ghi working_tree_dirty=false và SHA256 ZIP. BUILD-INFO chứa hash từng file. Đây vẫn là gói ứng viên vì thiếu LICENSE; khi phát hành phải tạo lại từ commit bàn giao đủ gate. ZIP ở dist/ không commit vào Git. Bản candidate đầu trước f970332 chỉ là kiểm thử công cụ.

Lần đầu test CLI của AI đọc dòng đầu JSONL như snapshot, nhưng day có event khởi tạo trước snapshot; đã sửa test chọn đúng type=snapshot. Không đổi thứ tự output để phục vụ test.

Test P3 của Ân từng phát hiện JSONL khác file kho vì làm tròn fresh. Trong lúc review, đã thử phép so dung sai theo contract; sau khi Trung sửa precision ở main `04cd262`, giữ lại phép so bằng tuyệt đối gốc của test để bảo vệ bàn giao ID/kind/fresh. Không còn nới assertion này trong bản cuối.

## Bàn giao cho Duy

```python
session = Session("day", tuning, {}, seed, days=10, soak=True)
```

Adapter của Ân đã sẵn sàng và **đã tích hợp DaySim/soak thật của Duy `6a445b8`**. Hai lệnh CLI10ngày đã đạt, khác với unit test mock constructor chỉ kiểm truyền tham số. Duy tiếp tục giữ DaySim/soak và ma trận QA.

## Còn phải chốt trước phase-4 / Release

- Soak đã kiểm xong trên bản tích hợp; gửi các log ở trên cho Duy cập nhật AC-P4-01/05/06 trong ma trận (tránh sửa đè file Duy đang giữ).
- Đức kiểm lại load_ms tính từ lúc khởi chạy và chơi thật ba cảnh báo ở tương phản cao trên bản tích hợp. Kết quả nhánh cũ không thay nghiệm thu cuối.
- Release notes/CREDITS/retro mới của Trung đã gộp. **LICENSE vẫn chưa có**; nhóm cần chốt giấy phép phù hợp. Ân không tự đoán license cho source/tài sản.
- Duy cập nhật ma trận P4 và clone sạch; cả nhóm tự điền phản tư. Ân có file `docs/members/hoangan06.md`.
- Tạo lại gói từ code bàn giao, kiểm GUI trong gói, rồi tag phase-4 và Release v1.0.0 cùng SHA main. Chưa tạo tag/Release P4 khi các bước này còn thiếu.

## Dòng AI log gửi Trung tổng hợp

Ân — OpenAI Codex — P4 loader1.3/Session soak, version gates, CLI tests, README, packaging và tích hợp soak Duy. Chưa đo token/chi phí. AI từng đọc event đầu JSONL thành snapshot; phát hiện bằng chạy CLI thật và sửa test chọn đúng type. Test bàn giao fresh bằng tuyệt đối được giữ sau khi Trung sửa serializer, không đổi runtime để né test.

## Tag P3 đã xử lý trong lượt này

Theo yêu cầu riêng của Ân, đã kiểm worktree sạch main `04cd262`: 232 test đạt, smoke v1.2 và tất định đạt; gắn/đẩy annotated tag `phase-3` tại commit đó. Bằng chứng: `docs/proof/phase-3/an/tag-*.txt`. Không lấy code P4 để gắn tag P3.
