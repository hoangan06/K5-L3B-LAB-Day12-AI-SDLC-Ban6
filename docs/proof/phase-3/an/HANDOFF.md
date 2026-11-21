# Phase 3 — Ân: nghiệm thu gather và runner

## Phạm vi và trạng thái

Theo `docs/plan-p3-p4.md`, Trung nhận migration runtime; Ân review gather/runner, viết test nghiệm thu và chốt tag khi đủ điều kiện. Nhánh làm việc: `p3/an`, nền `feb93a2`.

Đã viết `tests/test_p3_an.py` với 16 ca. **Chưa nghiệm thu P3 và chưa gắn tag**: manifest nền vẫn là 1.1; runtime gather/scenario/inventory chưa chuyển sang cá thể.

## Chạy test

Từ thư mục gốc repo, trong WSL/Linux:

```bash
# Bắt buộc kiểm P3 ngay cả khi manifest còn 1.1:
AN_REQUIRE_P3=1 PYTHONPATH=tests:. python3 -m unittest discover -s tests -p test_p3_an.py -v

# Toàn bộ regression:
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
```

Khi manifest là 1.2, 16 ca tự chạy trong regression. Khi manifest còn 1.1, chúng được đánh dấu skip để không áp hợp đồng P3 lên bản P2. **Skip không phải PASS P3.** Biến `AN_REQUIRE_P3=1` dùng tuning 1.2 riêng trong bộ test; không thay manifest trên đĩa. Các ca CLI chỉ thay nguồn nạp manifest bằng bản test, còn scenario loader, runner, sim, JSONL và writer kho đều chạy thật.

## Các yêu cầu đã đưa vào test

- Fresh 30 phát `spoiled` tick 1 đúng payload `item_id/kind/location: hold`; không phát lặp.
- Hao 0.5 mỗi giây, kẹp tại 0; đúng 30 chưa ươn; hàng đã ươn vẫn chiếm chỗ và chặn hái khi đầy.
- Nhiều cá thể cùng ươn: phát theo ID tự nhiên; không sắp lại giỏ, vì giỏ giữ thứ tự nhặt.
- Hái/bắt cấp cá thể mới fresh 100; chỉ hao từ bước sau; một đàn yield nhiều cá thể phải có ID và object riêng.
- Fixture có I10 thì ID mới phải tiếp tục I11; không tái dùng ID.
- `monster_hit.lost` rồi `faint.lost` là mảng cá thể theo thứ tự pop LIFO, giữ fresh sau hao đầu bước.
- Hao/ươn trước ngạt/ngất; pause đóng băng gameplay, resume hao ngay bước tiếp tục.
- Không mutate fixture nguồn; xuất kho sắp bản sao theo ID, không đổi thứ tự giỏ.
- Gather cập bến: file kho bằng `gather_end.data.inventory`, quán tick 0 giữ đúng ID/kind/fresh, không hao thêm hoặc làm tròn 29.9999 thành 30.
- Hết tick budget mà chưa kết thúc gather thì không ghi đè file kho đã có.

## Kết quả trên nền trước migration

`acceptance-before-migration.txt`: 16 ca chạy bắt buộc, 2 đạt, 13 FAIL, 1 ERROR. Đây là bằng chứng trước triển khai, không phải kết quả nghiệm thu cuối.

`regression-before-migration.txt`: chạy trong WSL bằng lệnh regression ở trên, tổng 215 ca, **199 đạt và 16 skip**. Không có regression mới đối với nền P1/P2. Lần fetch cuối khi bàn giao chưa thấy main cập nhật sau `feb93a2`.

Các lỗi chính đã đối chiếu nguồn:

1. `scenario.py` từ chối `hold` dạng object, nên 3 ca CLI bị mã 2 trước khi tới runtime.
2. `gather.py` chưa hao fresh/phát spoiled; `gather_actions.py` vẫn thêm kind dạng chuỗi. Chưa cấp ID cá thể mới trong giỏ.
3. `inventory.hold_to_items` vẫn cộng kho đếm; truyền giỏ cá thể gây `TypeError: unhashable type: dict` khi kết thúc.
4. `jsonl._clean` đang làm tròn mọi float 3 chữ số. Cần giữ đủ độ chính xác của fresh trong file/event để bàn giao không đổi nhánh ngưỡng.
5. Review `runner.Session`: pause được xử lý trước `sim.step`; writer chỉ gọi khi gather đã kết thúc và có cờ chống ghi lặp. Cần xác nhận lại schema và precision bằng các ca CLI sau khi adapter kho được đổi.

## Sau khi Trung đẩy migration

1. Gộp main mới vào `p3/an`, chạy 16 ca bắt buộc; điều tra từng lỗi bằng PRD/giao diện, không hạ assertion để lấy xanh.
2. Chạy toàn bộ regression, smoke kho cá thể của Duy và kiểm tất định; lưu lại log cuối, không ghi đè bằng chứng trước migration.
3. Kiểm bằng chứng day/HUD của Đức và ma trận `docs/verification/phase-3.md`; chốt CHANGELOG, AI log, retro cùng nhóm.
4. Chỉ gắn/đẩy tag `phase-3` trên commit main đã đủ các điều kiện trên.

Tin nhắn có thể gửi Trung:

> Ân đã chuẩn bị 16 test gather/runner P3 trên nhánh p3/an. Bản nền feb93a2 còn manifest 1.1 nên chạy bắt buộc hiện 2 đạt, 13 FAIL, 1 ERROR: loader chưa nhận hold cá thể; gather chưa hao/phát spoiled; kho đếm lỗi khi gather_end. Nhờ Trung báo khi migration lên main để Ân gộp vào, chạy nghiệm thu và chốt tag. Lưu ý giữ thứ tự giỏ cho LIFO, chỉ sort bản xuất kho; JSONL đừng làm tròn fresh qua ngưỡng 30.
