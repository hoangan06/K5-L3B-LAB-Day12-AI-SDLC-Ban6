"""Check the contract's gather-to-quan inventory pipeline in temporary files."""
import json
import shlex
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    try:
        command = shlex.split(json.loads((ROOT / "game.contract.json").read_text(encoding="utf-8"))["headless_cmd"])
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "scenario.json").write_text(json.dumps({"gather": {"hold": ["ca_loc", "bong_sung", "bong_sung"]}}), encoding="utf-8")
            (p / "inputs.json").write_text(json.dumps({"frames": [{"tick": 0, "interact": True}]}), encoding="utf-8")
            inv, gout, qout = (p / x for x in ("inventory.json", "gather.jsonl", "quan.jsonl"))
            def run(*args):
                subprocess.run(command + list(map(str, args)), cwd=ROOT, check=True, capture_output=True, text=True)
            run("--mode", "gather", "--seed", "42", "--ticks", "1", "--scenario", p / "scenario.json", "--inputs", p / "inputs.json", "--inventory-out", inv, "--out", gout)
            saved = json.loads(inv.read_text(encoding="utf-8"))
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
        print("PASS: gather inventory matches quan stock at tick 0")
        return 0
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}")
        if isinstance(exc, subprocess.CalledProcessError):
            print(exc.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
