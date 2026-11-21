"""Exercise the actual LiveGame/HTTP five-day loop with accelerated ticks.

No gameplay rules/timers are patched. UI intro gates are skipped via /ui.
Use --keep-open to inspect the resulting summary in a browser.
"""

import argparse
import json
from pathlib import Path
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from chonoi.contract import load_contract
from chonoi.live import LiveGame, LiveServer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep-open", action="store_true")
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()
    game = LiveGame("day", load_contract()["tuning"], {}, 1, days=5)
    server = LiveServer(game, port=args.port)
    server.start()
    base = server.url.rstrip("/")

    def state():
        with urllib.request.urlopen(base + "/state", timeout=5) as response:
            return json.load(response)

    def ui(action):
        request = urllib.request.Request(base + "/ui", data=json.dumps({"action": action}).encode(),
                                         headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(request, timeout=5) as response:
            if response.status != 200:
                raise RuntimeError("UI action failed")

    try:
        with urllib.request.urlopen(base, timeout=5) as response:
            assert b"<canvas" in response.read()
        first = state()
        assert first["ui"]["screen"] == "menu"
        ui("start")
        visited = []
        started = time.perf_counter()
        while not game.session.done:
            current = state()
            if current["ui"]["screen"] is not None:
                ui("continue")
            with game._lock:
                # Same method as the normal live loop, only pumped faster.
                for _ in range(1200):
                    if game._screen is not None or game.session.done:
                        break
                    old = (game.session.sim.day, game.session.sim.phase)
                    game._tick_once()
                    new = (game.session.sim.day, game.session.sim.phase)
                    if old != new:
                        visited.append([*old, *new])
            if time.perf_counter() - started > 60:
                raise RuntimeError("Live five-day check exceeded 60 seconds")
        last = state()
        end = game.session.end_row()
        assert last["finished"] and last["reason"] == "days_complete"
        assert last["ui"]["screen"] == "summary" and len(last["ui"]["days"]) == 5
        assert end["days_completed"] == 5 and not last["error"]
        summary = {"method": "real LiveGame/HTTP, accelerated _tick_once; no rule/timer overrides",
                   "elapsed_seconds": round(time.perf_counter() - started, 3),
                   "end": end, "ui": last["ui"], "phase_transitions": visited}
        proof = ROOT / "docs/proof/phase-2/an/live-five-summary.json"
        proof.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"PASS live HTTP: five days complete, summary rendered by /state; {base}", flush=True)
        if args.keep_open:
            print("Server stays open at summary for browser inspection; Ctrl+C to stop.", flush=True)
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()


if __name__ == "__main__":
    main()
