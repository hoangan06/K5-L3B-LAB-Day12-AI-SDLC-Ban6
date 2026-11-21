import json
import unittest

from chonoi.contract import load_contract
from chonoi.inputs import InputState
from chonoi.live import LiveGame
from chonoi.runner import Session


IDLE = InputState((0, 0), {}, set())


class LiveFishTank(unittest.TestCase):
    def setUp(self):
        self.tuning = load_contract()["tuning"]
        self.stock = [{"id": "I1", "kind": "ca_loc", "fresh": 30},
                      {"id": "I2", "kind": "bong_sung", "fresh": 30}]

    def test_live_tank_preserves_fish_and_slows_other_items(self):
        game = LiveGame("quan", self.tuning, {"random_customers": False}, 7, inventory=self.stock)
        for _ in range(60):
            game._tick_once()
        snapshot = json.loads(game.state_json())
        stock = {item["id"]: item["fresh"] for item in snapshot["stock"]}
        self.assertEqual(stock["I1"], 30)
        self.assertAlmostEqual(stock["I2"], 29.875)
        self.assertIn("ca_loc", snapshot["meta"]["freshness"]["tank_fish_kinds"])
        spoiled = [event["data"]["item_id"] for event in game.events if event["name"] == "spoiled"]
        self.assertEqual(spoiled, ["I2"])
        self.assertEqual(self.tuning["freshness"]["quan_decay_per_s"], 0.25)

    def test_gather_slower_and_headless_unchanged(self):
        scenario = {"hold": [{"id": "I1", "kind": "ca_loc", "fresh": 100}],
                    "random_fish": False, "monsters": []}
        game = LiveGame("gather", self.tuning, scenario, 7)
        headless = Session("gather", self.tuning, scenario, 7)
        for _ in range(60):
            game._tick_once()
            headless.step(IDLE)
        self.assertAlmostEqual(game.session.snapshot()["hold"][0]["fresh"], 99.75)
        self.assertAlmostEqual(headless.snapshot()["hold"][0]["fresh"], 99.5)

    def test_restart_restores_fresh_stock(self):
        game = LiveGame("quan", self.tuning, {"random_customers": False}, 7, inventory=self.stock)
        game._tick_once()
        game._reset()
        self.assertEqual([it["fresh"] for it in game.session.snapshot()["stock"]], [30, 30])

    def test_tank_fish_stays_available_and_can_be_cooked(self):
        scenario = {"random_customers": False, "player": {"pos": [2, 8]},
                    "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui"}]}
        game = LiveGame("quan", self.tuning, scenario, 7, inventory=[self.stock[0]])
        game.inputs.set(interact=True)
        game._tick_once()
        names = [event["name"] for event in game.events]
        self.assertIn("cook_started", names)
        self.assertNotIn("spoiled", names)
        self.assertEqual(game.session.sim.stock, [])
