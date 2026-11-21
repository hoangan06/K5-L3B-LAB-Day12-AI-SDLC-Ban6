"""Test Phase 3 (Trung): kho cá thể và độ tươi ở quán — TICKET-03 §1, Test Contract v1.2.

Tuning = mẫu P2 (docs/contracts/phase-2-tuning.sample.json) + khối freshness theo TICKET-03 (100, 0.5, 0.25, 30).
Chạy: PYTHONPATH=tests:. python3 -m unittest tests.test_p3_trung -v
"""

import copy
import json
import unittest
from pathlib import Path

from chonoi.errors import BadInput
from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.rng import Streams
from chonoi.sim.quan import QuanSim

ROOT = Path(__file__).resolve().parent.parent
with open(ROOT / "docs/contracts/phase-2-tuning.sample.json", encoding="utf-8-sig") as f:
    P2 = json.load(f)["tuning"]
TUNING = dict(P2, freshness={"initial": 100, "gather_decay_per_s": 0.5, "quan_decay_per_s": 0.25,
                             "spoiled_below": 30})
IDLE = InputState((0.0, 0.0), {}, set())
PRESS = InputState((0.0, 0.0), {"interact": True}, {"interact"})
STOVE = [2, 8]  # đứng ngay bếp B1


def it(i, kind, fresh):
    return {"id": i, "kind": kind, "fresh": fresh}


def quan(stock, customers=(), seed=1, tuning=TUNING, **sc):
    scenario = {"random_customers": False, "customers": list(customers), **sc}
    return QuanSim(tuning, scenario, Streams(seed), IdAllocator(), inventory=copy.deepcopy(stock))


def fresh_of(sim, iid):
    return next(x["fresh"] for x in sim.snapshot()["stock"] if x["id"] == iid)


def run(sim, n, inp=IDLE):
    out = []
    for _ in range(n):
        out += sim.step(inp)
    return out


def goi(cid="C1", table="T1", **kw):
    return {"id": cid, "table_id": table, "dish_id": "goi_bong_sung", **kw}


class Decay(unittest.TestCase):
    def test_exact_quarter_point_per_second(self):
        sim = quan([it("I1", "ca_loc", 100)])
        run(sim, 240)
        self.assertEqual(fresh_of(sim, "I1"), 99.0)
        run(sim, 60)
        self.assertAlmostEqual(fresh_of(sim, "I1"), 98.75, delta=0.01)

    def test_reserved_item_also_decays(self):
        sim = quan([it("I1", "bong_sung", 90), it("I2", "bong_sung", 90)], [goi()])
        run(sim, 240)
        self.assertEqual([x["fresh"] for x in sim.snapshot()["stock"]], [89.0, 89.0])

    def test_clamp_at_zero(self):
        sim = quan([it("I1", "ca_loc", 0.001)])
        run(sim, 10)
        self.assertEqual(fresh_of(sim, "I1"), 0.0)

    def test_spoiled_once_on_crossing_by_id(self):
        sim = quan([it("I10", "ca_loc", 30), it("I2", "ca_keo", 30), it("I3", "ca_loc", 29), it("I4", "ca_loc", 31)])
        ev = sim.step(IDLE)
        spoiled = [d for n, d in ev if n == "spoiled"]
        self.assertEqual(spoiled, [{"item_id": "I2", "kind": "ca_keo", "location": "stock"},
                                   {"item_id": "I10", "kind": "ca_loc", "location": "stock"}])
        later = [d for n, d in run(sim, 600) if n == "spoiled"]
        self.assertEqual([d["item_id"] for d in later], ["I4"])  # 31 → <30 sau 4 s; I2/I10/I3 không phát lại

    def test_threshold_exact_no_float_drift(self):
        # 30.25 cần đúng 60 tick để về 30.0 (chưa ươn), tick 61 mới ươn.
        sim = quan([it("I1", "ca_loc", 30.25)])
        self.assertFalse([1 for n, _ in run(sim, 60) if n == "spoiled"])
        self.assertEqual(fresh_of(sim, "I1"), 30.0)
        self.assertTrue([1 for n, _ in sim.step(IDLE) if n == "spoiled"])


class Reserve(unittest.TestCase):
    def test_missing_reserved_takes_freshest_then_smallest_id(self):
        stock = [it("I1", "bong_sung", 50), it("I2", "bong_sung", 80), it("I3", "bong_sung", 80),
                 it("I4", "bong_sung", 90)]
        sim = quan(stock, [goi()])
        self.assertEqual(sim.snapshot()["customers"][0]["reserved"], ["I2", "I4"])

    def test_tie_uses_numeric_id_order(self):
        stock = [it("I10", "bong_sung", 80), it("I2", "bong_sung", 80), it("I9", "bong_sung", 80)]
        self.assertEqual(quan(stock, [goi()]).snapshot()["customers"][0]["reserved"], ["I2", "I9"])

    def test_missing_reserved_order_tick_then_table(self):
        stock = [it("I1", "bong_sung", 90), it("I2", "bong_sung", 80), it("I3", "bong_sung", 70),
                 it("I4", "bong_sung", 60)]
        sim = quan(stock, [goi("C1", "T2", order_tick=5), goi("C2", "T3", order_tick=0)])
        res = {c["id"]: c["reserved"] for c in sim.snapshot()["customers"]}
        self.assertEqual(res, {"C2": ["I1", "I2"], "C1": ["I3", "I4"]})

    def test_explicit_reserved_respected_then_auto(self):
        stock = [it("I1", "bong_sung", 90), it("I2", "bong_sung", 80), it("I3", "bong_sung", 70),
                 it("I4", "bong_sung", 60)]
        sim = quan(stock, [goi("C1", "T1", reserved=["I3", "I1"]), goi("C2", "T2")])
        res = {c["id"]: c["reserved"] for c in sim.snapshot()["customers"]}
        self.assertEqual(res, {"C1": ["I1", "I3"], "C2": ["I2", "I4"]})

    def test_spoiled_never_reserved(self):
        stock = [it("I1", "bong_sung", 29), it("I2", "bong_sung", 40), it("I3", "bong_sung", 35)]
        sim = quan(stock, [goi()])
        self.assertEqual(sim.snapshot()["customers"][0]["reserved"], ["I2", "I3"])

    def test_spawn_reserves_by_id_and_only_spoiled_gives_no_dish(self):
        sim = QuanSim(TUNING, {}, Streams(1), IdAllocator(),
                      inventory=[it("I1", "bong_sung", 29), it("I2", "bong_sung", 29)])
        names = [n for n, _ in run(sim, 3000)]
        self.assertNotIn("customer_arrived", names)
        sim = QuanSim(TUNING, {}, Streams(1), IdAllocator(),
                      inventory=[it("I1", "bong_sung", 80), it("I2", "bong_sung", 90), it("I3", "bong_sung", 70)])
        arrived = [d for n, d in run(sim, 3000) if n == "customer_arrived"]
        self.assertEqual(len(arrived), 1)
        self.assertEqual(arrived[0]["dish_id"], "goi_bong_sung")
        c = sim.snapshot()["customers"][0]
        self.assertEqual(c["reserved"], ["I1", "I2"])

    def test_spoiled_reservation_released_and_retried_once(self):
        stock = [it("I1", "bong_sung", 30), it("I2", "bong_sung", 80), it("I3", "bong_sung", 70)]
        sim = quan(stock, [goi(reserved=["I1", "I2"])])
        ev = sim.step(IDLE)
        self.assertEqual([n for n, _ in ev][:1], ["spoiled"])
        c = sim.snapshot()["customers"][0]
        self.assertEqual((c["order_status"], c["reserved"]), ("reserved", ["I2", "I3"]))

    def test_spoiled_reservation_not_enough_becomes_unfulfillable(self):
        stock = [it("I1", "bong_sung", 30), it("I2", "bong_sung", 80)]
        sim = quan(stock, [goi(reserved=["I1", "I2"])])
        sim.step(IDLE)
        c = sim.snapshot()["customers"][0]
        self.assertEqual((c["state"], c["order_status"], c["reserved"]), ("waiting", "unfulfillable", []))

    def test_affected_orders_by_order_tick_then_table(self):
        # Hai đơn cùng mất 1 cá thể; chỉ còn 1 cá thể dự phòng → đơn order_tick nhỏ được giữ lại.
        stock = [it("I1", "bong_sung", 30), it("I2", "bong_sung", 80), it("I3", "bong_sung", 30),
                 it("I4", "bong_sung", 80), it("I5", "bong_sung", 60)]
        sim = quan(stock, [goi("C1", "T1", order_tick=3, reserved=["I1", "I2"]),
                           goi("C2", "T2", order_tick=1, reserved=["I3", "I4"])])
        sim.step(IDLE)
        st = {c["id"]: (c["order_status"], c["reserved"]) for c in sim.snapshot()["customers"]}
        self.assertEqual(st, {"C2": ("reserved", ["I4", "I5"]), "C1": ("unfulfillable", [])})


class CookPrice(unittest.TestCase):
    def test_locked_price_items_and_tip(self):
        # goi 40 đ; fresh 90 và 80 sau 1 tick hao (−1/240) → mean < 85 → floor(40×mean/100) = 33.
        stock = [it("I2", "bong_sung", 80), it("I1", "bong_sung", 90)]
        sim = quan(stock, [goi()], player={"pos": STOVE})
        ev = sim.step(PRESS)
        cook = [d for n, d in ev if n == "cook_started"]
        self.assertEqual(len(cook), 1)
        self.assertEqual(cook[0]["base_price"], 33)
        self.assertEqual([x["id"] for x in cook[0]["items"]], ["I1", "I2"])
        self.assertAlmostEqual(cook[0]["items"][0]["fresh"], 90 - 1 / 240, delta=0.01)
        self.assertEqual(sim.snapshot()["stock"], [])
        self.assertEqual(sim.snapshot()["customers"][0]["reserved"], [])

    def test_price_exact_mean(self):
        from fractions import Fraction
        from chonoi.sim.quan_fresh import locked_price
        self.assertEqual(locked_price(40, Fraction(85)), 34)
        self.assertEqual(locked_price(55, Fraction(2999, 100)), 16)
        self.assertEqual(locked_price(40, Fraction(100)), 40)

    def test_items_sorted_by_kind_then_id(self):
        from chonoi.sim.quan_fresh import consume
        sim = quan([it("I9", "ca_loc", 90), it("I3", "bong_dien_dien", 50), it("I10", "ca_loc", 70)])
        used, mean = consume(sim, ["I10", "I3", "I9"])
        self.assertEqual([x["id"] for x in used], ["I3", "I9", "I10"])
        sim = quan([it("I1", "ca_loc", 90), it("I2", "bong_dien_dien", 50)])
        self.assertEqual([x["id"] for x in consume(sim, ["I1", "I2"])[0]], ["I2", "I1"])
        self.assertEqual(mean, 70)


class Snapshot(unittest.TestCase):
    def test_stock_schema_keeps_spoiled_and_reserved(self):
        sim = quan([it("I2", "bong_sung", 20), it("I10", "bong_sung", 90), it("I1", "bong_sung", 95)], [goi()])
        snap = sim.snapshot()
        self.assertEqual([x["id"] for x in snap["stock"]], ["I1", "I2", "I10"])
        self.assertEqual(set(snap["stock"][0]), {"id", "kind", "fresh"})
        self.assertIsInstance(snap["stock"][0]["fresh"], float)
        self.assertEqual(snap["customers"][0]["reserved"], ["I1", "I10"])
        json.dumps(snap)

    def test_empty_stock(self):
        self.assertEqual(quan([]).snapshot()["stock"], [])

    def test_item_ids_reserved_in_allocator(self):
        sim = quan([it("I7", "ca_loc", 90)])
        self.assertEqual(sim.ids.new("I"), "I8")


class BadFixtures(unittest.TestCase):
    def bad(self, stock, customers=()):
        with self.assertRaises(BadInput):
            quan(stock, customers)

    def test_count_inventory_under_v12(self):
        self.bad({"bong_sung": 2})

    def test_list_inventory_without_freshness(self):
        with self.assertRaises(BadInput):
            quan([it("I1", "ca_loc", 90)], tuning=P2)

    def test_item_schema(self):
        self.bad([it("I1", "ca_loc", 90), it("I1", "ca_loc", 80)])
        self.bad([it("", "ca_loc", 90)])
        self.bad([it(1, "ca_loc", 90)])
        self.bad([it("I1", "ca_ro", 90)])
        self.bad([it("I1", "ca_loc", 101)])
        self.bad([it("I1", "ca_loc", -0.5)])
        self.bad([it("I1", "ca_loc", True)])
        self.bad([it("I1", "ca_loc", float("nan"))])
        self.bad([it("I1", "ca_loc", "90")])
        self.bad([{"id": "I1", "kind": "ca_loc"}])
        self.bad([dict(it("I1", "ca_loc", 90), extra=1)])

    def test_reserved_errors(self):
        s = [it("I1", "bong_sung", 90), it("I2", "bong_sung", 90), it("I3", "bong_sung", 20),
             it("I4", "ca_loc", 90)]
        self.bad(s, [goi(reserved=["I1", "I9"])])                 # id không có
        self.bad(s, [goi(reserved=["I1", "I3"])])                 # đã ươn
        self.bad(s, [goi(reserved=["I1", "I4"])])                 # sai công thức
        self.bad(s, [goi(reserved=["I1"])])                       # thiếu
        self.bad(s, [goi(reserved=["I1", "I1"])])                 # trùng trong đơn
        self.bad(s, [goi("C1", "T1", reserved=["I1", "I2"]), goi("C2", "T2", reserved=["I2", "I1"])])  # dùng chung
        self.bad(s, [goi(reserved={"bong_sung": 2})])             # dạng đếm cũ
        self.bad(s, [goi(order_status="assigned", reserved=["I1"])])  # đơn không reserved mà giữ

    def test_missing_reserved_not_enough(self):
        self.bad([it("I1", "bong_sung", 90), it("I2", "bong_sung", 25)], [goi()])
        self.bad([it("I1", "bong_sung", 90), it("I2", "bong_sung", 90)],
                 [goi("C1", "T1", reserved=["I1", "I2"]), goi("C2", "T2")])


if __name__ == "__main__":
    unittest.main()
