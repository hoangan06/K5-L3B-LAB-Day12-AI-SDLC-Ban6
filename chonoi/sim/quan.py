"""Mô phỏng buổi tối, dùng chung cho headless và live. Context Phase 2: giao diện P2 §2, §5."""

from .. import TICK_HZ
from ..errors import BadInput
from ..ids import sort_by_id
from .quan_fresh import decay, dump_item, item_mode, load_items
from .quan_customers import advance_timers, init_customers, resolve_departures, spawn_customer
from .quan_kitchen import finish_cooking, interact
from .quan_validation import menu_kinds, validate_quan_fixture, validate_quan_state
from .ramp import ramp_velocity


class QuanSim:
    mode = "quan"
    phase = "quan"

    def __init__(self, tuning, scenario, streams, ids, inventory=None, *, context=None):
        if context is not None:
            for key in ("stock", "reputation"):
                if key in scenario:
                    raise BadInput(f"quan.{key} bị cấm khi chạy day (kho/uy tín lấy từ bàn giao)")
            allowed = context.get("allowed_dishes")
            if not isinstance(allowed, list) or not all(isinstance(d, str) and d in tuning["menu"] for d in allowed):
                raise BadInput("context.allowed_dishes phải là danh sách id món trong thực đơn")
        validate_quan_fixture(scenario, tuning)
        t = tuning["quan"]
        self.t = t
        self.menu = tuning["menu"]
        self.rng = streams
        self.ids = ids
        p = scenario.get("player", {})
        self.pos = list(p.get("pos", t["start_pos"]))
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0
        # kho: --inventory HOẶC scenario.stock (cả hai -> cli đã báo mã 2)
        self.fresh_cfg = tuning.get("freshness")  # có khối này = contract v1.2, kho cá thể (TICKET-03)
        self.items_mode = item_mode(tuning)
        if self.items_mode:
            raw = inventory if inventory is not None else scenario.get("stock", [])
            self.stock = load_items(raw, menu_kinds(self.menu), "kho quán")
            for it in self.stock:
                ids.reserve(it["id"])
        else:
            if isinstance(inventory, list) or isinstance(scenario.get("stock"), list):
                raise BadInput("kho cá thể chỉ hợp lệ khi contract v1.2 (có khối freshness)")
            self.stock = dict(inventory if inventory is not None else scenario.get("stock", {}))
        self.hand = scenario.get("hand")
        self.time_left_ticks = scenario.get("time_left_ticks", round(t["duration_s"] * TICK_HZ))
        self.reputation = scenario.get("reputation", t["reputation_initial"])
        self.allowed_dishes = None  # None: toàn menu (quán độc lập)
        self.stoves = [dict(s, state=s.get("state", "idle"), dish=s.get("dish"),
                            cook_ticks_left=s.get("cook_ticks_left", 0), ready_ticks=s.get("ready_ticks", 0))
                       for s in self._merge(t["stoves"], scenario.get("stoves", []))]
        self.tables = self._merge(t["tables"], scenario.get("tables", []))
        self.phase_tick = 0
        self.random_customers = scenario.get("random_customers", True)
        self.money = 0
        self.earned = 0
        self.shift_earned = 0
        if context is not None:  # bản sao trạng thái đầu pha; sim giữ working copy, không sửa context
            self.money, self.earned = context["money"], context["earned"]
            self.reputation = context["reputation"]
            self.allowed_dishes = list(context["allowed_dishes"])
        self.done = False
        self.reason = None
        init_customers(self, scenario)
        validate_quan_state(self)

    @staticmethod
    def _merge(defaults, updates):
        by_id = {d["id"]: dict(d) for d in defaults}
        for u in updates:
            if u["id"] not in by_id:
                raise BadInput(f"id bếp/bàn không tồn tại: {u['id']}")
            by_id[u["id"]].update(u)
        return sort_by_id(list(by_id.values()))

    def snapshot(self) -> dict:
        occupied = {c["table_id"]: c["id"] for c in self.customers}
        customers = []
        for customer in sort_by_id(self.customers):
            entry = customer.copy()
            if entry.get("state") != "eating":
                entry.pop("base_price", None)
                entry.pop("tip", None)
            customers.append(entry)
        return {
            "player": {"pos": self.pos, "vel": self.vel},
            "stock": ([dump_item(it) for it in self.stock] if self.items_mode
                      else {k: self.stock[k] for k in sorted(self.stock) if self.stock[k] > 0}),
            "hand": self.hand,
            "stoves": [{k: s.get(k) for k in ("id", "pos", "state", "dish", "cook_ticks_left", "ready_ticks")}
                       for s in self.stoves],
            "tables": [{"id": tb["id"], "pos": tb["pos"], "customer_id": occupied.get(tb["id"])} for tb in self.tables],
            "customers": customers,
        }

    def step(self, inp):
        events = []
        self.phase_tick += 1
        advance_timers(self)
        if self.items_mode:
            decay(self, events)
        finish_cooking(self, events)
        self._move(inp)
        if inp.pressed("interact"):
            interact(self, events)
        resolve_departures(self, events)
        if self.time_left_ticks == 0:
            self.done = True
            self.reason = "time"
            events.append(("quan_end", {"reason": "time", "money": self.money, "earned": self.earned,
                                        "shift_earned": self.shift_earned, "reputation": self.reputation}))
            return events
        spawn_customer(self, events)
        return events

    def _move(self, inp):
        speed = self.t["walk_speed"]
        mx, mz = inp.move
        self.vel = ramp_velocity(self, (mx * speed, mz * speed), int(self.t.get("ramp_max_ticks", 6)))
        b = self.t["bounds"]
        for i, axis in enumerate(("x", "z")):
            self.pos[i] += self.vel[i] / TICK_HZ
            lo, hi = b[axis]
            if self.pos[i] <= lo:
                self.pos[i], self.vel[i] = lo, max(0.0, self.vel[i])
            elif self.pos[i] >= hi:
                self.pos[i], self.vel[i] = hi, min(0.0, self.vel[i])
