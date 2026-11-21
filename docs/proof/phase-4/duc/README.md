# Phase 4 · Benchmark và cảnh báo

## Benchmark gather

Từ thư mục gốc, dùng Python 3, Node.js 22+ và Google Chrome. Nếu Chrome nằm ngoài đường dẫn mặc định, đặt biến `CHONOI_CHROME` trỏ tới file thực thi.

```sh
node tools/bench.mjs --seed 42 --duration 30 --out docs/proof/phase-4/bench.json
```

Giá trị đề xuất cho `bench_cmd` là `node tools/bench.mjs`. Lần đo dùng Chrome 158 headless, canvas 1280×720, seed 42 và làm nóng 3 giây. [Kết quả đo](../bench.json) ghi 1.801 khung hình trong 30,015 giây, trung bình 60,00 FPS, 1% thấp nhất 59,52 FPS và khung cảnh đầu tiên sau 162,7 ms. Mốc tải tính từ lúc điều hướng đến khung vẽ có snapshot đầu tiên. 1% thấp nhất tính theo nghịch đảo thời lượng trung bình của 1% khung chậm nhất.

## Kiểm tra giao diện

Chạy `python3 -m chonoi.live --mode day` và bật **Tương phản cao** ở góc dưới bên phải. Kiểm tra Chrome 1280×720 dùng trang thật qua localhost, với snapshot từ engine được điều chỉnh để tái hiện từng cảnh báo.

- [Thủy quái ở gần](thuy-quai.png) khi người chơi ở vùng nước đủ sâu và trong bán kính phát hiện hoặc rượt đuổi của loài.
- [Oxy sắp hết](oxy.png) khi còn dưới 25% dung lượng.
- [Khách sắp giận](khach.png) khi khách đang chờ còn tối đa 25% thời gian kiên nhẫn.

Bật bằng Space khi nút có tiêu điểm, tắt bằng chuột. Cả ba cảnh báo có chữ và biểu tượng. Cảnh báo khách biến mất khi chuyển sang ăn. Console ghi 0 lỗi.

Regression đạt 199/199 với `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v` trên nhánh Phase 4 của Đức.
