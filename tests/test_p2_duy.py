import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from chonoi.contract import validate_tuning
from chonoi.errors import BadInput
from chonoi.ids import IdAllocator
from chonoi.inventory import validate_items
from chonoi.rng import Streams
from chonoi.scenario import load_scenario
from chonoi.sim.gather_fish import init_fish, update_fish, snapshot_fish
from chonoi.sim.gather_actions import catch_fish, gather_node


def tuning():
    with open("docs/contracts/phase-2-tuning.sample.json", encoding="utf-8-sig") as f:
        return json.load(f)["tuning"]


def sim(seed=1, scenario=None):
    s = SimpleNamespace(t=tuning()["gather"], rng=Streams(seed), ids=IdAllocator(), phase_tick=0)
    init_fish(s, scenario or {})
    return s


class Fish(unittest.TestCase):
    def test_initial_unique_and_deterministic(self):
        a, b = sim(12), sim(12)
        self.assertEqual(snapshot_fish(a), snapshot_fish(b))
        self.assertEqual(len(a.fish), 8)
        self.assertEqual(len({tuple(f["pos"]) for f in a.fish}), 8)
        for tick in range(1, 721):
            a.phase_tick = b.phase_tick = tick
            ea, eb = [], []
            update_fish(a, ea)
            update_fish(b, eb)
            self.assertEqual(ea, eb)
        self.assertEqual(snapshot_fish(a), snapshot_fish(b))
        self.assertEqual(len(a.fish), 10)

    def test_reflect_and_turn_before_move(self):
        s = sim(scenario={"fish": [{"id": "F2", "kind": "ca_loc", "pos": [95.99, 10], "heading_deg": 0}]})
        s.phase_tick = 1
        update_fish(s, [])
        self.assertAlmostEqual(s.fish[0]["pos"][0], 95.985)
        self.assertAlmostEqual(s.fish[0]["heading_deg"], 180)
        s.fish[0].update(pos=[50, 10], age_ticks=119, heading_deg=180)
        expected = Streams(1).get("fish_turn").uniform(0, 360)
        update_fish(s, [])
        self.assertAlmostEqual(s.fish[0]["heading_deg"], expected)

    def test_fixture_static_and_spawn_cap(self):
        fixture = {"random_fish": False, "fish": [{"id": "F1", "kind": "ca_loc", "pos": [30, 10]}]}
        s = sim(scenario=fixture)
        before = snapshot_fish(s)
        s.phase_tick = 360
        update_fish(s, [])
        self.assertEqual(snapshot_fish(s), before)
        s = sim()
        s.t["fish_max"] = len(s.fish)
        s.phase_tick = 360
        events = []
        update_fish(s, events)
        self.assertEqual(events, [])

    def test_no_spawn_candidates_consumes_no_rng(self):
        s = sim(scenario={"fish": []})
        s.t["fish_spawn_clearance"] = 1000
        s.fish = [{"id": "F1", "kind": "ca_loc", "pos": [30, 10], "heading_deg": 0, "age_ticks": 0}]
        s.phase_tick = 360
        update_fish(s, [])
        self.assertNotIn("fish_spawn", s.rng._streams)


class Validation(unittest.TestCase):
    def test_new_kinds_harvest(self):
        t = tuning()["gather"]
        s = SimpleNamespace(t=t, pos=[76, 0], hold=[], catch_cd_ticks=0,
                            nodes=[{"id": "N5", "kind": "keo_neo", "pos": [76, 0], "regrow_ticks": 0}],
                            fish=[{"id": "F1", "kind": "ca_keo", "pos": [76, 24]}])
        s._at_surface = lambda: s.pos[1] <= t["surface_depth"]
        events = []
        gather_node(s, events)
        s.pos = [76, 24]
        catch_fish(s, events)
        self.assertEqual(s.hold, ["keo_neo", "ca_keo", "ca_keo"])
        self.assertEqual([e[0] for e in events], ["gather", "fish_caught"])

    def test_tuning_and_six_kinds(self):
        t = tuning()
        validate_tuning(t)
        self.assertEqual(validate_items({"ca_keo": 2, "keo_neo": 1}), {"ca_keo": 2, "keo_neo": 1})
        del t["gather"]["fish_depths"]["ca_keo"]
        with self.assertRaises(BadInput):
            validate_tuning(t)

    def test_day_scenario_preserved_and_bad_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "scenario.json"
            data = {"day": {"money": 2, "earned": 5}, "quan": {"random_customers": False}}
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertEqual(load_scenario(path, "day", tuning()), data)
            data["quan"]["stock"] = {}
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(BadInput):
                load_scenario(path, "day", tuning())

    def test_invalid_fish_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "scenario.json"
            data = {"gather": {"fish": [{"id": "F1", "kind": "ca_keo", "pos": [20, 2]}]}}
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(BadInput):
                load_scenario(path, "gather", tuning())
