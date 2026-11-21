"""Nghiệm thu gather/runner P3 của Ân, theo TICKET-03.

Mặc định chạy khi manifest1.2; khi đang migration dùng AN_REQUIRE_P3=1 để
chạy bắt buộc với tuning1.2 riêng. Không sửa manifest/runtime hoặc mock sim.
"""

from contextlib import redirect_stderr
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from chonoi.headless import main as headless_main
from chonoi.inputs import InputPlayer
from chonoi.runner import Session

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "game.contract.json").read_text(encoding="utf-8-sig"))
ENABLED = MANIFEST.get("contract_version") == "1.2" or os.environ.get("AN_REQUIRE_P3") == "1"
FRESHNESS = {"initial": 100, "gather_decay_per_s": 0.5, "quan_decay_per_s": 0.25, "spoiled_below": 30}


def item(ident, kind="ca_linh", fresh=100):
    return {"id": ident, "kind": kind, "fresh": fresh}


def monster():
    return {"id": "M1", "kind": "ca_sau", "pos": [60, 24],
            "waypoints": [[60, 24], [64, 24]]}


@unittest.skipUnless(ENABLED, "P3 chưa bật; AN_REQUIRE_P3=1 để kiểm nghiệm thu bắt buộc")
class GatherFreshnessAcceptance(unittest.TestCase):
    def setUp(self):
        self.contract = deepcopy(MANIFEST)
        self.contract["contract_version"] = "1.2"
        self.contract["tuning"]["freshness"] = dict(FRESHNESS)

    def session(self, hold=(), player=None, **extra):
        scenario = {"hold": deepcopy(list(hold)), "random_fish": False, "fish": [],
                    "monsters": [], "nodes": [], "player": {"pos": [50, 0], **(player or {})}, **extra}
        return Session("gather", self.contract["tuning"], scenario, 7)

    def step(self, session, frames=None, ticks=1):
        inputs = InputPlayer(frames or [])
        rows = []
        for tick in range(ticks):
            rows.extend(session.step(inputs.advance(tick)))
        return rows

    def held(self, session):
        held = session.snapshot()["hold"]
        self.assertIsInstance(held, list)
        for it in held:
            self.assertEqual(set(it), {"id", "kind", "fresh"})
            self.assertIsInstance(it["fresh"], (int, float))
        return held

    def test_exact_thirty_spoils_on_first_tick_once(self):
        session = self.session([item("I1", fresh=30)])
        rows = self.step(session, ticks=2)
        self.assertEqual([(r["tick"], r["data"]) for r in rows if r["name"] == "spoiled"],
                         [(1, {"item_id": "I1", "kind": "ca_linh", "location": "hold"})])
        self.assertEqual(session.snapshot()["hold_count"], 1)
        self.assertAlmostEqual(self.held(session)[0]["fresh"], 30 - 1 / 60, places=10)

    def test_sixty_ticks_decay_half_point(self):
        session = self.session([item("I1")])
        self.step(session, ticks=60)
        self.assertAlmostEqual(self.held(session)[0]["fresh"], 99.5, places=10)

    def test_exact_boundary_not_rounded_before_decision(self):
        session = self.session([item("I1", fresh=30.5)])
        rows = self.step(session, ticks=60)
        self.assertEqual([r for r in rows if r["name"] == "spoiled"], [])
        self.assertEqual(self.held(session)[0]["fresh"], 30)
        rows = self.step(session)
        self.assertEqual([r["data"]["item_id"] for r in rows if r["name"] == "spoiled"], ["I1"])

    def test_crossings_sort_by_numeric_id_without_reordering_hold(self):
        session = self.session([item("I10", fresh=30), item("I2", fresh=30), item("I7", fresh=30)])
        rows = self.step(session)
        self.assertEqual([r["data"]["item_id"] for r in rows if r["name"] == "spoiled"], ["I2", "I7", "I10"])
        self.assertEqual([it["id"] for it in self.held(session)], ["I10", "I2", "I7"])

    def test_already_spoiled_clamps_to_zero_and_keeps_slot(self):
        session = self.session([item("I1", fresh=0.001)])
        self.assertEqual([r for r in self.step(session, ticks=2) if r["name"] == "spoiled"], [])
        self.assertEqual(self.held(session), [item("I1", fresh=0)])
        self.assertEqual(session.snapshot()["hold_count"], 1)

    def test_spoiled_hold_still_blocks_harvest(self):
        capacity = self.contract["tuning"]["gather"]["hold_capacity"]
        session = self.session([item(f"I{i}", fresh=0) for i in range(1, capacity + 1)],
            nodes=[{"id": "N1", "kind": "bong_sung", "pos": [50, 0]}])
        rows = self.step(session, [{"tick": 0, "interact": True}])
        self.assertEqual([r["name"] for r in rows], ["hold_full"])
        self.assertEqual(rows[0]["data"]["free"], 0)

    def test_new_harvest_starts_full_then_decays_next_step(self):
        session = self.session(nodes=[{"id": "N1", "kind": "bong_sung", "pos": [50, 0]}])
        self.step(session, [{"tick": 0, "interact": True}])
        self.assertEqual(self.held(session), [item("I1", "bong_sung", 100)])
        self.step(session)
        self.assertAlmostEqual(self.held(session)[0]["fresh"], 100 - 1 / 120, places=10)

    def test_fish_yield_has_distinct_objects_and_monotonic_ids(self):
        session = self.session([item("I10", "ca_loc")], player={"pos": [50, 10]},
            fish=[{"id": "F1", "kind": "ca_linh", "pos": [50, 10]}])
        self.step(session, [{"tick": 0, "catch": True}])
        held = self.held(session)
        self.assertEqual([it["id"] for it in held], ["I10", "I11", "I12", "I13"])
        self.assertTrue(all(it["fresh"] == 100 for it in held[1:]))
        self.assertEqual(len({id(it) for it in session.sim.hold}), 4)

    def test_hit_and_faint_lost_are_lifo_individuals(self):
        initial = [item("I10", "ca_loc", 100), item("I2", "bong_sung", 80),
                   item("I7", "ca_linh", 60), item("I4", "ca_keo", 40), item("I8", "keo_neo", 20)]
        session = self.session(initial, player={"pos": [60, 24], "hp": 1}, monsters=[monster()])
        rows = self.step(session)
        self.assertEqual([r["name"] for r in rows], ["monster_hit", "faint", "gather_end"])
        hit, faint, end = [r["data"] for r in rows]
        self.assertEqual([it["id"] for it in hit["lost"]], ["I8", "I4"])
        self.assertEqual([it["id"] for it in faint["lost"]], ["I7", "I2", "I10"])
        originals = {it["id"]: it for it in initial}
        for it in hit["lost"] + faint["lost"]:
            self.assertEqual(set(it), {"id", "kind", "fresh"})
            self.assertAlmostEqual(float(it["fresh"]), originals[it["id"]]["fresh"] - 1 / 120, places=10)
        self.assertEqual(end["inventory"], {"items": []})
        self.assertEqual(faint["cause"], "monster")

    def test_spoiled_precedes_lethal_choke_and_faint(self):
        session = self.session([item("I7", fresh=30), item("I2", "ca_loc", 90)],
            player={"pos": [50, 10], "hp": 1, "oxygen_ticks": 0, "zero_oxy_ticks": 59})
        rows = self.step(session)
        self.assertEqual([r["name"] for r in rows], ["spoiled", "choke", "faint", "gather_end"])
        self.assertEqual([it["id"] for it in rows[2]["data"]["lost"]], ["I2", "I7"])

    def test_pause_freezes_freshness_resume_decays_immediately(self):
        session = self.session([item("I1", fresh=30)])
        rows = self.step(session, [{"tick": 0, "pause": True}, {"tick": 1, "pause": False},
                                   {"tick": 3, "pause": True}], ticks=4)
        spoiled = [r for r in rows if r["name"] == "spoiled"]
        self.assertEqual([(r["tick"], r["data"]["item_id"]) for r in spoiled], [(4, "I1")])
        self.assertEqual(session.sim_tick, 1)

    def test_input_fixture_is_not_mutated(self):
        original = [item("I2", fresh=80), item("I10", fresh=90)]
        scene = {"hold": original, "random_fish": False, "monsters": [], "nodes": []}
        saved = deepcopy(scene)
        session = Session("gather", self.contract["tuning"], scene, 1)
        self.step(session, ticks=60)
        self.assertEqual(scene, saved)

    def test_inventory_end_sorts_copy_preserving_hold_order(self):
        session = self.session([item("I10"), item("I2", "ca_loc")], time_left_ticks=1)
        rows = self.step(session)
        self.assertEqual(rows[-1]["name"], "gather_end")
        self.assertEqual([it["id"] for it in rows[-1]["data"]["inventory"]["items"]], ["I2", "I10"])
        self.assertEqual([it["id"] for it in self.held(session)], ["I10", "I2"])

    def cli(self, directory, scenario, ticks, inputs=None, *, name="gather", inventory=None):
        scene = directory / f"{name}-scene.json"
        commands = directory / f"{name}-inputs.json"
        output = directory / f"{name}.jsonl"
        scene.write_text(json.dumps(scenario), encoding="utf-8")
        commands.write_text(json.dumps({"frames": inputs or []}), encoding="utf-8")
        args = ["--mode", name, "--seed", "7", "--ticks", str(ticks), "--scenario", str(scene),
                "--inputs", str(commands), "--out", str(output)]
        if inventory is not None:
            args += ["--inventory-out" if name == "gather" else "--inventory", str(inventory)]
        errors = io.StringIO()
        # Chọn manifest test1.2, nhưng chạy loader/runner/sim/writer thật.
        with patch("chonoi.headless.load_contract", return_value=deepcopy(self.contract)), redirect_stderr(errors):
            code = headless_main(args)
        self.assertEqual(code, 0, errors.getvalue())
        return [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]

    def test_cli_threshold_from_prd(self):
        with tempfile.TemporaryDirectory() as temp:
            rows = self.cli(Path(temp), {"gather": {"hold": [item("I1", fresh=30)],
                            "random_fish": False, "monsters": []}}, 1)
        spoiled = [r for r in rows if r.get("name") == "spoiled"]
        self.assertEqual([(r["tick"], r["data"]) for r in spoiled],
                         [(1, {"item_id": "I1", "kind": "ca_linh", "location": "hold"})])

    def test_cli_file_matches_end_and_quan_without_extra_decay(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            inventory = folder / "inventory.json"
            scenario = {"gather": {"hold": [item("I10", fresh=100), item("I2", "ca_loc", 29.9999)],
                                   "random_fish": False, "monsters": []}}
            rows = self.cli(folder, scenario, 1, [{"tick": 0, "interact": True}], inventory=inventory)
            saved = json.loads(inventory.read_text(encoding="utf-8"))
            ended = next(r for r in rows if r.get("name") == "gather_end")
            self.assertEqual(saved, ended["data"]["inventory"])
            self.assertEqual([it["id"] for it in saved["items"]], ["I2", "I10"])
            self.assertLess(saved["items"][0]["fresh"], 30)
            quan = self.cli(folder, {}, 0, name="quan", inventory=inventory)
            self.assertEqual(quan[0]["stock"], saved["items"])

    def test_cli_tick_limit_preserves_existing_destination(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            inventory = folder / "inventory.json"
            sentinel = b"existing inventory must remain untouched\n"
            inventory.write_bytes(sentinel)
            self.cli(folder, {"gather": {"hold": [item("I1")], "random_fish": False,
                                        "monsters": []}}, 1, inventory=inventory)
            self.assertEqual(inventory.read_bytes(), sentinel)


if __name__ == "__main__":
    unittest.main()
