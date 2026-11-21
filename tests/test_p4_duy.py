import unittest
from copy import deepcopy
from unittest.mock import patch

from chonoi.contract import load_contract
from chonoi.errors import BadInput
from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.rng import Streams
from chonoi.sim.day import DaySim
from chonoi.soak import Bot, run_soak


class SoakDay(unittest.TestCase):
    def setUp(self):
        self.tuning = load_contract()["tuning"]

    def test_validation_preserves_standard_five_day_limit(self):
        for days, soak in [(6, False), (True, True), (0, True), (10, "yes")]:
            with self.subTest(days=days, soak=soak), self.assertRaises(BadInput):
                DaySim(self.tuning, {}, Streams(1), IdAllocator(), days=days, soak=soak)

    def test_ten_days_plans_ids_and_results(self):
        item = {"id": "I42", "kind": "ca_loc", "fresh": 100}
        sc = {"day": {"money": 7, "earned": 10},
              "gather": {"hold": [item], "random_fish": False, "monsters": [], "time_left_ticks": 1},
              "quan": {"random_customers": False, "time_left_ticks": 1}}
        sim = DaySim(self.tuning, sc, Streams(7), IdAllocator(), days=10, soak=True)
        plans, ids = [], []
        for day in range(1, 11):
            self.assertEqual(sim.day, day)
            plans.append(dict(sim.day_plan["dishes"]))
            ids.append(sim.current_sim.hold[0]["id"])
            sim.step(InputState((0, 0), {}, {"interact"}))
            self.assertEqual(sim.phase, "quan")
            sim.step(InputState((0, 0), {}, set()))
            self.assertEqual(sim.phase, "shop")
            self.assertEqual(len(sim.completed_results), day - 1)
            sim.step(InputState((0, 0), {}, {"shop_done"}))
        self.assertTrue(sim.done)
        self.assertEqual(sim.days_completed, 10)
        self.assertEqual(plans[:5], plans[5:])
        self.assertEqual(len(set(ids)), 10)
        self.assertEqual(ids[0], "I42")
        self.assertEqual([r["day"] for r in sim.completed_results], list(range(1, 11)))
        self.assertTrue(all(r["earned"] == 10 and r["score"] == 10 + self.tuning["score"]["reputation_multiplier"] * 3 for r in sim.completed_results))
        self.assertEqual(sim.money, 7)

    def test_bot_edges_and_adapter_absence(self):
        sim = DaySim(self.tuning, {}, Streams(7), IdAllocator())
        bot = Bot()
        inp = bot.input(sim)
        self.assertEqual(inp.move, (1.0, 0.0))
        self.assertFalse(inp.pressed("interact"))
        with self.assertRaises(BadInput):
            run_soak(self.tuning, 7, 0)

    def test_harness_one_session_and_deterministic_gameplay(self):
        tuning = deepcopy(self.tuning)
        # Shorten a private test fixture only; the CLI uses the unmodified manifest.
        tuning["gather"]["duration_s"] = 0.1
        tuning["quan"]["duration_s"] = 0.1
        tuning["shop"]["max_ticks"] = 2
        class SessionAdapter:
            created = 0
            def __init__(self, mode, config, scenario, seed, *, days, soak):
                SessionAdapter.created += 1
                self.sim = DaySim(config, scenario, Streams(seed), IdAllocator(), days=days, soak=soak)
            @property
            def done(self):
                return self.sim.done
            def step(self, inp):
                return self.sim.step(inp)
        with patch("chonoi.soak.Session", SessionAdapter):
            a, b = run_soak(tuning, 7, 10), run_soak(tuning, 7, 10)
        self.assertEqual(SessionAdapter.created, 2)
        for result in (a, b):
            result.pop("duration_s")
            self.assertEqual(result["days_completed"], 10)
            self.assertEqual(result["crashes"], 0)
        self.assertEqual(a, b)
