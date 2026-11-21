"""Hồi quy từ các lỗi đã tái hiện khi Ân rà bản nộp cuối."""

from contextlib import redirect_stderr
from copy import deepcopy
from fractions import Fraction
import io
import json
import math
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from chonoi.contract import load_contract
from chonoi.errors import BadInput
from chonoi.headless import main
from chonoi.ids import IdAllocator, id_key, sort_by_id
from chonoi.reputation import adjust_reputation
from chonoi.runner import Session
from chonoi.soak import Bot


class ReputationScore(unittest.TestCase):
    def test_ten_tips_from_zero_score_exactly_two_reputation(self):
        tuning = load_contract()["tuning"]
        stock = [{"id": f"I{i}", "kind": "bong_sung", "fresh": 100} for i in range(1, 27)]
        session = Session("quan", tuning, {"stock": stock, "reputation": 0}, 7)
        bot = Bot()
        expected_reputation = Fraction(0)
        tipped = 0
        checked_tenth = False
        for _ in range(round(tuning["quan"]["duration_s"] * 60)):
            events = session.step(bot.input(SimpleNamespace(phase="quan", current_sim=session.sim)))
            for event in events:
                if event["name"] == "paid" and event["data"]["tip"] > 0:
                    tipped += 1
                    expected_reputation = min(Fraction(str(tuning["quan"]["reputation_max"])),
                        expected_reputation + Fraction(str(tuning["quan"]["tip_reputation"])))
                elif event["name"] == "customer_left" and event["data"]["reason"] == "patience":
                    expected_reputation = max(Fraction(str(tuning["quan"]["reputation_min"])),
                        expected_reputation + Fraction(str(tuning["quan"]["left_reputation_delta"])))
            snap = session.snapshot()
            self.assertEqual(snap["score"], snap["earned"] +
                             tuning["score"]["reputation_multiplier"] * math.floor(expected_reputation))
            if tipped == 10:
                self.assertEqual(snap["reputation"], 2.0)
                checked_tenth = True
            if session.done:
                break
        self.assertTrue(checked_tenth, "Phải chơi thật đến ít nhất10lần nhận boa")

    def test_add_loss_and_caps_without_rounding_legitimate_fixture(self):
        reputation = 0
        for _ in range(10):
            reputation = adjust_reputation(reputation, 0.2, 0, 5)
        self.assertEqual(reputation, 2.0)
        self.assertEqual(adjust_reputation(reputation, -0.5, 0, 5), 1.5)
        self.assertEqual(adjust_reputation(4.9, 0.2, 0, 5), 5)
        self.assertEqual(adjust_reputation(0.1, -0.5, 0, 5), 0)
        self.assertEqual(math.floor(adjust_reputation(1.9999999999, 0, 0, 5)), 1)


class FinalCLI(unittest.TestCase):
    def run_case(self, mode, scenario=None, inventory=None, frames=None, ticks=0):
        with tempfile.TemporaryDirectory() as temp, redirect_stderr(io.StringIO()) as errors:
            folder = Path(temp)
            output = folder / "out.jsonl"
            args = ["--mode", mode, "--seed", "7", "--ticks", str(ticks), "--out", str(output)]
            for flag, data in (("--scenario", scenario), ("--inventory", inventory), ("--inputs", frames)):
                if data is not None:
                    path = folder / (flag[2:] + ".json")
                    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
                    args.extend([flag, str(path)])
            code = main(args)
            rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()] if output.exists() else []
            return code, rows, errors.getvalue(), output.exists()

    def test_wrong_item_kind_type_returns_two_before_output(self):
        for kind in ([], {}, None, True, 3):
            item = {"id": "I1", "kind": kind, "fresh": 100}
            for mode, scenario, inventory in (
                ("quan", None, {"items": [item]}),
                ("gather", {"gather": {"hold": [item]}}, None),
                ("quan", {"quan": {"stock": [item]}}, None),
            ):
                with self.subTest(kind=kind, mode=mode, inventory=inventory):
                    code, _, error, exists = self.run_case(mode, scenario, inventory)
                    self.assertEqual(code, 2, error)
                    self.assertFalse(exists)

    def test_node_unknown_field_is_rejected(self):
        code, _, error, exists = self.run_case("gather", {"gather": {"nodes": [
            {"id": "N1", "kind": "bong_sung", "pos": [50, 0], "unexpected": True}]}})
        self.assertEqual(code, 2, error)
        self.assertFalse(exists)

    def test_monster_requires_two_waypoints_and_index_zero_or_one(self):
        for points, index in (([[60, 24], [64, 24], [68, 24]], 1), ([[60, 24], [64, 24]], 2)):
            with self.subTest(points=points, index=index):
                code, _, error, exists = self.run_case("gather", {"gather": {"monsters": [
                    {"id": "M1", "kind": "ca_sau", "pos": [60, 24], "waypoints": points, "target_idx": index}]}})
                self.assertEqual(code, 2, error)
                self.assertFalse(exists)

    def test_manifest_rejects_three_monster_waypoints(self):
        contract = deepcopy(load_contract())
        contract["tuning"]["gather"]["monsters"]["spawns"][0]["waypoints"].append([68, 24])
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "contract.json"
            path.write_text(json.dumps(contract), encoding="utf-8")
            with self.assertRaises(BadInput):
                load_contract(path)

    def test_quan_snapshot_includes_velocity_at_zero_and_after_clamping(self):
        scene = {"quan": {"player": {"pos": [16, 10], "vel": [3, 4]}, "random_customers": False}}
        code, rows, error, _ = self.run_case("quan", scene)
        self.assertEqual(code, 0, error)
        self.assertEqual(rows[0]["player"]["vel"], [3, 4])
        code, rows, error, _ = self.run_case("quan", scene, frames={"frames": [{"tick": 0, "move": [1, 1]}]}, ticks=1)
        self.assertEqual(code, 0, error)
        snapshot = [row for row in rows if row["type"] == "snapshot"][-1]
        self.assertEqual(snapshot["player"], {"pos": [16, 10], "vel": [0, 0]})

    def test_inventory_sort_uses_ascii_suffixes(self):
        items = [{"id": ident, "kind": "ca_linh", "fresh": 100} for ident in ("I２", "I10")]
        code, rows, error, _ = self.run_case("gather", {"gather": {
            "hold": items, "random_fish": False, "monsters": [], "time_left_ticks": 1}}, ticks=1)
        self.assertEqual(code, 0, error)
        event = next(row for row in rows if row.get("name") == "gather_end")
        self.assertEqual([it["id"] for it in event["data"]["inventory"]["items"]], ["I10", "I２"])


class NaturalIds(unittest.TestCase):
    def test_unicode_digits_and_linebreaks_follow_literal_ascii_suffix_rule(self):
        self.assertEqual(id_key("F٢"), ("F٢", -1, "F٢"))
        self.assertEqual(id_key("F２"), ("F２", -1, "F２"))
        self.assertEqual(id_key("F2\n"), ("F2\n", -1, "F2\n"))
        self.assertEqual(id_key("F\n2"), ("F\n", 2, "F\n2"))
        self.assertEqual([row["id"] for row in sort_by_id([{"id": "F２"}, {"id": "F10"}, {"id": "F2"}])],
                         ["F2", "F10", "F２"])
        ids = IdAllocator()
        ids.reserve("I２")
        self.assertEqual(ids.new("I"), "I1")
        ids.reserve("I010")
        self.assertEqual(ids.new("I"), "I11")


if __name__ == "__main__":
    unittest.main()
