"""Kiểm fixture quán mức luật (lát 3, Trung) — PRD-0 mục D, giao diện docs/contracts/phase-1-interfaces.md §5.3.

validate_quan_fixture: kiểm trường thô/kiểu/enum TRƯỚC khi dựng sim. validate_quan_state: kiểm liên kết, trạng thái,
timer SAU khi chuẩn hóa. Sai -> BadInput (mã 2) trước khi ghi output. Chỉ kiểm điều mục D nêu; chỗ chưa rõ ở
docs/clarify.md, không tự thêm luật kiểm. Không gọi giữa bước runtime (trạng thái chuyển tiếp là hợp lệ).
"""

from ..errors import BadInput
from ..inventory import validate_items

CUSTOMER_KEYS = {"id", "table_id", "dish_id", "order_tick", "state", "patience_ticks_left", "eat_ticks_left",
                 "order_status", "reserved", "base_price", "tip"}
STATES = ("waiting", "eating")
ORDER_STATUSES = ("reserved", "assigned", "unfulfillable", "served")
STOVE_KEYS = {"id", "pos", "state", "dish", "cook_ticks_left", "ready_ticks"}
STOVE_STATES = ("idle", "cooking", "ready")
TABLE_KEYS = {"id", "pos"}
DISH_KEYS = {"order_id", "dish_id", "base_price"}


def ticks(seconds):
    return int(round(seconds * 60))


def _int(name, v, lo=0, hi=None):
    if isinstance(v, bool) or not isinstance(v, int) or v < lo or (hi is not None and v > hi):
        raise BadInput(f"{name} phải là số nguyên " + (f"[{lo}, {hi}]" if hi is not None else f">= {lo}"))


def _pos(name, pos, bounds):
    ok = isinstance(pos, list) and len(pos) == 2 and all(
        isinstance(v, (int, float)) and not isinstance(v, bool) for v in pos)
    if not ok or not all(bounds[a][0] <= v <= bounds[a][1] for v, a in zip(pos, ("x", "z"))):
        raise BadInput(f"{name} phải là [x, z] trong quán")


def _keys(name, obj, allowed):
    if not isinstance(obj, dict):
        raise BadInput(f"{name} phải là object")
    if set(obj) - allowed:
        raise BadInput(f"{name}: trường lạ/chưa hỗ trợ {sorted(set(obj) - allowed)}")


def _dish_shape(name, dish, menu):
    _keys(name, dish, DISH_KEYS)
    if set(dish) != DISH_KEYS:
        raise BadInput(f"{name}: món phải có đủ order_id, dish_id, base_price")
    if not isinstance(dish["order_id"], str) or dish["dish_id"] not in menu:
        raise BadInput(f"{name}: order_id phải là chuỗi, dish_id phải thuộc thực đơn")
    _int(f"{name}.base_price", dish["base_price"])


def validate_quan_fixture(scenario, tuning):
    """Kiểm khối `quan` thô (đã qua scenario.py: id trùng, bàn có thật, khách trùng bàn, stock, player)."""
    q, menu = tuning["quan"], tuning["menu"]
    if "random_customers" in scenario and not isinstance(scenario["random_customers"], bool):
        raise BadInput("random_customers phải là boolean")
    if "reputation" in scenario:
        r = scenario["reputation"]
        if isinstance(r, bool) or not isinstance(r, (int, float)) or not q["reputation_min"] <= r <= q["reputation_max"]:
            raise BadInput("reputation ngoài miền uy tín")
    if scenario.get("hand") is not None:
        _dish_shape("hand", scenario["hand"], menu)
    for tb in scenario.get("tables", []):
        _keys(f"tables.{tb['id']}", tb, TABLE_KEYS)
        if "pos" in tb:
            _pos(f"tables.{tb['id']}.pos", tb["pos"], q["bounds"])
    for s in scenario.get("stoves", []):
        name = f"stoves.{s['id']}"
        _keys(name, s, STOVE_KEYS)
        if "pos" in s:
            _pos(f"{name}.pos", s["pos"], q["bounds"])
        if "state" in s and s["state"] not in STOVE_STATES:
            raise BadInput(f"{name}: state phải là một trong {STOVE_STATES}")
        for key in ("cook_ticks_left", "ready_ticks"):
            if key in s:
                _int(f"{name}.{key}", s[key])
        if s.get("dish") is not None:
            _dish_shape(f"{name}.dish", s["dish"], menu)
    for c in scenario.get("customers", []):
        name = f"customers.{c['id']}"
        _keys(name, c, CUSTOMER_KEYS)
        if c.get("dish_id") not in menu:
            raise BadInput(f"{name}: dish_id thiếu hoặc ngoài thực đơn")
        if "state" in c and c["state"] not in STATES:
            raise BadInput(f"{name}: state phải là một trong {STATES}")
        if "order_status" in c and c["order_status"] not in ORDER_STATUSES:
            raise BadInput(f"{name}: order_status phải là một trong {ORDER_STATUSES}")
        if "order_tick" in c:
            _int(f"{name}.order_tick", c["order_tick"])
        if "patience_ticks_left" in c:
            _int(f"{name}.patience_ticks_left", c["patience_ticks_left"], 0, ticks(q["patience_s"]))
        if "eat_ticks_left" in c:
            _int(f"{name}.eat_ticks_left", c["eat_ticks_left"], 0, ticks(q["eat_s"]))
        for key in ("base_price", "tip"):
            if key in c:
                _int(f"{name}.{key}", c[key])
        if "reserved" in c:
            validate_items(c["reserved"])


def validate_quan_state(sim):
    """Kiểm liên kết, trạng thái, timer của quán sau khi dựng fixture và init_customers."""
    by_id = {c["id"]: c for c in sim.customers}
    holders = {}  # order_id -> nơi đang giữ món

    def holds(name, dish):
        c = by_id.get(dish["order_id"])
        if c is None:
            raise BadInput(f"{name}: order_id {dish['order_id']!r} không có khách")
        if c["order_status"] != "assigned":
            raise BadInput(f"{name}: món của đơn {c['id']} nhưng đơn không ở trạng thái assigned")
        if dish["dish_id"] != c["dish_id"]:
            raise BadInput(f"{name}: món không khớp đơn {c['id']}")
        if c["id"] in holders:
            raise BadInput(f"đơn {c['id']} có món ở cả {holders[c['id']]} và {name}")
        holders[c["id"]] = name

    for s in sim.stoves:
        name = f"stoves.{s['id']}"
        if s["state"] == "idle":
            if s["dish"] is not None or s["cook_ticks_left"] or s["ready_ticks"]:
                raise BadInput(f"{name}: bếp idle không có món và bộ đếm bằng 0")
            continue
        if s["dish"] is None:
            raise BadInput(f"{name}: bếp {s['state']} phải có món")
        if s["state"] == "cooking" and (s["cook_ticks_left"] <= 0 or s["ready_ticks"]):
            raise BadInput(f"{name}: bếp cooking cần cook_ticks_left > 0 và ready_ticks = 0")
        if s["state"] == "ready" and s["cook_ticks_left"]:
            raise BadInput(f"{name}: bếp ready có cook_ticks_left = 0")
        holds(name, s["dish"])
    if sim.hand is not None:
        holds("hand", sim.hand)

    reserved_total = {}
    for c in sim.customers:
        name, st, res = f"customers.{c['id']}", c["order_status"], c["reserved"]
        if st == "reserved":
            if res != sim.menu[c["dish_id"]]["recipe"]:
                raise BadInput(f"{name}: phần giữ khác công thức món {c['dish_id']}")
        elif res:
            raise BadInput(f"{name}: đơn {st} phải có phần giữ rỗng")
        for k, n in res.items():
            reserved_total[k] = reserved_total.get(k, 0) + n
        if (st == "assigned") != (c["id"] in holders):
            raise BadInput(f"{name}: chỉ đơn assigned có (đúng một) món ở bếp/tay")
        if st == "unfulfillable" and c["state"] != "waiting":
            raise BadInput(f"{name}: đơn unfulfillable phải còn chờ")
        if c["state"] == "eating":
            if st != "served" or c["eat_ticks_left"] <= 0 or "base_price" not in c or "tip" not in c:
                raise BadInput(f"{name}: khách eating cần served, eat_ticks_left > 0, base_price và tip")
        elif c["eat_ticks_left"]:
            raise BadInput(f"{name}: eat_ticks_left chỉ dương khi khách đang ăn")
    for k, n in reserved_total.items():
        if n > sim.stock.get(k, 0):
            raise BadInput(f"tổng giữ chỗ {k} = {n} vượt tồn kho {sim.stock.get(k, 0)}")
