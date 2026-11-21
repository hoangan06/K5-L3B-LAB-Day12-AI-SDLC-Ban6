# Kiểm chứng thanh toán và dọn món

Kiểm trên nhánh `p1/duc` với các thay đổi local dựa trên `dd568c3`.

| Lệnh | Kết quả |
|---|---|
| `PYTHONPATH=tests:. PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_p1_duc.py -v` | 5/5 test đạt |
| `PYTHONPATH=tests:. PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` | 37/37 test đạt, gồm test live trên localhost |

Test riêng kiểm bộ đếm tiền, cách cộng boa, giới hạn uy tín và payload `paid`. Test dọn món kiểm việc xóa đúng món trên tay hoặc bếp và giữ nguyên tồn kho.

Kết quả xác nhận hai helper độc lập. Việc thu đúng một lần khi khách ăn xong hoặc khi đóng ca sẽ được kiểm khi ghép với `resolve_departures`.
