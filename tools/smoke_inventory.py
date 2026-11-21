"""Check the contract's gather-to-quan inventory pipeline in temporary files."""
import json
import shlex
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    try:
        contract = json.loads((ROOT / "game.contract.json").read_text(encoding="utf-8"))
        command = shlex.split(contract["headless_cmd"])
        v12 = contract["contract_version"] == "1.2"  # TICKET-03: kho cá thể {id,kind,fresh}
        kinds = ["ca_loc", "bong_sung", "bong_sung"]
        hold = [{"id": f"I{i}", "kind": k, "fresh": 100} for i, k in enumerate(kinds, 1)] if v12 else kinds
        def close(a, b):
            return len(a) == len(b) and all(x["id"] == y["id"] and x["kind"] == y["kind"]
                                            and abs(x["fresh"] - y["fresh"]) <= 0.01 for x, y in zip(a, b))
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "scenario.json").write_text(json.dumps({"gather": {"hold": hold}}), encoding="utf-8")
            (p / "inputs.json").write_text(json.dumps({"frames": [{"tick": 0, "interact": True}]}), encoding="utf-8")
            inv, gout, qout = (p / x for x in ("inventory.json", "gather.jsonl", "quan.jsonl"))
            def run(*args):
                subprocess.run(command + list(map(str, args)), cwd=ROOT, check=True, capture_output=True, text=True)
            run("--mode", "gather", "--seed", "42", "--ticks", "1", "--scenario", p / "scenario.json", "--inputs", p / "inputs.json", "--inventory-out", inv, "--out", gout)
            saved = json.loads(inv.read_text(encoding="utf-8"))
            expected = {"bong_sung": 2, "ca_loc": 1}
            if v12:
                # một bước gather: hao 0.5/60 trước khi cập bến; id giữ nguyên
                if [(i["id"], i["kind"]) for i in saved["items"]] != [(h["id"], h["kind"]) for h in hold] or \
                        any(abs(i["fresh"] - (100 - 0.5 / 60)) > 1e-9 for i in saved["items"]):
                    raise ValueError(f"inventory mismatch: {saved}")
                expected = saved["items"]
            elif saved != {"items": expected}:
                raise ValueError(f"inventory mismatch: {saved}")
            rows = [json.loads(line) for line in gout.read_text(encoding="utf-8").splitlines()]
            ends = [r for r in rows if r.get("name") == "gather_end"]
            if len(ends) != 1 or not (close(ends[0]["data"]["inventory"]["items"], saved["items"]) if v12
                                      else ends[0]["data"]["inventory"] == saved):
                raise ValueError("gather_end does not match inventory")
            run("--mode", "quan", "--seed", "42", "--ticks", "0", "--inventory", inv, "--out", qout)
            rows = [json.loads(line) for line in qout.read_text(encoding="utf-8").splitlines()]
            if rows[0]["type"] != "snapshot" or rows[0]["tick"] != 0 or not (
                    close(rows[0]["stock"], expected) if v12 else rows[0]["stock"] == expected):
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
