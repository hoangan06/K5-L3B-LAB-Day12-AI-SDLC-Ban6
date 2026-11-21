"""Kho cá thể và độ tươi của quán (Trung, P3) — TICKET-03 §1, Test Contract v1.2.

Bật khi tuning có khối `freshness` (contract v1.2); không có thì quán chạy kho đếm như P1–P2.
Kho quán: list cá thể {id, kind, fresh}; fresh lưu bằng Fraction để so ngưỡng 30 và floor chính xác.
Phần giữ của khách: list id cá thể (sort theo id).
"""

from math import floor

from ..ids import id_key, sort_by_id
from ..items import decay_items, dump_item, exact, item_mode  # noqa: F401 (quan.py import từ đây)
from ..items import load_items as _load_items


def load_items(raw, kinds, where):
    """Kiểm mảng cá thể v1.2 (chonoi.items) → list sort theo id. Sai schema → mã 2."""
    return sort_by_id(_load_items(raw, kinds, where))


def spoiled_below(sim):
    return exact(sim.fresh_cfg["spoiled_below"])


def is_spoiled(sim, item):
    return item["fresh"] < spoiled_below(sim)


def reserved_ids(sim, skip=None):
    return {i for c in sim.customers if c is not skip for i in c["reserved"]}


def pick(sim, recipe, taken):
    """Mỗi kind lấy cá thể chưa ươn, chưa ai giữ, tươi nhất rồi id nhỏ. Thiếu → None."""
    out = []
    for kind, n in sorted(recipe.items()):
        cand = sorted((it for it in sim.stock if it["kind"] == kind and it["id"] not in taken
                       and not is_spoiled(sim, it)), key=lambda it: (-it["fresh"], id_key(it["id"])))
        if len(cand) < n:
            return None
        out += [it["id"] for it in cand[:n]]
    return sorted(out, key=id_key)


def available_counts(sim):
    """Số cá thể dùng được (chưa ươn, chưa giữ) theo kind, đủ kind của thực đơn."""
    from .quan_validation import menu_kinds
    taken = reserved_ids(sim)
    out = {k: 0 for k in menu_kinds(sim.menu)}
    for it in sim.stock:
        if it["id"] not in taken and not is_spoiled(sim, it):
            out[it["kind"]] = out.get(it["kind"], 0) + 1
    return out


def decay(sim, events):
    """Hao tươi kho quán (kể cả hàng đang giữ), phát spoiled theo id, rồi giữ lại cho đơn bị ảnh hưởng."""
    newly = decay_items(sim.stock, sim.fresh_cfg["quan_decay_per_s"], spoiled_below(sim), "stock", events)
    if not newly:
        return
    hit = [c for c in sim.customers if c["order_status"] == "reserved" and newly & set(c["reserved"])]
    for c in sorted(hit, key=lambda c: (c["order_tick"], id_key(c["table_id"]))):
        c["reserved"] = []
        got = pick(sim, sim.menu[c["dish_id"]]["recipe"], reserved_ids(sim, skip=c))
        if got is None:
            c["order_status"] = "unfulfillable"  # khách vẫn chờ tới hết kiên nhẫn
        else:
            c["reserved"] = got


def consume(sim, ids):
    """Lấy các cá thể theo id ra khỏi kho; trả (items sort kind rồi id, giá trung bình fresh)."""
    want = set(ids)
    used = [it for it in sim.stock if it["id"] in want]
    sim.stock = [it for it in sim.stock if it["id"] not in want]
    used.sort(key=lambda it: (it["kind"], id_key(it["id"])))
    return used, sum(it["fresh"] for it in used) / len(used)


def locked_price(list_price, mean_fresh):
    return floor(list_price * mean_fresh / 100)
