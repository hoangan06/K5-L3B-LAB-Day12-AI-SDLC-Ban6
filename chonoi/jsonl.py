"""Ghi JSONL tất định: làm tròn 3 chữ số khi XUẤT (tính toán dùng giá trị chính xác).

Ngoại lệ Contract v1.2: trường `fresh` giữ đủ chính xác, để JSONL khớp file kho và không đổi phía ngưỡng 30
(vd 29.9999 không hiện thành 30.0). Xem docs/contracts/phase-3-interfaces.md §8.
"""

import json


def _clean(v, key=None):
    if isinstance(v, float) and key == "fresh":
        return v
    if isinstance(v, float):
        r = round(v, 3)
        return 0.0 if r == 0 else r  # tránh -0.0
    if isinstance(v, dict):
        return {k: _clean(x, k) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_clean(x) for x in v]
    return v


def dumps(obj) -> str:
    return json.dumps(_clean(obj), ensure_ascii=False, separators=(",", ":"))


class JsonlWriter:
    def __init__(self, path: str):
        self._f = open(path, "w", encoding="utf-8", newline="\n")

    def write(self, obj):
        self._f.write(dumps(obj) + "\n")

    def close(self):
        self._f.close()
