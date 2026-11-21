"""Test lát 3 (Trung): khách, giữ chỗ, kiên nhẫn, rời bàn, kiểm fixture quán. Gọi trực tiếp hàm trong
chonoi/sim/quan_customers.py và quan_validation.py. Helper bếp/tiền của Đức được thay bằng module giả để
kiểm riêng phần khách (contract §1); sim là SimpleNamespace dựng theo §4, không phụ thuộc QuanSim. Test tích hợp
hộp đen chạy sau khi Đức ghép vào QuanSim.

Chạy: PYTHONPATH=tests:. python3 -m unittest tests.test_p1_trung -v
"""

import sys
import types
import unittest
from unittest import mock

from chonoi.contract import load_contract
from chonoi.errors import BadInput
from chonoi.ids import IdAllocator, sort_by_id
from chonoi.rng import Streams
from chonoi.sim.quan_customers import (advance_timers, available_stock, init_customers, resolve_departures,
                                       spawn_customer)
from chonoi.sim.quan_validation import validate_quan_fixture, validate_quan_state

TUNING = load_contract()["tuning"]
Q = TUNING["quan"]
PATIENCE = int(round(Q["patience_s"] * 60))
EVERY = int(round(Q["customer_interval_s"] * 60))
FULL = {"ca_loc": 5, "ca_linh": 5, "bong_dien_dien": 5, "bong_sung": 5}


def make(sc=None, stock=None, seed=1):
    """Dựng trạng thái quán theo thứ tự constructor ở contract §6 (phần của Đức được thay bằng bản tối thiểu)."""
    sc = dict(sc or {})
    validate_quan_fixture(sc, TUNING)
    stoves = {s["id"]: dict(s, state="idle", dish=None, cook_ticks_left=0, ready_ticks=0) for s in Q["stoves"]}
    for u in sc.get("stoves", []):
        stoves[u["id"]].update(u)
    sim = types.SimpleNamespace(
        t=Q, menu=TUNING["menu"], rng=Streams(seed), ids=IdAllocator(),
        stock=dict(stock if stock is not None else sc.get("stock", {})), hand=sc.get("hand"),
        stoves=sort_by_id(list(stoves.values())), tables=sort_by_id([dict(t) for t in Q["tables"]]),
        time_left_ticks=sc.get("time_left_ticks", int(round(Q["duration_s"] * 60))),
        reputation=sc.get("reputation", Q["reputation_initial"]), phase_tick=0,
        random_customers=sc.get("random_customers", True))
    init_customers(sim, sc)
    validate_quan_state(sim)
    return sim


def fake_kitchen():
    m = types.ModuleType("chonoi.sim.quan_kitchen")
    m.paid, m.discarded = [], []

    def pay_customer(sim, c, reason, events):
        m.paid.append((c["id"], reason))
        events.append(("paid", {"order_id": c["id"], "reason": reason}))

    m.pay_customer = pay_customer
    m.discard_order = lambda sim, order_id: m.discarded.append(order_id)
    return m


def resolve(sim):
    k = fake_kitchen()
    ev = []
    with mock.patch.dict(sys.modules, {"chonoi.sim.quan_kitchen": k}):
        resolve_departures(sim, ev)
    return ev, k


class Spawn(unittest.TestCase):
    def test_lich_khach_theo_phase_tick(self):
        sim = make(stock=FULL)
        for pt, want in ((Q["first_customer_tick"] - 1, 0), (Q["first_customer_tick"], 1),
                         (Q["first_customer_tick"] + 1, 0)):
            sim.phase_tick, ev = pt, []
            spawn_customer(sim, ev)
            self.assertEqual(len(ev), want, pt)
        c = sim.customers[0]
        self.assertEqual((c["table_id"], c["order_tick"], c["patience_ticks_left"], c["order_status"]),
                         ("T1", Q["first_customer_tick"], PATIENCE, "reserved"))
        self.assertEqual(c["reserved"], TUNING["menu"][c["dish_id"]]["recipe"])

    def test_ban_ban_bo_luot_va_luot_sau(self):
        sim = make(stock=FULL)
        sim.phase_tick = Q["first_customer_tick"]
        spawn_customer(sim, [])
        ev = []
        sim.phase_tick += EVERY
        spawn_customer(sim, ev)
        self.assertEqual(ev, [])
        self.assertEqual(len(sim.customers), 1)

    def test_luot_thu_hai_dung_chu_ky(self):
        sim = make({"random_customers": True}, stock=FULL)
        hits = []
        for pt in range(1, Q["first_customer_tick"] + 2 * EVERY + 1):
            sim.phase_tick, ev = pt, []
            spawn_customer(sim, ev)
            if ev:
                hits.append(pt)
                sim.customers = []  # bàn trống lại để thấy mọi lượt
        self.assertEqual(hits, [Q["first_customer_tick"] + i * EVERY for i in range(3)])
        self.assertEqual(sim.ids.new("C"), "C4", "id khách nối tiếp")

    def test_timer_bep(self):
        dish = {"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": 60}
        cust = {"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "order_status": "assigned",
                "reserved": {}}
        sim = make({"customers": [cust], "stoves": [{"id": "B1", "state": "cooking", "dish": dish,
                                                     "cook_ticks_left": 2}]})
        advance_timers(sim)
        self.assertEqual((sim.stoves[0]["cook_ticks_left"], sim.stoves[0]["ready_ticks"]), (1, 0))
        sim = make({"customers": [cust], "stoves": [{"id": "B1", "state": "ready", "dish": dish, "ready_ticks": 4}]})
        advance_timers(sim)
        self.assertEqual(sim.stoves[0]["ready_ticks"], 5)

    def test_no_dish_khi_co_ban_ma_thieu_mon(self):
        sim = make(stock={"ca_linh": 2, "bong_sung": 1})
        sim.phase_tick, ev = Q["first_customer_tick"], []
        spawn_customer(sim, ev)
        self.assertEqual(ev, [("no_dish", {})])
        self.assertEqual(sim.customers, [])

    def test_chi_chon_mon_du_nguyen_lieu_kha_dung(self):
        sim = make(stock={"ca_loc": 1})
        sim.phase_tick, ev = Q["first_customer_tick"], []
        spawn_customer(sim, ev)
        self.assertEqual(ev, [("customer_arrived", {"order_id": "C1", "table_id": "T1",
                                                    "dish_id": "ca_loc_nuong_trui"})])

    def test_tat_khach_ngau_nhien_va_het_gio(self):
        sim = make({"random_customers": False}, stock=FULL)
        sim.phase_tick, ev = Q["first_customer_tick"], []
        spawn_customer(sim, ev)
        sim2 = make({"time_left_ticks": 1}, stock=FULL)
        sim2.phase_tick, sim2.time_left_ticks = Q["first_customer_tick"], 0
        spawn_customer(sim2, ev)
        self.assertEqual(ev, [])

    def test_cung_seed_cung_mon(self):
        picks = []
        for _ in range(2):
            sim = make(stock=FULL, seed=7)
            sim.phase_tick = Q["first_customer_tick"]
            spawn_customer(sim, [])
            picks.append(sim.customers[0]["dish_id"])
        self.assertEqual(picks[0], picks[1])

    def test_kien_nhan_giam_tu_buoc_sau(self):
        sim = make(stock=FULL)
        sim.phase_tick = Q["first_customer_tick"]
        spawn_customer(sim, [])
        advance_timers(sim)
        self.assertEqual(sim.customers[0]["patience_ticks_left"], PATIENCE - 1)


class Stock(unittest.TestCase):
    def test_kha_dung_tru_giu_cho_khong_doi_ton(self):
        sim = make({"customers": [{"id": "C1", "table_id": "T1", "dish_id": "lau_ca_linh_dien_dien"}]},
                   stock={"ca_linh": 3, "bong_dien_dien": 1, "ca_loc": 1})
        self.assertEqual(sim.customers[0]["reserved"], {"ca_linh": 3, "bong_dien_dien": 1})
        self.assertEqual(available_stock(sim), {"ca_linh": 0, "bong_dien_dien": 0, "ca_loc": 1, "bong_sung": 0})
        self.assertEqual(sim.stock, {"ca_linh": 3, "bong_dien_dien": 1, "ca_loc": 1})


class Departures(unittest.TestCase):
    def test_het_kien_nhan_roi_tru_uy_tin_nha_giu(self):
        sim = make({"customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
                                   "patience_ticks_left": 1}]}, stock={"ca_loc": 1})
        advance_timers(sim)
        ev, k = resolve(sim)
        self.assertEqual(ev, [("customer_left", {"order_id": "C1", "table_id": "T1", "reason": "patience",
                                                 "reputation": Q["reputation_initial"] + Q["left_reputation_delta"]})])
        self.assertEqual((sim.customers, k.discarded), ([], ["C1"]))
        self.assertEqual(available_stock(sim)["ca_loc"], 1)

    def test_an_xong_tra_tien_roi_ban(self):
        sim = make({"customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "state": "eating",
                                   "order_status": "served", "eat_ticks_left": 1, "base_price": 60, "tip": 12}]})
        advance_timers(sim)
        ev, k = resolve(sim)
        self.assertEqual((k.paid, sim.customers), ([("C1", "finished_eating")], []))
        self.assertEqual([e[0] for e in ev], ["paid"])

    def test_dong_ca(self):
        sim = make({"time_left_ticks": 1, "customers": [
            {"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "state": "eating",
             "order_status": "served", "eat_ticks_left": Q["eat_s"] * 60, "base_price": 60, "tip": 0}]})
        advance_timers(sim)
        self.assertEqual(sim.time_left_ticks, 0)
        ev, k = resolve(sim)
        self.assertEqual(k.paid, [("C1", "closing")])
        sim = make({"time_left_ticks": 1, "customers": [
            {"id": "C2", "table_id": "T1", "dish_id": "ca_loc_nuong_trui"}]}, stock={"ca_loc": 1})
        advance_timers(sim)
        ev, _ = resolve(sim)
        self.assertEqual(ev[0][1]["reason"], "closing")
        self.assertEqual(sim.reputation, Q["reputation_initial"], "đóng ca không trừ uy tín")

    def test_an_xong_dung_tick_dong_ca_la_finished_eating(self):
        sim = make({"time_left_ticks": 1, "customers": [
            {"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "state": "eating",
             "order_status": "served", "eat_ticks_left": 1, "base_price": 60, "tip": 0}]})
        advance_timers(sim)
        _, k = resolve(sim)
        self.assertEqual(k.paid, [("C1", "finished_eating")])


class Validation(unittest.TestCase):
    def bad(self, sc, stock=None):
        with self.assertRaises(BadInput):
            make(sc, stock=stock)

    def test_fixture_mac_dinh(self):
        c = make({"customers": [{"id": "C1", "table_id": "T1", "dish_id": "goi_bong_sung"}]},
                 stock={"bong_sung": 2}).customers[0]
        self.assertEqual((c["state"], c["order_tick"], c["patience_ticks_left"], c["order_status"],
                          c["reserved"]), ("waiting", 0, PATIENCE, "reserved", {"bong_sung": 2}))

    def test_tu_choi(self):
        cust = {"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui"}
        dish = {"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": 60}
        assigned = dict(cust, order_status="assigned", reserved={})
        cases = [
            ({"customers": [dict(cust, mood="vui")]}, None),                              # trường lạ
            ({"customers": [dict(cust, dish_id="pho")]}, None),                           # món ngoài phạm vi
            ({"customers": [{"id": "C1", "table_id": "T1"}]}, None),                      # liên kết thiếu
            ({"customers": [cust]}, {}),                                                  # giữ quá tồn
            ({"customers": [dict(cust, reserved={"ca_loc": 2})]}, {"ca_loc": 2}),         # giữ khác công thức
            ({"customers": [assigned]}, None),                                            # assigned thiếu món
            ({"customers": [assigned], "hand": dish,
              "stoves": [{"id": "B1", "state": "ready", "dish": dish}]}, None),           # bếp và tay cùng đơn
            ({"customers": [assigned], "hand": dict(dish, dish_id="goi_bong_sung")}, None),  # món không khớp
            ({"hand": dish}, None),                                                       # tham chiếu không có khách
            ({"customers": [assigned], "stoves": [{"id": "B1", "state": "cooking", "dish": dish}]}, None),  # timer 0
            ({"customers": [dict(cust, state="eating", order_status="served", reserved={},
                                 eat_ticks_left=5)]}, None),                              # eating thiếu giá/boa
            ({"customers": [dict(cust, eat_ticks_left=5)]}, {"ca_loc": 1}),               # bộ đếm mâu thuẫn
            ({"customers": [dict(cust, patience_ticks_left=-1)]}, {"ca_loc": 1}),         # bộ đếm âm
            ({"customers": [dict(cust, order_status="unfulfillable", reserved={}, state="eating",
                                 eat_ticks_left=5, base_price=60, tip=0)]}, None),        # unfulfillable phải chờ
            ({"stoves": [{"id": "B1", "pos": [20, 1]}]}, None),                           # tọa độ ngoài miền
            ({"customers": [dict(cust, order_status="served", reserved={})]}, None),     # Q5: served mà waiting
            ({"customers": [assigned], "hand": dict(dish, base_price=0)}, None),         # Q8: giá payload không dương
            ({"reputation": 9}, None),
            ({"random_customers": "yes"}, None),
        ]
        for sc, stock in cases:
            with self.subTest(sc=sc):
                self.bad(sc, stock)

    def test_fixture_chung_cua_nhom_hop_le_va_khong_bi_sua(self):
        import json
        for name in ("quan-reserved.json", "quan-ready.json"):
            with open(f"docs/contracts/phase-1-fixtures/{name}", encoding="utf-8") as f:
                sc = json.load(f)["quan"]
            before = json.dumps(sc, sort_keys=True)
            sim = make(sc)
            sim.customers[0]["reserved"]["ca_loc"] = 99  # runtime sửa state không được lan về scenario
            self.assertEqual(json.dumps(sc, sort_keys=True), before, f"{name}: init không được sửa scenario")
            self.assertEqual(sim.ids.new("C"), "C2")

    def test_hop_le(self):
        dish = {"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": 60}
        assigned = {"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "order_status": "assigned",
                    "reserved": {}}
        make({"customers": [assigned], "stoves": [{"id": "B1", "state": "cooking", "dish": dish,
                                                   "cook_ticks_left": 3}]})
        make({"customers": [assigned], "hand": dish})
        make({"customers": [assigned], "hand": dict(dish, base_price=999)})  # Q8: giá khác menu vẫn hợp lệ
        make({"customers": [dict(assigned, order_status="reserved", reserved={"ca_loc": 1}, order_tick=50,
                                 patience_ticks_left=0)]}, stock={"ca_loc": 1})  # Q6
        make({"customers": [{"id": "C1", "table_id": "T1", "dish_id": "goi_bong_sung",
                             "order_status": "unfulfillable", "reserved": {}}]})


if __name__ == "__main__":
    unittest.main()
