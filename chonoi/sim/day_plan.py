"""Kế hoạch ngày D1–D5 (Trung, P2) — TICKET-02 §2, giao diện P2 §5. Chỉ xử lý dữ liệu, không import sim.

resolve_day_plans(tuning, overrides): trả 5 object {day, dishes, ingredients} mới, ingredients luôn tính lại từ
dishes × recipe trong tuning.menu. Khai ingredients (preset hoặc override) mà lệch thì BadInput (mã 2).
"""

from ..errors import BadInput

PLAN_KEYS = {"day", "dishes", "ingredients"}
DAYS = range(1, 6)


def _pos_int(v):
    return not isinstance(v, bool) and isinstance(v, int) and v > 0


def _ingredients(dishes, menu):
    out = {}
    for dish, n in dishes.items():
        for kind, k in menu[dish]["recipe"].items():
            out[kind] = out.get(kind, 0) + k * n
    return out


def _resolve(entry, menu, where):
    if not isinstance(entry, dict) or set(entry) - PLAN_KEYS or "dishes" not in entry:
        raise BadInput(f"{where}: cần object {{day, dishes[, ingredients]}}")
    day, dishes = entry.get("day"), entry["dishes"]
    if not _pos_int(day) or day not in DAYS:
        raise BadInput(f"{where}: day phải là số nguyên 1..5")
    if not isinstance(dishes, dict) or not dishes:
        raise BadInput(f"{where}: dishes phải là map món → số suất, không rỗng")
    for dish, n in dishes.items():
        if dish not in menu or not _pos_int(n):
            raise BadInput(f"{where}: món {dish!r} ngoài thực đơn hoặc số suất không nguyên dương")
    ingredients = _ingredients(dishes, menu)
    if "ingredients" in entry and entry["ingredients"] != ingredients:
        raise BadInput(f"{where}: ingredients khai lệch tổng công thức × số suất {ingredients}")
    return {"day": day, "dishes": dict(dishes), "ingredients": ingredients}


def resolve_day_plans(tuning, overrides=None):
    menu = tuning["menu"]
    plans = {}
    for i, entry in enumerate(tuning["day_plan"]):
        p = _resolve(entry, menu, f"tuning.day_plan[{i}]")
        if p["day"] in plans:
            raise BadInput(f"tuning.day_plan: trùng ngày {p['day']}")
        plans[p["day"]] = p
    if set(plans) != set(DAYS):
        raise BadInput("tuning.day_plan phải có đủ ngày 1..5")
    if overrides is not None:
        if not isinstance(overrides, list):
            raise BadInput("day.day_plan phải là mảng")
        seen = set()
        for i, entry in enumerate(overrides):
            p = _resolve(entry, menu, f"day.day_plan[{i}]")
            if p["day"] in seen:
                raise BadInput(f"day.day_plan: trùng ngày {p['day']}")
            seen.add(p["day"])
            plans[p["day"]] = p
    return [plans[d] for d in DAYS]
