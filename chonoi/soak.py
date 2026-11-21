"""Deterministic multi-day soak using one Session and ordinary player input."""
import argparse
import inspect
import json
import math
import os
import sys
import tempfile
import time

from .contract import load_contract
from .errors import BadInput
from .inputs import InputState
from .runner import Session


class Bot:
    """Collect two flowers, serve available orders and buy an affordable upgrade."""

    def __init__(self):
        self.previous = set()

    def input(self, sim):
        pressed, move, buy = set(), (0.0, 0.0), None
        child = sim.current_sim
        if sim.phase == "gather":
            node = next((n for n in child.nodes if n["kind"] == "bong_sung"), None)
            finished = len(child.hold) >= 2 or node is None
            target = child.t["dock_pos"] if finished else node["pos"]
            radius = child.t["dock_radius"] if finished else child.t["interact_radius"]
            move = self._move(child.pos, target, radius)
            if move == (0.0, 0.0) and (finished or node["regrow_ticks"] == 0):
                pressed.add("interact")
        elif sim.phase == "quan":
            target = None
            if child.hand:
                customer = next((c for c in child.customers if c["id"] == child.hand["order_id"]), None)
                target = next((t for t in child.tables if customer and t["id"] == customer["table_id"]), None)
            else:
                target = next((s for s in child.stoves if s["state"] == "ready"), None)
                if target is None and any(c["order_status"] == "reserved" for c in child.customers):
                    target = next((s for s in child.stoves if s["state"] == "idle"), None)
            if target is not None:
                move = self._move(child.pos, target["pos"], child.t["interact_radius"])
                if move == (0.0, 0.0):
                    pressed.add("interact")
        elif sim.phase == "shop":
            for name in sorted(child.upgrades):
                next_level = child.upgrades[name] + 1
                option = next((entry for entry in child.t["upgrades"][name] if entry["level"] == next_level), None)
                if option and child.money >= option["price"]:
                    buy = name
                    break
            pressed.add("shop_done")
        # Releasing between attempts creates real rising edges, including after a failed interaction.
        if "interact" in self.previous:
            pressed.discard("interact")
        edges = pressed - self.previous
        self.previous = pressed
        return InputState(move, {b: b in pressed for b in ("interact", "shop_done")}, edges, buy=buy)

    @staticmethod
    def _move(pos, target, radius):
        dx, dy = target[0] - pos[0], target[1] - pos[1]
        distance = math.hypot(dx, dy)
        if distance <= radius * 0.5:
            return (0.0, 0.0)
        return (dx / distance, dy / distance)


def run_soak(tuning, seed, days):
    if type(days) is not int or days < 1 or type(seed) is not int:
        raise BadInput("seed must be an integer and days must be a positive integer")
    if "soak" not in inspect.signature(Session).parameters:
        raise RuntimeError("Session soak adapter is not integrated; ask the runner owner to add soak=True")
    started = time.perf_counter()
    session = Session("day", tuning, {}, seed, days=days, soak=True)
    bot = Bot()
    limit = days * (math.ceil(tuning["gather"]["duration_s"] * 60)
                    + math.ceil(tuning["quan"]["duration_s"] * 60)
                    + tuning["shop"]["max_ticks"] + 1)
    for _ in range(limit):
        if session.done:
            break
        session.step(bot.input(session.sim))
    if not session.done or session.sim.days_completed != days:
        raise RuntimeError("soak did not complete the requested days within the gameplay tick limit")
    rows = [dict(row) for row in session.sim.completed_results]
    if len(rows) != days or [row["day"] for row in rows] != list(range(1, days + 1)):
        raise RuntimeError("completed_results is incomplete")
    return {"days": days, "days_completed": session.sim.days_completed, "crashes": 0,
            "results": rows, "duration_s": time.perf_counter() - started}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run deterministic day soak")
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--days", required=True, type=int)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        if args.days < 1:
            raise BadInput("days must be positive")
        result = run_soak(load_contract()["tuning"], args.seed, args.days)
        directory = os.path.dirname(os.path.abspath(args.out))
        fd, tmp = tempfile.mkstemp(prefix=".soak-", suffix=".tmp", dir=directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
                json.dump(result, f, ensure_ascii=False, indent=2, allow_nan=False)
                f.write("\n")
            os.replace(tmp, args.out)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
        return 0
    except BadInput as exc:
        print(f"input error: {exc}".encode("ascii", "backslashreplace").decode("ascii"), file=sys.stderr)
        return 2
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"soak failed: {exc}".encode("ascii", "backslashreplace").decode("ascii"), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
