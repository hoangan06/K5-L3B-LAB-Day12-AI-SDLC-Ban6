"""Chạy headless hai lần; so byte JSONL và kho, không chỉ exit code.

python3 tools/check_determinism.py [--python /path/to/python]
"""

import argparse
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", help="Override interpreter of a Python headless_cmd for this check only")
    args = parser.parse_args(argv)
    try:
        contract = json.loads((ROOT / "game.contract.json").read_text(encoding="utf-8"))
        command = shlex.split(contract["headless_cmd"])
        if not command:
            raise ValueError("headless_cmd is empty")
        if args.python:
            if Path(command[0]).stem.lower() not in ("python", "python3", "python3.12"):
                raise ValueError("--python requires a Python headless_cmd")
            command[0] = args.python
        with tempfile.TemporaryDirectory(prefix="chonoi-determinism-") as temp:
            folder = Path(temp)
            v12 = contract["contract_version"] in ("1.2", "1.3")  # P4 giữ kho cá thể P3
            def items(kinds):
                return [{"id": f"I{i}", "kind": k, "fresh": 100} for i, k in enumerate(kinds, 1)]
            scenarios = {
                "gather": {"gather": {"player": {"pos": [50, 10], "oxygen_ticks": 1,
                    "hp": 1}, "hold": items(["ca_loc", "bong_sung"]) if v12 else ["ca_loc", "bong_sung"],
                    "random_fish": False}},
                "quan": {"quan": {"stock": items(["ca_loc"] * 3 + ["bong_sung"] * 4) if v12
                                  else {"ca_loc": 3, "bong_sung": 4}}},
            }
            for mode, fixture in scenarios.items():
                scenario = folder / f"{mode}-scenario.json"
                scenario.write_text(json.dumps(fixture), encoding="utf-8")
                artifacts = []
                for attempt in (1, 2):
                    output = folder / f"{mode}-{attempt}.jsonl"
                    inventory = folder / f"{mode}-{attempt}-inventory.json"
                    cli = [*command, "--mode", mode, "--seed", "7", "--ticks", "240",
                           "--scenario", str(scenario), "--out", str(output)]
                    if mode == "gather":
                        cli.extend(["--inventory-out", str(inventory)])
                    result = subprocess.run(cli, cwd=ROOT, capture_output=True, text=True)
                    if result.returncode:
                        raise RuntimeError(f"{mode} run {attempt}: exit {result.returncode}: {result.stderr}")
                    content = output.read_bytes()
                    rows = [json.loads(line) for line in content.splitlines()]
                    if not rows or rows[-1].get("type") != "end":
                        raise ValueError(f"{mode}: missing end row")
                    if mode == "gather":
                        if rows[-1].get("reason") != "fainted":
                            raise ValueError("gather probe must finish by fainting")
                        saved = inventory.read_bytes()
                        if json.loads(saved) != {"items": [] if v12 else {}}:
                            raise ValueError("faint inventory must be empty")
                    else:
                        saved = None
                    artifacts.append((content, saved))
                if artifacts[0] != artifacts[1]:
                    raise ValueError(f"{mode}: byte mismatch between repeated runs")
                print(f"PASS {mode}: JSONL sha256={hashlib.sha256(artifacts[0][0]).hexdigest()}")
                if mode == "gather":
                    print(f"PASS gather inventory: sha256={hashlib.sha256(artifacts[0][1]).hexdigest()}")
        print("PASS: repeated outputs match byte-for-byte (not proof of all gameplay rules)")
        return 0
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
