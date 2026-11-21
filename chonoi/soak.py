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
    """Collect one nearby surface node, return to dock, and close the shop."""

    def __init__(self):
        self.previous = set()

    def input(self, sim):
        pressed, move, buy = set(), (0.0, 0.0), None
        child = sim.current_sim
        if sim.phase == "gather":
            target = child.t["dock_pos"] if child.hold else child.nodes[0]["pos"]
            dx = target[0] - child.pos[0]
            radius = child.t["dock_radius"] if child.hold else child.t["interact_radius"]
            if abs(dx) <= radius * 0.6:
                pressed.add("interact")
            else:
                move = (1.0 if dx > 0 else -1.0, 0.0)
        elif sim.phase == "shop":
            pressed.add("shop_done")
        edges = pressed - self.previous
        self.previous = pressed
        return InputState(move, {b: b in pressed for b in ("interact", "shop_done")}, edges, buy=buy)


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
