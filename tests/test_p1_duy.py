import json
import unittest
from types import SimpleNamespace

from chonoi.sim.gather_actions import catch_fish, gather_node


class Actions(unittest.TestCase):
    def setUp(self):
        with open("game.contract.json", encoding="utf-8") as f:
            tuning = json.load(f)["tuning"]["gather"]
        self.s = SimpleNamespace(t=tuning, pos=[10, 0], hold=[], nodes=[], fish=[], catch_cd_ticks=0)
        self.s._at_surface = lambda: self.s.pos[1] <= tuning["surface_depth"]
        self.events = []

    def test_node_edge_tie_and_full(self):
        s = self.s
        s.nodes = [{"id": i, "kind": "bong_sung", "pos": [x, 0], "regrow_ticks": 0}
                   for i, x in (("N10", 12), ("N2", 8))]
        gather_node(s, self.events)
        self.assertEqual(self.events[0][1]["node_id"], "N2")
        self.assertEqual(s.nodes[1]["regrow_ticks"], round(s.t["regrow_s"] * 60))
        s.hold = ["ca_loc"] * s.t["hold_capacity"]
        gather_node(s, self.events)
        self.assertEqual(self.events[-1][0], "hold_full")
        self.assertEqual(s.nodes[0]["regrow_ticks"], 0)

    def test_fish_full_then_success_and_cooldown(self):
        s = self.s
        s.pos = [10, 5]
        s.fish = [{"id": "F10", "kind": "ca_loc", "pos": [12, 5]},
                  {"id": "F2", "kind": "ca_linh", "pos": [8, 5]}]
        s.hold = ["ca_loc"] * (s.t["hold_capacity"] - 2)
        catch_fish(s, self.events)
        self.assertEqual(self.events[-1][1]["fish_id"], "F2")
        self.assertEqual(len(s.fish), 2)
        self.assertEqual(s.catch_cd_ticks, 0)
        s.hold.pop()
        catch_fish(s, self.events)
        self.assertEqual(self.events[-1][0], "fish_caught")
        self.assertEqual(s.hold[-3:], ["ca_linh"] * 3)
        self.assertEqual(s.catch_cd_ticks, round(s.t["catch_cooldown_s"] * 60))
        catch_fish(s, self.events)
        self.assertEqual(len(s.fish), 1)

    def test_wrong_depth_and_no_target(self):
        catch_fish(self.s, self.events)
        self.s.pos = [10, 5]
        gather_node(self.s, self.events)
        catch_fish(self.s, self.events)
        self.assertEqual(self.events, [])
        self.assertEqual(self.s.catch_cd_ticks, 0)
