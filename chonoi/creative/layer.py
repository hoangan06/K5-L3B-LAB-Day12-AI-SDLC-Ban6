"""Lớp sáng tạo (Gói 2) bọc quanh Session TỪ BÊN NGOÀI; chỉ bật ở chonoi.live qua --creative.

Không sửa luật lõi: chỉ (a) đổi InputState đưa vào Session.step, (b) đọc/ghi trạng thái công khai của GatherSim
(pos, hp, oxygen_ticks, invuln_ticks...), (c) bọc `_faint` của đúng phiên gather đang chạy để cá Ông hồi sinh.
Ngẫu nhiên: luồng riêng `creative_*` trên một `Streams(seed)` riêng, không chạm luồng của sim.
Không dùng `hold`, nên chịu cả hold dạng chuỗi (v1.1) lẫn dict (v1.2).
"""

import json
import math
import os

from ..ids import IdAllocator, sort_by_id
from ..inputs import BUTTONS_V11, InputState
from ..rng import Streams

DIRS = ("up", "down", "left", "right")
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "creative.json")


def load_config(path=CONFIG_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def move_dirs(move):
    """Tập hướng đang giữ. Gather: d dương = xuống, nên move[1] < 0 là 'up'."""
    out = set()
    if move[0] > 0.5:
        out.add("right")
    if move[0] < -0.5:
        out.add("left")
    if move[1] < -0.5:
        out.add("up")
    if move[1] > 0.5:
        out.add("down")
    return out


class CreativeLayer:
    def __init__(self, seed, config=None):
        self.cfg = config or load_config()
        streams = Streams(seed)
        self.rng_monster = streams.get("creative_monster")
        self.rng_dice = streams.get("creative_dice")
        self.rng_skip = streams.get("creative_skip")
        self.rng_patrol = streams.get("creative_serpent_patrol")  # luồng riêng: đổi tuần tra không lệch luồng spawn/xúc xắc
        self.ids = IdAllocator()
        self.tick = 0
        self.messages = []
        self._core = None
        self._pending = []
        self._dirs = set()
        self._raw_move = (0.0, 0.0)
        self._reset_phase()

    # --- trạng thái theo phiên gather ---------------------------------------------
    def _reset_phase(self):
        self.progress = {name: 0 for name in self.cfg["shrines"]}
        self.buff_left = 0
        self.ca_ong_lit = False
        self.revives = 0
        self.last_roll = None
        self.serpents = []
        self.spawned = 0
        self.coil = None
        self.immunity = 0
        self.phase_t = 0
        self._armed = {}

    def _say(self, text):
        self.messages.append({"tick": self.tick, "text": text})
        del self.messages[:-self.cfg["message_keep"]]

    def _bind(self, session):
        core = getattr(session.sim, "current_sim", session.sim)
        if core is not self._core:
            self._core = core
            self._reset_phase()
            self._pending.clear()
            if core.phase == "gather":
                original = core._faint

                def faint(cause, events):
                    if not self._try_revive(core):
                        original(cause, events)

                core._faint = faint
        return core

    def _active(self, core):
        return core is self._core and core.phase == "gather" and not core.done

    # --- vào ------------------------------------------------------------------------
    def note_move(self, move):
        """Gọi mỗi khi client gửi hướng: ghi CẠNH LÊN của từng hướng (không mất cú gõ nhanh giữa hai tick)."""
        dirs = move_dirs(move)
        for d in DIRS:
            if d in dirs and d not in self._dirs:
                self._pending.append(d)
        del self._pending[:-8]
        self._dirs = dirs

    def before(self, session, inp):
        core = self._bind(session)
        self._raw_move = (float(inp.move[0]), float(inp.move[1]))
        if session.paused or session.done or not self._active(core):
            return inp
        self._maybe_skip_croc_hit(core)
        old_edges = {b for b in BUTTONS_V11 if inp.pressed(b)}
        move, edges = inp.move, set(old_edges)
        if self.coil:
            move = (0.0, 0.0)
            edges -= {"interact", "catch"}
        elif self.buff_left > 0:
            m = self.cfg["ba_thuy_buff"]["swim_speed_mult"]
            move = (move[0] * m, move[1] * m)
        if move == inp.move and edges == old_edges:
            return inp
        return InputState(move, dict(inp.held), edges, buy=inp.buy)

    # --- ra -------------------------------------------------------------------------
    def after(self, session):
        core = self._core
        self.tick = session.tick
        if session.paused or core is None:
            return
        if core.done:
            self.coil = None
            return
        if not self._active(core):
            return
        self.phase_t += 1
        self.immunity = max(0, self.immunity - 1)
        if self.buff_left > 0:
            self.buff_left -= 1
            if self.buff_left == 0:
                self._say("Phước Bà Thủy đã hết, có thể thắp hương lại.")
        self._update_shrines(core)
        self._update_serpents(core)

    def _at_surface(self, core):
        return core.pos[1] <= core.t["surface_depth"]

    def _update_shrines(self, core):
        standing = (not self.coil and self._at_surface(core) and self._raw_move == (0.0, 0.0))
        for name, s in self.cfg["shrines"].items():
            lit = self.buff_left > 0 if name == "ba_thuy" else self.ca_ong_lit
            if lit:
                self.progress[name] = 0
                continue
            if standing and abs(core.pos[0] - s["x"]) <= s["radius"]:
                self.progress[name] += 1
            else:
                self.progress[name] = 0
            if self.progress[name] >= s["stand_ticks"]:
                self.progress[name] = 0
                if name == "ba_thuy":
                    self.buff_left = self.cfg["ba_thuy_buff"]["duration_ticks"]
                    self._say("Đã thắp hương Bà Thủy: bơi nhanh hơn, quái ít tìm tới hơn.")
                else:
                    self.ca_ong_lit = True
                    self._say("Đã thắp hương miếu Cá Ông: nếu gặp nạn, ngài có thể đưa Út Sen về.")

    def _update_serpents(self, core):
        c = self.cfg["serpent"]
        if self.phase_t % c["check_interval_ticks"] == 0 and self.spawned < c["max_per_phase"]:
            chance = c["spawn_chance"]
            if self.buff_left > 0:
                chance *= self.cfg["ba_thuy_buff"]["serpent_spawn_mult"]
            roll = self.rng_monster.random()
            x = self.rng_monster.uniform(*c["x"])
            d = self.rng_monster.uniform(*c["depth"])
            if roll < chance and math.dist(core.pos, (x, d)) >= c["min_distance_from_player"]:
                self.spawned += 1
                self.serpents.append({"id": self.ids.new("MX"), "pos": [x, d], "ttl": c["ttl_ticks"],
                                      "state": "patrol", "vel": [0.0, 0.0], "target": None, "retarget": 0})
        for s in self.serpents:
            s["ttl"] -= 1
        coiling = self.coil["serpent_id"] if self.coil else None
        self.serpents = [s for s in self.serpents if s["ttl"] > 0 or s["id"] == coiling]
        self._move_serpents(core)
        if not self.coil:
            self._pending.clear()
            if self.immunity == 0 and not self._at_surface(core):
                for s in sort_by_id(self.serpents):
                    if math.dist(core.pos, s["pos"]) <= c["coil_radius"]:
                        self._start_coil(s)
                        self._say("Mãng Xà Vương quấn lấy Út Sen! Gõ đúng chuỗi mũi tên để thoát.")
                        break
            return
        coil = self.coil
        for d in self._pending:
            if d == coil["chain"][coil["index"]]:
                coil["index"] += 1
                if coil["index"] == len(coil["chain"]):
                    self.serpents = [s for s in self.serpents if s["id"] != coil["serpent_id"]]
                    self.coil, self.immunity = None, c["immunity_ticks"]
                    self._say("Thoát được rồi! Mãng Xà Vương rút đi.")
                    break
            else:
                coil["index"] = 0
        self._pending.clear()
        if self.coil:
            coil["time_left"] -= 1
            if coil["time_left"] <= 0:
                core.oxygen_ticks = max(0, core.oxygen_ticks - c["squeeze_oxygen_ticks"])
                coil["chain"] = self._new_chain()
                coil["index"], coil["time_left"] = 0, c["chain_time_ticks"]
                self._say("Bị siết thêm một lượt, oxy hao đi.")

    def _move_serpents(self, core):
        """Mãng Xà tuần tra (đi lang thang tới điểm ngẫu nhiên) rồi ĐUỔI người chơi khi lại gần.
        Số liệu (bán kính, tốc độ) trong creative.json là giả định chờ PO duyệt. Cá Sấu lõi không bị đụng tới."""
        c = self.cfg["serpent"]
        hz = float(self.cfg.get("tick_hz", 60))
        coiling = self.coil["serpent_id"] if self.coil else None
        hunt = not self._at_surface(core)
        chase_mult = self.cfg["ba_thuy_buff"].get("serpent_chase_speed_mult", 1.0) if self.buff_left > 0 else 1.0
        for s in sort_by_id(self.serpents):
            if s["id"] == coiling:
                s["vel"] = [0.0, 0.0]
                continue
            dist = math.dist(core.pos, s["pos"])
            state = s.get("state", "patrol")
            if state == "patrol" and hunt and dist <= c["chase_radius"]:
                state = "chase"
            elif state == "chase" and (not hunt or dist > c["lose_radius"]):
                state, s["target"] = "patrol", None
            s["state"] = state
            if state == "chase":
                tx, ty = core.pos
                step = c["chase_speed_per_s"] * chase_mult / hz
            else:
                s["retarget"] = s.get("retarget", 0) - 1
                tg = s.get("target")
                if tg is None or s["retarget"] <= 0 or math.dist(tg, s["pos"]) < 0.5:
                    tg = [self.rng_patrol.uniform(*c["x"]), self.rng_patrol.uniform(*c["depth"])]
                    s["target"], s["retarget"] = tg, c["patrol_retarget_ticks"]
                tx, ty = tg
                step = c["patrol_speed_per_s"] / hz
            dx, dy = tx - s["pos"][0], ty - s["pos"][1]
            gap = math.hypot(dx, dy)
            if gap > 1e-9:
                k = min(step, gap) / gap
                s["vel"] = [dx * k, dy * k]
                s["pos"] = [s["pos"][0] + dx * k, s["pos"][1] + dy * k]
            else:
                s["vel"] = [0.0, 0.0]

    def _new_chain(self):
        c = self.cfg["serpent"]
        n = c["chain_length"]
        if self.buff_left > 0:
            n -= self.cfg["ba_thuy_buff"]["chain_reduction"]
        n = max(c["chain_min"], n)
        return [self.rng_monster.choice(DIRS) for _ in range(n)]

    def _start_coil(self, serpent):
        t = self.cfg["serpent"]["chain_time_ticks"]
        self.coil = {"serpent_id": serpent["id"], "chain": self._new_chain(), "index": 0,
                     "time_left": t, "time_total": t}
        self._pending.clear()

    # --- phước Bà Thủy với Cá Sấu lõi (không sửa luật lõi: chỉ cấp bất tử ngắn khi sắp chạm) ---------
    def _maybe_skip_croc_hit(self, core):
        b = self.cfg["ba_thuy_buff"]
        monsters = getattr(core, "monsters", None)
        if self.buff_left <= 0 or not monsters:
            return
        for m in monsters:
            sp = core.t["monsters"]["species"][m["kind"]]
            gap = math.dist(core.pos, m["pos"])
            if gap > sp["hit_radius"] + b["crocodile_rearm_margin"]:
                self._armed[m["id"]] = True
            elif (self._armed.get(m["id"], True) and m["state"] != "recoil" and core.invuln_ticks == 0
                  and core.pos[1] >= sp["depths"][0] and gap <= sp["hit_radius"] + b["crocodile_approach_margin"]):
                self._armed[m["id"]] = False
                if self.rng_skip.random() < b["crocodile_skip_chance"]:
                    core.invuln_ticks = b["crocodile_skip_invuln_ticks"]
                    self._say("Bà Thủy phù hộ: Cá Sấu lướt qua, không chạm tới.")

    # --- cá Ông ---------------------------------------------------------------------
    def _try_revive(self, core):
        c = self.cfg["ca_ong"]
        if not self.ca_ong_lit or self.revives >= c["max_revives_per_phase"]:
            return False
        self.revives += 1
        self.last_roll = self.rng_dice.randint(1, c["dice_sides"])
        if self.last_roll < c["success_roll"]:
            self._say(f"Xúc xắc ra {self.last_roll}: cá Ông chưa kịp tới.")
            return False
        core.hp = 1
        core.oxygen_ticks = int(core.oxygen_max * c["revive_oxygen_fraction"])
        core.zero_oxy_ticks = 0
        core.pos = [float(v) for v in core.t["dock_pos"]]
        core.vel = [0.0, 0.0]
        core.invuln_ticks = max(core.invuln_ticks, c["revive_invuln_ticks"])
        self.coil = None
        self._say(f"Xúc xắc ra {self.last_roll}: được cá Ông đưa về bến.")
        return True

    # --- snapshot cho client -----------------------------------------------------------
    def snapshot(self, session):
        core = getattr(session.sim, "current_sim", session.sim)
        active = core is self._core and core.phase == "gather"
        shrines = []
        for name, s in self.cfg["shrines"].items():
            lit = self.buff_left > 0 if name == "ba_thuy" else self.ca_ong_lit
            shrines.append({"id": name, "name": s["name"], "x": s["x"], "radius": s["radius"],
                            "stand_ticks": s["stand_ticks"], "progress": self.progress[name], "lit": lit})
        buffs = []
        if self.buff_left > 0:
            buffs.append({"id": "ba_thuy", "name": "Phước Bà Thủy", "left_ticks": self.buff_left,
                          "total_ticks": self.cfg["ba_thuy_buff"]["duration_ticks"],
                          "effects": ["swim_speed", "fewer_monsters"]})
        if self.ca_ong_lit and self.revives == 0:
            buffs.append({"id": "ca_ong", "name": "Cá Ông phù hộ", "left_ticks": None, "total_ticks": None,
                          "effects": ["revive"]})
        return {"enabled": True, "active": active, "tick": self.tick, "shrines": shrines, "buffs": buffs,
                "serpents": [{"id": s["id"], "pos": list(s["pos"]), "state": s.get("state", "patrol"),
                              "vel": list(s.get("vel", (0.0, 0.0)))} for s in sort_by_id(self.serpents)],
                "coil": dict(self.coil, chain=list(self.coil["chain"])) if self.coil else None,
                "immunity_ticks": self.immunity, "last_roll": self.last_roll,
                "messages": list(self.messages)}
