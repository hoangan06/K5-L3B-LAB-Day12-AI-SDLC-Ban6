"""Black-box validation of the v1.2 inventory and scenario contract."""
import json
import os
import unittest

from helpers import Workdir, run_headless, write_json


with open("game.contract.json", encoding="utf-8") as f:
    VERSION = json.load(f).get("contract_version")


@unittest.skipUnless(VERSION in ("1.2", "1.3"), "requires integrated runtime and manifest 1.2/1.3")
class InventoryContractV12(unittest.TestCase):
    def test_reject_bad_file_before_output(self):
        item = {"id": "I1", "kind": "ca_linh", "fresh": 100}
        invalid = [
            {"items": {}}, {"items": {"ca_linh": 1}}, {"items": [], "extra": 1},
            {"items": [item, dict(item)]},
            {"items": [{**item, "id": ""}]}, {"items": [{**item, "id": 12}]},
            {"items": [{**item, "kind": "unknown"}]},
            {"items": [{**item, "fresh": -0.01}]}, {"items": [{**item, "fresh": 100.01}]},
            {"items": [{**item, "fresh": True}]}, {"items": [{**item, "fresh": float("nan")}]},
            {"items": [{**item, "fresh": float("inf")}]},
            {"items": [{"id": "I1", "kind": "ca_linh"}]},
            {"items": [{**item, "extra": 1}]},
        ]
        with Workdir() as w:
            for index, data in enumerate(invalid):
                with self.subTest(case=index):
                    inv = write_json(w.path("inventory.json"), data)
                    out = w.path(f"out{index}.jsonl")
                    code, err = run_headless("--mode", "quan", "--seed", "1", "--ticks", "0", "--inventory", inv, "--out", out)
                    self.assertEqual(code, 2, err)
                    self.assertFalse(os.path.exists(out))

    def test_bad_hold_rejected_before_output(self):
        item = {"id": "I1", "kind": "ca_linh", "fresh": 30}
        cases = [[item, dict(item)], [{**item, "id": ""}], [{**item, "fresh": -1}],
                 [{**item, "fresh": True}], [{**item, "kind": "invalid"}], ["ca_linh"]]
        with Workdir() as w:
            for index, hold in enumerate(cases):
                with self.subTest(case=index):
                    sc = write_json(w.path("scenario.json"), {"gather": {"hold": hold}})
                    out = w.path(f"out{index}.jsonl")
                    code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "0", "--scenario", sc, "--out", out)
                    self.assertEqual(code, 2, err)
                    self.assertFalse(os.path.exists(out))

    def test_bad_stock_scenario_rejected_before_output(self):
        item = {"id": "I1", "kind": "ca_linh", "fresh": 100}
        for stock in ([item, dict(item)], [{**item, "id": ""}],
                      [{**item, "fresh": 101}], [{**item, "kind": "invalid"}], {"ca_linh": 1}):
            with self.subTest(stock=stock), Workdir() as w:
                sc = write_json(w.path("scenario.json"), {"quan": {"stock": stock}})
                out = w.path("out.jsonl")
                code, err = run_headless("--mode", "quan", "--seed", "1", "--ticks", "0", "--scenario", sc, "--out", out)
                self.assertEqual(code, 2, err)
                self.assertFalse(os.path.exists(out))

    def test_valid_empty_and_precision_snapshot(self):
        from helpers import read_jsonl, snapshots
        with Workdir() as w:
            for index, items in enumerate(([], [{"id": "I2", "kind": "ca_loc", "fresh": 29.9999},
                                                {"id": "I1", "kind": "ca_linh", "fresh": 30}])):
                inv = write_json(w.path("inventory.json"), {"items": items})
                out = w.path(f"out{index}.jsonl")
                code, err = run_headless("--mode", "quan", "--seed", "1", "--ticks", "0", "--inventory", inv, "--out", out)
                self.assertEqual(code, 0, err)
                self.assertEqual(snapshots(read_jsonl(out))[0]["stock"], sorted(items, key=lambda x: int(x["id"][1:])))
