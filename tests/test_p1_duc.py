import unittest
from types import SimpleNamespace

from chonoi.contract import load_contract
from chonoi.sim.quan_kitchen import discard_order, pay_customer


class PaymentTests(unittest.TestCase):
    def setUp(self):
        self.tuning = load_contract()["tuning"]["quan"]
        self.customer = {
            "id": "C1",
            "table_id": "T1",
            "state": "eating",
            "order_status": "served",
            "base_price": 60,
            "tip": 12,
        }
        self.sim = SimpleNamespace(
            t=self.tuning,
            money=10,
            earned=20,
            shift_earned=5,
            reputation=self.tuning["reputation_initial"],
            customers=[self.customer],
        )

    def test_pay_adds_price_and_tip_and_appends_contract_event(self):
        original_customer = self.customer.copy()
        events = [("served", {"order_id": "C1"})]

        pay_customer(self.sim, self.customer, "finished_eating", events)

        self.assertEqual((self.sim.money, self.sim.earned, self.sim.shift_earned), (82, 92, 77))
        self.assertAlmostEqual(
            self.sim.reputation, self.tuning["reputation_initial"] + self.tuning["tip_reputation"]
        )
        self.assertEqual(self.sim.customers, [original_customer])
        self.assertEqual(events, [
            ("served", {"order_id": "C1"}),
            ("paid", {
                "order_id": "C1",
                "table_id": "T1",
                "base_price": 60,
                "tip": 12,
                "amount": 72,
                "reason": "finished_eating",
            }),
        ])

    def test_pay_without_tip_at_closing_preserves_reputation(self):
        self.customer["tip"] = 0
        events = []

        pay_customer(self.sim, self.customer, "closing", events)

        self.assertEqual((self.sim.money, self.sim.earned, self.sim.shift_earned), (70, 80, 65))
        self.assertEqual(self.sim.reputation, self.tuning["reputation_initial"])
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0][1]["reason"], "closing")

    def test_pay_clamps_reputation_at_maximum(self):
        reputation_max = self.tuning["reputation_max"]
        self.sim.reputation = reputation_max - self.tuning["tip_reputation"] / 2

        pay_customer(self.sim, self.customer, "finished_eating", [])

        self.assertEqual(self.sim.reputation, reputation_max)


class DiscardTests(unittest.TestCase):
    def test_discard_resets_matching_stove_and_keeps_other_dish_and_stock(self):
        for state, cook_ticks, ready_ticks in (("cooking", 8, 0), ("ready", 0, 4)):
            with self.subTest(state=state):
                stove = {
                    "id": "B1",
                    "state": state,
                    "dish": {"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": 60},
                    "cook_ticks_left": cook_ticks,
                    "ready_ticks": ready_ticks,
                }
                hand = {"order_id": "C2", "dish_id": "ca_loc_nuong_trui", "base_price": 60}
                idle_stove = dict(stove, id="B2", state="idle", dish=None, cook_ticks_left=0, ready_ticks=0)
                sim = SimpleNamespace(hand=hand, stoves=[stove, idle_stove], stock={"ca_loc": 1})

                discard_order(sim, "C1")

                self.assertEqual(stove, dict(idle_stove, id="B1"))
                self.assertIs(sim.hand, hand)
                self.assertEqual(sim.stock, {"ca_loc": 1})

    def test_discard_clears_matching_hand_and_keeps_unrelated_stove(self):
        stove = {
            "id": "B1",
            "state": "ready",
            "dish": {"order_id": "C2", "dish_id": "ca_loc_nuong_trui", "base_price": 60},
            "cook_ticks_left": 0,
            "ready_ticks": 4,
        }
        original_stove = dict(stove, dish=stove["dish"].copy())
        hand = {"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": 60}
        sim = SimpleNamespace(hand=hand, stoves=[stove], stock={})

        discard_order(sim, "C1")
        discard_order(sim, "C3")

        self.assertIsNone(sim.hand)
        self.assertEqual(sim.stoves, [original_stove])
        self.assertEqual(sim.stock, {})
