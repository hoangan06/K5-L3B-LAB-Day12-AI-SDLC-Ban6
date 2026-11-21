"""Kiểm chứng phần Ân: tick biên, ngất và kho qua CLI thật."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from chonoi.contract import load_contract
from helpers import hold_of, v12

# Unit test P1 (kho đếm). Từ v1.2 (TICKET-03) runtime dùng kho cá thể, nên test này giữ manifest P1 cố định.
FIXTURE_CONTRACT = Path(__file__).resolve().parent / "fixtures/phase-1/game.contract.json"
from chonoi.inputs import InputState
from chonoi.runner import Session


ROOT = Path(__file__).resolve().parents[1]


class GatherAn(unittest.TestCase):
    def session(self, player=None, **scenario):
        tuning = copy.deepcopy(load_contract(FIXTURE_CONTRACT)["tuning"])
        scenario["player"] = {"pos": [50, 10], **(player or {})}
        return Session("gather", tuning, scenario, 7)

    def advance(self, session, count=1, move=(0, 0), edges=()):
        rows = []
        for _ in range(count):
            rows.extend(session.step(InputState(move, {}, set(edges))))
        return rows

    def test_underwater_consumes_one_tick(self):
        session = self.session()
        oxygen = session.sim.oxygen_ticks
        self.assertEqual(self.advance(session), [])
        self.assertEqual(session.sim.oxygen_ticks, oxygen - 1)
        self.assertEqual(session.sim.hp, session.sim.t["hp_max"])

    def test_surface_boundary_refills_and_caps(self):
        for depth in (0, 0.5):
            with self.subTest(depth=depth):
                session = self.session({"pos": [50, depth], "oxygen_ticks": 1})
                self.advance(session)
                self.assertEqual(session.sim.oxygen_ticks, 7)
                session.sim.oxygen_ticks = session.sim.oxygen_max - 1
                self.advance(session)
                self.assertEqual(session.sim.oxygen_ticks, session.sim.oxygen_max)

    def test_empty_event_once_and_first_choke_at_t_plus_59(self):
        session = self.session({"oxygen_ticks": 1})
        rows = self.advance(session, 60)
        self.assertEqual([(r["tick"], r["name"]) for r in rows],
                         [(1, "oxygen_empty"), (60, "choke")])
        self.assertEqual(session.sim.hp, 2)
        self.assertEqual(session.sim.zero_oxy_ticks, 0)

    def test_choke_repeats_every_interval(self):
        session = self.session({"oxygen_ticks": 0})
        rows = self.advance(session, 120)
        self.assertEqual([(r["tick"], r["data"]["hp"]) for r in rows], [(60, 2), (120, 1)])

    def test_surface_on_choke_step_saves_player(self):
        session = self.session({"pos": [50, 0.501], "oxygen_ticks": 0,
                                "zero_oxy_ticks": 59, "hp": 1})
        rows = self.advance(session, move=(0, -1))
        self.assertEqual([r["name"] for r in rows], ["surface"])
        self.assertEqual(session.sim.oxygen_ticks, 6)
        self.assertEqual(session.sim.zero_oxy_ticks, 0)
        self.assertEqual(session.sim.hp, 1)
        self.assertFalse(session.done)

    def test_dive_uses_final_depth_and_emits_only_on_crossing(self):
        session = self.session({"pos": [50, 0.5], "oxygen_ticks": 10})
        rows = self.advance(session, move=(0, 1))
        self.assertEqual([r["name"] for r in rows], ["dive"])
        self.assertEqual(session.sim.oxygen_ticks, 9)
        saved_position = list(rows[0]["data"]["pos"])
        self.assertEqual(self.advance(session, move=(0, 1)), [])
        self.assertEqual(rows[0]["data"]["pos"], saved_position)

    def test_surface_resets_partial_choke_counter(self):
        session = self.session({"pos": [50, 0.501], "oxygen_ticks": 0, "zero_oxy_ticks": 58})
        self.advance(session, move=(0, -1))
        self.assertEqual(session.sim.zero_oxy_ticks, 0)
        self.assertGreater(session.sim.oxygen_ticks, 0)

    def test_faint_clears_hold_lifo_before_end(self):
        session = self.session({"oxygen_ticks": 0, "zero_oxy_ticks": 59, "hp": 1},
                               hold=["ca_loc", "bong_sung", "ca_linh"])
        rows = self.advance(session)
        self.assertEqual([r["name"] for r in rows], ["choke", "faint", "gather_end"])
        self.assertEqual(rows[1]["data"], {"cause": "choke", "hp": 0,
                                          "lost": ["ca_linh", "bong_sung", "ca_loc"]})
        self.assertEqual(rows[2]["data"], {"reason": "fainted", "inventory": {"items": {}}})
        self.assertEqual(session.sim.hold, [])
        self.assertEqual(session.snapshot()["hold_count"], 0)
        self.assertEqual(session.end_row()["reason"], "fainted")

    def test_faint_precedes_dock_catch_and_time(self):
        session = self.session({"pos": [2, 1], "oxygen_ticks": 0,
                                "zero_oxy_ticks": 59, "hp": 1}, time_left_ticks=1)
        rows = self.advance(session, edges=("interact", "catch"))
        self.assertEqual([r["name"] for r in rows], ["choke", "faint", "gather_end"])
        self.assertEqual(session.sim.reason, "fainted")

    def test_dock_on_final_tick_wins_over_time(self):
        session = self.session({"pos": [2, 0]}, hold=["ca_loc"], time_left_ticks=1)
        rows = self.advance(session, edges=("interact",))
        self.assertEqual([r["name"] for r in rows], ["gather_end"])
        self.assertEqual(session.sim.reason, "docked")
        self.assertEqual(session.sim.inventory_items(), {"ca_loc": 1})

    def test_time_keeps_hold_underwater(self):
        session = self.session(hold=["ca_loc"], time_left_ticks=1)
        self.advance(session)
        self.assertEqual(session.sim.reason, "time")
        self.assertEqual(session.sim.inventory_items(), {"ca_loc": 1})

    def test_finished_sim_does_not_emit_end_again(self):
        session = self.session(time_left_ticks=1)
        self.advance(session)
        self.assertEqual(session.sim.step(InputState((0, 0), {}, set())), [])

    def test_existing_movement_limits_and_heading(self):
        session = self.session({"pos": [99.99, 29.99]})
        self.advance(session, 120, move=(1 / 2**0.5, 1 / 2**0.5))
        self.assertEqual(session.sim.pos, [100, 30])
        self.assertEqual(session.sim.vel, [0, 0])
        self.assertAlmostEqual(session.sim.heading, 45)

    def test_regrow_event_precedes_oxygen_and_timers_decrease_once(self):
        session = self.session({"oxygen_ticks": 1, "catch_cd_ticks": 2},
                               nodes=[{"id": "N10", "kind": "bong_sung", "pos": [50, 0], "regrow_ticks": 1},
                                      {"id": "N2", "kind": "bong_sung", "pos": [60, 0], "regrow_ticks": 1}])
        before = session.sim.time_left_ticks
        rows = self.advance(session)
        self.assertEqual([r["name"] for r in rows], ["node_regrown", "node_regrown", "oxygen_empty"])
        self.assertEqual([r["data"]["node_id"] for r in rows[:2]], ["N2", "N10"])
        self.assertEqual(session.sim.catch_cd_ticks, 1)
        self.assertEqual(session.sim.time_left_ticks, before - 1)

    def test_cli_faint_writes_empty_inventory_and_stops_early(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            scenario = folder / "scenario.json"
            scenario.write_text(json.dumps({"gather": {"player": {"pos": [50, 10],
                "oxygen_ticks": 0, "zero_oxy_ticks": 59, "hp": 1}, "hold": hold_of(["ca_loc"])}}), encoding="utf-8")
            output, inventory = folder / "out.jsonl", folder / "inventory.json"
            result = subprocess.run([sys.executable, "-m", "chonoi.headless", "--mode", "gather",
                "--seed", "7", "--ticks", "100", "--scenario", str(scenario),
                "--out", str(output), "--inventory-out", str(inventory)], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            # Ngất ghi kho rỗng; v1.2 là {"items": []} (TICKET-03)
            self.assertEqual(json.loads(inventory.read_text(encoding="utf-8")), {"items": [] if v12() else {}})
            rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(rows[-1]["reason"], "fainted")
            self.assertEqual(rows[-1]["ticks"], 1)
            self.assertEqual(sum(r["type"] == "end" for r in rows), 1)

    def test_integrated_regrow_then_gather_on_last_tick(self):
        session = self.session({"pos": [50, 0]}, time_left_ticks=1,
            nodes=[{"id": "N1", "kind": "bong_sung", "pos": [50, 0], "regrow_ticks": 1}])
        rows = self.advance(session, edges=("interact",))
        self.assertEqual([r["name"] for r in rows], ["node_regrown", "gather", "gather_end"])
        self.assertEqual(rows[-1]["data"]["inventory"], {"items": {"bong_sung": 1}})

    def test_integrated_catch_on_last_tick_keeps_yield(self):
        session = self.session(time_left_ticks=1,
            fish=[{"id": "F1", "kind": "ca_linh", "pos": [50, 10]}])
        rows = self.advance(session, edges=("catch",))
        self.assertEqual([r["name"] for r in rows], ["fish_caught", "gather_end"])
        self.assertEqual(session.sim.inventory_items(), {"ca_linh": 3})

    def test_integrated_dock_precedes_nearby_node(self):
        session = self.session({"pos": [2, 0]},
            nodes=[{"id": "N1", "kind": "bong_sung", "pos": [2, 0]}])
        rows = self.advance(session, edges=("interact",))
        self.assertEqual([r["name"] for r in rows], ["gather_end"])
        self.assertEqual(session.sim.hold, [])

    def test_integrated_held_interact_does_not_gather_twice(self):
        from chonoi.inputs import InputPlayer
        session = self.session({"pos": [50, 0]},
            nodes=[{"id": "N1", "kind": "bong_sung", "pos": [50, 0]},
                   {"id": "N2", "kind": "bong_sung", "pos": [50, 0]}])
        inputs = InputPlayer([{"tick": 0, "interact": True}])
        rows = session.step(inputs.advance(0)) + session.step(inputs.advance(1))
        self.assertEqual([r["name"] for r in rows], ["gather"])
        self.assertEqual(session.sim.hold, ["bong_sung"])


if __name__ == "__main__":
    unittest.main()
