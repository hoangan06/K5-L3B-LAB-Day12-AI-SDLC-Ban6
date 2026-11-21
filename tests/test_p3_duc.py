import json
import unittest
from pathlib import Path

from chonoi.live import LiveGame


class FreshnessHUD(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / "docs/contracts/phase-2-tuning.sample.json"
        self.tuning = json.loads(path.read_text(encoding="utf-8-sig"))["tuning"]

    def test_live_exposes_freshness_and_item_ids_for_ui(self):
        self.tuning["freshness"] = {
            "initial": 100, "gather_decay_per_s": 0.5, "quan_decay_per_s": 0.25, "spoiled_below": 30,
        }
        stock = [{"id": "I1", "kind": "ca_loc", "fresh": 30}, {"id": "I2", "kind": "ca_loc", "fresh": 29.99}]
        customer = {"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "reserved": ["I1"]}
        game = LiveGame("quan", self.tuning, {"customers": [customer], "random_customers": False}, 1, inventory=stock)
        state = json.loads(game.state_json())
        self.assertEqual(state["meta"]["freshness"]["spoiled_below"], 30)
        self.assertEqual(state["stock"], stock)
        self.assertEqual(state["customers"][0]["reserved"], ["I1"])
        self.assertNotIn("freshness", self.tuning["quan"])

    def test_legacy_stock_remains_a_count_map(self):
        game = LiveGame("quan", self.tuning, {}, 1, inventory={"ca_loc": 2})
        state = json.loads(game.state_json())
        self.assertEqual(state["stock"], {"ca_loc": 2})
        self.assertNotIn("freshness", state["meta"])
