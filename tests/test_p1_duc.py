import unittest
from pathlib import Path
from types import SimpleNamespace

from chonoi import TICK_HZ
from chonoi.contract import load_contract
from chonoi.inputs import InputPlayer
from chonoi.runner import Session
from chonoi.scenario import load_scenario
from chonoi.sim.quan_kitchen import discard_order, finish_cooking, interact, pay_customer

from helpers import Workdir, run_headless, write_json


FIXTURES = Path(__file__).resolve().parents[1] / "docs" / "contracts" / "phase-1-fixtures"


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


class KitchenTests(unittest.TestCase):
    def setUp(self):
        self.tuning = load_contract()["tuning"]

    def fixture(self, name):
        scenario = load_scenario(FIXTURES / f"quan-{name}.json", "quan", self.tuning)
        return Session("quan", self.tuning, scenario, seed=1).sim

    def test_cooking_uses_tuning_and_consumes_only_the_oldest_reserved_order(self):
        sim = self.fixture("reserved")
        first = sim.customers[0]
        later = dict(first, id="C2", table_id="T2", order_tick=10, reserved={"ca_loc": 1})
        sim.customers.insert(0, later)
        sim.stock["ca_loc"] = 2
        stove = sim.stoves[0]
        sim.pos = [stove["pos"][0] + sim.t["interact_radius"], stove["pos"][1]]
        menu_item = sim.menu[first["dish_id"]]
        events = []

        interact(sim, events)

        self.assertEqual(sim.stock, {"ca_loc": 1})
        self.assertEqual((first["order_status"], first["reserved"]), ("assigned", {}))
        self.assertEqual((later["order_status"], later["reserved"]), ("reserved", {"ca_loc": 1}))
        self.assertEqual(stove["state"], "cooking")
        self.assertEqual(stove["cook_ticks_left"], round(menu_item["cook_s"] * TICK_HZ))
        self.assertEqual(events, [("cook_started", {
            "stove_id": stove["id"], "order_id": first["id"], "dish_id": first["dish_id"],
            "base_price": menu_item["price"], "items": ["ca_loc"],
        })])

    def test_target_tie_prefers_stoves_then_numeric_ids(self):
        sim = self.fixture("reserved")
        sim.hand = {"order_id": "C2", "dish_id": "ca_loc_nuong_trui", "base_price": 60}
        sim.stoves = [dict(sim.stoves[0], id=stove_id) for stove_id in ("B10", "B2")]
        sim.tables[0]["pos"] = list(sim.pos)
        events = []

        interact(sim, events)

        self.assertEqual([stove["state"] for stove in sim.stoves], ["idle", "cooking"])
        self.assertEqual([data["stove_id"] for _, data in events], ["B2"])
        self.assertEqual(sim.hand["order_id"], "C2")

    def test_cooking_completes_once_when_timer_reaches_zero(self):
        sim = self.fixture("ready")
        stove = sim.stoves[0]
        stove.update(state="cooking", cook_ticks_left=1)
        events = []

        finish_cooking(sim, events)
        self.assertEqual(events, [])
        self.assertEqual(stove["cook_ticks_left"], 1)
        stove["cook_ticks_left"] = 0
        finish_cooking(sim, events)
        finish_cooking(sim, events)

        self.assertEqual((stove["state"], stove["ready_ticks"]), ("ready", 0))
        self.assertEqual(events, [("dish_ready", {
            "stove_id": stove["id"], "order_id": stove["dish"]["order_id"],
            "dish_id": stove["dish"]["dish_id"],
        })])

    def test_ready_stove_with_full_hand_does_not_fall_through_to_table(self):
        sim = self.fixture("ready")
        stove = sim.stoves[0]
        customer = sim.customers[0]
        stove["dish"] = dict(stove["dish"], order_id="C2")
        sim.hand = dict(stove["dish"], order_id=customer["id"])
        sim.tables[0]["pos"] = [sim.pos[0] + sim.t["interact_radius"], sim.pos[1]]
        events = []

        interact(sim, events)

        self.assertEqual(events, [])
        self.assertEqual(stove["state"], "ready")
        self.assertEqual(sim.hand["order_id"], customer["id"])
        self.assertEqual(customer["state"], "waiting")

    def test_serve_uses_payload_price_at_tip_threshold_and_at_zero_patience(self):
        quan = self.tuning["quan"]
        threshold = round(quan["patience_s"] * TICK_HZ * quan["tip_min_patience_ratio"])
        for patience, expected_tip in ((threshold, 15), (threshold - 1, 0), (0, 0)):
            with self.subTest(patience=patience):
                sim = self.fixture("ready")
                stove = sim.stoves[0]
                dish = stove["dish"]
                dish["base_price"] = 77
                customer = sim.customers[0]
                customer["patience_ticks_left"] = patience
                events = []

                interact(sim, events)
                self.assertIs(sim.hand, dish)
                self.assertEqual(stove["state"], "idle")
                self.assertNotIn("base_price", sim.snapshot()["customers"][0])
                self.assertNotIn("tip", sim.snapshot()["customers"][0])

                sim.pos = sim.tables[0]["pos"]
                interact(sim, events)

                self.assertIsNone(sim.hand)
                self.assertEqual((customer["state"], customer["order_status"]), ("eating", "served"))
                self.assertEqual(customer["eat_ticks_left"], round(quan["eat_s"] * TICK_HZ))
                self.assertEqual((customer["base_price"], customer["tip"]), (77, expected_tip))
                self.assertEqual(sim.snapshot()["customers"][0]["base_price"], 77)
                self.assertEqual(sim.money, 0)
                self.assertEqual(events, [
                    ("dish_picked", {"stove_id": stove["id"], "order_id": customer["id"], "dish_id": dish["dish_id"]}),
                    ("served", {**dish, "table_id": customer["table_id"], "patience_ticks_left": patience, "tip": expected_tip}),
                ])

    def test_table_rejects_dish_for_another_order(self):
        sim = self.fixture("ready")
        events = []
        interact(sim, events)
        sim.hand["order_id"] = "C2"
        sim.pos = sim.tables[0]["pos"]

        interact(sim, events)

        self.assertEqual([name for name, _ in events], ["dish_picked"])
        self.assertEqual(sim.hand["order_id"], "C2")
        self.assertEqual(sim.customers[0]["order_status"], "assigned")


class QuanIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tuning = load_contract()["tuning"]

    def scenario(self, name):
        return load_scenario(FIXTURES / f"quan-{name}.json", "quan", self.tuning)

    def test_hold_interact_cooks_once_and_release_then_press_picks_up(self):
        session = Session("quan", self.tuning, self.scenario("reserved"), seed=1)
        dish = self.tuning["menu"][session.snapshot()["customers"][0]["dish_id"]]
        cook_ticks = round(dish["cook_s"] * TICK_HZ)
        player = InputPlayer([
            {"tick": 0, "interact": True},
            {"tick": cook_ticks + 1, "interact": False},
            {"tick": cook_ticks + 2, "interact": True},
        ])
        events = []

        for tick in range(cook_ticks + 3):
            events.extend(session.step(player.advance(tick)))

        self.assertEqual([(e["name"], e["tick"]) for e in events], [
            ("cook_started", 1), ("dish_ready", cook_ticks + 1), ("dish_picked", cook_ticks + 3),
        ])
        self.assertEqual(session.snapshot()["stock"], {})
        self.assertEqual(session.snapshot()["hand"]["order_id"], "C1")

    def test_serve_at_zero_patience_on_closing_tick_pays_the_fixture_price_once(self):
        scenario = self.scenario("ready")
        dish = scenario.pop("stoves")[0]["dish"]
        dish["base_price"] = 77
        scenario["hand"] = dish
        scenario["time_left_ticks"] = 1
        scenario["player"]["pos"] = self.tuning["quan"]["tables"][0]["pos"]
        scenario["customers"][0].update(patience_ticks_left=0, order_tick=17)
        session = Session("quan", self.tuning, scenario, seed=1)
        self.assertEqual(session.snapshot()["customers"][0]["order_tick"], 17)
        player = InputPlayer([{"tick": 0, "interact": True}])

        events = session.step(player.advance(0))

        self.assertEqual([e["name"] for e in events], ["served", "paid", "quan_end"])
        self.assertEqual(events[1]["data"], {
            "order_id": "C1", "table_id": "T1", "base_price": 77, "tip": 0, "amount": 77, "reason": "closing",
        })
        self.assertEqual(session.snapshot()["customers"], [])
        self.assertEqual(session.end_row()["money"], 77)

    def test_eating_timer_reaches_zero_on_closing_tick_and_gets_finished_eating_reason(self):
        scenario = self.scenario("ready")
        del scenario["stoves"]
        scenario["time_left_ticks"] = 1
        scenario["customers"][0].update(
            state="eating", order_status="served", eat_ticks_left=1, base_price=77, tip=15,
        )
        session = Session("quan", self.tuning, scenario, seed=1)

        events = session.step(InputPlayer([]).advance(0))

        self.assertEqual([e["name"] for e in events], ["paid", "quan_end"])
        self.assertEqual(events[0]["data"]["reason"], "finished_eating")
        self.assertEqual(session.end_row()["money"], 92)

    def test_non_string_dish_id_is_rejected_before_output(self):
        customer_fixture = self.scenario("reserved")
        customer_fixture["customers"][0]["dish_id"] = []
        stove_fixture = self.scenario("ready")
        stove_fixture["stoves"][0]["dish"]["dish_id"] = []

        for location, scenario in (("customer", customer_fixture), ("stove", stove_fixture)):
            with self.subTest(location=location), Workdir() as work:
                scenario_path = write_json(work.path("scenario.json"), {"quan": scenario})
                output_path = Path(work.path("output.jsonl"))

                code, stderr = run_headless(
                    "--mode", "quan", "--seed", "1", "--ticks", "1",
                    "--scenario", scenario_path, "--out", str(output_path),
                )

                self.assertEqual(code, 2, stderr)
                self.assertFalse(output_path.exists())
