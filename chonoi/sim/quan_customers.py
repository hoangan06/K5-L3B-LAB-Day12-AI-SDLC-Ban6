"""Khách quán (lát 3, Trung): dựng khách fixture, kho khả dụng, timer, rời bàn, sinh khách. PRD-0 mục D/F.

Giao diện chốt ở docs/contracts/phase-1-interfaces.md §4–§5.1. Hàm nhận `events` và append (name, data).
Các điểm còn chờ coach xác nhận ghi ở docs/clarify.md (Q1–Q8).
"""

import copy

from ..ids import id_key, sort_by_id
from ..errors import BadInput
from .quan_fresh import available_counts, pick, reserved_ids
from .quan_validation import menu_kinds, ticks


def _by_table(customers):
    return sorted(customers, key=lambda c: id_key(c["table_id"]))


def init_customers(sim, scenario):
    """Khách fixture: điền mặc định, suy phần giữ cho đơn reserved thiếu `reserved`, reserve id."""
    sim.customers = []
    full = ticks(sim.t["patience_s"])
    out = []
    for raw in copy.deepcopy(scenario.get("customers", [])):
        c = {"state": "waiting", "order_tick": 0, "patience_ticks_left": full, "eat_ticks_left": 0,
             "order_status": "reserved", **raw}
        out.append(c)
    # Thiếu reserved ở đơn reserved: cấp đúng công thức. Kho không đủ -> validate_quan_state báo quá tồn
    # (mã 2). TẠM theo Q4: nếu coach nói thiếu kho thì chuyển unfulfillable, mới cần thứ tự (order_tick, id bàn).
    if getattr(sim, "items_mode", False):
        _init_reserved_items(sim, out)
    for c in out:
        if "reserved" not in c:
            c["reserved"] = dict(sim.menu[c["dish_id"]]["recipe"]) if c["order_status"] == "reserved" else {}
    for c in out:
        sim.ids.reserve(c["id"])
    sim.customers = sort_by_id(out)


def _init_reserved_items(sim, out):
    """v1.2: phần giữ là mảng id. Đơn reserved bỏ trống thì cấp theo (order_tick, id bàn), sau phần đã khai."""
    sim.customers = [c for c in out if "reserved" in c]
    for c in out:
        if "reserved" in c:
            c["reserved"] = sorted(c["reserved"], key=id_key)
        elif c["order_status"] != "reserved":
            c["reserved"] = []
    for c in sorted((c for c in out if "reserved" not in c), key=lambda c: (c["order_tick"], id_key(c["table_id"]))):
        got = pick(sim, sim.menu[c["dish_id"]]["recipe"], reserved_ids(sim))
        if got is None:
            raise BadInput(f"customers.{c['id']}: kho không đủ cá thể chưa ươn để giữ cho đơn (mã 2)")
        c["reserved"] = got
        sim.customers.append(c)
    sim.customers = []


def available_stock(sim):
    """Tồn vật lý trừ tổng phần giữ, đủ mọi kind của thực đơn (kể cả 0). Trả map mới, không sửa sim.stock."""
    if getattr(sim, "items_mode", False):
        return available_counts(sim)
    avail = {k: sim.stock.get(k, 0) for k in menu_kinds(sim.menu) | set(sim.stock)}
    for c in sim.customers:
        for k, n in c["reserved"].items():
            avail[k] = avail.get(k, 0) - n
    return avail


def advance_timers(sim):
    """Bước 1 mục F (quán): giảm timer ca, nấu, ăn, kiên nhẫn; tăng ready_ticks của món đã ready đầu bước."""
    sim.time_left_ticks = max(0, sim.time_left_ticks - 1)
    for s in sim.stoves:
        if s["state"] == "ready":
            s["ready_ticks"] += 1
        elif s["state"] == "cooking":
            s["cook_ticks_left"] = max(0, s["cook_ticks_left"] - 1)
    for c in sim.customers:
        if c["state"] == "eating":
            c["eat_ticks_left"] = max(0, c["eat_ticks_left"] - 1)
        else:
            c["patience_ticks_left"] = max(0, c["patience_ticks_left"] - 1)


def _remove(sim, c, discard_order):
    discard_order(sim, c["id"])  # bỏ món của đơn ở bếp/tay; nguyên liệu đã dùng không hoàn
    sim.customers = [x for x in sim.customers if x["id"] != c["id"]]  # phần giữ thô nhả theo khách


def _leave(sim, c, reason, events, discard_order):
    if reason == "patience":
        t = sim.t
        sim.reputation = min(t["reputation_max"], max(t["reputation_min"],
                                                      sim.reputation + t["left_reputation_delta"]))
    events.append(("customer_left", {"order_id": c["id"], "table_id": c["table_id"], "reason": reason,
                                     "reputation": sim.reputation}))
    _remove(sim, c, discard_order)


def resolve_departures(sim, events):
    """Theo id bàn: ăn xong trả tiền rồi rời; hết kiên nhẫn rời (khi còn giờ); hết ca thì dọn hết."""
    from .quan_kitchen import discard_order, pay_customer  # Đức; import muộn để tránh vòng import

    closing = sim.time_left_ticks == 0
    for c in _by_table(sim.customers):
        if c["state"] == "eating":
            if c["eat_ticks_left"] == 0:
                pay_customer(sim, c, "finished_eating", events)
            elif closing:
                pay_customer(sim, c, "closing", events)  # chỉ paid, không customer_left (contract §5.1; Q3)
            else:
                continue
            _remove(sim, c, discard_order)
        elif closing:
            _leave(sim, c, "closing", events, discard_order)
        elif c["patience_ticks_left"] == 0:
            _leave(sim, c, "patience", events, discard_order)


def spawn_customer(sim, events):
    """Cuối bước: lượt khách theo first_customer_tick rồi mỗi customer_interval_s (theo phase_tick)."""
    t = sim.t
    if not sim.random_customers or sim.time_left_ticks <= 0:
        return
    first, every = t["first_customer_tick"], ticks(t["customer_interval_s"])
    if sim.phase_tick < first or (sim.phase_tick - first) % every:
        return
    taken = {c["table_id"] for c in sim.customers}
    free = [tb["id"] for tb in sort_by_id(sim.tables) if tb["id"] not in taken]
    if not free:
        return  # không còn bàn: bỏ lượt
    items = getattr(sim, "items_mode", False)
    avail = None if items else available_stock(sim)
    allowed = getattr(sim, "allowed_dishes", None)  # None: toàn menu; day: id món của kế hoạch (P2 §5)
    dishes = [d for d in sorted(sim.menu) if (allowed is None or d in allowed)
              and (pick(sim, sim.menu[d]["recipe"], reserved_ids(sim)) is not None if items
                   else all(avail.get(k, 0) >= n for k, n in sim.menu[d]["recipe"].items()))]
    if not dishes:
        events.append(("no_dish", {}))
        return
    dish = sim.rng.get("customer_orders").choice(dishes)
    cid = sim.ids.new("C")
    sim.customers = sort_by_id(sim.customers + [{
        "id": cid, "table_id": free[0], "dish_id": dish, "order_tick": sim.phase_tick, "state": "waiting",
        "patience_ticks_left": ticks(t["patience_s"]), "eat_ticks_left": 0, "order_status": "reserved",
        "reserved": (pick(sim, sim.menu[dish]["recipe"], reserved_ids(sim)) if items
                     else dict(sim.menu[dish]["recipe"]))}])
    events.append(("customer_arrived", {"order_id": cid, "table_id": free[0], "dish_id": dish}))
