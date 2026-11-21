"""Điều phối các pha sáng, quán và cửa hàng qua nhiều ngày."""

from copy import deepcopy

from .. import TICK_HZ
from ..errors import BadInput
from .day_plan import resolve_day_plans
from .gather import GatherSim
from .quan import QuanSim
from .shop import ShopSim, initial_upgrades


class DaySim:
    mode = "day"

    def __init__(self, tuning, scenario, streams, ids, *, days=1):
        if type(days) is not int or not 1 <= days <= 5:
            raise BadInput("days phải là số nguyên từ 1 đến 5")
        if not isinstance(scenario, dict) or scenario.keys() - {"day", "gather", "quan"}:
            raise BadInput("scenario day chỉ nhận các khối day, gather và quan")
        day = scenario.get("day", {})
        gather = scenario.get("gather", {})
        quan = scenario.get("quan", {})
        if not all(isinstance(block, dict) for block in (day, gather, quan)):
            raise BadInput("day, gather và quan phải là object")
        if day.keys() - {"money", "earned", "reputation", "upgrades", "day_plan"}:
            raise BadInput("day: trường không được hỗ trợ")
        if "day_plan" in day and not isinstance(day["day_plan"], list):
            raise BadInput("day.day_plan phải là mảng")
        if quan.keys() & {"stock", "reputation"}:
            raise BadInput("day: kho và uy tín của quán đến từ pha trước")

        self.money = day.get("money", 0)
        self.earned = day.get("earned", 0)
        if (("money" in day) != ("earned" in day)
                or type(self.money) is not int or type(self.earned) is not int
                or not 0 <= self.money <= self.earned):
            raise BadInput("day.money và day.earned phải cùng có và thỏa 0 <= money <= earned")
        q = tuning["quan"]
        self.reputation = day.get("reputation", q["reputation_initial"])
        if type(self.reputation) not in (int, float) or not q["reputation_min"] <= self.reputation <= q["reputation_max"]:
            raise BadInput("day.reputation ngoài miền uy tín")

        self.tuning, self.streams, self.ids = tuning, streams, ids
        self._gather = deepcopy(gather)
        self._quan = deepcopy(quan)
        self._plans = resolve_day_plans(tuning, day.get("day_plan"))
        self._upgrades = initial_upgrades(tuning, day.get("upgrades", {}))
        self.days = days
        self.day = 1
        self.days_completed = 0
        self.done = False
        self.reason = None
        self._start_day()

    @property
    def phase(self):
        return self.current_sim.phase

    @property
    def phase_tick(self):
        return self.current_sim.phase_tick

    @property
    def time_left_ticks(self):
        return self.current_sim.time_left_ticks

    @property
    def upgrades(self):
        return self.current_sim.upgrades if self.phase == "shop" else self._upgrades

    def initial_events(self):
        return self._day_events()

    def step(self, inp):
        if self.done:
            return []
        child = self.current_sim
        events = [self._event(name, data) for name, data in child.step(inp)]
        self.money, self.earned, self.reputation = child.money, child.earned, child.reputation
        if not child.done:
            return events

        if child.phase == "gather":
            self.current_sim = QuanSim(
                self.tuning, deepcopy(self._quan), self.streams, self.ids,
                inventory=child.inventory_items(), context=self._context(),
            )
            events.append(self._event("phase_start", {}))
        elif child.phase == "quan":
            self.current_sim = ShopSim(
                self.tuning, {"stock": child.stock}, self.streams, self.ids, context=self._context(),
            )
            events.append(self._event("phase_start", {}))
        else:
            self._upgrades = child.upgrades.copy()
            self.days_completed += 1
            if self.days_completed == self.days:
                self.done = True
                self.reason = "days_complete"
            else:
                self.day += 1
                self._start_day()
                events.extend(self._day_events())
        return events

    def snapshot(self):
        return {
            **self.current_sim.snapshot(),
            "day": self.day,
            "day_plan": deepcopy(self.day_plan),
            "upgrades": self.upgrades.copy(),
            "active_upgrades": self.active_upgrades.copy(),
        }

    def _start_day(self):
        self.day_plan = self._plans[self.day - 1]
        self.active_upgrades = self._upgrades.copy()
        self.current_sim = GatherSim(
            self.tuning, deepcopy(self._gather), self.streams, self.ids, context=self._context(),
        )

    def _context(self):
        gather = self.tuning["gather"]
        shop = self.tuning["shop"]["upgrades"]
        caps = {}
        for upgrade, key in (("oxygen", "oxygen_max_s"), ("hp", "hp_max")):
            level = self.active_upgrades[upgrade]
            caps[key] = gather[key] if not level else next(row[key] for row in shop[upgrade] if row["level"] == level)
        return {
            "day": self.day, "money": self.money, "earned": self.earned, "reputation": self.reputation,
            "upgrades": self._upgrades.copy(), "active_upgrades": self.active_upgrades.copy(),
            "day_plan": deepcopy(self.day_plan), "allowed_dishes": sorted(self.day_plan["dishes"]),
            "oxygen_max_ticks": round(caps["oxygen_max_s"] * TICK_HZ), "hp_max": caps["hp_max"],
        }

    def _event(self, name, data):
        return {"phase": self.phase, "day": self.day, "name": name, "data": data}

    def _day_events(self):
        payload = {key: self.day_plan[key].copy() for key in ("dishes", "ingredients")}
        return [self._event("day_start", {}), self._event("day_plan", payload), self._event("phase_start", {})]
