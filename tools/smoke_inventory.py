"""Check the contract's gather-to-quan inventory pipeline in temporary files."""
import json
import argparse
import math
import shlex
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    try:
        parser = argparse.ArgumentParser(description="Smoke gather → file kho → quán")
        parser.add_argument("--require-v12", action="store_true", help="yêu cầu schema cá thể Phase 3")
        args = parser.parse_args()
        contract = json.loads((ROOT / "game.contract.json").read_text(encoding="utf-8"))
        version = contract.get("contract_version")
        if args.require_v12 and version not in ("1.2", "1.3"):
            raise ValueError(f"contract 1.2/1.3 required; current version is {version!r}")
        individual = version in ("1.2", "1.3")
        command = shlex.split(contract["headless_cmd"])
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            hold = ([{"id": "I10", "kind": "ca_linh", "fresh": 100},
                     {"id": "I2", "kind": "ca_loc", "fresh": 29.9999}]
                    if individual else ["ca_loc", "bong_sung", "bong_sung"])
            gather = {"hold": hold, "random_fish": False}
            if version != "1.0":
                gather["monsters"] = []
            (p / "scenario.json").write_text(json.dumps({"gather": gather}), encoding="utf-8")
            (p / "inputs.json").write_text(json.dumps({"frames": [{"tick": 0, "interact": True}]}), encoding="utf-8")
            inv, gout, qout = (p / x for x in ("inventory.json", "gather.jsonl", "quan.jsonl"))
            def run(*args):
                subprocess.run(command + list(map(str, args)), cwd=ROOT, check=True, capture_output=True, text=True)
            run("--mode", "gather", "--seed", "42", "--ticks", "1", "--scenario", p / "scenario.json", "--inputs", p / "inputs.json", "--inventory-out", inv, "--out", gout)
            saved = json.loads(inv.read_text(encoding="utf-8"))
            if individual:
                items = saved.get("items")
                if not isinstance(items, list) or [item.get("id") for item in items] != ["I2", "I10"]:
                    raise ValueError(f"inventory ids/order mismatch: {saved}")
                source = {item["id"]: item for item in hold}
                decay = contract["tuning"]["freshness"]["gather_decay_per_s"] / 60
                for item in items:
                    original = source[item["id"]]
                    if set(item) != {"id", "kind", "fresh"} or item["kind"] != original["kind"] or not math.isclose(item["fresh"], max(0, original["fresh"] - decay), abs_tol=1e-10, rel_tol=0):
                        raise ValueError(f"inventory item mismatch: {item}")
                expected = items
            else:
                expected = {"bong_sung": 2, "ca_loc": 1}
                if saved != {"items": expected}:
                    raise ValueError(f"inventory mismatch: {saved}")
            rows = [json.loads(line) for line in gout.read_text(encoding="utf-8").splitlines()]
            ends = [r for r in rows if r.get("name") == "gather_end"]
            if len(ends) != 1 or ends[0]["data"]["inventory"] != saved:
                raise ValueError("gather_end does not match inventory")
            run("--mode", "quan", "--seed", "42", "--ticks", "0", "--inventory", inv, "--out", qout)
            rows = [json.loads(line) for line in qout.read_text(encoding="utf-8").splitlines()]
            if rows[0]["type"] != "snapshot" or rows[0]["tick"] != 0 or rows[0]["stock"] != expected:
                raise ValueError("quan tick 0 stock mismatch")
        print(f"PASS: contract {version}, gather inventory matches quan stock at tick 0")
        return 0
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}".encode("ascii", "backslashreplace").decode("ascii"))
        if isinstance(exc, subprocess.CalledProcessError):
            print((exc.stderr or "").encode("ascii", "backslashreplace").decode("ascii"))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
