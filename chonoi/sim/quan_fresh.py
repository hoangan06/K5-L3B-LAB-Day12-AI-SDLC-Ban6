"""Kho cá thể và độ tươi của quán (Trung, P3) — TICKET-03 §1, Test Contract v1.2.

Bật khi tuning có khối `freshness` (contract v1.2); không có thì quán chạy kho đếm như P1–P2.
Kho quán: list cá thể {id, kind, fresh}; fresh lưu bằng Fraction để so ngưỡng 30 và floor chính xác.
Phần giữ của khách: list id cá thể (sort theo id).
"""

import math
from fractions import Fraction
from math import floor

from ..errors import BadInput
from ..ids import id_key, sort_by_id


def item_mode(tuning):
    return "freshness" in tuning


def _num(v):
    return not isinstance(v, bool) and isinstance(v, (int, float)) and math.isfinite(v)


def load_items(raw, kinds, where):
    """Kiểm mảng cá thể v1.2 → list mới {id, kind, fresh: Fraction}, sort theo id. Sai schema → mã 2."""
    if not isinstance(raw, list):
        raise BadInput(f"{where}: contract v1.2 cần mảng cá thể {{id,kind,fresh}} (kho đếm → mã 2)")
    out, seen = [], set()
    for it in raw:
        if not isinstance(it, dict) or set(it) != {"id", "kind", "fresh"}:
            raise BadInput(f"{where}: cá thể phải có đúng id, kind, fresh")
        iid, kind, fresh = it["id"], it["kind"], it["fresh"]
        if not isinstance(iid, str) or not iid or iid in seen:
            raise BadInput(f"{where}: id cá thể rỗng hoặc trùng: {iid!r}")
        if kind not in kinds:
            raise BadInput(f"{where}: nguyên liệu lạ {kind!r}")
        if not _num(fresh) or not 0 <= fresh <= 100:
            raise BadInput(f"{where}: fresh của {iid} phải hữu hạn trong [0, 100]")
        seen.add(iid)
        out.append({"id": iid, "kind": kind, "fresh": Fraction(str(fresh))})
    return sort_by_id(out)


def spoiled_below(sim):
    return Fraction(str(sim.fresh_cfg["spoiled_below"]))


def is_spoiled(sim, item):
    return item["fresh"] < spoiled_below(sim)


def dump_item(item):
    return {"id": item["id"], "kind": item["kind"], "fresh": float(item["fresh"])}


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
    rate = Fraction(str(sim.fresh_cfg["quan_decay_per_s"])) / 60
    limit = spoiled_below(sim)
    newly = set()
    for it in sim.stock:  # stock luôn sort theo id
        was_ok = it["fresh"] >= limit
        it["fresh"] = max(Fraction(0), it["fresh"] - rate)
        if was_ok and it["fresh"] < limit:
            newly.add(it["id"])
            events.append(("spoiled", {"item_id": it["id"], "kind": it["kind"], "location": "stock"}))
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
