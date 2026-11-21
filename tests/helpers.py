"""Tiện ích test: chạy headless, đọc JSONL, dựng fixture, so sánh có dung sai."""

import json
import math
import os
import shlex
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)
    return path


def frames(*fr):
    return {"frames": list(fr)}


def headless_cmd():
    """Lệnh headless khai trong game.contract.json — test chạy qua đây nên dùng được với MỌI ngôn ngữ."""
    with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
        return shlex.split(json.load(f)["headless_cmd"])


def run_headless(*args, cwd=ROOT):
    """Chạy `<headless_cmd> <args>`; trả (mã thoát, stderr)."""
    p = subprocess.run([*headless_cmd(), *args], cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stderr


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def snapshots(rows):
    return [r for r in rows if r["type"] == "snapshot"]


def events(rows, name=None):
    return [r for r in rows if r["type"] == "event" and (name is None or r["name"] == name)]


def close(a, b, tol=0.1):
    return abs(a - b) <= tol


def dist(p, q):
    return math.dist(p, q)


class Workdir:
    """Thư mục tạm tự dọn: with Workdir() as w: w.path('x.json')."""

    def __enter__(self):
        self._d = tempfile.TemporaryDirectory()
        return self

    def __exit__(self, *a):
        self._d.cleanup()

    def path(self, name):
        return os.path.join(self._d.name, name)


def contract_version():
    with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
        return json.load(f)["contract_version"]


def v12():
    """TICKET-03: từ v1.2 giỏ/kho là mảng cá thể {id,kind,fresh} thay kho đếm."""
    return contract_version() == "1.2"


def hold_of(kinds):
    """Giỏ mẫu theo đúng schema của manifest đang chạy: v1.2 cá thể I1.. fresh 100, trước đó mảng kind."""
    kinds = list(kinds)
    return [{"id": f"I{i}", "kind": k, "fresh": 100} for i, k in enumerate(kinds, 1)] if v12() else kinds


def counts(items):
    """Đếm theo kind từ kho cá thể (để so nội dung với kỳ vọng kiểu cũ)."""
    out = {}
    for it in items:
        out[it["kind"]] = out.get(it["kind"], 0) + 1
    return {k: out[k] for k in sorted(out)}


def same_items(a, b, tol=0.01):
    """So kho cá thể: id/kind đúng thứ tự, fresh trong dung sai ±0.01 (JSONL làm tròn 3 chữ số)."""
    return (len(a) == len(b) and all(x["id"] == y["id"] and x["kind"] == y["kind"]
                                     and abs(x["fresh"] - y["fresh"]) <= tol for x, y in zip(a, b)))
