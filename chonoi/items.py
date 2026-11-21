"""Kho cá thể Contract v1.2 (TICKET-03): {"items":[{"id","kind","fresh"}]}, dùng chung gather/quán/shop/CLI.

Bật khi tuning có khối `freshness`. Độ tươi lưu bằng Fraction để so ngưỡng 30 và floor chính xác:
hao mỗi tick là 0.5/60 = 1/120 (giỏ) và 0.25/60 = 1/240 (quán). Khi đọc lại số thực từ file/JSON,
`exact()` khôi phục đúng phân số có mẫu nhỏ (vd k/240) nếu số thực là ảnh của nó, nên giá trị và nhánh
ở ngưỡng không đổi sau bàn giao.
"""

import math
from fractions import Fraction

from .errors import BadInput
from .ids import sort_by_id

ITEM_KEYS = {"id", "kind", "fresh"}


def item_mode(tuning):
    return "freshness" in tuning


def _num(v):
    return not isinstance(v, bool) and isinstance(v, (int, float, Fraction)) and math.isfinite(v)


def exact(v):
    """Số → Fraction. Số thực gần (< 1e-9) một phân số mẫu ≤ 10^6 thì lấy phân số đó."""
    if isinstance(v, Fraction):
        return v
    f = Fraction(str(v))
    g = f.limit_denominator(10**6)
    return g if abs(g - f) < Fraction(1, 10**9) else f


def load_items(raw, kinds, where):
    """Kiểm mảng cá thể → list mới {id, kind, fresh: Fraction}, giữ thứ tự mảng. Sai schema → mã 2."""
    if not isinstance(raw, list):
        raise BadInput(f"{where}: contract v1.2 cần mảng cá thể {{id,kind,fresh}} (kho đếm → mã 2)")
    out, seen = [], set()
    for it in raw:
        if not isinstance(it, dict) or set(it) != ITEM_KEYS:
            raise BadInput(f"{where}: cá thể phải có đúng id, kind, fresh")
        iid, kind, fresh = it["id"], it["kind"], it["fresh"]
        if not isinstance(iid, str) or not iid or iid in seen:
            raise BadInput(f"{where}: id cá thể rỗng hoặc trùng: {iid!r}")
        if not isinstance(kind, str) or kind not in kinds:
            raise BadInput(f"{where}: nguyên liệu lạ {kind!r}")
        if not _num(fresh) or not 0 <= fresh <= 100:
            raise BadInput(f"{where}: fresh của {iid} phải hữu hạn trong [0, 100]")
        seen.add(iid)
        out.append({"id": iid, "kind": kind, "fresh": exact(fresh)})
    return out


def dump_item(item):
    return {"id": item["id"], "kind": item["kind"], "fresh": float(item["fresh"])}


def dump_sorted(items):
    return [dump_item(it) for it in sort_by_id(items)]


def spoiled_below(tuning_fresh):
    return exact(tuning_fresh["spoiled_below"])


def decay_items(items, rate_per_s, limit, location, events):
    """Trừ rate/60 mỗi cá thể (kẹp 0); phát spoiled theo id cho cá thể vừa qua ngưỡng. Trả set id vừa ươn."""
    step = exact(rate_per_s) / 60
    newly = set()
    for it in sort_by_id(items):
        was_ok = it["fresh"] >= limit
        it["fresh"] = max(Fraction(0), it["fresh"] - step)
        if was_ok and it["fresh"] < limit:
            newly.add(it["id"])
            events.append(("spoiled", {"item_id": it["id"], "kind": it["kind"], "location": location}))
    return newly
