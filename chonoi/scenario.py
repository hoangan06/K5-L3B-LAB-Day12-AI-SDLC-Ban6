"""Nạp và kiểm scenario (Contract D). Trả về dict của đúng khối theo mode.

KHUNG: kiểm cú pháp, id trùng, bộ đếm âm, khoang vượt sức chứa, trường lạ.
TODO(nhóm): bổ sung kiểm mâu thuẫn mức luật mà nhóm cần (khách giữ chỗ quá kho, đơn assigned
phải có đúng một món, khách eating thiếu giá/tip...) — xem PRD-0 mục D và 'Mâu thuẫn -> mã 2'.
"""

import json
import math

from .errors import BadInput
from .inventory import KINDS_P1, KINDS_P2, validate_items

GATHER_KEYS = {"player", "hold", "nodes", "fish", "random_fish", "time_left_ticks", "monsters"}
GATHER_PLAYER_KEYS = {"pos", "vel", "heading_deg", "hp", "oxygen_ticks", "zero_oxy_ticks",
                      "invuln_ticks", "catch_cd_ticks"}
NODE_KINDS = ("bong_dien_dien", "bong_sung")
FISH_KINDS = ("ca_linh", "ca_loc")
QUAN_PLAYER_KEYS = {"pos", "vel"}
QUAN_KEYS = {"player", "stock", "hand", "stoves", "tables", "customers", "random_customers",
             "reputation", "time_left_ticks"}


def _check_ids(name, arr):
    if not isinstance(arr, list):
        raise BadInput(f"{name} phải là mảng")
    seen = set()
    for e in arr:
        if not isinstance(e, dict) or not isinstance(e.get("id"), str) or not e["id"]:
            raise BadInput(f"{name}: mỗi phần tử cần id (chuỗi khác rỗng)")
        if e["id"] in seen:
            raise BadInput(f"{name}: id trùng {e['id']}")
        seen.add(e["id"])


def load_scenario(path, mode: str, tuning: dict) -> dict:
    if path is None:
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được scenario {path}: {e}")
    if not isinstance(data, dict) or not set(data) <= ({"gather", "quan", "day"} if mode == "day" else {"gather", "quan"}):
        raise BadInput("scenario chỉ được có khối 'gather' hoặc 'quan'")
    if mode == "day":
        for name, block in data.items():
            if not isinstance(block, dict):
                raise BadInput(f"khối {name} phải là object")
        day = data.get("day", {})
        if set(day) - {"money", "earned", "reputation", "upgrades", "day_plan"}:
            raise BadInput("trường lạ trong day")
        if ("money" in day) != ("earned" in day):
            raise BadInput("money và earned phải được khai cùng nhau")
        if "money" in day:
            for key in ("money", "earned"):
                _nonneg_int("day." + key, day[key])
            if day["money"] > day["earned"]:
                raise BadInput("money vượt earned")
        if "reputation" in day and not (_num(day["reputation"]) and 0 <= day["reputation"] <= 5):
            raise BadInput("reputation không hợp lệ")
        if "upgrades" in day:
            upgrades = day["upgrades"]
            if not isinstance(upgrades, dict) or set(upgrades) - {"hp", "oxygen"}:
                raise BadInput("upgrades không hợp lệ")
            for level in upgrades.values():
                if isinstance(level, bool) or not isinstance(level, int) or not 0 <= level <= 2:
                    raise BadInput("upgrade level phải từ 0 đến 2")
        if "day_plan" in tuning:
            from .sim.day_plan import resolve_day_plans
            resolve_day_plans(tuning, day.get("day_plan"))
        quan = data.get("quan", {})
        if {"stock", "reputation"} & set(quan):
            raise BadInput("day.quan không nhận stock/reputation")
        # Validate syntax and bounds now; actual stock/customer relationships belong to QuanSim.
        for name in ("gather", "quan"):
            block = data.get(name, {})
            allowed = GATHER_KEYS if name == "gather" else QUAN_KEYS
            if set(block) - allowed:
                raise BadInput(f"trường lạ trong {name}")
            if "time_left_ticks" in block:
                n = block["time_left_ticks"]
                if isinstance(n, bool) or not isinstance(n, int) or not 1 <= n <= round(tuning[name]["duration_s"] * 60):
                    raise BadInput("time_left_ticks không hợp lệ")
            if name == "quan":
                _validate_quan(block, tuning)
            else:
                # Upgraded player caps are checked when the day context is known.
                copy = dict(block)
                player = dict(copy.get("player", {}))
                player.pop("hp", None)
                player.pop("oxygen_ticks", None)
                player.pop("zero_oxy_ticks", None)
                copy["player"] = player
                _validate_gather(copy, tuning)
                for key in ("hp", "oxygen_ticks", "zero_oxy_ticks"):
                    if key in block.get("player", {}):
                        _nonneg_int("player." + key, block["player"][key])
        return data
    if set(data) - {mode}:
        raise BadInput(f"khối sai mode: chạy --mode {mode} chỉ nhận khối '{mode}'")
    block = data.get(mode, {})
    if not isinstance(block, dict):
        raise BadInput(f"khối {mode} phải là object")
    allowed = (GATHER_KEYS if isinstance(tuning["gather"].get("fish_initial"), int)
               else GATHER_KEYS - {"monsters"}) if mode == "gather" else QUAN_KEYS
    extra = set(block) - allowed
    if extra:
        raise BadInput(f"trường lạ/chưa hỗ trợ trong {mode}: {sorted(extra)}")
    dur = int(round(tuning[mode]["duration_s"] * 60))
    if "time_left_ticks" in block:
        t = block["time_left_ticks"]
        if isinstance(t, bool) or not isinstance(t, int) or not (1 <= t <= dur):
            raise BadInput(f"time_left_ticks phải là số nguyên trong [1, {dur}]")
    if mode == "gather":
        _validate_gather(block, tuning)
    else:
        _validate_quan(block, tuning)
    return block


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _nonneg_int(name, v):
    if isinstance(v, bool) or not isinstance(v, int) or v < 0:
        raise BadInput(f"{name} phải là số nguyên không âm")


def _pos(name, pos, bounds, axes=("x", "d")):
    if not (isinstance(pos, list) and len(pos) == 2 and all(_num(c) for c in pos)):
        raise BadInput(f"{name} phải là [{axes[0]}, {axes[1]}]")
    for c, axis in zip(pos, axes):
        lo, hi = bounds[axis]
        if not (lo <= c <= hi):
            raise BadInput(f"{name} nằm ngoài vùng nước ({axis} ∈ [{lo}, {hi}])")


def _validate_gather(b, tuning):
    g = tuning["gather"]
    bounds = g["bounds"]
    for arr in ("nodes", "fish"):
        if arr in b:
            _check_ids(arr, b[arr])
    if "random_fish" in b and not isinstance(b["random_fish"], bool):
        raise BadInput("random_fish phải là boolean")
    if "hold" in b:
        h = b["hold"]
        kinds = KINDS_P2 if isinstance(g.get("fish_initial"), int) else KINDS_P1
        if not isinstance(h, list) or any(not isinstance(k, str) or k not in kinds for k in h):
            raise BadInput("hold phải là mảng id nguyên liệu hợp lệ")
        if len(h) > g["hold_capacity"]:
            raise BadInput("hold vượt sức chứa")
    p = b.get("player", {})
    if not isinstance(p, dict):
        raise BadInput("player phải là object")
    extra = set(p) - GATHER_PLAYER_KEYS
    if extra:
        raise BadInput(f"trường lạ/chưa hỗ trợ trong gather.player: {sorted(extra)}")
    if "pos" in p:
        _pos("player.pos", p["pos"], bounds)
    if "vel" in p and not (isinstance(p["vel"], list) and len(p["vel"]) == 2 and all(_num(c) for c in p["vel"])):
        raise BadInput("player.vel phải là [x, d]")
    if "heading_deg" in p and not _num(p["heading_deg"]):
        raise BadInput("player.heading_deg phải là số")
    for key in ("invuln_ticks", "catch_cd_ticks", "zero_oxy_ticks", "oxygen_ticks", "hp"):
        if key in p:
            _nonneg_int(f"player.{key}", p[key])
    omax = int(round(g["oxygen_max_s"] * 60))
    if "oxygen_ticks" in p and p["oxygen_ticks"] > omax:
        raise BadInput("player.oxygen_ticks vượt oxy tối đa")
    if "hp" in p and not (1 <= p["hp"] <= g["hp_max"]):
        raise BadInput("player.hp phải trong [1, hp_max]")
    if "zero_oxy_ticks" in p:
        pos = p.get("pos", g["start_pos"])
        oxy = p.get("oxygen_ticks", omax)
        if p["zero_oxy_ticks"] > 59:
            raise BadInput("player.zero_oxy_ticks phải trong [0, 59]")
        if p["zero_oxy_ticks"] > 0 and not (oxy == 0 and pos[1] > g["surface_depth"]):
            raise BadInput("player.zero_oxy_ticks > 0 chỉ khi oxy = 0 và đang dưới nước")
    for n in b.get("nodes", []):
        if set(n) - {"id", "kind", "pos", "regrow_ticks"}:
            raise BadInput("nodes có trường lạ")
        if n.get("kind") not in (NODE_KINDS + (("keo_neo",) if isinstance(g.get("fish_initial"), int) else ())):
            raise BadInput(f"nodes.{n['id']}: kind phải là một trong {NODE_KINDS}")
        _pos(f"nodes.{n['id']}.pos", n.get("pos"), bounds)
        if n["pos"][1] != 0:
            raise BadInput(f"nodes.{n['id']}: nút hái nằm ở mặt nước (d = 0)")
        if "regrow_ticks" in n:
            _nonneg_int(f"nodes.{n['id']}.regrow_ticks", n["regrow_ticks"])
    for f in b.get("fish", []):
        if set(f) - {"id", "kind", "pos", "heading_deg", "age_ticks"}:
            raise BadInput("fish có trường lạ")
        if f.get("kind") not in (FISH_KINDS + (("ca_keo",) if isinstance(g.get("fish_initial"), int) else ())):
            raise BadInput(f"fish.{f['id']}: kind phải là một trong {FISH_KINDS}")
        _pos(f"fish.{f['id']}.pos", f.get("pos"), bounds)
        if f["pos"][1] <= g["surface_depth"]:
            raise BadInput(f"fish.{f['id']}: đàn cá phải ở dưới nước")
        if isinstance(g.get("fish_initial"), int) and not (g["fish_x"][0] <= f["pos"][0] <= g["fish_x"][1] and g["fish_depths"][f["kind"]][0] <= f["pos"][1] <= g["fish_depths"][f["kind"]][1]):
            raise BadInput("fish nằm ngoài vùng bơi của loài")
        if "heading_deg" in f and not _num(f["heading_deg"]):
            raise BadInput(f"fish.{f['id']}.heading_deg phải là số")
        if "age_ticks" in f:
            _nonneg_int(f"fish.{f['id']}.age_ticks", f["age_ticks"])
    if isinstance(g.get("fish_initial"), int) and len(b.get("fish", [])) > g["fish_max"]:
        raise BadInput("fish vượt giới hạn")


def _validate_quan(b, tuning):
    for arr in ("stoves", "tables", "customers"):
        if arr in b:
            _check_ids(arr, b[arr])
    if "stock" in b:
        validate_items(b["stock"])
    p = b.get("player", {})
    if not isinstance(p, dict) or set(p) - QUAN_PLAYER_KEYS:
        raise BadInput("quan.player chỉ có pos và vel")
    qb = tuning["quan"]["bounds"]
    if "pos" in p:
        _pos("player.pos", p["pos"], qb, axes=("x", "z"))
    if "vel" in p and not (isinstance(p["vel"], list) and len(p["vel"]) == 2 and all(_num(c) for c in p["vel"])):
        raise BadInput("player.vel phải là [x, z]")
    table_ids = [c.get("table_id") for c in b.get("customers", [])]
    known = {t["id"] for t in tuning["quan"]["tables"]} | {t.get("id") for t in b.get("tables", [])}
    for c in b.get("customers", []):
        if not isinstance(c.get("table_id"), str) or c["table_id"] not in known:
            raise BadInput(f"customers.{c['id']}: table_id phải là bàn có thật")
    if len(table_ids) != len(set(table_ids)):
        raise BadInput("hai khách cùng bàn")
