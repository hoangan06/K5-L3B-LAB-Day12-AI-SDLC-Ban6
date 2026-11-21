"""Khởi tạo, bơi và sinh đàn cá bằng các luồng RNG riêng."""

from math import atan2, cos, degrees, dist, radians, sin

from .. import TICK_HZ
from ..ids import sort_by_id


def init_fish(sim, scenario):
    sim.random_fish = scenario.get("random_fish", True)
    sim.fish = [
        {"id": row["id"], "kind": row["kind"], "pos": list(map(float, row["pos"])),
         "heading_deg": float(row.get("heading_deg", 0)), "age_ticks": row.get("age_ticks", 0)}
        for row in scenario.get("fish", [])
    ]
    for fish in sim.fish:
        sim.ids.reserve(fish["id"])
    if "fish" not in scenario and sim.random_fish:
        for _ in range(sim.t["fish_initial"]):
            if _spawn(sim) is None:
                break


def _spawn(sim):
    tuning = sim.t
    locations = {}
    for kind in sorted(tuning["fish_weights"]):
        open_points = [
            [x, depth] for x in sorted(tuning["fish_spawn_x"])
            for depth in sorted(tuning["fish_spawn_depths"][kind])
            if all(dist((x, depth), fish["pos"]) > tuning["fish_spawn_clearance"] for fish in sim.fish)
        ]
        if open_points:
            locations[kind] = open_points
    if not locations:
        return None
    stream = sim.rng.get("fish_spawn")
    kinds = list(locations)
    weights = [tuning["fish_weights"][kind] for kind in kinds]
    kind = stream.choices(kinds, weights=weights, k=1)[0]
    fish = {"id": sim.ids.new("F"), "kind": kind, "pos": list(map(float, stream.choice(locations[kind]))),
            "heading_deg": stream.random() * 360, "age_ticks": 0}
    sim.fish.append(fish)
    return fish


def _reflect(position, delta, interval):
    low, high = interval
    position += delta
    while position < low or position > high:
        edge = low if position < low else high
        position = 2 * edge - position
        delta = -delta
    if (position == low and delta < 0) or (position == high and delta > 0):
        delta = -delta
    return position, delta


def update_fish(sim, events):
    if not sim.random_fish:
        return
    tuning = sim.t
    speed = tuning["fish_speed"] / TICK_HZ
    for fish in sort_by_id(sim.fish):
        fish["age_ticks"] += 1
        if fish["age_ticks"] % tuning["fish_turn_ticks"] == 0:
            fish["heading_deg"] = sim.rng.get("fish_turn").random() * 360
        angle = radians(fish["heading_deg"])
        dx, dd = cos(angle) * speed, sin(angle) * speed
        x, rx = _reflect(fish["pos"][0], dx, tuning["fish_x"])
        depth, rd = _reflect(fish["pos"][1], dd, tuning["fish_depths"][fish["kind"]])
        fish["pos"] = [x, depth]
        if (rx, rd) != (dx, dd):
            fish["heading_deg"] = degrees(atan2(rd, rx)) % 360
    if sim.phase_tick % tuning["fish_spawn_ticks"] == 0 and len(sim.fish) < tuning["fish_max"]:
        fish = _spawn(sim)
        if fish is not None:
            events.append(("fish_spawned", {"id": fish["id"], "kind": fish["kind"], "pos": list(fish["pos"])}))


def snapshot_fish(sim):
    return [dict(fish, pos=list(fish["pos"])) for fish in sort_by_id(sim.fish)]
