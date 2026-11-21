# Ghi chú cài đặt sáng tạo Gói 2 (nhánh `p3/creative-trung`)

Chạy: `python3 -m chonoi.live --mode day --days 5 --creative` (hoặc `--mode gather --creative`). Không có cờ thì live và headless y hệt cũ.
Mã: `chonoi/creative/` (layer.py, creative.json), `chonoi/web/creative.js`, test `tests/test_creative_trung.py`.

## Đã làm
- **Đền Bà Thủy** (x=36, mặt nước): đứng yên trong bán kính 2,5 trong 180 tick (3 giây) thì thắp hương xong. Tốn thời gian ca sáng (đồng hồ vẫn chạy), không tốn tiền.
- **Buff Bà Thủy** (yêu cầu bổ sung của PO, thay cho "luck" trong file ý tưởng): (1) bơi nhanh x1,25; (2) giảm tỷ lệ gặp quái: Mãng Xà ra với xác suất x0,5, chuỗi mũi tên bớt 1 phím (tối thiểu 3), và với Cá Sấu lõi mỗi lần sắp chạm có 50% được "lướt qua" (cấp bất tử 60 tick trước cú chạm; luồng RNG `creative_skip`). HUD hiện biểu tượng buff kèm số giây còn lại.
- **Mãng Xà Vương**: mỗi 600 tick roll 35% (tối đa 2 con mỗi ca sáng) ở vị trí ngẫu nhiên sâu 8–20, nằm rình tối đa 40 giây. Lại gần (<= 2,0) thì quấn: Út Sen đứng yên, oxy vẫn giảm, không trừ Máu. Chuỗi 6 mũi tên, đọc cạnh lên của hướng (ghi ở `note_move`, nên không mất cú gõ nhanh). Đúng hết thì thoát + 2 giây không bị quấn lại; sai thì làm lại từ đầu; quá 8 giây thì mất thêm 2 giây oxy và ra chuỗi mới.
- **Miếu Cá Ông** (x=68): thắp hương như trên. Khi ngất (ngạt hoặc Cá Sấu), được roll d6 một lần mỗi ca sáng, ra 6 thì hồi sinh: Máu 1, oxy 50%, về bến, giữ nguyên giỏ, bất tử 120 tick. Cài bằng cách bọc `_faint` của phiên gather từ ngoài.
- Nạp script: live tự chèn `<script src="/creative.js">` vào trang khi bật `--creative`; không sửa `index.html`. Nếu PO muốn nhúng cố định, thêm đúng dòng đó trước `</body>` (đã có chống chèn trùng).

## Giả định của agent, chờ PO duyệt
1. Buff thay hẳn "luck" (không có hai cơ chế). Thời lượng 90 giây (5400 tick), hết thì có thể thắp lại; không phải "đến hết ca sáng".
2. Vị trí đền (x=36, x=68), 3 giây đứng yên, hệ số 1,25 / 0,5 / 50% đều là số tạm trong `creative.json`.
3. Hồi sinh cá Ông chỉ khi đã thắp hương miếu Cá Ông (file ý tưởng không nói rõ điều kiện); mỗi ca sáng một lần; hồi sinh không phát event lõi (`faint` không phát khi hồi sinh).
4. Mọi trạng thái sáng tạo reset mỗi ca sáng (ngày mới thắp lại).
5. Mãng Xà đứng yên (không đuổi); không xuất hiện ở ca tối/shop.
6. Tính năng "giảm quái" với Cá Sấu lõi là ngoại lệ so với câu "không đổi Cá Sấu lõi" trong file ý tưởng, theo yêu cầu bổ sung của PO; chỉ ở live, headless không đổi.
7. Việc đứng yên bất kỳ lúc nào gần đền (kể cả đang đợi) cũng tính là thắp hương; không cần phím riêng (Test Contract không cho nút mới).

## Chưa làm / không kiểm
- Gói 3 (Bà Chúa Xứ, Neak Ta, cháo Má Tư): chưa làm. Thẻ truyền thuyết "?" và bảng "ngất vì…" thuộc Gói 1 (nhánh khác).
- UNVERIFIED: chơi tay thật bằng bàn phím một ca đầy đủ có gặp Mãng Xà thật; chuỗi mũi tên trên trình duyệt chỉ xem bằng snapshot giả (ảnh `02-...GIA-LAP`); logic đã có test.
- UNVERIFIED: khi tay gõ cực nhanh hơn 2 cú trong cùng một lần poll POST thì `note_move` vẫn ghi đủ vì mỗi POST là một lần gọi; chưa đo trên trình duyệt thật.
