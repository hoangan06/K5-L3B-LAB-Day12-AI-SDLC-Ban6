"""Phase 2 fish lifecycle. Called by GatherSim, not by the runner."""
import math

from ..errors import BadInput
from ..ids import sort_by_id


def _points(t, fish):
    result = {}
    for kind in sorted(t["fish_yield"]):
        result[kind] = [[x, d] for x in sorted(t["fish_spawn_x"])
                        for d in sorted(t["fish_spawn_depths"][kind])
                        if all(math.dist([x, d], f["pos"]) > t["fish_spawn_clearance"] for f in fish)]
    return result


def _choose(sim, points):
    kinds = [k for k in sorted(points) if points[k] and sim.t["fish_weights"][k] > 0]
    if not kinds:
        return None
    rng = sim.rng.get("fish_spawn")
    total = sum(sim.t["fish_weights"][k] for k in kinds)
    pick = rng.random() * total
    kind = kinds[-1]
    for candidate in kinds:
        pick -= sim.t["fish_weights"][candidate]
        if pick < 0:
            kind = candidate
            break
    return kind, list(rng.choice(points[kind])), rng.uniform(0, 360)


def init_fish(sim, scenario: dict) -> None:
    sim.random_fish = scenario.get("random_fish", True)
    sim.fish = []
    for f in scenario.get("fish", []):
        fish = {"id": f["id"], "kind": f["kind"], "pos": list(f["pos"]),
                "heading_deg": f.get("heading_deg", 0), "age_ticks": f.get("age_ticks", 0)}
        sim.ids.reserve(fish["id"])
        sim.fish.append(fish)
    if "fish" not in scenario and sim.random_fish:
        for _ in range(sim.t["fish_initial"]):
            choice = _choose(sim, _points(sim.t, sim.fish))
            if choice is None:
                raise BadInput("không đủ điểm sinh cá ban đầu")
            kind, pos, heading = choice
            sim.fish.append({"id": sim.ids.new("F"), "kind": kind, "pos": pos,
                             "heading_deg": heading, "age_ticks": 0})


def _reflect(value, velocity, lo, hi):
    # Fold an arbitrary displacement into the interval, including repeated bounces.
    width = hi - lo
    offset = (value - lo) % (2 * width)
    if offset == 0:
        return lo, abs(velocity)
    if offset == width:
        return hi, -abs(velocity)
    if offset < width:
        return lo + offset, velocity
    return hi - (offset - width), -velocity


def update_fish(sim, events: list) -> None:
    if not sim.random_fish:
        return
    t = sim.t
    for f in sort_by_id(sim.fish):
        f["age_ticks"] += 1
        if f["age_ticks"] % t["fish_turn_ticks"] == 0:
            f["heading_deg"] = sim.rng.get("fish_turn").uniform(0, 360)
        angle = math.radians(f["heading_deg"])
        dx = math.cos(angle) * t["fish_speed"] / 60
        dd = math.sin(angle) * t["fish_speed"] / 60
        x, dx = _reflect(f["pos"][0] + dx, dx, *t["fish_x"])
        d, dd = _reflect(f["pos"][1] + dd, dd, *t["fish_depths"][f["kind"]])
        f["pos"] = [x, d]
        f["heading_deg"] = math.degrees(math.atan2(dd, dx)) % 360
    if sim.phase_tick % t["fish_spawn_ticks"] or len(sim.fish) >= t["fish_max"]:
        return
    choice = _choose(sim, _points(t, sim.fish))
    if choice is None:
        return
    kind, pos, heading = choice
    fish = {"id": sim.ids.new("F"), "kind": kind, "pos": pos,
            "heading_deg": heading, "age_ticks": 0}
    sim.fish.append(fish)
    events.append(("fish_spawned", {"id": fish["id"], "kind": kind, "pos": list(pos)}))


def snapshot_fish(sim) -> list:
    return [{"id": f["id"], "kind": f["kind"], "pos": list(f["pos"]),
             "heading_deg": f["heading_deg"], "age_ticks": f["age_ticks"]}
            for f in sort_by_id(sim.fish)]
