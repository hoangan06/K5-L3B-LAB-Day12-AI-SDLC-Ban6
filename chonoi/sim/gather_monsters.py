"""Cá Sấu Phase 2: init, di chuyển, một hit/bước và snapshot tất định."""

from copy import deepcopy
import math

from ..errors import BadInput
from ..ids import id_key, sort_by_id

TICK_HZ = 60
KEYS = {"id", "kind", "pos", "waypoints", "target_idx", "state", "state_ticks_left", "recoil_dir"}


def _integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _vector(value):
    return (isinstance(value, list) and len(value) == 2
            and all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in value))


def init_monsters(sim, scenario):
    """Fixture thay thế spawns; không có config P2 thì không tự thêm quái P1."""
    config = sim.t.get("monsters")
    if config is None:
        if "monsters" in scenario:
            raise BadInput("gather.monsters cần tuning.monsters của Phase 2")
        sim.monsters = []
        return
    source = scenario.get("monsters")
    if source is None and "monsters" in scenario:
        raise BadInput("gather.monsters phải là mảng")
    if "monsters" not in scenario:
        source = [{k: deepcopy(v) for k, v in spawn.items() if k != "from_day"}
                  for spawn in config["spawns"] if spawn["from_day"] <= sim.day]
    if not isinstance(source, list):
        raise BadInput("gather.monsters phải là mảng")
    monsters, seen = [], set()
    for raw in source:
        if not isinstance(raw, dict) or set(raw) - KEYS:
            raise BadInput("monster: object có trường lạ hoặc sai kiểu")
        monster = deepcopy(raw)
        ident, kind = monster.get("id"), monster.get("kind")
        if not isinstance(ident, str) or not ident or ident in seen:
            raise BadInput("monster: cần id duy nhất, khác rỗng")
        seen.add(ident)
        # Chỉ loài lõi; extension snake/stunned chưa bật.
        if kind != "ca_sau" or kind not in config["species"]:
            raise BadInput("monster.kind chưa hỗ trợ")
        species = config["species"][kind]
        positions = [monster.get("pos")]
        waypoints = monster.get("waypoints")
        if not isinstance(waypoints, list) or len(waypoints) != 2:
            raise BadInput("monster.waypoints cần đúng hai điểm")
        positions.extend(waypoints)
        for pos in positions:
            if (not _vector(pos) or not sim.t["bounds"]["x"][0] <= pos[0] <= sim.t["bounds"]["x"][1]
                    or not max(sim.t["bounds"]["d"][0], species["depths"][0]) <= pos[1]
                    <= min(sim.t["bounds"]["d"][1], species["depths"][1])):
                raise BadInput("monster.pos/waypoints ngoài miền loài hoặc map")
        monster.setdefault("target_idx", 1)
        monster.setdefault("state", "patrol")
        monster.setdefault("state_ticks_left", 0)
        monster.setdefault("recoil_dir", None)
        if not _integer(monster["target_idx"]) or monster["target_idx"] not in (0, 1):
            raise BadInput("monster.target_idx phải là 0 hoặc 1")
        state, timer, direction = monster["state"], monster["state_ticks_left"], monster["recoil_dir"]
        if not _integer(timer) or timer < 0 or state not in ("patrol", "chase", "recoil"):
            raise BadInput("monster.state/timer không hợp lệ")
        if state == "recoil":
            if timer <= 0 or not _vector(direction) or not math.isclose(math.hypot(*direction), 1.0, abs_tol=1e-9):
                raise BadInput("monster recoil cần timer dương và recoil_dir đơn vị")
        elif timer != 0 or direction is not None:
            raise BadInput("monster không recoil phải có timer0 và recoil_dir null")
        monster["pos"] = [float(v) for v in monster["pos"]]
        monsters.append(monster)
        sim.ids.reserve(ident)
    sim.monsters = sort_by_id(monsters)


def _clamp(sim, monster, species):
    bounds = sim.t["bounds"]
    monster["pos"][0] = min(bounds["x"][1], max(bounds["x"][0], monster["pos"][0]))
    monster["pos"][1] = min(bounds["d"][1], species["depths"][1],
                            max(bounds["d"][0], species["depths"][0], monster["pos"][1]))


def _towards(monster, target, distance):
    delta = [target[i] - monster["pos"][i] for i in (0, 1)]
    length = math.hypot(*delta)
    if length <= distance:
        monster["pos"] = list(target)
        return True
    monster["pos"] = [monster["pos"][i] + delta[i] * distance / length for i in (0, 1)]
    return False


def update_monsters(sim, events):
    config = sim.t.get("monsters")
    if config is None:
        return
    candidates = []
    for monster in sort_by_id(sim.monsters):
        species = config["species"][monster["kind"]]
        if monster["state"] == "recoil":
            distance = species["recoil_dist"] / species["recoil_ticks"]
            monster["pos"] = [monster["pos"][i] + monster["recoil_dir"][i] * distance for i in (0, 1)]
            _clamp(sim, monster, species)
            monster["state_ticks_left"] -= 1
            if monster["state_ticks_left"] == 0:
                monster["state"] = "patrol"
                monster["recoil_dir"] = None
            # Bước recoil cuối vẫn không phát hiện/chạm.
            continue
        distance = math.dist(monster["pos"], sim.pos)
        in_depth = sim.pos[1] >= species["depths"][0]
        if monster["state"] == "chase":
            if not in_depth or distance > species["exit_radius"]:
                monster["state"] = "patrol"
        elif in_depth and distance <= species["detect_radius"]:
            monster["state"] = "chase"
        if monster["state"] == "chase":
            _towards(monster, sim.pos, species["chase_speed"] / TICK_HZ)
        else:
            target = monster["waypoints"][monster["target_idx"]]
            if _towards(monster, target, species["patrol_speed"] / TICK_HZ):
                monster["target_idx"] = 1 - monster["target_idx"]
        _clamp(sim, monster, species)
        distance = math.dist(monster["pos"], sim.pos)
        if in_depth and distance <= species["hit_radius"]:
            candidates.append((distance, id_key(monster["id"]), monster))
    if sim.invuln_ticks > 0 or not candidates:
        return
    monster = min(candidates, key=lambda item: (item[0], item[1]))[2]
    species = config["species"][monster["kind"]]
    delta = [monster["pos"][i] - sim.pos[i] for i in (0, 1)]
    length = math.hypot(*delta)
    monster["recoil_dir"] = [v / length for v in delta] if length else [1.0, 0.0]
    monster["state"] = "recoil"
    monster["state_ticks_left"] = species["recoil_ticks"]
    sim.hp = max(0, sim.hp - 1)
    lost = [sim.hold.pop() for _ in range(math.floor(len(sim.hold) * config["loss_ratio"]))]
    sim.invuln_ticks = config["invuln_ticks"]
    events.append(("monster_hit", {"monster_id": monster["id"], "hp": sim.hp,
                                   "lost": lost, "pos": list(sim.pos)}))
    if sim.hp == 0:
        sim._faint("monster", events)


def snapshot_monsters(sim):
    return deepcopy(sort_by_id(sim.monsters))
