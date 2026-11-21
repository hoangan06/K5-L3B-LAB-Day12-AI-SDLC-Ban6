"""Cá Sấu và gather thật với tuning mẫu P2, chưa phụ thuộc cá của Duy."""

from copy import deepcopy
import json
import math
from pathlib import Path
import unittest

from chonoi.errors import BadInput
from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.rng import Streams
from chonoi.sim.gather import GatherSim
from chonoi.sim.gather_monsters import update_monsters

ROOT = Path(__file__).resolve().parents[1]


def monster(ident="M1", pos=None, **values):
    pos = list(pos or [60, 24])
    return {"id": ident, "kind": "ca_sau", "pos": pos,
            "waypoints": [list(pos), [min(100, pos[0] + 4), pos[1]]], **values}


class Monsters(unittest.TestCase):
    def setUp(self):
        self.tuning = json.loads((ROOT / "docs/contracts/phase-2-tuning.sample.json").read_text(encoding="utf-8-sig"))["tuning"]

    def sim(self, *, player=None, monsters=None, day=1, hold=None, tuning=None, **fields):
        scenario = {"random_fish": False, "fish": [], "nodes": [],
                    "player": {"pos": [60, 24], **(player or {})}, "hold": hold or [], **fields}
        if monsters is not None:
            scenario["monsters"] = monsters
        context = {"day": day, "money": 200, "earned": 300, "reputation": 3.2,
                   "oxygen_max_ticks": 1800, "hp_max": 3}
        return GatherSim(tuning or self.tuning, scenario, Streams(7), IdAllocator(), context=context)

    def step(self, sim, move=(0, 0), edges=()):
        return sim.step(InputState(move, {}, set(edges)))

    def test_defaults_by_day_and_explicit_empty_override(self):
        self.assertEqual([m["id"] for m in self.sim(day=1).monsters], ["M1"])
        self.assertEqual([m["id"] for m in self.sim(day=3).monsters], ["M1", "M2"])
        self.assertEqual(self.sim(monsters=[]).monsters, [])

    def test_patrol_speed_and_waypoint_does_not_spend_leftover(self):
        sim = self.sim(player={"pos": [2, 0]}, monsters=[monster()])
        self.step(sim)
        self.assertAlmostEqual(sim.monsters[0]["pos"][0], 60 + 1 / 60)
        sim.monsters[0]["pos"] = [63.999, 24]
        self.step(sim)
        self.assertEqual(sim.monsters[0]["pos"], [64, 24])
        self.assertEqual(sim.monsters[0]["target_idx"], 0)
        self.step(sim)
        self.assertAlmostEqual(sim.monsters[0]["pos"][0], 64 - 1 / 60)

    def test_detect_at_radius_then_chase_speed(self):
        sim = self.sim(player={"pos": [70, 24]}, monsters=[monster()])
        self.step(sim)
        self.assertEqual(sim.monsters[0]["state"], "chase")
        self.assertAlmostEqual(sim.monsters[0]["pos"][0], 60.05)

    def test_chase_exit_threshold_and_shallow_player(self):
        for pos, expected in (([76, 24], "chase"), ([76.01, 24], "patrol"), ([60, 9.99], "patrol")):
            with self.subTest(pos=pos):
                sim = self.sim(player={"pos": pos}, monsters=[monster(state="chase")])
                self.step(sim)
                self.assertEqual(sim.monsters[0]["state"], expected)

    def test_hit_after_movement_at_radius_boundary(self):
        tuning = deepcopy(self.tuning)
        tuning["gather"]["monsters"]["species"]["ca_sau"]["chase_speed"] = 0
        for distance, hits in ((1.5, 1), (1.50001, 0)):
            with self.subTest(distance=distance):
                sim = self.sim(player={"pos": [60 + distance, 24]}, monsters=[monster()], tuning=tuning)
                events = self.step(sim)
                self.assertEqual(sum(name == "monster_hit" for name, _ in events), hits)

    def test_nearest_then_numeric_id_and_one_hit_per_step(self):
        sim = self.sim(monsters=[monster("M10"), monster("M2")])
        events = self.step(sim)
        self.assertEqual([name for name, _ in events], ["monster_hit"])
        self.assertEqual(events[0][1]["monster_id"], "M2")
        self.assertEqual(sim.hp, 2)
        self.assertEqual(sum(m["state"] == "recoil" for m in sim.monsters), 1)
        sim = self.sim(monsters=[monster("M1", [61, 24]), monster("M9")])
        self.assertEqual(self.step(sim)[0][1]["monster_id"], "M9")

    def test_hit_loses_floor_half_lifo_and_sets_invulnerability(self):
        sim = self.sim(monsters=[monster()], hold=["ca_loc", "bong_sung", "ca_linh", "keo_neo", "ca_keo"])
        events = self.step(sim)
        self.assertEqual(events[0][1]["lost"], ["ca_keo", "keo_neo"])
        self.assertEqual(sim.hold, ["ca_loc", "bong_sung", "ca_linh"])
        self.assertEqual(sim.invuln_ticks, 90)
        self.assertEqual(sim.monsters[0]["state_ticks_left"], 60)

    def test_recoil_starts_next_step_and_last_step_is_still_safe(self):
        sim = self.sim(monsters=[monster()])
        self.step(sim)
        self.assertEqual(sim.monsters[0]["pos"], [60, 24])
        self.assertEqual(sim.monsters[0]["recoil_dir"], [1.0, 0.0])
        self.step(sim)
        self.assertAlmostEqual(sim.monsters[0]["pos"][0], 60 + 2 / 60)
        for _ in range(59):
            self.step(sim)
        self.assertAlmostEqual(sim.monsters[0]["pos"][0], 62)
        self.assertEqual(sim.monsters[0]["state"], "patrol")
        self.assertEqual(sim.monsters[0]["state_ticks_left"], 0)
        self.assertIsNone(sim.monsters[0]["recoil_dir"])
        sim = self.sim(monsters=[monster(state="recoil", state_ticks_left=1, recoil_dir=[1, 0])])
        self.assertEqual(self.step(sim), [])
        self.assertEqual(sim.monsters[0]["state"], "patrol")
        self.assertEqual(self.step(sim)[0][0], "monster_hit")

    def test_invulnerability_expires_exactly_at_hit_tick_plus_90(self):
        sim = self.sim(monsters=[monster()])
        hit_ticks = []
        for tick in range(1, 92):
            sim.pos = list(sim.monsters[0]["pos"])
            if any(name == "monster_hit" for name, _ in self.step(sim)):
                hit_ticks.append(tick)
        self.assertEqual(hit_ticks, [1, 91])

    def test_invulnerable_contact_does_not_start_recoil(self):
        sim = self.sim(player={"invuln_ticks": 2}, monsters=[monster()])
        self.assertEqual(self.step(sim), [])
        self.assertEqual(sim.monsters[0]["state"], "chase")
        self.assertEqual(sim.hp, 3)

    def test_monster_faint_lost_payloads_partition_the_hold(self):
        sim = self.sim(player={"hp": 1}, monsters=[monster()],
                       hold=["ca_loc", "bong_sung", "ca_linh", "ca_keo", "keo_neo"], time_left_ticks=1)
        events = self.step(sim, edges=("catch", "interact"))
        self.assertEqual([name for name, _ in events], ["monster_hit", "faint", "gather_end"])
        self.assertEqual(events[0][1]["lost"], ["keo_neo", "ca_keo"])
        self.assertEqual(events[1][1], {"cause": "monster", "lost": ["ca_linh", "bong_sung", "ca_loc"], "hp": 0})
        self.assertEqual(events[2][1], {"reason": "fainted", "inventory": {"items": {}}})
        self.assertTrue(sim.done)

    def test_choke_bypasses_invulnerability_and_does_not_drop_half(self):
        sim = self.sim(player={"hp": 2, "oxygen_ticks": 0, "zero_oxy_ticks": 59, "invuln_ticks": 50},
                       monsters=[monster()], hold=["ca_loc", "ca_keo"])
        events = self.step(sim)
        self.assertEqual([name for name, _ in events], ["choke"])
        self.assertEqual(sim.hp, 1)
        self.assertEqual(sim.hold, ["ca_loc", "ca_keo"])

    def test_choke_then_hit_can_both_happen_on_same_tick(self):
        sim = self.sim(player={"hp": 2, "oxygen_ticks": 0, "zero_oxy_ticks": 59}, monsters=[monster()])
        events = self.step(sim)
        self.assertEqual([name for name, _ in events], ["choke", "monster_hit", "faint", "gather_end"])

    def test_lethal_choke_stops_before_monsters_move(self):
        sim = self.sim(player={"hp": 1, "oxygen_ticks": 0, "zero_oxy_ticks": 59}, monsters=[monster()])
        events = self.step(sim)
        self.assertEqual([name for name, _ in events], ["choke", "faint", "gather_end"])
        self.assertEqual(sim.monsters[0]["state"], "patrol")

    def test_player_shallower_than_species_depth_cannot_be_hit(self):
        sim = self.sim(player={"pos": [60, 9.99]}, monsters=[monster(pos=[60, 10])])
        self.assertFalse(any(name == "monster_hit" for name, _ in self.step(sim)))

    def test_recoil_clamps_to_map_and_species_depth(self):
        direction = [1 / math.sqrt(2), 1 / math.sqrt(2)]
        sim = self.sim(player={"pos": [2, 0]}, monsters=[monster(pos=[100, 30], state="recoil", state_ticks_left=1, recoil_dir=direction)])
        self.step(sim)
        self.assertEqual(sim.monsters[0]["pos"], [100, 30])

    def test_snapshot_is_sorted_and_detached_from_state(self):
        sim = self.sim(monsters=[monster("M10"), monster("M2")])
        snapshot = sim.snapshot()
        self.assertEqual([m["id"] for m in snapshot["monsters"]], ["M2", "M10"])
        snapshot["monsters"][0]["pos"][0] = 0
        self.assertEqual(sim.monsters[0]["pos"][0], 60)

    def test_context_caps_and_balances_do_not_mutate_tuning(self):
        scenario = {"random_fish": False, "monsters": []}
        context = {"day": 3, "money": 123, "earned": 300, "reputation": 4.2,
                   "oxygen_max_ticks": 3600, "hp_max": 5}
        before = deepcopy(self.tuning)
        sim = GatherSim(self.tuning, scenario, Streams(1), IdAllocator(), context=context)
        self.assertEqual((sim.oxygen_ticks, sim.hp, sim.snapshot()["player"]["hp_max"]), (3600, 5, 5))
        self.assertEqual((sim.money, sim.earned, sim.reputation), (123, 300, 4.2))
        self.assertEqual(self.tuning, before)
        self.assertEqual(sim.phase_tick, 0)
        self.step(sim)
        self.assertEqual(sim.phase_tick, 1)

    def test_invalid_fixtures_raise_bad_input(self):
        cases = [None, "bad", [monster(), monster()],
                 [monster(target_idx=True)], [monster(state="stunned", state_ticks_left=1)],
                 [monster(state="recoil", state_ticks_left=0, recoil_dir=[1, 0])],
                 [monster(state="recoil", state_ticks_left=2, recoil_dir=[2, 0])],
                 [monster(state_ticks_left=1)], [monster(pos=[60, 9])],
                 [monster(waypoints=[[60, 24]])], [monster(unexpected=1)],
                 [monster(pos=[float("nan"), 24])]]
        for fixture in cases:
            with self.subTest(fixture=fixture), self.assertRaises(BadInput):
                scenario = {"random_fish": False, "monsters": fixture}
                GatherSim(self.tuning, scenario, Streams(1), IdAllocator())


if __name__ == "__main__":
    unittest.main()
