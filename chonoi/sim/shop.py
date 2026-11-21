"""Cửa hàng cuối ngày."""

from ..errors import BadInput


def initial_upgrades(tuning, upgrades):
    levels = tuning["shop"]["upgrades"]
    if not isinstance(upgrades, dict) or set(upgrades) - levels.keys():
        raise BadInput("day.upgrades phải là map cấp nâng cấp đã khai báo")
    result = {}
    for name, options in levels.items():
        level = upgrades.get(name, 0)
        if type(level) is not int or (level != 0 and all(row["level"] != level for row in options)):
            raise BadInput(f"day.upgrades.{name}: cấp không hợp lệ")
        result[name] = level
    return result


class ShopSim:
    mode = "shop"
    phase = "shop"

    def __init__(self, tuning, scenario, streams, ids, *, context):
        self.t = tuning["shop"]
        self.stock = dict(scenario.get("stock", {}))
        self.upgrades = initial_upgrades(tuning, context["upgrades"])
        self.money = context["money"]
        self.earned = context["earned"]
        self.reputation = context["reputation"]
        self.phase_tick = 0
        self.time_left_ticks = self.t["max_ticks"]
        self.done = False
        self.reason = None

    def snapshot(self):
        return {"stock": {kind: amount for kind, amount in self.stock.items() if amount > 0}}

    def step(self, inp):
        if self.done:
            return []

        self.phase_tick += 1
        self.time_left_ticks -= 1
        events = []
        if inp.buy is not None:
            events.append(self._buy(inp.buy))
        if inp.pressed("shop_done"):
            self.reason = "done"
        elif self.time_left_ticks == 0:
            self.reason = "time"
        if self.reason is not None:
            self.done = True
            events.append(("shop_end", {"reason": self.reason}))
        return events

    def _buy(self, action):
        levels = self.t["upgrades"].get(action)
        if levels is None:
            return "buy_failed", {"action": action, "reason": "unknown"}
        level = self.upgrades[action] + 1
        item = next((row for row in levels if row["level"] == level), None)
        if item is None:
            return "buy_failed", {"action": action, "reason": "max_level"}
        price = item["price"]
        if self.money < price:
            return "buy_failed", {"action": action, "reason": "funds"}

        self.money -= price
        self.upgrades[action] = level
        return "bought", {"upgrade": action, "level": level, "price": price, "money": self.money}
