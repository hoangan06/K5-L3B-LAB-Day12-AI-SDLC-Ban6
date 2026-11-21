# Phase 4 — phân tích và phân công Ban6

Nguồn: [TICKET-04 / Test Contract v1.3 trên lab board](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg#phase-4), đã đọc trực tiếp. Tài liệu này cụ thể hóa phần P4 trong `docs/plan-p3-p4.md`; các API, tên file và phân công dưới đây là quyết định triển khai của nhóm, không phải nguyên văn đề.

## 1. Phase này phải bàn giao gì?

P4 là gói phát hành, đo đạc và kiểm chứng; giữ gameplay, tuning, kho cá thể và JSONL của P3. Thời lượng đề: phút 2:30–3:00 của lab, không phải giờ đồng hồ máy. Hạn cuối: tag `phase-4` và GitHub Release `v1.0.0` cùng commit trên main.

| Hạng mục | Điều kiện cần đạt |
|---|---|
| Manifest | `contract_version: "1.3"`; có `bench_cmd`, `soak_cmd` ở gốc và các lệnh chạy được |
| Bench có render | Cảnh gather lõi, độ tươi, cá bơi, Cá Sấu và hiệu ứng mặc định; nhân vật đứng ở bến; 1280×720; seed 42; nóng 3 giây rồi đo 30 giây; xuất đủ 5 trường |
| Cảnh báo/UI | Thủy quái gần, oxy thấp, khách sắp giận: có chữ hoặc biểu tượng. Có tương phản cao và chơi thử cả ba trong chế độ này |
| Clone sạch | Chạy được GUI trên macOS hoặc Linux bằng tối đa 3 lệnh theo README; ghi môi trường, điều khiển, test/headless/bench |
| Soak | Lệnh seed/days/out; 10 ngày liên tục trong một tiến trình; qua gather → quan → shop; kế hoạch D1–D5 lặp, trạng thái và ID nối tiếp |
| Release | Có gói chạy được đính kèm, release notes, CHANGELOG theo phase, CREDITS và LICENSE được rà |
| Bằng chứng | Regression P1–P3 còn hiệu lực đạt; ma trận AC-P4-xx, bench/soak/UI/clone khớp code bàn giao; clarify, AI log, retro và phản tư đủ người |
| Demo | Trực tiếp hoặc mp4 dưới 5 phút: chơi một ngày, cho thấy test đạt, phối hợp và ma trận bằng chứng |

Mốc 60 FPS trung bình, 30 FPS cho 1% low, tải ≤10 giây là mốc báo cáo. Đề chấm phần bench theo khả năng chạy lệnh và tạo đúng báo cáo, không yêu cầu sửa số để vượt mốc. Soak do giảng viên chạy để báo cáo, nhưng lệnh soak vẫn thuộc DoD. Nhóm 4 người không bắt buộc leaderboard/phụ đề SFX; ưu tiên lõi.

## 2. Hiện trạng đã xác minh trước khi chia

- Lần rà cuối: `origin/main` đã lên `5f9a0aa`, manifest 1.2, có migration kho cá thể gather/day/shop của Trung. Dùng commit này hoặc main mới hơn làm nền; chưa suy ra P3 đã nghiệm thu chỉ từ việc code được push.
- Nhánh `p3/an` đã có 16 test P3 và log trước migration, commit `163b50f`. Trung cần tích hợp và cho Ân nghiệm thu lại.
- Đức đã đẩy `origin/p4/duc`, HEAD `04f3681`: có `tools/bench.mjs`, UI cảnh báo/tương phản, báo cáo bench và ảnh. Tiếp tục trên nhánh đó, không làm lại công cụ khác.
- `runner.Session` và `DaySim` hiện chặn `days > 5`; `DaySim._start_day` lấy trực tiếp kế hoạch theo ngày. Đây là việc thật cần sửa cho soak 10 ngày.
- `contract.py` hiện nhận đến version1.2; điều kiện freshness đang gắn riêng1.2, headless day cũng chưa nhận1.3. Ân phải cập nhật cả kiểm version và yêu cầu freshness cho1.3. Test P3 của Ân hiện chỉ tự bật ở1.2: phải giữ chúng chạy khi nâng1.3.

Các artifact đã có ở nhánh Đức là bằng chứng của bản nhánh đó; chưa thay thế lần đo/chơi thử trên bản tích hợp có P3 và v1.3.

## 3. Chia việc và quyền sửa file

| Người / nhánh | Làm ngay, có thể song song | File sở hữu trong P4 | Hoàn thành khi |
|---|---|---|---|
| **Ân — `p4/an`** | Tích hợp P3/P4; adapter Session cho soak; parser/version1.3; README, đóng gói và phát hành. Chốt runtime với Duy trước, nâng manifest sau khi đã có migration P3 và lệnh thật | `game.contract.json`, `chonoi/contract.py`, `chonoi/headless.py`, `chonoi/runner.py`, `README.md`, `AGENTS.md`, `tests/test_p4_an.py`; sửa gate `tests/test_p3_an.py`; `tools/package_release.py`; proof `phase-4/an/` | Lệnh manifest chạy được; P3 test không bị skip trên1.3; gói sạch chạy GUI; tag/Release đúng commit sau QA |
| **Duy — `p4/duy`** | Viết `chonoi.soak`, bot tất định và test 10 ngày; chủ trì regression/smoke/clone sạch, ma trận kiểm chứng. Chuẩn bị harness ngay, sửa DaySim sau khi Trung bàn giao migration file này | `chonoi/soak.py`, `chonoi/sim/day.py` sau bàn giao; `tests/test_p4_duy.py`; `docs/verification/phase-4.md`; proof `phase-4/duy/`, `soak.json` | Một Session chạy đủ 10 ngày, không reset RNG/ID/trạng thái; gameplay báo cáo lặp lại được; regression và clone sạch có log |
| **Đức — `p4/duc` hiện có** | Hoàn thiện bench thật và 3 cảnh báo/tương phản; chạy lại trên bản tích hợp; ghi rõ môi trường và giới hạn | `tools/bench.mjs`, `chonoi/web/`, test bench riêng nếu cần; proof `phase-4/duc/`, `bench.json` | Bench đúng thời gian/công thức/cảnh; load_ms đo từ khởi chạy; chơi thử cảnh báo thật ở tương phản cao; ghi lỗi console và ảnh |
| **Trung — `p4/trung`** | Migration đã lên main: review kết quả P3 và hỗ trợ lỗi ở module còn giữ. Rà luật, release notes, credits/license, retro và checklist demo; review soak và giá/freshness | Module P3 chưa chuyển chủ; P4: `CHANGELOG.md`, `CREDITS.md`, `LICENSE`, `docs/release-notes-v1.0.0.md`, `docs/retro.md`, `docs/clarify.md`, `docs/ai-usage-log.md`, proof `phase-4/trung/` | P3 được nghiệm thu; docs phản ánh bản thật, retro rà hành động P2; release notes/checklist sẵn sàng |

**Mỗi file một người giữ tại một thời điểm.** Riêng `day.py`: Trung làm xong migration, push và báo commit bàn giao; Duy cập nhật nhánh theo commit đó rồi mới sửa soak. Nếu Duy chưa nhận file, vẫn làm module soak/test/ma trận song song. Nếu lỗi ở file người khác giữ, gửi lỗi + test tái hiện cho chủ file sửa; không tự merge đè.

**Bàn giao đã có:** migration `5f9a0aa` là nền chuyển `day.py` sang Duy, `contract.py`/manifest sang Ân. Từ P4, Trung review các file này và gửi lỗi/test cho chủ mới; nếu cần trực tiếp sửa thì báo nhận lại file trước. Ân/Duy phải giữ các thay đổi kho cá thể của commit nền khi thêm P4.

| Có thể bắt đầu ngay, không chờ code người khác | Phần cần đợi tích hợp |
|---|---|
| Ân: loader1.3, test parser, README và script đóng gói; draft runner theo API dưới đây | Kiểm soak10ngày cần DaySim của Duy; tag cần toàn bộ QA |
| Duy: DaySim soak, completed_results, bot, test và ma trận | Chạy qua Session cần adapter runner của Ân |
| Đức: sửa load_ms, cảnh báo/tương phản, test UI và bench | Bằng chứng cuối cần bản tích hợp P3/P4 |
| Trung: notes, CHANGELOG, credits/license, retro và review migration | Kết luận release cần kết quả cuối từ ba người |

Không có lời hứa Git sẽ tự hết conflict: phân công giảm xung đột bằng quyền sửa file và nền chung. Nếu main đổi trong lúc làm, chủ file xử lý trên nhánh mình và báo lại SHA nền; không chọn toàn bộ ours/theirs để bỏ mất code nhóm.

`live.py` hiện thuộc luồng UI của Đức: nếu cần sửa, Đức nhận; Ân chỉ phối hợp version qua loader, không cùng sửa file đó. Tài liệu dùng chung do Trung tổng hợp: mỗi người viết đoạn bàn giao trong proof của mình để Trung chép vào AI log/retro, tránh bốn người sửa cùng bảng. Mỗi người tự viết `docs/members/<GitHub-handle>.md` ≤200 từ, dẫn commit/bằng chứng, phần đã giúp người khác và một lỗi AI/bài học.

## 4. Giao diện dùng chung chốt cho P4

### 4.1. Lệnh và môi trường

```json
{"contract_version":"1.3","bench_cmd":"node tools/bench.mjs","soak_cmd":"python3 -m chonoi.soak"}
```

Đây là các khóa cần cập nhật trong manifest hiện có, không phải toàn bộ manifest. Giữ tuning P3 và các lệnh hiện hành. Đức giữ bench Node đang có; yêu cầu hiện tại của nhánh Đức: Node.js22+, Google Chrome, Python3; `CHONOI_CHROME` chọn Chrome và `PYTHON` chọn Python. Ân ghi rõ môi trường chơi và môi trường bench trong README; Duy thử trên Linux/macOS thật hoặc môi trường Linux có GUI/browser phù hợp, không suy ra từ Windows.

```bash
node tools/bench.mjs --seed 42 --duration 30 --out docs/proof/phase-4/bench.json
python3 -m chonoi.soak --seed 7 --days 10 --out docs/proof/phase-4/soak.json
```

Không ghi số liệu mẫu thành kết quả thật; lệnh lỗi phải trả mã khác0, ghi nguyên nhân. Nhóm dùng mã2 cho input sai, mã1 cho lỗi thực thi/ghi báo cáo.

### 4.2. Session/DaySim dùng cho soak

Giao diện nhóm chọn để không đổi luật chạy 5 ngày chuẩn:

```python
Session(mode, tuning, scenario, seed, inventory=None, *, days=1, soak=False)
build_sim(mode, tuning, scenario, seed, inventory, *, days=1, soak=False)
DaySim(tuning, scenario, streams, ids, *, days=1, soak=False)
```

- Ân giữ `runner.py`, truyền `soak` tới DaySim. Duy giữ constructor/logic DaySim sau bàn giao P3 và gọi Session từ `chonoi.soak`.
- `soak=False`: giữ giới hạn 1–5 ngày của luồng chuẩn; không thêm cờ soak vào headless/live chuẩn trong phạm vi này.
- `soak=True`: chỉ dùng mode day, `days` nguyên dương (không nhận bool); harness dùng scenario rỗng và một Session duy nhất cho toàn lượt.
- Duy đổi chọn kế hoạch thành chỉ số `(day - 1) % 5`; số Ngày thật, days_completed và ngữ cảnh sự kiện vẫn tăng đến10. Không tạo Session/RNG/allocator mới sau ngày5, không chạy hai lượt5ngày rồi ghép JSON.
- Tiền, tổng thu, uy tín và cấp nâng cấp đi qua các ngày theo gameplay; ID không tái dùng. Kho dư xử lý theo luật ngày P2/P3, không tự chuyển thành luật giữ toàn bộ kho qua ngày.
- Bot chỉ phát input hợp lệ dựa vào state và bộ đếm tất định; không sửa trực tiếp money/earned/reputation/IDs, không rút ngắn tuning để báo đã đủ10ngày.
- Mỗi kết quả lấy tại thời điểm Shop đóng của từng Ngày, trước khi pha sau thay state. Duy cần giữ bản sao state Shop cuối/row kết quả trước chuyển pha; không đọc snapshot ngày mới để gán cho ngày cũ. Không thêm event/field vào JSONL chuẩn chỉ để tiện soak.
- Chốt API lấy kết quả: `DaySim.completed_results` khởi tạo là list rỗng; sau mỗi Shop đóng, append một dict mới `{day, earned, reputation, score}` trước dựng ngày tiếp. `chonoi.soak` đọc qua `session.sim.completed_results` và copy vào báo cáo. Duy sở hữu cả nơi ghi và nơi đọc; không cần Ân thêm schema JSONL. Score dùng tuning hiện hành; không hard-code hệ số.
- Ân và Duy có thể test riêng adapter và DaySim trước khi gộp. Bản main trung gian phải vẫn chơi chuẩn được: runner chỉ truyền keyword `soak=True` khi đang soak (không bắt DaySim cũ nhận keyword mới ở lượt chuẩn), hoặc Ân tích hợp hai thay đổi cùng một lượt rồi chạy test trước push. Lượt soak chưa có adapter/DaySim đủ thì báo chưa sẵn sàng, không fallback thành hai Session5ngày.

### 4.3. Định dạng và cách đo

Bench: `avg_fps`, `p1_low_fps`, `frames`, `measured_s`, `load_ms`. `avg_fps = frames / measured_s`; 1% low lấy `max(1, ceil(0.01*frames))` frame chậm nhất rồi nghịch đảo thời gian trung bình của chúng (giây). Chỉ đếm khoảng đo sau nóng3giây; giữ render thật, không dùng số vòng mô phỏng làm FPS.

**Điểm cần Đức sửa/kiểm:** nhánh hiện có trả `load_ms` theo mốc `requestAnimationFrame` của trang sau điều hướng; chưa bao gồm thời gian khởi chạy tiến trình. Đề tính từ khởi chạy đến frame đầu tiên của cảnh. Đặt mốc trước khởi chạy và đồng bộ mốc/frame thực tế; lưu bằng chứng rõ cách đo. Ảnh hiện có dùng snapshot điều chỉnh để tái hiện cảnh báo: giữ làm kiểm UI, bổ sung chơi thử gameplay thật đủ ba cảnh ở tương phản cao.

Soak: `days`, `days_completed`, `crashes`, `results`, `duration_s`; `results[]` gồm `day`, `earned`, `reputation`, `score` lúc Shop đóng. Kết quả tốt: đủ N dòng ngày, `days_completed == days`, `crashes == 0`. Chạy cùng seed hai lần, so các trường gameplay; bỏ `duration_s` và metadata thời gian khỏi so tất định. Không đặt ngưỡng bộ nhớ không có trong đề.

## 5. Lịch tích hợp và phụ thuộc bắt buộc

| Mốc trong P4 | Người / việc | Điều kiện đi tiếp |
|---|---|---|
| 0–5 phút | Trung chốt/bàn giao P3; Ân+Duy chốt Session/DaySim; Đức sửa phép đo; Trung nháp docs | Có commit P3 làm nền. Nếu chưa có, báo ngay và chia người hỗ trợ, không đổi version để giả đã xong |
| 5–15 phút | Duy nối soak10ngày; Ân nối Session/version/README/package; Đức UI/bench; Trung docs | Mỗi nhánh push sớm. Module/ảnh mẫu có thể chuẩn bị trước, nhưng chưa gọi là nghiệm thu cuối |
| 15–20 phút | Ân tích hợp P3 rồi P4; Duy regression/smoke; Đức bench/UI trên bản tích hợp | DaySim nhận soak trước khi chạy nghiệm thu10ngày; parser nhận1.3 trước CLI cuối; migration P3 trước test freshness cuối |
| Phút20 | Cả nhóm rà blocker và điều người xong hỗ trợ | Chốt bản ứng viên, ngừng thêm ý tưởng ngoài lõi |
| 20–25 phút | Duy clone sạch từ gói/commit ứng viên; Đức đo lại nếu code render đổi; Trung retro/notes; mọi người phản tư | Lưu SHA bản ứng viên, lệnh, môi trường, mãthoát và kết quả thật; cập nhật ma trận |
| 25–30 phút | Ân kiểm main, artifact, gói, tag và Release; Trung review đối chiếu | Test/gameplay/UI/bench/soak khớp code bàn giao, gói đính kèm chạy được. Nếu lỗi còn lại, ghi thật giới hạn và trạng thái, không ghi PASS giả |

Không cần chờ xong toàn bộ P3 mới soạn docs/UI/bench/soak harness. **Nghiệm thu cuối** phải chờ P3 tích hợp; bench cuối phải chờ UI cuối; clone/package cuối phải chờ lệnh và dependency được chốt; tag/Release phải chờ commit bàn giao đã được kiểm.

## 6. Ma trận bàn giao do Duy giữ

Các mã dưới đây do nhóm đặt để truy vết yêu cầu TICKET-04:

| Mã | Bằng chứng cần gắn | Người cung cấp |
|---|---|---|
| AC-P4-01 | Manifest1.3, lệnh bench/soak thật và kiểm CLI/version | Ân |
| AC-P4-02 | bench.json, lệnh đo, môi trường, công thức và cấu hình cảnh | Đức |
| AC-P4-03 | Chơi thử ba cảnh báo ở tương phản cao, ảnh và console | Đức |
| AC-P4-04 | Log clone/gói sạch, tối đa3lệnh GUI trên Linux/macOS | Duy + Ân |
| AC-P4-05 | soak.json10ngày và so gameplay của hai lần cùng seed | Duy |
| AC-P4-06 | Regression P1–P3, smoke kho, test P3 thực sự chạy trên1.3 | Duy + Ân |
| AC-P4-07 | Gói, release notes, CHANGELOG, credits/license, SHA/tag/Release | Ân + Trung |
| AC-P4-08 | Retro rà hành động P2, clarify, AI log, phản tư4người | Trung + từng người |

Trong `docs/verification/phase-4.md`, ghi từng mã → đường dẫn bằng chứng → lệnh/kết quả → SHA nguồn kiểm. Không chỉ ghi “đã xong”. Khi commit cuối chỉ thêm báo cáo, ghi rõ SHA code đã chạy; nếu runtime/render/package thay đổi phải kiểm lại phần bị ảnh hưởng. Không đòi log nhúng chính SHA của commit đang tạo ra log.

Ân tạo `phase-4` và tag của Release `v1.0.0` cùng SHA trên main; kiểm cả hai tag đã push và release có asset tải được. Không di chuyển tag phase cũ. Gói không chứa token, môi trường cá nhân hoặc file tạm. README dùng đường chạy từ root gói; không dựa vào file không được đóng gói.

## 7. Cách làm trên Git

Mỗi người dùng nhánh riêng; cập nhật từ main đã bàn giao rồi mới sửa file đang nhận. Không merge cả nhánh người khác vào nhánh mình nếu chỉ cần gọi API; báo Ân tích hợp để tránh kéo theo lịch sử chồng chéo.

Phân công được phát hành riêng trên nhánh `p4/plan-an`, chỉ thay file này. Có thể đọc trực tiếp trên GitHub; muốn đưa file vào nhánh đang làm, commit công việc hiện tại cho working tree sạch rồi `git fetch origin` và `git cherry-pick <commit-phan-cong>` (SHA được Ân gửi trong chat). Không cần switch sang nhánh phân công, không cherry-pick cả nhánh code của người khác.

Ví dụ cho người chưa có nhánh P4, thay `<ten>` bằng `an`, `duy` hoặc `trung`:

```bash
git fetch origin
git switch -c p4/<ten> origin/main
```

Nếu working tree chưa sạch, commit đúng phần mình trước khi đổi nhánh. Đức tiếp tục `p4/duc` đã có. Mỗi người chỉ add file sở hữu; push nhánh và gửi commit + lệnh kiểm + phần còn thiếu. Ân là người chốt merge main và tag, Trung review đối chiếu trước phát hành.
