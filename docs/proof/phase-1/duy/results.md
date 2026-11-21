# Kết quả kiểm tra phần Duy

- Trong sandbox, `.venv` không truy cập được Python nền trong WindowsApps. Chạy ngoài sandbox: `.\.venv\Scripts\python.exe --version` trả `Python 3.11.9`; `python3` cũng có trên PATH.
- `.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_p1_duy.py -v`: 3 test đạt.
- `.\.venv\Scripts\python.exe tools/smoke_inventory.py`: PASS, kho gather khớp stock quán tick 0.
- `$env:PYTHONPATH='tests;.'; .\.venv\Scripts\python.exe -m unittest discover -s tests -v`: 35 test đạt, 19.149 giây.
- Helper chưa nối vào `GatherSim.step()`, thuộc phần Ân. Các test hồi cây đúng tick, giữ phím, ưu tiên bến và kho ngất cần kiểm lại sau tích hợp; test tick limit ghi đè file có sẵn cũng chưa được bổ sung. Không xác nhận pipeline đầy đủ từ test helper.
- Chưa có commit bàn giao; ghi SHA và kết quả thực tế sau khi môi trường và tích hợp sẵn sàng.
