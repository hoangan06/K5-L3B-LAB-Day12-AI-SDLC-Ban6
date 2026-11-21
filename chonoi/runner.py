"""Vòng tick (Contract B, mô hình tick). KHUNG — thường không cần sửa.

Thứ tự ghi: snapshot tick 0 -> với mỗi bước: sự kiện (theo thứ tự xử lý) rồi snapshot (nếu tới lượt
hoặc buổi kết thúc) -> dòng 'end'. Mỗi tick tối đa một snapshot.

`Session` là API bước tick gọn dùng chung cho headless (`run`) và cửa sổ chơi trực tiếp (`chonoi.live`):
cả hai chạy CÙNG một lớp sim, không nhân đôi logic.
"""

import math
from copy import deepcopy

from .errors import BadInput

from .ids import IdAllocator
from .inputs import InputPlayer
from .inventory import write_inventory
from .jsonl import JsonlWriter
from .rng import Streams
from .sim.gather import GatherSim
from .sim.quan import QuanSim


def _validate_days(mode, days, soak):
    if type(soak) is not bool:
        raise BadInput("soak phải là boolean")
    if soak and mode != "day":
        raise BadInput("soak chỉ dùng với day")
    if type(days) is not int or days < 1 or (not soak and days > 5):
        raise BadInput("days phải là số nguyên dương" if soak else "days phải là số nguyên 1..5")
    if mode != "day" and days != 1:
        raise BadInput("days chỉ dùng với day")


def build_sim(mode, tuning, scenario, seed, inventory, *, days=1, soak=False):
    _validate_days(mode, days, soak)
    streams, ids = Streams(seed), IdAllocator()
    if mode == "gather":
        return GatherSim(tuning, scenario, streams, ids)
    if mode == "quan":
        return QuanSim(tuning, scenario, streams, ids, inventory=inventory)
    if mode == "day":
        try:
            from .sim.day import DaySim
        except ModuleNotFoundError as exc:
            if exc.name != "chonoi.sim.day":
                raise
            raise BadInput("DaySim chưa được tích hợp; cần chonoi/sim/day.py của Đức") from exc
        # Giữ tương thích DaySim P2/P3 cho lượt chuẩn; soak cần API P4 của Duy.
        if soak:
            return DaySim(tuning, scenario, streams, ids, days=days, soak=True)
        return DaySim(tuning, scenario, streams, ids, days=days)
    raise BadInput(f"mode không hỗ trợ: {mode}")


def _common(sim, tick, sim_tick, phase_tick, tuning, state):
    mult = tuning["score"]["reputation_multiplier"]
    return {
        "type": "snapshot", "tick": tick, "sim_tick": sim_tick, "mode": sim.mode, "phase": sim.phase,
        "phase_tick": phase_tick, "state": state, "time_left_ticks": sim.time_left_ticks,
        "money": sim.money, "earned": sim.earned, "reputation": sim.reputation,
        "score": sim.earned + mult * math.floor(sim.reputation),
    }


class Session:
    """Một lượt chơi: dựng sim, bước từng tick, lấy snapshot / dòng end."""

    def __init__(self, mode, tuning, scenario, seed, inventory=None, *, days=1, soak=False):
        _validate_days(mode, days, soak)
        if inventory is not None and mode != "quan":
            raise BadInput("inventory chỉ dùng với quan")
        self.mode = mode
        self.tuning = tuning
        self.sim = build_sim(mode, tuning, scenario, seed, inventory, days=days, soak=soak)
        self.tick = 0
        self.sim_tick = 0
        self.paused = False
        self._phase_tick = 0  # tương thích GatherSim P1 chưa có phase_tick
        self._inventory_written = False
        self._initial = deepcopy(self.sim.initial_events()) if mode == "day" else []

    @property
    def phase_tick(self):
        return getattr(self.sim, "phase_tick", self._phase_tick)

    def _event_rows(self, events, phase, day=None):
        rows = []
        for event in events:
            if self.mode == "day":
                row = {"type": "event", "tick": self.tick, "phase": event["phase"],
                       "day": event["day"], "name": event["name"], "data": deepcopy(event["data"])}
            else:
                name, data = event
                row = {"type": "event", "tick": self.tick, "phase": phase,
                       "name": name, "data": deepcopy(data)}
            rows.append(row)
        return rows

    def initial_events(self):
        """Drain sự kiện khởi tạo một lần; không phát lại khi GET /state."""
        events, self._initial = self._initial, []
        return self._event_rows(events, self.sim.phase)

    def _pause_event(self, name):
        row = {"type": "event", "tick": self.tick, "phase": self.sim.phase,
               "name": name, "data": {}}
        if self.mode == "day":
            row["day"] = self.sim.day
        return row

    @property
    def done(self) -> bool:
        return self.sim.done

    def snapshot(self) -> dict:
        state = "paused" if self.paused else "finished" if self.done else "playing"
        s = _common(self.sim, self.tick, self.sim_tick, self.phase_tick, self.tuning, state)
        s.update(self.sim.snapshot())
        # Vỏ output do Session giữ, child không được ghi đè các bộ đếm/state.
        s.update(tick=self.tick, sim_tick=self.sim_tick, phase_tick=self.phase_tick,
                 mode=self.mode, phase=self.sim.phase, state=state)
        return s

    def step(self, inp) -> list:
        """Chạy một bước với `inp` (chonoi.inputs.InputState); trả các dòng event (tick = k + 1)."""
        if self.done:
            return []
        self.tick += 1
        rows = []
        if inp.pressed("pause"):
            self.paused = not self.paused
            rows.append(self._pause_event("paused" if self.paused else "resumed"))
        if self.paused:
            return rows
        phase = self.sim.phase
        events = self.sim.step(inp)
        self.sim_tick += 1
        self._phase_tick += 1
        rows.extend(self._event_rows(events, phase))
        return rows

    def end_row(self) -> dict:
        sim = self.sim
        score = _common(sim, self.tick, self.sim_tick, self.phase_tick, self.tuning, "")["score"]
        row = {"type": "end", "ticks": self.tick, "sim_tick": self.sim_tick, "mode": self.mode,
                "state": "paused" if self.paused else "finished" if sim.done else "playing",
                "reason": sim.reason if sim.done else "tick_limit",
                "money": sim.money, "earned": sim.earned, "reputation": sim.reputation, "score": score}
        if self.mode == "day":
            row["days_completed"] = sim.days_completed
        return row

    def write_inventory_if_done(self, inventory_out):
        """File kho: ghi MỘT lần khi có gather_end; chưa kết thúc thì giữ nguyên file đích."""
        if self.mode == "gather" and self.sim.done and inventory_out and not self._inventory_written:
            write_inventory(inventory_out, self.sim.inventory_items())
            self._inventory_written = True


def run(mode, tuning, scenario, seed, frames, ticks, out_path, snapshot_every, inventory=None, inventory_out=None, *, days=1):
    sess = Session(mode, tuning, scenario, seed, inventory, days=days)
    player = InputPlayer(frames)
    w = JsonlWriter(out_path)
    try:
        for row in sess.initial_events():
            w.write(row)
        w.write(sess.snapshot())  # tick 0: sau khi dựng scenario, trước mọi input
        last_snapped = 0
        while sess.tick < ticks and not sess.done:
            previous_phase = (getattr(sess.sim, "day", None), sess.sim.phase)
            inp = player.advance(sess.tick)  # bước k đọc input có tick == k
            for row in sess.step(inp):
                w.write(row)
            changed_phase = previous_phase != (getattr(sess.sim, "day", None), sess.sim.phase)
            if sess.tick % snapshot_every == 0 or sess.done or changed_phase:
                w.write(sess.snapshot())
                last_snapped = sess.tick
        if last_snapped != sess.tick:
            w.write(sess.snapshot())
        w.write(sess.end_row())
    finally:
        w.close()
    sess.write_inventory_if_done(inventory_out)
    return sess.sim
