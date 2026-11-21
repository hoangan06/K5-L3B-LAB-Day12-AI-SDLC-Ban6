"""Kiểm gói đã giải nén: hash, import, CLI và GUI HTTP thật, không cần Git.

python3 tools/check_release_package.py --archive dist/chonoi-v1.0.0.zip --out package-check.json
Không thay thế kiểm chơi bằng mắt hoặc clone sạch của QA.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
from queue import Empty, Queue
import re
import subprocess
import sys
import tempfile
from threading import Thread
import urllib.request
import zipfile


def check(archive_path):
    with tempfile.TemporaryDirectory(prefix="chonoi-package-") as temporary:
        folder = Path(temporary)
        with zipfile.ZipFile(archive_path) as archive:
            for name in archive.namelist():
                if Path(name).is_absolute() or ".." in Path(name).parts:
                    raise ValueError("đường dẫn ZIP không hợp lệ")
            archive.extractall(folder)
        root = folder / "chonoi-v1.0.0"
        metadata = json.loads((root / "BUILD-INFO.json").read_text(encoding="utf-8"))
        for name, expected in metadata["files_sha256"].items():
            actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
            if actual != expected:
                raise ValueError(f"hash khác: {name}")
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)
        env["PYTHONNOUSERSITE"] = "1"
        imported = subprocess.run([sys.executable, "-c", "import chonoi; print(chonoi.__file__)"],
                                  cwd=root, env=env, capture_output=True, text=True, check=True, timeout=15)
        if root not in Path(imported.stdout.strip()).parents:
            raise ValueError("import nhầm source bên ngoài gói")
        output = folder / "day.jsonl"
        subprocess.run([sys.executable, "-m", "chonoi.headless", "--mode", "day", "--days", "5",
                        "--seed", "7", "--ticks", "0", "--out", str(output)],
                       cwd=root, env=env, capture_output=True, text=True, check=True, timeout=15)
        rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
        snap = next(row for row in rows if row["type"] == "snapshot")
        if (snap["phase"], snap["day"]) != ("gather", 1):
            raise ValueError("CLI gói không khởi tạo đúng ngày")
        server = subprocess.Popen([sys.executable, "-m", "chonoi.live", "--mode", "day", "--days", "5",
                                   "--seed", "7", "--port", "0"], cwd=root, env=env,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        try:
            startup = Queue()
            def read_startup():
                for line in server.stdout:
                    startup.put(line)
            Thread(target=read_startup, daemon=True).start()
            line = startup.get(timeout=15)
            found = re.search(r"http://127\.0\.0\.1:\d+/", line)
            if not found:
                raise ValueError(f"server không có URL: {line.strip()}")
            url = found.group()
            with urllib.request.urlopen(url, timeout=5) as response:
                html = response.read()
            with urllib.request.urlopen(url + "state", timeout=5) as response:
                state = json.load(response)
            if b"<canvas" not in html or state.get("mode") != "day" or state.get("ui", {}).get("screen") != "menu":
                raise ValueError("GUI gói thiếu canvas hoặc state menu")
        finally:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)
            server.stdout.close()
        return {"status": "PASS", "platform": platform.platform(), "python": platform.python_version(),
                "archive_sha256": hashlib.sha256(Path(archive_path).read_bytes()).hexdigest(),
                "source_commit": metadata["source_commit"], "working_tree_dirty": metadata.get("working_tree_dirty"),
                "files_checked": len(metadata["files_sha256"]),
                "isolated_import": True, "headless_day": True, "gui_http": True,
                "missing_release_inputs": metadata["missing_release_inputs"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    try:
        report = check(args.archive)
        Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, StopIteration, KeyError, Empty, subprocess.SubprocessError, zipfile.BadZipFile) as exc:
        print(f"FAIL package: {exc}", file=sys.stderr)
        return 1
    print("PASS package: isolated source, file hashes, CLI day and GUI HTTP")
    return 0


if __name__ == "__main__":
    sys.exit(main())
