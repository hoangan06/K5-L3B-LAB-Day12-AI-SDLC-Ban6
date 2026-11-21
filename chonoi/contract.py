"""Đọc game.contract.json và kiểm dải hợp lệ của tuning P1/P2 (PRD mục 13.2, Test Contract)."""

import json
import math
import os

from .errors import BadInput
from .inventory import inventory_kinds
from .sim.day_plan import resolve_day_plans

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "game.contract.json")


def _num(v):
    return type(v) is int or (type(v) is float and math.isfinite(v))


def _between(name, v, lo, hi):
    if not _num(v) or not (lo <= v <= hi):
        raise BadInput(f"tuning.{name} phải trong [{lo}, {hi}], đang là {v!r}")


def load_contract(path=DEFAULT_PATH) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            c = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được {path}: {e}")
    if not isinstance(c, dict) or c.get("contract_version") not in ("1.0", "1.1", "1.2"):
        raise BadInput("contract_version phải là 1.0, 1.1 hoặc 1.2")
    v = c["contract_version"]
    validate_tuning(c.get("tuning"), phase_two=v in ("1.1", "1.2"))
    if (v == "1.2") != ("freshness" in c["tuning"]):
        raise BadInput("khối tuning.freshness có đúng khi contract_version 1.2")
    if v == "1.2":
        _validate_freshness(c["tuning"]["freshness"])
    return c


def _int_between(name, v, lo, hi):
    if isinstance(v, bool) or not isinstance(v, int) or not (lo <= v <= hi):
        raise BadInput(f"tuning.{name} phải là số nguyên trong [{lo}, {hi}], đang là {v!r}")


def _pos_in(name, pos, bounds, keys):
    if (not isinstance(pos, list) or len(pos) != 2 or not all(_num(c) for c in pos)):
        raise BadInput(f"tuning.{name} phải là [số, số]")
    for c, k in zip(pos, keys):
        lo, hi = bounds[k]
        if not (lo <= c <= hi):
            raise BadInput(f"tuning.{name} nằm ngoài vùng {k} ∈ [{lo}, {hi}]")


def _bounds(name, b, keys):
    if not isinstance(b, dict) or set(b) != set(keys):
        raise BadInput(f"tuning.{name}.bounds phải có đúng khóa {list(keys)}")
    for k in keys:
        v = b[k]
        if not (isinstance(v, list) and len(v) == 2 and all(_num(c) for c in v) and v[0] == 0 and v[1] > 0):
            raise BadInput(f"tuning.{name}.bounds.{k} phải là [0, số dương]")


def _validate_gather(g, phase_two):
    """Dải hợp lệ P1 theo PRD mục 13.2."""
    _between("gather.duration_s", g.get("duration_s"), 60, 600)
    _bounds("gather", g.get("bounds"), ("x", "d"))
    b = g["bounds"]
    _between("gather.dock_radius", g.get("dock_radius"), 0.5, 5)
    _between("gather.interact_radius", g.get("interact_radius"), 0.5, 5)
    _between("gather.catch_radius", g.get("catch_radius"), 0.5, 5)
    _between("gather.swim_speed", g.get("swim_speed"), 1, 10)
    _between("gather.catch_cooldown_s", g.get("catch_cooldown_s"), 0, 10)
    _between("gather.oxygen_max_s", g.get("oxygen_max_s"), 10, 120)
    _int_between("gather.ramp_max_ticks", g.get("ramp_max_ticks"), 0, 6)
    _int_between("gather.hold_capacity", g.get("hold_capacity"), 4, 30)
    _int_between("gather.hp_max", g.get("hp_max"), 1, 99)
    _int_between("gather.oxygen_refill_per_tick", g.get("oxygen_refill_per_tick"), 1, 10_000)
    _int_between("gather.choke_interval_ticks", g.get("choke_interval_ticks"), 1, 10_000)
    _int_between("gather.node_yield", g.get("node_yield"), 1, 12)
    _between("gather.regrow_s", g.get("regrow_s"), 0.1, 600)
    _between("gather.surface_depth", g.get("surface_depth"), 0, 5)
    _pos_in("gather.dock_pos", g.get("dock_pos"), b, ("x", "d"))
    _pos_in("gather.start_pos", g.get("start_pos"), b, ("x", "d"))
    if not _num(g.get("start_heading_deg")):
        raise BadInput("tuning.gather.start_heading_deg phải là số")
    fy = g.get("fish_yield")
    fish_kinds = {"ca_linh", "ca_loc", "ca_keo"} if phase_two else {"ca_linh", "ca_loc"}
    if not isinstance(fy, dict) or not fish_kinds <= set(fy) or (phase_two and set(fy) != fish_kinds):
        raise BadInput("tuning.gather.fish_yield thiếu hoặc thừa loài cá")
    for k, v in fy.items():
        _int_between(f"gather.fish_yield.{k}", v, 1, g["hold_capacity"])
    nodes = g.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        raise BadInput("tuning.gather.nodes phải là mảng không rỗng")
    plant_kinds = {"bong_dien_dien", "bong_sung", "keo_neo"} if phase_two else {"bong_dien_dien", "bong_sung"}
    seen, kinds = set(), set()
    for n in nodes:
        if not isinstance(n, dict) or not isinstance(n.get("id"), str) or n["id"] in seen:
            raise BadInput("tuning.gather.nodes: mỗi nút cần id duy nhất")
        seen.add(n["id"])
        if type(n.get("kind")) is not str or n["kind"] not in plant_kinds:
            raise BadInput(f"tuning.gather.nodes.{n['id']}: loại cây không được hỗ trợ")
        kinds.add(n["kind"])
        _pos_in(f"gather.nodes.{n['id']}.pos", n.get("pos"), b, ("x", "d"))
        if n["pos"][1] != 0:
            raise BadInput(f"tuning.gather.nodes.{n['id']}: nút hái nằm ở mặt nước (d = 0)")
    if kinds != plant_kinds:
        raise BadInput("tuning.gather.nodes phải có ít nhất một nút mỗi loại cây")
    if phase_two:
        _validate_fish_phase_two(g)
        _validate_monster_data(g)
        return
    fish = g.get("fish_initial")
    if not isinstance(fish, list) or len(fish) != 6:
        raise BadInput("tuning.gather.fish_initial phải là danh sách đúng 6 đàn")
    seen = set()
    for f in fish:
        if not isinstance(f, dict) or not isinstance(f.get("id"), str) or f["id"] in seen:
            raise BadInput("tuning.gather.fish_initial: mỗi đàn cần id duy nhất")
        seen.add(f["id"])
        if f.get("kind") not in fy:
            raise BadInput(f"tuning.gather.fish_initial.{f['id']}: kind phải thuộc fish_yield")
        _pos_in(f"gather.fish_initial.{f['id']}.pos", f.get("pos"), b, ("x", "d"))
        if f["pos"][1] <= g["surface_depth"]:
            raise BadInput(f"tuning.gather.fish_initial.{f['id']}: đàn cá phải ở dưới nước")


def validate_tuning(t, *, phase_two=None):
    if not isinstance(t, dict):
        raise BadInput("thiếu khối tuning")
    g, q, menu = t.get("gather"), t.get("quan"), t.get("menu")
    if not isinstance(g, dict) or not isinstance(q, dict) or not isinstance(menu, dict):
        raise BadInput("tuning phải có gather, quan, menu")
    if phase_two is None:  # gọi không kèm phiên bản (test Duy): nhận P2 qua fish_initial là số nguyên
        phase_two = type(g.get("fish_initial")) is int
    _validate_gather(g, phase_two)
    # Quán: dải hợp lệ P1 (PRD mục 13.2)
    _between("quan.duration_s", q.get("duration_s"), 60, 600)
    _bounds("quan", q.get("bounds"), ("x", "z"))
    _between("quan.patience_s", q.get("patience_s"), 20, 180)
    _between("quan.walk_speed", q.get("walk_speed"), 1, 10)
    _between("quan.interact_radius", q.get("interact_radius"), 0.5, 5)
    _int_between("quan.ramp_max_ticks", q.get("ramp_max_ticks", 6), 0, 6)
    _between("quan.eat_s", q.get("eat_s"), 0.1, 600)
    _between("quan.customer_interval_s", q.get("customer_interval_s"), 0.1, 600)
    _int_between("quan.first_customer_tick", q.get("first_customer_tick"), 1, int(q["duration_s"] * 60) - 1)
    if not (_num(q.get("tip_rate")) and q["tip_rate"] > 0 and _num(q.get("left_reputation_delta"))
            and q["left_reputation_delta"] < 0):
        raise BadInput("tip_rate phải > 0 và left_reputation_delta phải < 0")
    ratio = q.get("tip_min_patience_ratio")
    if not (_num(ratio) and 0 < ratio <= 1):
        raise BadInput("quan.tip_min_patience_ratio phải thuộc (0, 1]")
    if not (_num(q.get("tip_reputation")) and q["tip_reputation"] > 0):
        raise BadInput("quan.tip_reputation phải > 0")
    if q.get("burn_s") is not None:
        raise BadInput("burn_s phải là null ở Phase 1")
    # TODO(nhóm): bổ sung kiểm các khóa còn lại nếu muốn chặt hơn (bếp/bàn, uy tín, ...).
    for dish_id, d in menu.items():
        if not isinstance(d, dict):
            raise BadInput(f"menu.{dish_id} phải là object")
        price, cook = d.get("price"), d.get("cook_s")
        if isinstance(price, bool) or not isinstance(price, int) or price <= 0 or not _num(cook) or cook <= 0:
            raise BadInput(f"menu.{dish_id}: price (nguyên) và cook_s phải > 0")
    if phase_two:
        _validate_phase_two(t)


def _validate_freshness(f):
    """TICKET-03: freshness {initial, gather_decay_per_s, quan_decay_per_s, spoiled_below}."""
    if not isinstance(f, dict) or set(f) != {"initial", "gather_decay_per_s", "quan_decay_per_s", "spoiled_below"}:
        raise BadInput("tuning.freshness phải có đúng initial, gather_decay_per_s, quan_decay_per_s, spoiled_below")
    _between("freshness.initial", f["initial"], 0, 100)
    _between("freshness.spoiled_below", f["spoiled_below"], 0, 100)
    for key in ("gather_decay_per_s", "quan_decay_per_s"):
        _between(f"freshness.{key}", f[key], 0, 100)


def _positive(name, value, *, integer=False, minimum=1):
    valid = type(value) is int if integer else _num(value)
    if not valid or value < minimum:
        raise BadInput(f"{name}: số không hợp lệ")


def _interval(name, interval, domain):
    if not (isinstance(interval, list) and len(interval) == 2 and all(_num(value) for value in interval)
            and domain[0] <= interval[0] < interval[1] <= domain[1]):
        raise BadInput(f"{name}: khoảng phải tăng và nằm trong miền")


def _validate_fish_phase_two(g):
    _positive("gather.fish_max", g.get("fish_max"), integer=True)
    _int_between("gather.fish_initial", g.get("fish_initial"), 0, g["fish_max"])
    _positive("gather.fish_turn_ticks", g.get("fish_turn_ticks"), integer=True)
    _positive("gather.fish_spawn_ticks", g.get("fish_spawn_ticks"), integer=True)
    _between("gather.fish_speed", g.get("fish_speed"), 0.001, 10)
    _positive("gather.fish_spawn_clearance", g.get("fish_spawn_clearance"), minimum=0)
    _interval("fish_x", g.get("fish_x"), g["bounds"]["x"])
    kinds = g["fish_yield"].keys()
    for key in ("fish_depths", "fish_spawn_depths", "fish_weights"):
        if not isinstance(g.get(key), dict) or g[key].keys() != kinds:
            raise BadInput(f"gather.{key} phải có đủ các loài cá")
    x_values = g.get("fish_spawn_x")
    if not isinstance(x_values, list) or not x_values:
        raise BadInput("gather.fish_spawn_x phải là mảng tọa độ")
    for x in x_values:
        _between("gather.fish_spawn_x", x, *g["fish_x"])
    for kind in kinds:
        lane = g["fish_depths"][kind]
        _interval(f"fish_depths.{kind}", lane, [g["surface_depth"], g["bounds"]["d"][1]])
        _between(f"gather.fish_weights.{kind}", g["fish_weights"][kind], 0.001, 100_000)
        depths = g["fish_spawn_depths"][kind]
        if not isinstance(depths, list) or not depths:
            raise BadInput(f"gather.fish_spawn_depths.{kind} phải là mảng độ sâu")
        for depth in depths:
            _between(f"gather.fish_spawn_depths.{kind}", depth, *lane)


def _validate_monster_data(g):
    data = g.get("monsters")
    if not isinstance(data, dict) or not isinstance(data.get("species"), dict) or not isinstance(data.get("spawns"), list):
        raise BadInput("gather.monsters cần có species và spawns")
    _positive("gather.monsters.invuln_ticks", data.get("invuln_ticks"), integer=True, minimum=0)
    _between("gather.monsters.loss_ratio", data.get("loss_ratio"), 0, 1)
    ca_sau = data["species"].get("ca_sau")
    if not isinstance(ca_sau, dict):
        raise BadInput("gather.monsters.species.ca_sau thiếu cấu hình")
    _interval("monsters.ca_sau.depths", ca_sau.get("depths"), g["bounds"]["d"])
    for key in ("patrol_speed", "chase_speed", "detect_radius", "exit_radius", "hit_radius", "recoil_dist"):
        _between(f"gather.monsters.ca_sau.{key}", ca_sau.get(key), 0.001, 1000)
    _positive("gather.monsters.ca_sau.recoil_ticks", ca_sau.get("recoil_ticks"), integer=True)
    if ca_sau["exit_radius"] < ca_sau["detect_radius"]:
        raise BadInput("exit_radius của cá sấu nhỏ hơn detect_radius")
    seen = set()
    for spawn in data["spawns"]:
        if (not isinstance(spawn, dict) or not isinstance(spawn.get("id"), str) or not spawn["id"]
                or spawn["id"] in seen or spawn.get("kind") != "ca_sau"):
            raise BadInput("gather.monsters.spawns cần ID khác rỗng, duy nhất và loại ca_sau")
        seen.add(spawn["id"])
        _int_between("gather.monsters.spawns.from_day", spawn.get("from_day"), 1, 5)
        waypoints = spawn.get("waypoints")
        if not isinstance(waypoints, list) or len(waypoints) < 2:
            raise BadInput("gather.monsters.spawns cần ít nhất hai waypoint")
        domain = {"x": g["bounds"]["x"], "d": ca_sau["depths"]}
        for pos in [spawn.get("pos"), *waypoints]:
            _pos_in("gather.monsters.spawns", pos, domain, ("x", "d"))


def _validate_phase_two(t):
    q = t["quan"]
    for key, count in (("stoves", 2), ("tables", 4)):
        stations = q.get(key)
        if not isinstance(stations, list) or len(stations) != count:
            raise BadInput(f"quan.{key} cần đúng {count} vị trí")
        ids = set()
        for station in stations:
            if not isinstance(station, dict) or not isinstance(station.get("id"), str) or not station["id"] or station["id"] in ids:
                raise BadInput(f"quan.{key} cần ID duy nhất")
            ids.add(station["id"])
            _pos_in(f"quan.{key}", station.get("pos"), q["bounds"], ("x", "z"))
    kinds = inventory_kinds(t)
    if len(t["menu"]) != 6:
        raise BadInput("thực đơn Phase 2 cần đúng 6 món")
    for dish, data in t["menu"].items():
        recipe = data.get("recipe")
        if not isinstance(recipe, dict) or not recipe or set(recipe) - kinds:
            raise BadInput(f"menu.{dish}.recipe có nguyên liệu không hợp lệ")
        for count in recipe.values():
            _int_between(f"menu.{dish}.recipe", count, 1, t["gather"]["hold_capacity"])
    if not isinstance(t.get("day_plan"), list):
        raise BadInput("tuning.day_plan phải là mảng")
    resolve_day_plans(t)
    shop = t.get("shop")
    if not isinstance(shop, dict) or not isinstance(shop.get("upgrades"), dict) or set(shop["upgrades"]) != {"hp", "oxygen"}:
        raise BadInput("tuning.shop cần bảng nâng cấp oxy và máu")
    _int_between("shop.max_ticks", shop.get("max_ticks"), 1, 600)
    for name, cap in (("hp", "hp_max"), ("oxygen", "oxygen_max_s")):
        levels = shop["upgrades"][name]
        if not isinstance(levels, list) or len(levels) != 2:
            raise BadInput(f"shop.upgrades.{name} cần hai cấp")
        for level, data in enumerate(levels, 1):
            if not isinstance(data, dict) or type(data.get("level")) is not int or data["level"] != level:
                raise BadInput(f"shop.upgrades.{name} cần cấp 1, 2 theo thứ tự")
            _positive(f"shop.upgrades.{name}.price", data.get("price"), integer=True)
            _int_between(f"shop.upgrades.{name}.{cap}", data.get(cap), 1, 120)
