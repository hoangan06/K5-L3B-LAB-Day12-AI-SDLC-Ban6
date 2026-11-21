import unittest
from copy import deepcopy
from unittest.mock import patch
from types import SimpleNamespace

from chonoi.contract import load_contract
from chonoi.errors import BadInput
from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.rng import Streams
from chonoi.runner import Session
from chonoi.sim.day import DaySim
from chonoi.sim.quan import QuanSim
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

    def test_bot_serves_real_customer(self):
        session = Session("day", self.tuning, {}, 7, days=1, soak=True)
        bot = Bot()
        names = set()
        while not session.done:
            names.update(event["name"] for event in session.step(bot.input(session.sim)))
        self.assertTrue({"gather", "gather_end", "customer_arrived", "cook_started",
                         "dish_picked", "served", "paid", "shop_end"} <= names)
        self.assertGreater(session.sim.earned, 0)

    def test_bot_buys_only_affordable_next_level(self):
        shop = SimpleNamespace(upgrades={"hp": 0, "oxygen": 0}, money=200,
                               t=self.tuning["shop"])
        inp = Bot().input(SimpleNamespace(phase="shop", current_sim=shop))
        self.assertEqual(inp.buy, "oxygen")
        self.assertTrue(inp.pressed("shop_done"))

    def test_bot_serves_each_menu_dish_from_real_stock(self):
        """Exercise each recipe through the real reservation/cooking/serving pipeline."""
        for dish_id, recipe_data in self.tuning["menu"].items():
            with self.subTest(dish=dish_id):
                stock = []
                for kind, amount in recipe_data["recipe"].items():
                    for _ in range(amount):
                        stock.append({"id": f"I{len(stock) + 1}", "kind": kind, "fresh": 100})
                scenario = {"random_customers": False,
                            "customers": [{"id": "C1", "table_id": "T1", "dish_id": dish_id}]}
                quan = QuanSim(self.tuning, scenario, Streams(7), IdAllocator(), inventory=stock)
                bot = Bot()
                state = SimpleNamespace(phase="quan", current_sim=quan)
                seen = []
                for _ in range(6000):
                    seen.extend(quan.step(bot.input(state)))
                    if any(name == "paid" for name, _ in seen):
                        break
                names = [name for name, _ in seen]
                for event in ("cook_started", "dish_ready", "dish_picked", "served", "paid"):
                    self.assertIn(event, names, (dish_id, names))
                started = next(data for name, data in seen if name == "cook_started")
                self.assertEqual(started["dish_id"], dish_id)
                used = {}
                for item in started["items"]:
                    used[item["kind"]] = used.get(item["kind"], 0) + 1
                self.assertEqual(used, recipe_data["recipe"])
                self.assertGreater(quan.earned, 0)
