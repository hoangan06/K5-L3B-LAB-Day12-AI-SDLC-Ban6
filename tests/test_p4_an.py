"""P4 Ân: version, schema kế thừa P3, adapter soak và CLI thật."""

from contextlib import redirect_stderr
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from chonoi.contract import load_contract
from chonoi.errors import BadInput
from chonoi.headless import main
from chonoi.runner import Session, build_sim
from chonoi.sim.day import DaySim
from tools.package_release import build_archive


class P4Contract(unittest.TestCase):
    def test_manifest_keeps_p3_tuning(self):
        contract = load_contract()
        self.assertEqual(contract["contract_version"], "1.3")
        self.assertEqual(contract["bench_cmd"], "node tools/bench.mjs")
        self.assertEqual(contract["soak_cmd"], "python3 -m chonoi.soak")
        self.assertEqual(contract["tuning"]["freshness"],
                         {"initial": 100, "gather_decay_per_s": .5, "quan_decay_per_s": .25, "spoiled_below": 30})

    def test_v13_rejects_missing_commands_and_missing_freshness(self):
        for key, value in (("bench_cmd", None), ("bench_cmd", " "), ("soak_cmd", 7),
                           ("soak_cmd", ""), ("freshness", None)):
            with self.subTest(key=key, value=value), tempfile.TemporaryDirectory() as temp:
                contract = deepcopy(load_contract())
                if key == "freshness":
                    del contract["tuning"][key]
                else:
                    contract[key] = value
                path = Path(temp) / "contract.json"
                path.write_text(json.dumps(contract), encoding="utf-8")
                with self.assertRaises(BadInput):
                    load_contract(path)

    def test_v12_remains_compatible_without_bench_soak(self):
        contract = deepcopy(load_contract())
        contract["contract_version"] = "1.2"
        del contract["bench_cmd"], contract["soak_cmd"]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "contract.json"
            path.write_text(json.dumps(contract), encoding="utf-8")
            self.assertEqual(load_contract(path)["tuning"], contract["tuning"])

    def test_cli_v13_day_and_item_inventory_real(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            output = folder / "out.jsonl"
            self.assertEqual(main(["--mode", "day", "--days", "5", "--seed", "7", "--ticks", "0",
                                   "--out", str(output)]), 0)
            snap = next(row for row in map(json.loads, output.read_text(encoding="utf-8").splitlines())
                        if row["type"] == "snapshot")
            self.assertEqual((snap["day"], snap["phase"]), (1, "gather"))
            self.assertIsInstance(snap["hold"], list)
            stock = folder / "stock.json"
            stock.write_text('{"items":[{"id":"I7","kind":"ca_linh","fresh":29.9999}]}', encoding="utf-8")
            self.assertEqual(main(["--mode", "quan", "--seed", "7", "--ticks", "0", "--out", str(output),
                                   "--inventory", str(stock)]), 0)
            snap = json.loads(output.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual((snap["stock"][0]["id"], snap["stock"][0]["kind"]), ("I7", "ca_linh"))
            self.assertAlmostEqual(snap["stock"][0]["fresh"], 29.9999, delta=.01)

    def test_cli_standard_still_rejects_ten_days_before_output(self):
        with tempfile.TemporaryDirectory() as temp, redirect_stderr(io.StringIO()):
            output = Path(temp) / "out.jsonl"
            self.assertEqual(main(["--mode", "day", "--days", "10", "--seed", "7", "--ticks", "1",
                                   "--out", str(output)]), 2)
            self.assertFalse(output.exists())


class P4SessionAdapter(unittest.TestCase):
    def setUp(self):
        self.tuning = load_contract()["tuning"]

    def test_standard_uses_real_day_without_soak_keyword(self):
        with patch("chonoi.sim.day.DaySim", wraps=DaySim) as factory:
            session = Session("day", self.tuning, {}, 7, days=5)
        self.assertIsInstance(session.sim, DaySim)
        self.assertNotIn("soak", factory.call_args.kwargs)
        self.assertEqual(session.sim.days, 5)

    def test_adapter_forwards_ten_days_and_soak_to_day_constructor(self):
        # Test ranh giới API; không dùng mock để tuyên bố đã chơi đủ10ngày.
        with patch("chonoi.sim.day.DaySim") as factory:
            simulation = build_sim("day", self.tuning, {}, 7, None, days=10, soak=True)
        self.assertIs(simulation, factory.return_value)
        self.assertEqual(factory.call_args.kwargs, {"days": 10, "soak": True})

    def test_invalid_soak_and_days_fail_before_factory(self):
        for kwargs in ({"soak": "yes"}, {"soak": 1}, {"days": 6}, {"days": True},
                       {"soak": True, "days": False}, {"soak": True, "days": 0},
                       {"soak": True, "days": -1}, {"soak": True, "days": 1.5}):
            with self.subTest(kwargs=kwargs), patch("chonoi.runner.build_sim") as factory:
                with self.assertRaises(BadInput):
                    Session("day", self.tuning, {}, 7, **kwargs)
                factory.assert_not_called()
        for mode in ("gather", "quan"):
            with self.subTest(mode=mode), self.assertRaises(BadInput):
                build_sim(mode, self.tuning, {}, 7, None, soak=True)


class P4Package(unittest.TestCase):
    def test_archive_excludes_local_state_and_is_self_contained(self):
        import zipfile
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            source = folder / "source"
            for name in ("README.md", "game.contract.json", "chonoi/live.py", "chonoi/web/index.html",
                         "chonoi/__pycache__/live.pyc", ".env", "node_modules/module/index.js"):
                path = source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("test", encoding="utf-8")
            destination = folder / "game.zip"
            result = build_archive(source, destination)
            with zipfile.ZipFile(destination) as archive:
                names = archive.namelist()
                self.assertIn("chonoi-v1.0.0/chonoi/live.py", names)
                self.assertIn("chonoi-v1.0.0/BUILD-INFO.json", names)
                self.assertFalse(any(".env" in name or "node_modules" in name or "__pycache__" in name for name in names))
            self.assertIn("LICENSE", result["missing_release_inputs"])
            with self.assertRaises(FileExistsError):
                build_archive(source, destination)


if __name__ == "__main__":
    unittest.main()
