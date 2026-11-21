"""Cá sấu tuần tra, đuổi, chạm và lùi trong pha gather."""

from math import dist, floor, hypot

from .. import TICK_HZ
from ..errors import BadInput
from ..ids import id_key, sort_by_id


def init_monsters(sim, scenario):
    tuning = sim.t["monsters"]
    defaults = {row["id"]: row for row in tuning["spawns"]}
    source = scenario.get("monsters", [row for row in defaults.values() if row["from_day"] <= sim.day])
    if not isinstance(source, list):
        raise BadInput("gather.monsters phải là mảng")
    seen = set()
    monsters = []
    for raw in source:
        allowed = {"id", "kind", "pos", "waypoints", "target_idx", "state", "state_ticks_left", "recoil_dir"}
        if not isinstance(raw, dict) or set(raw) - (allowed | {"from_day"}):
            raise BadInput("fixture quái có trường không hợp lệ")
        if "monsters" in scenario and "from_day" in raw:
            raise BadInput("from_day chỉ dùng trong preset quái")
        ident = raw.get("id")
        if not isinstance(ident, str) or not ident or ident in seen:
            raise BadInput("quái cần id khác rỗng và duy nhất")
        seen.add(ident)
        monster = {**defaults.get(ident, {}), **raw}
        kind = monster.get("kind", "ca_sau")
        if not isinstance(kind, str) or kind not in tuning["species"]:
            raise BadInput(f"{ident}: loài quái không được hỗ trợ")
        species = tuning["species"][kind]
        waypoints = monster.get("waypoints")
        if not isinstance(waypoints, list) or len(waypoints) < 2:
            raise BadInput(f"{ident}: cần ít nhất hai waypoint")
        points = [_position(point, sim.t["bounds"]["x"], species["depths"], ident) for point in waypoints]
        position = _position(monster.get("pos", points[0]), sim.t["bounds"]["x"], species["depths"], ident)
        index = monster.get("target_idx", 1)
        state = monster.get("state", "patrol")
        timer = monster.get("state_ticks_left", 0)
        if type(index) is not int or not 0 <= index < len(points):
            raise BadInput(f"{ident}: target_idx không hợp lệ")
        if (state not in ("patrol", "chase", "recoil") or type(timer) is not int
                or not 0 <= timer <= species["recoil_ticks"] or (state == "recoil") != (timer > 0)):
            raise BadInput(f"{ident}: trạng thái và timer không khớp")
        direction = None
        if state == "recoil":
            dx, dd = _position(monster.get("recoil_dir", [1, 0]), (-1, 1), (-1, 1), ident)
            magnitude = hypot(dx, dd)
            if not magnitude:
                raise BadInput(f"{ident}: hướng lùi phải khác 0")
            direction = [dx / magnitude, dd / magnitude]
        elif monster.get("recoil_dir") is not None:
            raise BadInput(f"{ident}: chỉ quái đang lùi có recoil_dir")
        monsters.append({"id": ident, "kind": kind, "pos": position, "waypoints": points, "target_idx": index,
                         "state": state, "state_ticks_left": timer, "recoil_dir": direction})
        sim.ids.reserve(ident)
    sim.monsters = sort_by_id(monsters)


def _position(point, x_bounds, depth_bounds, ident):
    if (not isinstance(point, list) or len(point) != 2
            or any(type(value) not in (int, float) for value in point)
            or not (x_bounds[0] <= point[0] <= x_bounds[1] and depth_bounds[0] <= point[1] <= depth_bounds[1])):
        raise BadInput(f"{ident}: vị trí hoặc hướng nằm ngoài miền")
    return list(map(float, point))


def _toward(position, target, distance):
    length = dist(position, target)
    if length <= distance:
        return list(target)
    return [p + (t - p) * distance / length for p, t in zip(position, target)]


def _clamp(pos, x_bounds, depth_bounds):
    return [min(high, max(low, value)) for value, (low, high) in zip(pos, (x_bounds, depth_bounds))]


def update_monsters(sim, events):
    tuning = sim.t["monsters"]
    x_bounds = sim.t["bounds"]["x"]
    candidates = []
    for monster in sim.monsters:
        species = tuning["species"][monster["kind"]]
        depths = species["depths"]
        if monster["state"] == "recoil":
            speed = species["recoil_dist"] / species["recoil_ticks"]
            pos = [p + v * speed for p, v in zip(monster["pos"], monster["recoil_dir"])]
            monster["pos"] = _clamp(pos, x_bounds, depths)
            monster["state_ticks_left"] -= 1
            if monster["state_ticks_left"] == 0:
                monster.update(state="patrol", recoil_dir=None)
            continue

        player_deep = sim.pos[1] >= depths[0]
        radius = species["exit_radius"] if monster["state"] == "chase" else species["detect_radius"]
        chasing = player_deep and dist(sim.pos, monster["pos"]) <= radius
        if chasing:
            monster["state"] = "chase"
            target = _clamp(sim.pos, x_bounds, depths)
            monster["pos"] = _toward(monster["pos"], target, species["chase_speed"] / TICK_HZ)
        else:
            monster["state"] = "patrol"
            waypoint = monster["waypoints"][monster["target_idx"]]
            monster["pos"] = _toward(monster["pos"], waypoint, species["patrol_speed"] / TICK_HZ)
            if monster["pos"] == waypoint:
                monster["target_idx"] = (monster["target_idx"] + 1) % len(monster["waypoints"])
        gap = dist(sim.pos, monster["pos"])
        if sim.invuln_ticks == 0 and player_deep and gap <= species["hit_radius"]:
            candidates.append((gap, id_key(monster["id"]), monster, species))

    if not candidates:
        return
    _, _, monster, species = min(candidates, key=lambda row: row[:2])
    delta = [m - p for m, p in zip(monster["pos"], sim.pos)]
    magnitude = hypot(*delta)
    direction = [v / magnitude for v in delta] if magnitude else [1, 0]
    monster.update(state="recoil", state_ticks_left=species["recoil_ticks"], recoil_dir=direction)
    sim.invuln_ticks = tuning["invuln_ticks"]
    sim.hp -= 1
    lost = [sim.hold.pop() for _ in range(floor(len(sim.hold) * tuning["loss_ratio"]))]
    events.append(("monster_hit", {"monster_id": monster["id"], "hp": sim.hp, "lost": lost, "pos": list(sim.pos)}))
    if sim.hp == 0:
        sim._faint("monster", events)


def snapshot_monsters(sim):
    return [{"id": m["id"], "kind": m["kind"], "pos": list(m["pos"]), "state": m["state"],
             "state_ticks_left": m["state_ticks_left"]} for m in sim.monsters]
