import unittest

from chonoi.contract import load_contract
from chonoi.ids import IdAllocator
from chonoi.inputs import BUTTONS_V11, InputPlayer, LiveInputs
from chonoi.inventory import inventory_kinds, read_inventory
from chonoi.rng import Streams
from chonoi.runner import Session
from chonoi.sim.gather import GatherSim

from pathlib import Path

from helpers import Workdir, counts, same_items, events, frames, hold_of, read_jsonl, run_headless, snapshots, v12, write_json

# Unit test P2 gọi sim trực tiếp với kho đếm: giữ manifest 1.1 cố định (từ v1.2 runtime dùng kho cá thể, TICKET-03).
FIXTURE_CONTRACT = Path(__file__).resolve().parent / "fixtures/phase-2/game.contract.json"


class PhaseTwoIntegration(unittest.TestCase):
    def setUp(self):
        self.tuning = load_contract(FIXTURE_CONTRACT)["tuning"]

    def test_headless_five_days_preserves_tick_provenance_and_upgrade_timing(self):
        scenario = {"day": {"money": 200, "earned": 250},
                    "gather": {"time_left_ticks": 1, "random_fish": False, "monsters": [], "hold": hold_of(["bong_sung"])},
                    "quan": {"time_left_ticks": 1, "random_customers": False}}
        inputs = [{"tick": 2, "pause": True, "buy": "oxygen", "shop_done": True},
                  {"tick": 3, "pause": False, "shop_done": False},
                  {"tick": 4, "pause": True, "buy": "oxygen", "shop_done": True}]
        for close_tick in (7, 10, 13, 16):
            inputs.extend(({"tick": close_tick - 2, "pause": False, "shop_done": False},
                           {"tick": close_tick, "shop_done": True}))
        with Workdir() as work:
            scene = write_json(work.path("day.json"), scenario)
            commands = write_json(work.path("input.json"), frames(*inputs))
            out = work.path("out.jsonl")
            code, error = run_headless("--mode", "day", "--days", "5", "--seed", "1", "--ticks", "30",
                                       "--snapshot-every", "1", "--scenario", scene, "--inputs", commands, "--out", out)
            self.assertEqual(code, 0, error)
            rows = read_jsonl(out)
        self.assertEqual([(row["day"], row["tick"]) for row in events(rows, "day_start")], [(1, 0), (2, 5), (3, 8), (4, 11), (5, 14)])
        self.assertEqual([row["day"] for row in events(rows, "shop_end")], list(range(1, 6)))
        self.assertEqual([row["tick"] for row in events(rows, "bought")], [5])
        step = [row for row in events(rows) if row["tick"] == 5]
        self.assertEqual([(row["name"], row["phase"]) for row in step], [
            ("resumed", "shop"), ("bought", "shop"), ("shop_end", "shop"),
            ("day_start", "gather"), ("day_plan", "gather"), ("phase_start", "gather"),
        ])
        next_day = next(row for row in snapshots(rows) if row["tick"] == 5)
        self.assertEqual((next_day["phase_tick"], next_day["active_upgrades"]["oxygen"]), (0, 1))
        self.assertEqual((rows[-1]["reason"], rows[-1]["days_completed"], rows[-1]["sim_tick"]), ("days_complete", 5, 15))
        self.assertEqual((rows[-1]["money"], rows[-1]["earned"]), (0, 250))

    def test_standalone_pause_freezes_each_phase(self):
        for mode in ("gather", "quan"):
            with self.subTest(mode=mode):
                session = Session(mode, self.tuning, {}, 3)
                inputs = InputPlayer([{"tick": 0, "pause": True}, {"tick": 1, "pause": False},
                                      {"tick": 2, "pause": True}], BUTTONS_V11)
                start = session.snapshot()["time_left_ticks"]
                self.assertEqual(session.step(inputs.advance(0))[0]["name"], "paused")
                self.assertEqual(session.step(inputs.advance(1)), [])
                self.assertEqual((session.sim_tick, session.snapshot()["time_left_ticks"]), (0, start))
                self.assertEqual(session.step(inputs.advance(2))[0]["name"], "resumed")
                self.assertEqual((session.tick, session.sim_tick, session.snapshot()["time_left_ticks"]), (3, 1, start - 1))

    def test_live_buy_queue_and_frame_buy_are_one_shot(self):
        inputs = LiveInputs(BUTTONS_V11)
        inputs.set(buy="oxygen")
        inputs.set(buy="hp", shop_done=True)
        inputs.set(shop_done=False)
        first, second, third = inputs.advance(), inputs.advance(), inputs.advance()
        self.assertTrue(first.pressed("shop_done"))
        self.assertFalse(second.pressed("shop_done"))
        self.assertEqual([first.buy, second.buy, third.buy], ["oxygen", "hp", None])
        player = InputPlayer([{"tick": 0, "buy": "oxygen"}], BUTTONS_V11)
        self.assertEqual([player.advance(0).buy, player.advance(1).buy], ["oxygen", None])

    def test_six_kinds_roundtrip_across_processes(self):
        kinds = sorted(inventory_kinds(self.tuning))
        self.assertEqual(len(kinds), 6)
        with Workdir() as work:
            scenario = write_json(work.path("gather.json"), {"gather": {"hold": hold_of(kinds), "random_fish": False, "monsters": []}})
            command = write_json(work.path("input.json"), frames({"tick": 0, "interact": True}))
            inventory = work.path("stock.json")
            code, error = run_headless("--mode", "gather", "--seed", "1", "--ticks", "1", "--scenario", scenario,
                                       "--inputs", command, "--inventory-out", inventory, "--out", work.path("g.jsonl"))
            self.assertEqual(code, 0, error)
            saved = read_inventory(inventory, kinds, items_mode=v12())
            self.assertEqual(counts(saved) if v12() else saved, dict.fromkeys(kinds, 1))
            output = work.path("q.jsonl")
            code, error = run_headless("--mode", "quan", "--seed", "1", "--ticks", "0", "--inventory", inventory, "--out", output)
            self.assertEqual(code, 0, error)
            stock = read_jsonl(output)[0]["stock"]
            if v12():
                self.assertTrue(same_items(stock, saved), (stock, saved))
            else:
                self.assertEqual(stock, dict.fromkeys(kinds, 1))

    def test_fish_reflects_and_spawns_without_moving_on_birth_tick(self):
        scenario = {"monsters": [], "fish": [{"id": "F10", "kind": "ca_loc", "pos": [96, 10], "heading_deg": 0}]}
        sim = GatherSim(self.tuning, scenario, Streams(1), IdAllocator())
        inputs = InputPlayer([])
        sim.step(inputs.advance(0))
        self.assertAlmostEqual(sim.fish[0]["pos"][0], 96 - 1.5 / 60)
        self.assertAlmostEqual(sim.fish[0]["heading_deg"], 180)
        for tick in range(1, self.tuning["gather"]["fish_spawn_ticks"]):
            result = sim.step(inputs.advance(tick))
        [spawn] = [data for name, data in result if name == "fish_spawned"]
        self.assertEqual(spawn["id"], "F11")
        self.assertEqual(sim.fish[-1]["age_ticks"], 0)
        self.assertEqual(sim.fish[-1]["pos"], spawn["pos"])

    def test_monster_hit_then_faint_uses_nearest_id_and_lifo_stock(self):
        monsters = [{"id": ident, "pos": [60, 24], "waypoints": [[60, 24], [64, 24]]} for ident in ("M10", "M2")]
        scenario = {"player": {"pos": [60, 24], "hp": 1}, "hold": ["ca_loc", "ca_keo", "keo_neo"],
                    "random_fish": False, "monsters": monsters}
        sim = GatherSim(self.tuning, scenario, Streams(1), IdAllocator())
        rows = sim.step(InputPlayer([]).advance(0))
        self.assertEqual([name for name, _ in rows], ["monster_hit", "faint", "gather_end"])
        self.assertEqual((rows[0][1]["monster_id"], rows[0][1]["lost"]), ("M2", ["keo_neo"]))
        self.assertEqual((rows[1][1]["cause"], rows[1][1]["lost"]), ("monster", ["ca_keo", "ca_loc"]))
        self.assertEqual(sim.inventory_items(), {})
