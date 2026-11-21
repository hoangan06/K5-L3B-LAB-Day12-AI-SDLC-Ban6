"""Phá từng luật P3 quán một lần; test_p3_trung + test_p3_integration phải fail (CAUGHT). Chạy: python3 docs/proof/phase-3/trung/mutate.py"""
import subprocess, sys, pathlib
F, C, K, V, Q = ("chonoi/sim/quan_fresh.py", "chonoi/sim/quan_customers.py", "chonoi/sim/quan_kitchen.py",
                 "chonoi/sim/quan_validation.py", "chonoi/sim/quan.py")
I, G, A, D, S, N = ("chonoi/items.py", "chonoi/sim/gather.py", "chonoi/sim/gather_actions.py", "chonoi/sim/day.py",
                    "chonoi/scenario.py", "chonoi/inventory.py")
M = [
 (I, 'step = exact(rate_per_s) / 60', 'step = rate_per_s / 60'),
 (I, 'step = exact(rate_per_s) / 60', 'step = exact(rate_per_s) / 50'),
 (I, 'it["fresh"] = max(Fraction(0), it["fresh"] - step)', 'it["fresh"] = it["fresh"] - step'),
 (I, 'was_ok = it["fresh"] >= limit', 'was_ok = True'),
 (I, 'was_ok = it["fresh"] >= limit', 'was_ok = it["fresh"] > limit'),
 (I, 'for it in sort_by_id(items):', 'for it in items:'),
 (I, 'return g if abs(g - f) < Fraction(1, 10**9) else f', 'return f'),
 (I, 'if not _num(fresh) or not 0 <= fresh <= 100:', 'if not 0 <= fresh <= 100:'),
 (I, 'if not isinstance(iid, str) or not iid or iid in seen:', 'if not isinstance(iid, str) or not iid:'),
 (I, 'if kind not in kinds:', 'if False:'),
 (I, 'set(it) != ITEM_KEYS', 'not ITEM_KEYS <= set(it)'),
 (I, 'if not isinstance(raw, list):', 'if False:'),
 (F, 'return item["fresh"] < spoiled_below(sim)', 'return item["fresh"] <= spoiled_below(sim)'),
 (F, 'key=lambda it: (-it["fresh"], id_key(it["id"])))', 'key=lambda it: id_key(it["id"]))'),
 (F, 'key=lambda it: (-it["fresh"], id_key(it["id"])))', 'key=lambda it: (-it["fresh"], it["id"]))'),
 (F, 'and not is_spoiled(sim, it)), key', '), key'),
 (F, 'for c in sorted(hit, key=lambda c: (c["order_tick"], id_key(c["table_id"]))):', 'for c in sorted(hit, key=lambda c: id_key(c["table_id"])):'),
 (F, 'c["order_status"] = "unfulfillable"', 'pass'),
 (F, '        c["reserved"] = []\n        got', '        got'),
 (F, 'used.sort(key=lambda it: (it["kind"], id_key(it["id"])))', 'pass'),
 (F, 'return floor(list_price * mean_fresh / 100)', 'return round(list_price * mean_fresh / 100)'),
 (C, 'for c in sorted((c for c in out if "reserved" not in c), key=lambda c: (c["order_tick"], id_key(c["table_id"]))):',
     'for c in [c for c in out if "reserved" not in c]:'),
 (C, 'raise BadInput(f"customers.{c[\'id\']}: kho không đủ', 'c["reserved"] = []; continue; raise BadInput(f"customers.{c[\'id\']}: kho không đủ'),
 (K, '"base_price": locked_price(menu_item["price"], mean)}', '"base_price": menu_item["price"]}'),
 (V, 'if it is None or is_spoiled(sim, it) or iid in owner:', 'if it is None:'),
 (V, 'if not isinstance(r, list) or not all(isinstance(i, str) and i for i in r):', 'if False:'),
 (Q, '            for it in self.stock:\n                ids.reserve(it["id"])', '            pass'),
 (Q, 'if isinstance(inventory, list) or isinstance(scenario.get("stock"), list):', 'if False:'),
 (Q, '            decay(self, events)', '            pass'),
 # v1.2 gather / kho / day (Trung)
 (G, '                ids.reserve(it["id"])', '                pass'),
 (G, 'decay_items(self.hold, self.fresh_cfg["gather_decay_per_s"], spoiled_below(self.fresh_cfg),\n                        "hold", events)', 'pass'),
 (G, 'lost = self._hold_out(list(reversed(self.hold)))', 'lost = self._hold_out(list(self.hold))'),
 (A, '"fresh": exact(cfg["initial"])}', '"fresh": exact(cfg["initial"]) - 1}'),
 (D, 'return [dict(it) for it in gather.hold]', 'return gather.inventory_items()'),
 (D, 'gather["hold"] = [dict(it, id=self.ids.new("I")) for it in gather["hold"]]', 'pass'),
 (S, 'if len(load_items(b["hold"], kinds, "gather.hold")) > g["hold_capacity"]:', 'if False:'),
 (N, 'if items_mode:', 'if False:'),
]
for f, a, b in M:
    p = pathlib.Path(f); src = p.read_text()
    assert src.count(a) == 1, a
    p.write_text(src.replace(a, b))
    try:
        r = subprocess.run([sys.executable, "-m", "unittest", "tests.test_p3_trung", "tests.test_p3_integration"], capture_output=True, text=True,
                           env={"PYTHONPATH": "tests:.", "PATH": "/usr/bin:/bin"})
        print("CAUGHT " if r.returncode else "MISSED ", f, "|", a.splitlines()[0][:90])
    finally:
        p.write_text(src)
