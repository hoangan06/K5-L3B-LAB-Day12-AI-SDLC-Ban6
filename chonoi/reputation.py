"""Cộng/trừ uy tín theo số thập phân để điểm floor không lệch do cộng float.

Giữ float ở giao diện snapshot/context hiện có; không làm tròn gần số nguyên,
vì fixture hợp lệ như1.9999999999 vẫn phải có floor bằng1.
"""

from decimal import Decimal


def adjust_reputation(current, delta, minimum, maximum):
    updated = Decimal(str(current)) + Decimal(str(delta))
    return float(min(Decimal(str(maximum)), max(Decimal(str(minimum)), updated)))
