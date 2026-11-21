"""Actions for gathering; the caller handles inputs, timers and the dock."""

import math

from ..ids import id_key


def _nearest(pos, entities, radius):
    candidates = [(math.dist(pos, e["pos"]), id_key(e["id"]), e)
                  for e in entities if math.dist(pos, e["pos"]) <= radius]
    return min(candidates, key=lambda item: (item[0], item[1]))[2] if candidates else None


def gather_node(sim, events):
    if not sim._at_surface():
        return
    node = _nearest(sim.pos, (n for n in sim.nodes if n["regrow_ticks"] == 0),
                    sim.t["interact_radius"])
    if node is None:
        return
    amount = sim.t["node_yield"]
    free = sim.t["hold_capacity"] - len(sim.hold)
    if free < amount:
        events.append(("hold_full", {"action": "gather", "node_id": node["id"],
                                     "required": amount, "free": free}))
        return
    sim.hold.extend([node["kind"]] * amount)
    node["regrow_ticks"] = int(round(sim.t["regrow_s"] * 60))
    events.append(("gather", {"node_id": node["id"], "kind": node["kind"], "amount": amount}))


def catch_fish(sim, events):
    if sim._at_surface() or sim.catch_cd_ticks:
        return
    fish = _nearest(sim.pos, sim.fish, sim.t["catch_radius"])
    if fish is None:
        return
    amount = sim.t["fish_yield"][fish["kind"]]
    free = sim.t["hold_capacity"] - len(sim.hold)
    if free < amount:
        events.append(("hold_full", {"action": "catch", "fish_id": fish["id"],
                                     "required": amount, "free": free}))
        return
    sim.hold.extend([fish["kind"]] * amount)
    sim.fish.remove(fish)
    sim.catch_cd_ticks = int(round(sim.t["catch_cooldown_s"] * 60))
    events.append(("fish_caught", {"fish_id": fish["id"], "kind": fish["kind"], "yield": amount}))
