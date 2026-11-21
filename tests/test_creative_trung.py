"""Test phần sáng tạo Gói 2 (chonoi.creative): đền Bà Thủy (buff), Mãng Xà + chuỗi mũi tên, cá Ông hồi sinh.

Các test chạy lớp bọc đúng như live: inp = layer.before(...); session.step(inp); layer.after(...).
"""

import copy
import json
import subprocess
import sys
import unittest

from chonoi.contract import load_contract
from chonoi.creative import CreativeLayer, load_config
from chonoi.creative.layer import move_dirs
from chonoi.inputs import LiveInputs
from chonoi.live import LIVE_BUTTONS, LiveGame
from chonoi.runner import Session
from helpers import ROOT

TUNING = load_contract()["tuning"]


def make(scenario=None, cfg=None, seed=1, mode="gather"):
    session = Session(mode, TUNING, scenario or {}, seed)
    layer = CreativeLayer(seed, cfg or load_config())
    inputs = LiveInputs(buttons=LIVE_BUTTONS)
    layer.before(session, inputs.advance())  # nối vào phiên gather (bind) mà chưa bước
    return session, layer, inputs


def drive(session, layer, inputs, n=1, move=None, **buttons):
    if move is not None:
        inputs.set(move, **buttons)
        layer.note_move(move)
    for _ in range(n):
        inp = layer.before(session, inputs.advance())
        session.step(inp)
        layer.after(session)


def tap(session, layer, inputs, move):
    drive(session, layer, inputs, 1, move=move)
    drive(session, layer, inputs, 1, move=(0.0, 0.0))


def light_ba_thuy(session, layer, inputs):
    drive(session, layer, inputs, layer.cfg["shrines"]["ba_thuy"]["stand_ticks"] + 1, move=(0.0, 0.0))


class MoveDirsTest(unittest.TestCase):
    def test_directions(self):
        self.assertEqual(move_dirs((0, -1)), {"up"})
        self.assertEqual(move_dirs((1, 1)), {"right", "down"})
        self.assertEqual(move_dirs((0.2, 0.0)), set())


class ShrineAndBuffTest(unittest.TestCase):
    def setUp(self):
        self.scn = {"player": {"pos": [36.0, 0.0]}}

    def test_standing_lights_incense_and_costs_time_not_money(self):
        s, layer, inp = make(self.scn)
        money, left = s.sim.money, s.sim.time_left_ticks
        light_ba_thuy(s, layer, inp)
        self.assertGreater(layer.buff_left, 0)
        self.assertEqual(s.sim.money, money)
        self.assertEqual(left - s.sim.time_left_ticks, 181)  # đồng hồ ca sáng vẫn chạy

    def test_moving_resets_progress(self):
        s, layer, inp = make(self.scn)
        drive(s, layer, inp, 100, move=(0.0, 0.0))
        drive(s, layer, inp, 1, move=(1.0, 0.0))
        self.assertEqual(layer.progress["ba_thuy"], 0)

    def test_buff_speeds_up_swimming(self):
        def displacement(buff):
            s, layer, inp = make({"player": {"pos": [10.0, 0.0]}})
            layer.buff_left = 10000 if buff else 0
            x0 = s.sim.pos[0]
            drive(s, layer, inp, 60, move=(1.0, 0.0))
            return s.sim.pos[0] - x0
        base, fast = displacement(False), displacement(True)
        self.assertAlmostEqual(fast / base, load_config()["ba_thuy_buff"]["swim_speed_mult"], places=2)

    def test_buff_expires_and_shows_remaining(self):
        cfg = copy.deepcopy(load_config())
        cfg["ba_thuy_buff"]["duration_ticks"] = 30
        s, layer, inp = make(self.scn, cfg)
        light_ba_thuy(s, layer, inp)
        snap = layer.snapshot(s)
        self.assertEqual(snap["buffs"][0]["id"], "ba_thuy")
        self.assertEqual(snap["buffs"][0]["left_ticks"], 30 - 1)  # đã chạy 1 tick sau khi thắp
        drive(s, layer, inp, 40, move=(0.0, 0.0))
        self.assertEqual(layer.buff_left, 0)
        self.assertEqual(layer.snapshot(s)["buffs"], [])

    def test_buff_cuts_serpent_spawns(self):
        cfg = copy.deepcopy(load_config())
        cfg["serpent"].update(check_interval_ticks=1, spawn_chance=1.0, max_per_phase=5,
                              min_distance_from_player=0, ttl_ticks=10**6)
        cfg["ba_thuy_buff"]["serpent_spawn_mult"] = 0.0
        s, layer, inp = make({"player": {"pos": [10.0, 0.0]}}, cfg)
        drive(s, layer, inp, 5, move=(0.0, 0.0))
        self.assertEqual(len(layer.serpents), 5)  # không buff: lần nào cũng ra
        s, layer, inp = make({"player": {"pos": [10.0, 0.0]}}, cfg)
        layer.buff_left = 10**6
        drive(s, layer, inp, 5, move=(0.0, 0.0))
        self.assertEqual(layer.serpents, [])

    def test_buff_can_skip_crocodile_hit(self):
        cfg = copy.deepcopy(load_config())
        cfg["ba_thuy_buff"]["crocodile_skip_chance"] = 1.0
        scn = {"player": {"pos": [60.0, 22.5]}}  # sát Cá Sấu M1 (60,24), sâu hơn 10

        def hp_after(buff):
            s, layer, inp = make(scn, cfg)
            layer.buff_left = 10000 if buff else 0
            drive(s, layer, inp, 3, move=(0.0, 0.0))
            return s.sim.hp
        self.assertEqual(hp_after(False), TUNING["gather"]["hp_max"] - 1)  # đối chứng: lõi vẫn trúng
        self.assertEqual(hp_after(True), TUNING["gather"]["hp_max"])


class SerpentChaseTest(unittest.TestCase):
    def one(self, ppos, spos, **kw):
        cfg = copy.deepcopy(load_config())
        cfg["serpent"].update(check_interval_ticks=10**9, **kw)  # không spawn thêm: chỉ xét con thả tay
        s, layer, inp = make({"player": {"pos": list(ppos)}}, cfg)
        layer.serpents.append({"id": "MX1", "pos": list(spos), "ttl": 10**6, "state": "patrol",
                               "vel": [0.0, 0.0], "target": None, "retarget": 0})
        return s, layer, inp

    def test_patrols_when_player_far_and_is_deterministic(self):
        def run():
            s, layer, inp = self.one((5.0, 12.0), (80.0, 15.0))
            drive(s, layer, inp, 300, move=(0.0, 0.0))
            return layer.serpents[0]
        a, b = run(), run()
        self.assertEqual(a["state"], "patrol")
        self.assertNotEqual(a["pos"], [80.0, 15.0])  # có bơi lang thang
        self.assertEqual(a["pos"], b["pos"])  # cùng seed, cùng đường tuần tra

    def test_chases_when_player_near(self):
        s, layer, inp = self.one((30.0, 12.0), (38.0, 12.0))
        d0 = 8.0
        drive(s, layer, inp, 30, move=(0.0, 0.0))
        m = layer.serpents[0]
        self.assertEqual(m["state"], "chase")
        self.assertLess(abs(m["pos"][0] - 30.0), d0)  # đang áp sát người
        drive(s, layer, inp, 400, move=(0.0, 0.0))
        self.assertIsNotNone(layer.coil)  # chạm thì quấn (cơ chế chuỗi mũi tên có sẵn)

    def test_chase_slower_than_swimming_and_gives_up(self):
        s, layer, inp = self.one((70.0, 12.0), (78.0, 12.0))
        drive(s, layer, inp, 600, move=(-1.0, 0.0))  # bơi thẳng ra xa với tốc độ bơi (4 > 3,2)
        self.assertIsNone(layer.coil)
        self.assertEqual(layer.serpents[0]["state"], "patrol")

    def test_no_chase_when_player_at_surface(self):
        s, layer, inp = self.one((30.0, 0.0), (35.0, 8.0))
        drive(s, layer, inp, 20, move=(0.0, 0.0))
        self.assertEqual(layer.serpents[0]["state"], "patrol")

    def test_snapshot_exposes_state_and_velocity(self):
        s, layer, inp = self.one((30.0, 12.0), (38.0, 12.0))
        drive(s, layer, inp, 5, move=(0.0, 0.0))
        m = layer.snapshot(s)["serpents"][0]
        self.assertEqual(m["state"], "chase")
        self.assertLess(m["vel"][0], 0)  # đầu quay về phía người (bên trái)


class SerpentTest(unittest.TestCase):
    def coiled(self, buff=False):
        s, layer, inp = make({"player": {"pos": [30.0, 12.0]}})
        layer.buff_left = 10000 if buff else 0
        layer.serpents.append({"id": "MX1", "pos": [30.0, 12.0], "ttl": 10**6})
        drive(s, layer, inp, 1, move=(0.0, 0.0))
        return s, layer, inp

    def test_coil_blocks_swimming_but_oxygen_keeps_draining(self):
        s, layer, inp = self.coiled()
        self.assertIsNotNone(layer.coil)
        x, oxy = s.sim.pos[0], s.sim.oxygen_ticks
        drive(s, layer, inp, 30, move=(1.0, 0.0))
        self.assertAlmostEqual(s.sim.pos[0], x, places=1)
        self.assertEqual(s.sim.oxygen_ticks, oxy - 30)
        self.assertEqual(s.sim.hp, TUNING["gather"]["hp_max"])  # không trừ Máu trực tiếp

    def test_chain_escape_and_immunity(self):
        s, layer, inp = self.coiled()
        self.assertEqual(len(layer.coil["chain"]), 6)
        for d in list(layer.coil["chain"]):
            move = {"up": (0.0, -1.0), "down": (0.0, 1.0), "left": (-1.0, 0.0), "right": (1.0, 0.0)}[d]
            tap(s, layer, inp, move)
        self.assertIsNone(layer.coil)
        self.assertEqual(layer.serpents, [])
        self.assertGreater(layer.immunity, 0)
        drive(s, layer, inp, 3, move=(0.0, 0.0))
        self.assertIsNone(layer.coil)  # 2 giây không bị quấn lại

    def test_wrong_key_restarts_chain(self):
        s, layer, inp = self.coiled()
        first = layer.coil["chain"][0]
        right = {"up": (0.0, -1.0), "down": (0.0, 1.0), "left": (-1.0, 0.0), "right": (1.0, 0.0)}
        tap(s, layer, inp, right[first])
        self.assertEqual(layer.coil["index"], 1)
        wrong = next(d for d in right if d != layer.coil["chain"][1])
        tap(s, layer, inp, right[wrong])
        self.assertEqual(layer.coil["index"], 0)

    def test_timeout_squeezes_and_regenerates_chain(self):
        s, layer, inp = self.coiled()
        oxy = s.sim.oxygen_ticks
        t = layer.cfg["serpent"]["chain_time_ticks"]
        drive(s, layer, inp, t, move=(0.0, 0.0))
        squeeze = layer.cfg["serpent"]["squeeze_oxygen_ticks"]
        self.assertEqual(s.sim.oxygen_ticks, oxy - t - squeeze)
        self.assertEqual(layer.coil["time_left"], t)

    def test_luck_shortens_chain_by_one(self):
        _, layer, _ = self.coiled(buff=True)
        self.assertEqual(len(layer.coil["chain"]), 5)

    def test_paused_layer_does_not_advance(self):
        s, layer, inp = self.coiled()
        left = layer.coil["time_left"]
        inp.set(None, pause=True)
        drive(s, layer, inp, 1)
        inp.set(None, pause=False)
        self.assertTrue(s.paused)
        drive(s, layer, inp, 20)
        self.assertEqual(layer.coil["time_left"], left)


class CaOngTest(unittest.TestCase):
    def doomed(self, lit, success_roll):
        cfg = copy.deepcopy(load_config())
        cfg["ca_ong"]["success_roll"] = success_roll
        s, layer, inp = make({"player": {"pos": [20.0, 15.0], "hp": 1, "oxygen_ticks": 0, "zero_oxy_ticks": 59}}, cfg)
        layer.ca_ong_lit = lit
        drive(s, layer, inp, 1, move=(0.0, 0.0))
        return s, layer

    def test_control_without_blessing_faints(self):
        s, _ = self.doomed(False, 1)
        self.assertTrue(s.done)
        self.assertEqual(s.sim.reason, "fainted")

    def test_blessed_dice_success_revives_with_hold_kept(self):
        cfg = copy.deepcopy(load_config())
        cfg["ca_ong"]["success_roll"] = 1
        s, layer, inp = make({"player": {"pos": [20.0, 15.0], "hp": 1, "oxygen_ticks": 0, "zero_oxy_ticks": 59},
                              "hold": [{"id": "I1", "kind": "ca_loc", "fresh": 90}, {"id": "I2", "kind": "ca_linh", "fresh": 80}]}, cfg)
        layer.ca_ong_lit = True
        drive(s, layer, inp, 1, move=(0.0, 0.0))
        self.assertFalse(s.done)
        self.assertEqual(s.sim.hp, 1)
        self.assertEqual(s.sim.pos, [float(v) for v in TUNING["gather"]["dock_pos"]])
        self.assertEqual(len(s.sim.hold), 2)
        self.assertGreater(s.sim.oxygen_ticks, 0)

    def test_blessed_dice_failure_still_faints_once(self):
        s, layer = self.doomed(True, 7)  # xúc xắc 6 mặt không thể ra 7
        self.assertTrue(s.done)
        self.assertEqual(layer.revives, 1)

    def test_hold_as_dicts_is_tolerated(self):
        s, layer, inp = make({"player": {"pos": [36.0, 0.0]}, "hold": [{"id": "I1", "kind": "ca_loc", "fresh": 90}]})
        drive(s, layer, inp, 5, move=(0.0, 0.0))
        json.dumps(layer.snapshot(s))  # layer không đọc/ghi hold, nên hợp mọi dạng


class DeterminismAndLiveTest(unittest.TestCase):
    def run_layer(self, seed):
        s, layer, inp = make({"player": {"pos": [10.0, 0.0]}}, seed=seed)
        out = []
        for i in range(1500):
            drive(s, layer, inp, 1, move=(0.0, 0.0))
            out.append(json.dumps(layer.snapshot(s), sort_keys=True))
        return out

    def test_same_seed_same_creative_snapshots(self):
        self.assertEqual(self.run_layer(7), self.run_layer(7))

    def test_live_flag_off_has_no_creative_field(self):
        for creative, expect in ((False, False), (True, True)):
            game = LiveGame("gather", TUNING, {}, 1, creative=creative)
            self.assertEqual("creative" in json.loads(game.state_json()), expect)

    def test_live_day_mode_creative_snapshot(self):
        game = LiveGame("day", TUNING, {}, 1, days=1, creative=True)
        self.assertIn("creative", json.loads(game.state_json()))

    def test_headless_does_not_load_creative(self):
        code = "import sys, chonoi.headless; sys.exit(1 if any(m.startswith('chonoi.creative') for m in sys.modules) else 0)"
        self.assertEqual(subprocess.run([sys.executable, "-c", code], cwd=ROOT).returncode, 0)


if __name__ == "__main__":
    unittest.main()
