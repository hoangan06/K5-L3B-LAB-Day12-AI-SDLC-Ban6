"""Test nền tảng P2; FakeDay chỉ kiểm giao thức, không thay code của Đức."""

from contextlib import redirect_stderr
import io
import json
from pathlib import Path
import tempfile
from types import ModuleType
import unittest
from unittest.mock import patch

from chonoi.contract import load_contract
from chonoi.errors import BadInput
from chonoi.headless import main
from chonoi.inputs import BUTTONS_V11, InputPlayer, LiveInputs, load_frames
from chonoi.runner import Session, build_sim, run


class FakeDay:
    """Controller tối thiểu kiểm Session không làm mất phase/day của event."""
    mode = "day"

    def __init__(self, tuning, scenario, streams, ids, *, days=1):
        self.phase = "gather"
        self.day = 1
        self.phase_tick = 0
        self.time_left_ticks = 3
        self.money = self.earned = 200
        self.reputation = 3.0
        self.days_completed = 0
        self.done = False
        self.reason = None
        self.calls = []
        self.days = days

    def initial_events(self):
        return [{"phase": "gather", "day": 1, "name": name, "data": {}}
                for name in ("day_start", "day_plan", "phase_start")]

    def snapshot(self):
        return {"day": self.day, "day_plan": {}, "upgrades": {}, "active_upgrades": {}}

    def step(self, inp):
        self.calls.append(inp)
        self.phase_tick += 1
        old = self.phase
        if old == "gather":
            self.phase = "quan"
            name = "gather_end"
        elif old == "quan":
            self.phase = "shop"
            name = "quan_end"
        else:
            name = "shop_end"
            self.days_completed += 1
            self.done = True
            self.reason = "days_complete"
        events = [{"phase": old, "day": self.day, "name": name, "data": {}}]
        if not self.done:
            self.phase_tick = 0
            events.append({"phase": self.phase, "day": self.day, "name": "phase_start", "data": {}})
        return events


class P2Inputs(unittest.TestCase):
    def load(self, frames):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "inputs.json"
            path.write_text(json.dumps({"frames": frames}), encoding="utf-8")
            return load_frames(path, buttons=BUTTONS_V11)

    def test_buy_is_only_on_declared_frame(self):
        player = InputPlayer(self.load([{"tick": 0, "buy": "oxygen"},
                                       {"tick": 2, "buy": "oxygen"}]))
        self.assertEqual([player.advance(t).buy for t in range(4)], ["oxygen", None, "oxygen", None])

    def test_bool_edges_persist_across_frames(self):
        player = InputPlayer(self.load([{"tick": 0, "shop_done": True},
                                       {"tick": 2, "shop_done": False},
                                       {"tick": 3, "shop_done": True}]))
        self.assertEqual([player.advance(t).pressed("shop_done") for t in range(4)],
                         [True, False, False, True])

    def test_invalid_buy_and_bool_are_rejected(self):
        for value in (None, 0, True, [], "", " "):
            with self.subTest(value=value), self.assertRaises(BadInput):
                self.load([{"tick": 0, "buy": value}])
        with self.assertRaises(BadInput):
            self.load([{"tick": 0, "pause": 1}])

    def test_unknown_field_rejected_but_extensions_parse(self):
        self.load([{"tick": 0, "attack": True, "photo": False}])
        with self.assertRaises(BadInput):
            self.load([{"tick": 0, "teleport": True}])

    def test_live_buy_queue_is_fifo_and_not_held(self):
        inputs = LiveInputs()
        inputs.set(buy="oxygen", shop_done=True)
        inputs.set(buy="hp")
        first, second, third = inputs.advance(), inputs.advance(), inputs.advance()
        self.assertEqual([first.buy, second.buy, third.buy], ["oxygen", "hp", None])
        self.assertTrue(first.pressed("shop_done"))
        self.assertFalse(second.pressed("shop_done"))

    def test_live_rejects_invalid_buy_before_changing_buttons(self):
        inputs = LiveInputs()
        with self.assertRaises(BadInput):
            inputs.set(buy=True, pause=True)
        self.assertFalse(inputs.advance().pressed("pause"))


class P2Session(unittest.TestCase):
    def setUp(self):
        self.tuning = load_contract()["tuning"]

    def day(self):
        fake = FakeDay(self.tuning, {}, None, None)
        with patch("chonoi.runner.build_sim", return_value=fake):
            session = Session("day", self.tuning, {}, 1)
        return session

    def test_pause_freezes_real_gather_and_resume_runs_immediately(self):
        session = Session("gather", self.tuning, {"player": {"pos": [50, 10]}}, 1)
        inputs = InputPlayer([{"tick": 0, "pause": True}, {"tick": 1, "pause": False},
                              {"tick": 2, "pause": True}])
        before = session.sim.time_left_ticks, session.sim.oxygen_ticks
        self.assertEqual([r["name"] for r in session.step(inputs.advance(0))], ["paused"])
        session.step(inputs.advance(1))
        self.assertEqual((session.sim.time_left_ticks, session.sim.oxygen_ticks), before)
        self.assertEqual((session.tick, session.sim_tick, session.phase_tick), (2, 0, 0))
        self.assertEqual(session.snapshot()["state"], "paused")
        self.assertEqual([r["name"] for r in session.step(inputs.advance(2))], ["resumed"])
        self.assertEqual((session.tick, session.sim_tick, session.phase_tick), (3, 1, 1))
        self.assertEqual(session.sim.oxygen_ticks, before[1] - 1)

    def test_pause_freezes_real_quan_counter(self):
        session = Session("quan", self.tuning, {"random_customers": False}, 1)
        inputs = InputPlayer([{"tick": 0, "pause": True}])
        session.step(inputs.advance(0))
        self.assertEqual(session.sim.phase_tick, 0)
        self.assertEqual(session.sim_tick, 0)
        self.assertEqual(session.end_row()["reason"], "tick_limit")
        self.assertEqual(session.end_row()["state"], "paused")

    def test_buy_during_pause_is_not_replayed(self):
        session = self.day()
        inputs = InputPlayer([{"tick": 0, "pause": True, "buy": "hp"},
                              {"tick": 1, "pause": False, "buy": "oxygen"},
                              {"tick": 2, "pause": True}])
        for tick in range(3):
            session.step(inputs.advance(tick))
        self.assertEqual(len(session.sim.calls), 1)
        self.assertIsNone(session.sim.calls[0].buy)

    def test_resume_forwards_new_action_in_same_frame(self):
        session = self.day()
        inputs = InputPlayer([{"tick": 0, "pause": True}, {"tick": 1, "pause": False},
                              {"tick": 2, "pause": True, "buy": "hp"}])
        for tick in range(3):
            rows = session.step(inputs.advance(tick))
        self.assertEqual(rows[0]["name"], "resumed")
        self.assertEqual(session.sim.calls[0].buy, "hp")

    def test_event_old_phase_snapshot_new_phase_and_initial_drain(self):
        session = self.day()
        first = session.initial_events()
        self.assertEqual([r["name"] for r in first], ["day_start", "day_plan", "phase_start"])
        self.assertTrue(all(r["tick"] == 0 and r["day"] == 1 for r in first))
        self.assertEqual(session.initial_events(), [])
        rows = session.step(InputPlayer([]).advance(0))
        self.assertEqual([(r["phase"], r["name"]) for r in rows],
                         [("gather", "gather_end"), ("quan", "phase_start")])
        snapshot = session.snapshot()
        self.assertEqual((snapshot["phase"], snapshot["phase_tick"], snapshot["sim_tick"]), ("quan", 0, 1))

    def test_held_interact_not_recreated_across_phase_change(self):
        session = self.day()
        inputs = InputPlayer([{"tick": 0, "interact": True}])
        for tick in range(2):
            session.step(inputs.advance(tick))
        self.assertEqual([inp.pressed("interact") for inp in session.sim.calls], [True, False])

    def test_day_end_has_completion_and_stops_after_done(self):
        session = self.day()
        for tick in range(3):
            session.step(InputPlayer([]).advance(tick))
        end = session.end_row()
        self.assertEqual((end["days_completed"], end["reason"], end["sim_tick"]), (1, "days_complete", 3))
        self.assertEqual(session.step(InputPlayer([]).advance(3)), [])
        self.assertEqual(session.tick, 3)

    def test_run_forces_snapshot_on_phase_change_and_end_last(self):
        with tempfile.TemporaryDirectory() as temp, patch("chonoi.runner.build_sim", side_effect=lambda *a, **k: FakeDay(*a[1:3], None, None)):
            path = Path(temp) / "day.jsonl"
            run("day", self.tuning, {}, 1, [], 3, path, 10)
            rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual([r["name"] for r in rows[:3]], ["day_start", "day_plan", "phase_start"])
            self.assertEqual([(r["tick"], r["phase_tick"]) for r in rows if r["type"] == "snapshot"],
                             [(0, 0), (1, 0), (2, 0), (3, 1)])
            self.assertEqual(rows[-1]["reason"], "days_complete")

    def test_factory_passes_days_to_real_module_interface(self):
        module = ModuleType("chonoi.sim.day")
        module.DaySim = FakeDay
        with patch.dict("sys.modules", {"chonoi.sim.day": module}):
            sim = build_sim("day", self.tuning, {}, 1, None, days=5)
        self.assertEqual(sim.days, 5)

    def test_invalid_session_days(self):
        for days in (0, 6, True, 1.5):
            with self.subTest(days=days), self.assertRaises(BadInput):
                Session("day", self.tuning, {}, 1, days=days)
        with self.assertRaises(BadInput):
            Session("gather", self.tuning, {}, 1, days=2)


class P2CLI(unittest.TestCase):
    def test_days_invalid_before_output(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "out.jsonl"
            for mode, days in (("gather", "1"), ("quan", "2"), ("day", "0"), ("day", "6")):
                with self.subTest(mode=mode, days=days), redirect_stderr(io.StringIO()):
                    self.assertEqual(main(["--mode", mode, "--seed", "1", "--ticks", "0",
                                           "--days", days, "--out", str(out)]), 2)
                    self.assertFalse(out.exists())

    def test_day_inventory_flags_rejected(self):
        for flag in ("--inventory", "--inventory-out"):
            with self.subTest(flag=flag), redirect_stderr(io.StringIO()):
                self.assertEqual(main(["--mode", "day", "--seed", "1", "--ticks", "0",
                                       "--out", "unused.jsonl", flag, "unused.json"]), 2)

    def test_cli_passes_days_and_full_day_scenario(self):
        contract = load_contract()
        contract["contract_version"] = "1.1"
        scenario = {"day": {"money": 200, "earned": 200}, "gather": {"hold": ["ca_loc"]}}
        with patch("chonoi.headless.load_contract", return_value=contract), \
             patch("chonoi.headless.load_scenario", return_value=scenario), \
             patch("chonoi.headless.run") as execute, redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--mode", "day", "--seed", "7", "--ticks", "10",
                                   "--days", "5", "--out", "unused.jsonl"]), 0)
        self.assertEqual(execute.call_args.args[2], scenario)
        self.assertEqual(execute.call_args.kwargs["days"], 5)


if __name__ == "__main__":
    unittest.main()
