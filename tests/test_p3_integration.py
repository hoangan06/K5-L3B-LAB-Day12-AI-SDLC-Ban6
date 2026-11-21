"""Test tích hợp Phase 3 (TICKET-03, Test Contract v1.2): giỏ cá thể, file kho, bàn giao trong day.

Chạy: PYTHONPATH=tests:. python3 -m unittest tests.test_p3_integration -v
"""

import json
import unittest
from fractions import Fraction

from chonoi.contract import load_contract
from chonoi.errors import BadInput
from chonoi.ids import IdAllocator
from chonoi.inputs import BUTTONS_V11, InputPlayer
from chonoi.items import exact
from chonoi.rng import Streams
from chonoi.sim.day import DaySim
from chonoi.sim.gather import GatherSim
from helpers import Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json

TUNING = load_contract()["tuning"]
IDLE = InputPlayer([], BUTTONS_V11)


def item(i, kind, fresh):
    return {"id": i, "kind": kind, "fresh": fresh}


def gather(scenario, tuning=TUNING):
    return GatherSim(tuning, {"random_fish": False, "monsters": [], **scenario}, Streams(1), IdAllocator())


class Manifest(unittest.TestCase):
    def test_runtime_is_v12_with_ticket_values(self):
        with open("game.contract.json", encoding="utf-8") as f:
            c = json.load(f)
        # TICKET-04 giữ gameplay/kho v1.2 khi nâng manifest lên v1.3.
        self.assertIn(c["contract_version"], ("1.2", "1.3"))
        self.assertEqual(c["tuning"]["freshness"], {"initial": 100, "gather_decay_per_s": 0.5,
                                                    "quan_decay_per_s": 0.25, "spoiled_below": 30})

    def test_exact_restores_240th_units(self):
        for k in (7200, 7201, 7199, 23999):
            self.assertEqual(exact(float(Fraction(k, 240))), Fraction(k, 240))
        self.assertEqual(exact(97.5), Fraction(195, 2))


class GatherFresh(unittest.TestCase):
    def test_ticket_threshold_example(self):
        # TICKET-03: hold I1 fresh 30, một bước không input → spoiled tick 1, location hold.
        sim = gather({"hold": [item("I1", "ca_linh", 30)]})
        ev = sim.step(IDLE.advance(0))
        self.assertEqual([d for n, d in ev if n == "spoiled"],
                         [{"item_id": "I1", "kind": "ca_linh", "location": "hold"}])
        self.assertFalse([1 for n, _ in sim.step(IDLE.advance(1)) if n == "spoiled"])

    def test_gather_decay_half_per_second_and_order_by_id(self):
        sim = gather({"hold": [item("I10", "ca_loc", 30.004), item("I2", "ca_loc", 30.004)]})
        ev = sim.step(IDLE.advance(0))
        self.assertEqual([d["item_id"] for n, d in ev if n == "spoiled"], ["I2", "I10"])
        sim = gather({"hold": [item("I1", "ca_loc", 100)]})
        for t in range(120):
            sim.step(IDLE.advance(t))
        self.assertEqual(sim.snapshot()["hold"], [item("I1", "ca_loc", 99.0)])

    def test_new_item_fresh_100_new_id_and_decays_from_next_step(self):
        t = TUNING["gather"]
        node = dict(t["nodes"][0], regrow_ticks=0)
        sim = gather({"hold": [item("I7", "ca_loc", 80)], "nodes": [node],
                      "player": {"pos": list(node["pos"])}})
        press = InputPlayer([{"tick": 0, "interact": True}], BUTTONS_V11)
        sim.step(press.advance(0))
        hold = sim.snapshot()["hold"]
        self.assertEqual([h["id"] for h in hold], ["I7"] + [f"I{8 + i}" for i in range(t["node_yield"])])
        self.assertEqual({h["fresh"] for h in hold[1:]}, {100.0})
        sim.step(IDLE.advance(1))
        self.assertAlmostEqual(sim.snapshot()["hold"][1]["fresh"], 100 - 0.5 / 60, delta=1e-9)

    def test_faint_lost_is_items_lifo_and_inventory_empty(self):
        sim = gather({"hold": [item("I1", "ca_loc", 90), item("I2", "bong_sung", 80)],
                      "player": {"pos": [50, 10], "oxygen_ticks": 0, "zero_oxy_ticks": 59, "hp": 1}})
        ev = dict(sim.step(IDLE.advance(0)))
        self.assertEqual([x["id"] for x in ev["faint"]["lost"]], ["I2", "I1"])
        self.assertEqual(ev["gather_end"]["inventory"], {"items": []})

    def test_hold_capacity_counts_items(self):
        cap = TUNING["gather"]["hold_capacity"]
        with self.assertRaises(BadInput):
            from chonoi.scenario import _validate_gather
            _validate_gather({"hold": [item(f"I{i}", "ca_loc", 90) for i in range(cap + 1)]}, TUNING)


class FileHandoff(unittest.TestCase):
    def run_quan(self, w, inv_obj, ticks="0"):
        inv = write_json(w.path("inv.json"), inv_obj)
        out = w.path("q.jsonl")
        return run_headless("--mode", "quan", "--seed", "1", "--ticks", ticks, "--inventory", inv, "--out", out), out

    def test_count_file_and_bad_schema_exit_2(self):
        with Workdir() as w:
            for bad in ({"items": {"ca_loc": 1}}, {"items": [item("I1", "ca_loc", 90), item("I1", "ca_loc", 90)]},
                        {"items": [item("I1", "ca_ro", 90)]}, {"items": [item("I1", "ca_loc", 100.5)]},
                        {"items": [item("", "ca_loc", 90)]}, {"items": [{"id": "I1", "kind": "ca_loc"}]}):
                (code, _), out = self.run_quan(w, bad)
                self.assertEqual(code, 2, bad)

    def test_threshold_branch_survives_file_roundtrip(self):
        # 30 + 1/120 + 1/240 sau 1 tick gather còn 30 + 1/240; quán tick 1 về đúng 30 (chưa ươn), tick 2 ươn.
        start = float(30 + Fraction(1, 120) + Fraction(1, 240))
        with Workdir() as w:
            sc = write_json(w.path("g.json"), {"gather": {"hold": [item("I1", "ca_loc", start)],
                                                          "random_fish": False, "monsters": []}})
            inp = write_json(w.path("in.json"), frames({"tick": 0, "interact": True}))
            inv = w.path("inv.json")
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "1", "--scenario", sc,
                                     "--inputs", inp, "--inventory-out", inv, "--out", w.path("g.jsonl"))
            self.assertEqual(code, 0, err)
            out = w.path("q.jsonl")
            code, err = run_headless("--mode", "quan", "--seed", "1", "--ticks", "3", "--inventory", inv,
                                     "--out", out)
            self.assertEqual(code, 0, err)
            self.assertEqual([r["tick"] for r in events(read_jsonl(out), "spoiled")], [2])
            self.assertEqual(snapshots(read_jsonl(out))[0]["stock"][0]["id"], "I1")


class DayHandoff(unittest.TestCase):
    def day(self, scenario):
        return DaySim(TUNING, scenario, Streams(1), IdAllocator(), days=2)

    def test_same_tick_handoff_no_extra_decay_and_ids_continue(self):
        sim = self.day({"gather": {"time_left_ticks": 1, "random_fish": False, "monsters": [],
                                   "hold": [item("I1", "ca_loc", 90), item("I2", "bong_sung", 70)]},
                        "quan": {"time_left_ticks": 1, "random_customers": False}})
        sim.step(IDLE.advance(0))  # gather: hao 1 tick rồi hết giờ, bàn giao cùng tick
        self.assertEqual(sim.phase, "quan")
        stock = sim.snapshot()["stock"]
        self.assertEqual([s["id"] for s in stock], ["I1", "I2"])
        self.assertAlmostEqual(stock[0]["fresh"], 90 - 0.5 / 60, delta=1e-9)
        sim.step(IDLE.advance(1))  # quán: hao 1 tick rồi đóng ca → Shop
        self.assertEqual(sim.phase, "shop")
        shop = sim.snapshot()["stock"]
        self.assertAlmostEqual(shop[0]["fresh"], 90 - 0.5 / 60 - 0.25 / 60, delta=1e-9)
        sim.step(InputPlayer([{"tick": 2, "shop_done": True}], BUTTONS_V11).advance(2))
        self.assertEqual(sim.day, 2)
        # Ngày 2: mẫu hold cấp id mới theo thứ tự mảng, giữ kind/fresh ban đầu
        hold = sim.snapshot()["hold"]
        self.assertEqual([(h["id"], h["kind"], h["fresh"]) for h in hold],
                         [("I3", "ca_loc", 90.0), ("I4", "bong_sung", 70.0)])

    def test_headless_day_five_days_v12(self):
        with Workdir() as w:
            out = w.path("d.jsonl")
            code, err = run_headless("--mode", "day", "--days", "5", "--seed", "1", "--ticks", "111000",
                                     "--snapshot-every", "6000", "--out", out)
            self.assertEqual(code, 0, err)
            end = read_jsonl(out)[-1]
            self.assertEqual((end["reason"], end["days_completed"]), ("days_complete", 5))


if __name__ == "__main__":
    unittest.main()
