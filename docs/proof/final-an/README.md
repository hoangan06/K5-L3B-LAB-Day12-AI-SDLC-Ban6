# Rà soát và sửa bản nộp cuối — Ân

Nền: main58e0e91 (đã giữ bản phản tư mới của Trung); nhánh `fix/final-an`. Các sửa dưới đây thực hiện sau khi Release v1.0.0 đã công bố ở dbe6d20. Bản nộp cuối được tích hợp main và đóng gói lại; SHA chính xác ghi trong BUILD-INFO.json của ZIP và package-check.json trên Release. Asset mang tiền tố archive- là bản cũ, không dùng nộp.

## Đã sửa

1. Uy tín cộng/trừ qua Decimal(str(...)), kẹp theo tuning rồi giữ kiểu float ở giao diện hiện có. Không round tùy tiện sát số nguyên. Mười lần boa0.2 từ0 đạt2.0, tính điểm đúng.
2. Snapshot quán có player.vel tại tick0 và sau di chuyển/chặn mép.
3. kind sai kiểu ở file kho/hold/stock trả mã2, không crash hay tạo output.
4. Node không nhận trường lạ. Fixture/preset Cá Sấu đúng2waypoint, target_idx0/1.
5. Natural ID dùng hậu tốASCII; chữ số Unicode và newline không bị parse sai.
6. HUD/Canvas/nút tương phản dùng sans-serif từ18px, giữ cảnh đồ họa pixel.
7. TEAM: Ban6, 4người; kênh trực tiếp tại lớp; không phát sinh bất đồng/trễ theo người dùng; Nguyễn Bảo Trung; vai tích hợp/Release của Ân.
8. Phản tư Ân nêu từngphase, giúp nhóm, lỗi AI và bài học; dưới200từ, có link bằng chứng. Nhật ký AI chỉ bổ sung phần Ân; không giả viết thay thành viên khác.

## Kiểm chứng

| Kiểm | Kết quả / file |
|---|---|
| Toàn bộ test | **288/288 đạt, không skip**, all-tests.txt |
| Hồi quy mới | **9/9 đạt**, regressions.txt và tests/test_final_an.py |
| Replay CLI lỗi audit | input-probes.json: kind sai kiểu/node lạ/quái sai schema trả2 trước output; IDUnicode đúng thứ tự |
| Replay quán thật | score-probe.json: score_mismatch_count0 (trước sửa16snapshot sai), snapshot cópos/vel |
| TEAM | team-check.txt: đủ4tài khoản, khớp team_size4 |
| Kho / tất định | smoke.txt và determinism.txt: PASS |
| Soak | soak.json: 10/10ngày, 0crash |
| UI | ui-check.json + hai ảnhPNG: ba cảnh báo có tương phản cao, 0exception; đã xem ảnh chữ rõ sau đổi font |

Lệnh từ rootrepo trong WSL/Linux:

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
python3 tools/check_team.py
python3 tools/smoke_inventory.py --require-v12
python3 tools/check_determinism.py
python3 -m chonoi.soak --seed 7 --days 10 --out soak.json
```

UI dùng tools/verify_release_ui.mjs với Chrome/Node và Python thật. Các file replay được tạo lại bằng script trong thư mục audit trước nộp trên máy, chỉ sinh input hợp lệ rồi gọi CLI, không sửa tuning/game state để ép kết quả.

## Phạm vi còn lại

- Duy tự viết docs/members/duydang2k4.md và nhật ký AI của mình; Đức tự bổ sung nhật ký cácphase đã dùng AI nếu thiếu.
- Đề không bắt buộc có MP4 nếu demo trực tiếp; nhóm cần chọn hình thức và đáp ứng checklist demo.
- Chủ repo yêu cầu tích hợp và cập nhật Release. Giữ nguyên phần cá nhân của Duy/Đức theo yêu cầu; không tự điền thay. Kiểm gói và biên nhận phát hành được đính kèm Release, không ghi ngược vào source sau khi gắn tag.
