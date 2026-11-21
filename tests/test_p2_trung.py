"""Test Phase 2 (Trung): kế hoạch ngày (day_plan.py), quán 2 bếp/4 bàn/6 món, lọc món theo kế hoạch.

Dùng dữ liệu chuẩn ở docs/contracts/phase-2-tuning.sample.json (giao diện P2 §9) vì manifest runtime còn là v1.0.
Sim quán là SimpleNamespace dựng theo giao diện P1 §4 + P2 §5 (allowed_dishes); chưa phụ thuộc QuanSim.

Chạy: PYTHONPATH=tests:. python3 -m unittest tests.test_p2_trung -v
"""

import copy
import json
import types
import unittest
from pathlib import Path

from chonoi.errors import BadInput
from chonoi.ids import IdAllocator, sort_by_id
from chonoi.rng import Streams
from chonoi.sim.day_plan import resolve_day_plans
from chonoi.sim.quan_customers import available_stock, init_customers, spawn_customer
from chonoi.sim.quan_validation import validate_quan_fixture, validate_quan_state

ROOT = Path(__file__).resolve().parent.parent
with open(ROOT / "docs/contracts/phase-2-tuning.sample.json", encoding="utf-8-sig") as f:
    TUNING = json.load(f)["tuning"]
Q, MENU = TUNING["quan"], TUNING["menu"]
FIRST, EVERY = Q["first_customer_tick"], int(round(Q["customer_interval_s"] * 60))
KINDS = ("ca_loc", "ca_linh", "ca_keo", "bong_dien_dien", "bong_sung", "keo_neo")
LOTS = {k: 20 for k in KINDS}

# Bảng kế hoạch D1–D5 chép từ TICKET-02 §2 (đề), để đối chiếu với dữ liệu, không đọc lại từ tuning.
TICKET_PLANS = {
    1: ({"ca_loc_nuong_trui": 3, "goi_bong_sung": 3}, {"ca_loc": 3, "bong_sung": 6}),
    2: ({"ca_loc_nuong_trui": 2, "lau_ca_linh_dien_dien": 2}, {"ca_loc": 2, "ca_linh": 6, "bong_dien_dien": 2}),
    3: ({"goi_bong_sung": 2, "canh_chua_ca_loc": 2, "ca_keo_nuong": 2},
        {"bong_sung": 4, "ca_loc": 2, "bong_dien_dien": 2, "ca_keo": 4}),
    4: ({"lau_mam": 1, "ca_loc_nuong_trui": 2, "goi_bong_sung": 1},
        {"ca_linh": 2, "ca_keo": 1, "keo_neo": 1, "bong_dien_dien": 1, "ca_loc": 2, "bong_sung": 2}),
    5: ({"lau_mam": 1, "lau_ca_linh_dien_dien": 1, "ca_loc_nuong_trui": 1},
        {"ca_linh": 5, "ca_keo": 1, "keo_neo": 1, "bong_dien_dien": 2, "ca_loc": 1}),
}


def make(sc=None, stock=None, allowed=None, seed=1):
    sc = dict(sc or {})
    validate_quan_fixture(sc, TUNING)
    stoves = {s["id"]: dict(s, state="idle", dish=None, cook_ticks_left=0, ready_ticks=0) for s in Q["stoves"]}
    for u in sc.get("stoves", []):
        stoves[u["id"]].update(u)
    sim = types.SimpleNamespace(
        t=Q, menu=MENU, rng=Streams(seed), ids=IdAllocator(), stock=dict(stock or {}), hand=sc.get("hand"),
        stoves=sort_by_id(list(stoves.values())), tables=sort_by_id([dict(t) for t in Q["tables"]]),
        time_left_ticks=int(round(Q["duration_s"] * 60)), reputation=Q["reputation_initial"], phase_tick=0,
        random_customers=sc.get("random_customers", True), allowed_dishes=allowed)
    init_customers(sim, sc)
    validate_quan_state(sim)
    return sim


def spawn_at(sim, k):
    sim.phase_tick = FIRST + EVERY * k
    ev = []
    spawn_customer(sim, ev)
    return ev


class DayPlan(unittest.TestCase):
    def test_preset_matches_ticket(self):
        plans = resolve_day_plans(TUNING)
        self.assertEqual([p["day"] for p in plans], [1, 2, 3, 4, 5])
        for p in plans:
            dishes, ingredients = TICKET_PLANS[p["day"]]
            self.assertEqual(p["dishes"], dishes)
            self.assertEqual(p["ingredients"], ingredients)

    def test_returns_copies(self):
        before = copy.deepcopy(TUNING["day_plan"])
        plans = resolve_day_plans(TUNING)
        plans[0]["dishes"]["goi_bong_sung"] = 99
        plans[0]["ingredients"].clear()
        self.assertEqual(TUNING["day_plan"], before)
        self.assertEqual(resolve_day_plans(TUNING)[0]["dishes"]["goi_bong_sung"], 3)

    def test_override_recomputes_and_keeps_other_days(self):
        plans = resolve_day_plans(TUNING, [{"day": 2, "dishes": {"lau_mam": 2}}])
        self.assertEqual(plans[1], {"day": 2, "dishes": {"lau_mam": 2},
                                    "ingredients": {"ca_linh": 4, "ca_keo": 2, "keo_neo": 2, "bong_dien_dien": 2}})
        self.assertEqual(plans[0]["dishes"], TICKET_PLANS[1][0])
        self.assertEqual(plans[4]["dishes"], TICKET_PLANS[5][0])

    def test_override_ingredients_matching_accepted(self):
        plans = resolve_day_plans(TUNING, [{"day": 1, "dishes": {"goi_bong_sung": 1},
                                             "ingredients": {"bong_sung": 2}}])
        self.assertEqual(plans[0]["ingredients"], {"bong_sung": 2})

    def test_override_rejected(self):
        bad = [
            [{"day": 1, "dishes": {"goi_bong_sung": 1}}, {"day": 1, "dishes": {"lau_mam": 1}}],  # ngày trùng
            [{"day": 0, "dishes": {"goi_bong_sung": 1}}],
            [{"day": 6, "dishes": {"goi_bong_sung": 1}}],
            [{"day": True, "dishes": {"goi_bong_sung": 1}}],
            [{"day": 1.0, "dishes": {"goi_bong_sung": 1}}],
            [{"day": 1, "dishes": {"bun_nuoc_leo": 1}}],  # món lạ
            [{"day": 1, "dishes": {"goi_bong_sung": 0}}],
            [{"day": 1, "dishes": {"goi_bong_sung": 1.0}}],
            [{"day": 1, "dishes": {"goi_bong_sung": True}}],
            [{"day": 1, "dishes": {}}],
            [{"day": 1}],  # thiếu dishes
            [{"day": 1, "dishes": {"goi_bong_sung": 1}, "ingredients": {"bong_sung": 3}}],  # lệch recipe
            [{"day": 1, "dishes": {"goi_bong_sung": 1}, "ingredients": {"bong_sung": 2, "ca_loc": 0}}],
            [{"day": 1, "dishes": {"goi_bong_sung": 1}, "extra": 1}],
            "không phải list",
            [["day", 1]],
        ]
        for ov in bad:
            with self.subTest(ov=ov), self.assertRaises(BadInput):
                resolve_day_plans(TUNING, ov)

    def test_bad_preset_rejected(self):
        t = copy.deepcopy(TUNING)
        t["day_plan"][0]["ingredients"]["bong_sung"] = 7
        with self.assertRaises(BadInput):
            resolve_day_plans(t)


class QuanP2(unittest.TestCase):
    def test_four_tables_filled_in_id_order_then_skip(self):
        sim = make(stock=LOTS)
        tables = [spawn_at(sim, k)[0][1]["table_id"] for k in range(4)]
        self.assertEqual(tables, ["T1", "T2", "T3", "T4"])
        self.assertEqual(spawn_at(sim, 4), [])  # hết bàn: bỏ lượt, không cấp id
        self.assertEqual(sim.ids.new("C"), "C5")

    def test_standalone_uses_all_six_dishes(self):
        seen = set()
        for seed in range(40):
            sim = make(stock=LOTS, seed=seed)
            seen.add(spawn_at(sim, 0)[0][1]["dish_id"])
        self.assertEqual(seen, set(MENU))

    def test_allowed_dishes_filter_before_stock(self):
        allowed = ["ca_loc_nuong_trui", "goi_bong_sung"]
        for seed in range(30):
            sim = make(stock=LOTS, allowed=allowed, seed=seed)
            self.assertIn(spawn_at(sim, 0)[0][1]["dish_id"], allowed)

    def test_allowed_but_no_stock_is_no_dish(self):
        # Kho đủ cho lẩu mắm (ngoài kế hoạch) nhưng không đủ món trong kế hoạch -> no_dish.
        stock = {"ca_linh": 2, "ca_keo": 1, "keo_neo": 1, "bong_dien_dien": 1}
        sim = make(stock=stock, allowed=["goi_bong_sung"])
        self.assertEqual(spawn_at(sim, 0), [("no_dish", {})])
        sim = make(stock=stock)
        self.assertEqual(spawn_at(sim, 0)[0][1]["dish_id"], "lau_mam")

    def test_no_quota_after_planned_servings(self):
        # Không biến số suất kế hoạch thành quota: vẫn gọi tiếp khi còn nguyên liệu.
        sim = make(stock=LOTS, allowed=["goi_bong_sung"])
        dishes = [spawn_at(sim, k)[0][1]["dish_id"] for k in range(4)]
        self.assertEqual(dishes, ["goi_bong_sung"] * 4)

    def test_available_stock_covers_new_kinds(self):
        sim = make({"customers": [{"id": "C1", "table_id": "T1", "dish_id": "lau_mam"}]}, stock=LOTS)
        avail = available_stock(sim)
        self.assertEqual(set(avail), set(KINDS))
        self.assertEqual(avail["keo_neo"], 19)
        self.assertEqual(avail["ca_keo"], 19)
        self.assertEqual(sim.stock, LOTS)
        empty = available_stock(make(stock={"ca_loc": 1}))  # kind chưa có trong kho vẫn hiện với 0
        self.assertEqual(empty, {"ca_loc": 1, **{k: 0 for k in KINDS if k != "ca_loc"}})

    def test_fixture_on_b2_t4_and_new_kinds_valid(self):
        sim = make({
            "customers": [{"id": "C1", "table_id": "T4", "dish_id": "ca_keo_nuong", "order_status": "assigned",
                           "reserved": {}}],
            "stoves": [{"id": "B2", "state": "cooking", "cook_ticks_left": 30,
                        "dish": {"order_id": "C1", "dish_id": "ca_keo_nuong", "base_price": 70}}],
        }, stock={"ca_keo": 1})
        self.assertEqual(sim.stoves[1]["dish"]["order_id"], "C1")
        make({"customers": [{"id": "C1", "table_id": "T2", "dish_id": "lau_mam",
                             "reserved": {"ca_linh": 2, "ca_keo": 1, "keo_neo": 1, "bong_dien_dien": 1}}]},
             stock=LOTS)

    def test_fixture_dish_outside_plan_rejected(self):
        sc = {"customers": [{"id": "C1", "table_id": "T1", "dish_id": "lau_mam"}]}
        with self.assertRaises(BadInput):
            make(sc, stock=LOTS, allowed=["goi_bong_sung"])
        make(sc, stock=LOTS, allowed=["lau_mam"])

    def test_unknown_kind_in_reserved_rejected(self):
        with self.assertRaises(BadInput):
            make({"customers": [{"id": "C1", "table_id": "T1", "dish_id": "goi_bong_sung",
                                 "order_status": "unfulfillable", "reserved": {"ca_hu": 1}}]})


if __name__ == "__main__":
    unittest.main()
