import json
import unittest
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from chonoi import TICK_HZ
from chonoi.errors import BadInput
from chonoi.ids import IdAllocator
from chonoi.live import LiveGame
from chonoi.rng import Streams
from chonoi.sim.day import DaySim
from chonoi.sim.shop import ShopSim


SAMPLE = Path(__file__).resolve().parents[1] / "docs/contracts/phase-2-tuning.sample.json"


def tuning():
    return json.loads(SAMPLE.read_text(encoding="utf-8-sig"))["tuning"]


def action(*edges, buy=None):
    return SimpleNamespace(buy=buy, move=(0, 0), pressed=edges.__contains__)


class ShopTests(unittest.TestCase):
    def setUp(self):
        self.tuning = tuning()
        self.context = {"money": 200, "earned": 480, "reputation": 3.2, "upgrades": {"oxygen": 0, "hp": 0}}

    def shop(self):
        return ShopSim(self.tuning, {"stock": {"bong_sung": 2}}, Streams(1), IdAllocator(), context=self.context)

    def test_exact_price_changes_only_working_money_and_upgrade(self):
        shop = self.shop()
        self.assertEqual(shop.step(action(buy="oxygen")), [
            ("bought", {"upgrade": "oxygen", "level": 1, "price": 200, "money": 0}),
        ])
        self.assertEqual((shop.money, shop.earned, shop.reputation), (0, 480, 3.2))
        self.assertEqual(shop.upgrades, {"oxygen": 1, "hp": 0})
        self.assertEqual(self.context["upgrades"], {"oxygen": 0, "hp": 0})
        self.assertEqual(shop.snapshot()["stock"], {"bong_sung": 2})
        self.assertEqual(shop.phase_tick, 1)

    def test_unknown_funds_and_max_level(self):
        self.context["upgrades"]["hp"] = 2
        self.context["money"] = 199
        shop = self.shop()
        for name, reason in (("net", "unknown"), ("oxygen", "funds"), ("hp", "max_level")):
            with self.subTest(name=name):
                self.assertEqual(shop.step(action(buy=name)), [("buy_failed", {"action": name, "reason": reason})])
        self.assertEqual(shop.money, 199)
        self.assertEqual(shop.upgrades, {"oxygen": 0, "hp": 2})

    def test_purchase_before_done_on_last_tick(self):
        self.tuning["shop"]["max_ticks"] = 1
        shop = self.shop()
        self.assertEqual(shop.step(action("shop_done", buy="oxygen")), [
            ("bought", {"upgrade": "oxygen", "level": 1, "price": 200, "money": 0}),
            ("shop_end", {"reason": "done"}),
        ])
        self.assertTrue(shop.done)
        self.assertEqual(shop.time_left_ticks, 0)
        self.assertEqual(shop.step(action("shop_done")), [])

    def test_no_input_times_out_at_configured_tick(self):
        shop = self.shop()
        for _ in range(self.tuning["shop"]["max_ticks"] - 1):
            self.assertEqual(shop.step(action()), [])
        self.assertEqual(shop.step(action()), [("shop_end", {"reason": "time"})])
        self.assertEqual(shop.phase_tick, self.tuning["shop"]["max_ticks"])


class ShortGather:
    phase = "gather"

    def __init__(self, tuning, scenario, streams, ids, *, context):
        self.context = context
        self.scenario = scenario
        self.phase_tick = 0
        self.time_left_ticks = 1
        self.money, self.earned, self.reputation = (context[k] for k in ("money", "earned", "reputation"))
        self.done = False

    def step(self, inp):
        self.phase_tick += 1
        self.time_left_ticks = 0
        self.done = True
        return [("gather_end", {"reason": "docked", "inventory": {"items": self.inventory_items()}})]

    def inventory_items(self):
        return {"bong_sung": 2}

    def snapshot(self):
        return {"hold": [], "hold_capacity": 12}


class DayFixture(unittest.TestCase):
    def setUp(self):
        self.tuning = tuning()
        self.scenario = {"day": {"money": 200, "earned": 250}, "quan": {"time_left_ticks": 1, "random_customers": False}}
        self.tuning["shop"]["max_ticks"] = 1
        patcher = patch("chonoi.sim.day.GatherSim", ShortGather)
        patcher.start()
        self.addCleanup(patcher.stop)

    def day(self, days=1):
        return DaySim(self.tuning, self.scenario, Streams(1), IdAllocator(), days=days)


class DayTests(DayFixture):
    def test_transitions_keep_old_event_provenance_and_start_next_phase_at_zero(self):
        sim = self.day()
        self.assertEqual([(e["phase"], e["day"], e["name"]) for e in sim.initial_events()], [
            ("gather", 1, "day_start"), ("gather", 1, "day_plan"), ("gather", 1, "phase_start"),
        ])
        rows = sim.step(action())
        self.assertEqual([(e["phase"], e["name"]) for e in rows], [("gather", "gather_end"), ("quan", "phase_start")])
        self.assertEqual((sim.phase, sim.phase_tick), ("quan", 0))
        self.assertEqual(sim.current_sim.allowed_dishes, sorted(sim.day_plan["dishes"]))
        self.assertEqual(sim.current_sim.stock, {"bong_sung": 2})
        sim.step(action())
        self.assertEqual((sim.phase, sim.phase_tick, sim.days_completed), ("shop", 0, 0))
        self.assertFalse(sim.done)
        self.assertEqual(sim.snapshot()["stock"], {"bong_sung": 2})
        sim.step(action())
        self.assertEqual((sim.done, sim.reason, sim.days_completed), (True, "days_complete", 1))

    def test_upgrade_becomes_active_only_in_next_day_and_stock_does_not_carry(self):
        sim = self.day(days=2)
        first = sim.current_sim.context
        sim.step(action())
        sim.step(action())
        rows = sim.step(action("shop_done", buy="oxygen"))
        self.assertEqual([(e["day"], e["name"]) for e in rows], [
            (1, "bought"), (1, "shop_end"), (2, "day_start"), (2, "day_plan"), (2, "phase_start"),
        ])
        self.assertEqual(first["active_upgrades"]["oxygen"], 0)
        self.assertEqual(sim.snapshot()["active_upgrades"]["oxygen"], 1)
        self.assertEqual(sim.current_sim.context["oxygen_max_ticks"], 45 * TICK_HZ)
        self.assertEqual(sim.current_sim.scenario, {})
        self.assertEqual((sim.money, sim.earned, sim.days_completed), (0, 250, 1))

    def test_completes_five_days_after_fifth_shop(self):
        sim = self.day(days=5)
        for day in range(1, 6):
            self.assertEqual((sim.day, sim.phase), (day, "gather"))
            sim.step(action())
            sim.step(action())
            self.assertEqual((sim.days_completed, sim.phase), (day - 1, "shop"))
            sim.step(action("shop_done"))
        self.assertEqual((sim.days_completed, sim.phase, sim.reason), (5, "shop", "days_complete"))

    def test_static_invalid_fixture_is_rejected(self):
        for bad in ({"day": {"money": 1}}, {"day": {"money": True, "earned": 1}},
                    {"day": {"reputation": float("nan")}}, {"day": {"upgrades": {"hp": 3}}},
                    {"quan": {"stock": {}}}, {"shop": {}}):
            with self.subTest(scenario=bad), self.assertRaises(BadInput):
                DaySim(self.tuning, bad, Streams(1), IdAllocator())


class ProbeInputs:
    def __init__(self, *, buttons):
        self.buttons = buttons
        self.pending = action()

    def set(self, move=None, **commands):
        self.pending = action(*(name for name in self.buttons if commands.get(name)), buy=commands.get("buy"))

    def advance(self):
        previous = self.pending
        self.pending = action()
        return previous


class ProbeSession:
    def __init__(self, mode, tuning, scenario, seed, inventory, *, days):
        self.tick = 0
        self.sim = DaySim(tuning, deepcopy(scenario), Streams(seed), IdAllocator(), days=days)
        self.paused = False

    @property
    def done(self):
        return self.sim.done

    def initial_events(self):
        return self.sim.initial_events()

    def step(self, inp):
        self.tick += 1
        if inp.pressed("pause"):
            self.paused = not self.paused
        return [] if self.paused else self.sim.step(inp)

    def snapshot(self):
        return {"tick": self.tick, "mode": "day", "phase": self.sim.phase,
                "state": "paused" if self.paused else "playing", **self.sim.snapshot()}


class LiveDayTests(DayFixture):
    @patch("chonoi.live.Session", ProbeSession)
    @patch("chonoi.live.LiveInputs", ProbeInputs)
    def test_presentation_routes_all_phases_through_session(self):
        game = LiveGame("day", self.tuning, self.scenario, seed=1, days=2)

        def state():
            return json.loads(game.state_json())

        self.assertEqual(state()["ui"]["screen"], "menu")
        game._tick_once()
        self.assertEqual(game.session.tick, 0)
        game.ui_action("start")
        self.assertEqual(state()["ui"]["screen"], "day_intro")
        game._tick_once()
        self.assertEqual(game.session.tick, 0)
        game.ui_action("continue")
        game.set_input({"pause": True})
        game._tick_once()
        self.assertEqual(state()["state"], "paused")
        self.assertEqual(state()["phase"], "gather")
        game.set_input({"pause": True})
        game._tick_once()
        self.assertEqual(state()["ui"]["screen"], "evening_intro")
        game.ui_action("continue")
        game._tick_once()
        self.assertEqual(state()["ui"]["screen"], "day_result")
        game.ui_action("continue")
        game.set_input({"buy": "oxygen", "shop_done": True})
        game._tick_once()
        self.assertEqual((state()["day"], state()["ui"]["screen"]), (2, "day_intro"))
        self.assertEqual(state()["active_upgrades"]["oxygen"], 1)
        for _ in range(3):
            game.ui_action("continue")
            game._tick_once()
        self.assertEqual(state()["ui"]["screen"], "summary")
        self.assertTrue(game.session.done)
        self.assertEqual([row["day"] for row in state()["ui"]["days"]], [1, 2])
