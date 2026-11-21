"""Session dùng chung cho headless và live, giữ tick riêng khi tạm dừng."""

import math

from .errors import BadInput
from .ids import IdAllocator
from .inputs import BUTTONS_V10, BUTTONS_V11, InputPlayer
from .inventory import write_inventory
from .jsonl import JsonlWriter
from .rng import Streams
from .sim.day import DaySim
from .sim.gather import GatherSim
from .sim.quan import QuanSim


def build_sim(mode, tuning, scenario, seed, inventory, *, days=1):
    streams, ids = Streams(seed), IdAllocator()
    if mode == "gather":
        return GatherSim(tuning, scenario, streams, ids)
    if mode == "quan":
        return QuanSim(tuning, scenario, streams, ids, inventory=inventory)
    if mode == "day" and "shop" in tuning:
        return DaySim(tuning, scenario, streams, ids, days=days)
    raise BadInput(f"mode {mode} không được hỗ trợ bởi contract đang chạy")


class Session:
    def __init__(self, mode, tuning, scenario, seed, inventory=None, *, days=1):
        self.mode = mode
        self.tuning = tuning
        self.sim = build_sim(mode, tuning, scenario, seed, inventory, days=days)
        self.tick = 0
        self.sim_tick = 0
        self.paused = False

    @property
    def done(self):
        return self.sim.done

    def _score(self):
        return self.sim.earned + self.tuning["score"]["reputation_multiplier"] * math.floor(self.sim.reputation)

    def snapshot(self):
        sim = self.sim
        state = "finished" if sim.done else "paused" if self.paused else "playing"
        return {
            "type": "snapshot", "tick": self.tick, "sim_tick": self.sim_tick,
            "mode": self.mode, "phase": sim.phase, "phase_tick": sim.phase_tick,
            "state": state, "time_left_ticks": sim.time_left_ticks, "money": sim.money,
            "earned": sim.earned, "reputation": sim.reputation, "score": self._score(), **sim.snapshot(),
        }

    def _wrap(self, rows):
        return [{"type": "event", "tick": self.tick, **row} for row in rows]

    def _event(self, name, data):
        row = {"phase": self.sim.phase, "name": name, "data": data}
        if self.mode == "day":
            row["day"] = self.sim.day
        return row

    def initial_events(self):
        return self._wrap(self.sim.initial_events()) if self.mode == "day" else []

    def step(self, inp):
        if self.done:
            return []
        self.tick += 1
        events = []
        if inp.pressed("pause") and "shop" in self.tuning:
            self.paused = not self.paused
            events.append(self._event("paused" if self.paused else "resumed", {}))
        if not self.paused:
            self.sim_tick += 1
            rows = self.sim.step(inp)
            if self.mode == "day":
                events.extend(rows)
            else:
                events.extend(self._event(name, data) for name, data in rows)
        return self._wrap(events)

    def end_row(self):
        sim = self.sim
        row = {
            "type": "end", "ticks": self.tick, "sim_tick": self.sim_tick, "mode": self.mode,
            "state": "finished" if sim.done else "playing", "reason": sim.reason if sim.done else "tick_limit",
            "money": sim.money, "earned": sim.earned, "reputation": sim.reputation, "score": self._score(),
        }
        if self.mode == "day":
            row["days_completed"] = sim.days_completed
        return row

    def write_inventory_if_done(self, inventory_out):
        if self.mode == "gather" and self.done and inventory_out:
            write_inventory(inventory_out, self.sim.inventory_items())


def run(mode, tuning, scenario, seed, frames, ticks, out_path, snapshot_every, inventory=None, inventory_out=None, *, days=1):
    session = Session(mode, tuning, scenario, seed, inventory, days=days)
    player = InputPlayer(frames, buttons=BUTTONS_V11 if "shop" in tuning else BUTTONS_V10)
    writer = JsonlWriter(out_path)
    try:
        for event in session.initial_events():
            writer.write(event)
        writer.write(session.snapshot())
        last_snapshot = 0
        while session.tick < ticks and not session.done:
            for event in session.step(player.advance(session.tick)):
                writer.write(event)
            if session.tick % snapshot_every == 0 or session.done:
                writer.write(session.snapshot())
                last_snapshot = session.tick
        if last_snapshot != session.tick:
            writer.write(session.snapshot())
        writer.write(session.end_row())
    finally:
        writer.close()
    session.write_inventory_if_done(inventory_out)
    return session.sim
