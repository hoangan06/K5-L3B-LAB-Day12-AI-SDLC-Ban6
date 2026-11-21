"""Phá từng luật P3 quán một lần; test_p3_trung phải fail (CAUGHT). Chạy: python3 docs/proof/phase-3/trung/mutate.py"""
import subprocess, sys, pathlib
F, C, K, V, Q = ("chonoi/sim/quan_fresh.py", "chonoi/sim/quan_customers.py", "chonoi/sim/quan_kitchen.py",
                 "chonoi/sim/quan_validation.py", "chonoi/sim/quan.py")
M = [
 (F, 'rate = Fraction(str(sim.fresh_cfg["quan_decay_per_s"])) / 60', 'rate = sim.fresh_cfg["quan_decay_per_s"] / 60'),
 (F, 'rate = Fraction(str(sim.fresh_cfg["quan_decay_per_s"])) / 60', 'rate = Fraction(str(sim.fresh_cfg["quan_decay_per_s"])) / 50'),
 (F, 'it["fresh"] = max(Fraction(0), it["fresh"] - rate)', 'it["fresh"] = it["fresh"] - rate'),
 (F, 'was_ok = it["fresh"] >= limit', 'was_ok = True'),
 (F, 'was_ok = it["fresh"] >= limit', 'was_ok = it["fresh"] > limit'),
 (F, 'return item["fresh"] < spoiled_below(sim)', 'return item["fresh"] <= spoiled_below(sim)'),
 (F, 'key=lambda it: (-it["fresh"], id_key(it["id"])))', 'key=lambda it: id_key(it["id"]))'),
 (F, 'key=lambda it: (-it["fresh"], id_key(it["id"])))', 'key=lambda it: (-it["fresh"], it["id"]))'),
 (F, 'and not is_spoiled(sim, it)), key', '), key'),
 (F, 'for c in sorted(hit, key=lambda c: (c["order_tick"], id_key(c["table_id"]))):', 'for c in sorted(hit, key=lambda c: id_key(c["table_id"])):'),
 (F, 'c["order_status"] = "unfulfillable"', 'pass'),
 (F, '        c["reserved"] = []\n        got', '        got'),
 (F, 'used.sort(key=lambda it: (it["kind"], id_key(it["id"])))', 'pass'),
 (F, 'return floor(list_price * mean_fresh / 100)', 'return round(list_price * mean_fresh / 100)'),
 (F, 'if not _num(fresh) or not 0 <= fresh <= 100:', 'if not 0 <= fresh <= 100:'),
 (F, 'if not isinstance(iid, str) or not iid or iid in seen:', 'if not isinstance(iid, str) or not iid:'),
 (F, 'if kind not in kinds:', 'if False:'),
 (F, 'set(it) != {"id", "kind", "fresh"}', 'not {"id", "kind", "fresh"} <= set(it)'),
 (C, 'for c in sorted((c for c in out if "reserved" not in c), key=lambda c: (c["order_tick"], id_key(c["table_id"]))):',
     'for c in [c for c in out if "reserved" not in c]:'),
 (C, 'raise BadInput(f"customers.{c[\'id\']}: kho không đủ', 'c["reserved"] = []; continue; raise BadInput(f"customers.{c[\'id\']}: kho không đủ'),
 (K, '"base_price": locked_price(menu_item["price"], mean)}', '"base_price": menu_item["price"]}'),
 (V, 'if it is None or is_spoiled(sim, it) or iid in owner:', 'if it is None:'),
 (V, 'if not isinstance(r, list) or not all(isinstance(i, str) and i for i in r):', 'if False:'),
 (Q, '            for it in self.stock:\n                ids.reserve(it["id"])', '            pass'),
 (Q, 'if isinstance(inventory, list) or isinstance(scenario.get("stock"), list):', 'if False:'),
 (Q, '            decay(self, events)', '            pass'),
]
for f, a, b in M:
    p = pathlib.Path(f); src = p.read_text()
    assert src.count(a) == 1, a
    p.write_text(src.replace(a, b))
    try:
        r = subprocess.run([sys.executable, "-m", "unittest", "tests.test_p3_trung"], capture_output=True, text=True,
                           env={"PYTHONPATH": "tests:.", "PATH": "/usr/bin:/bin"})
        print("CAUGHT " if r.returncode else "MISSED ", f, "|", a.splitlines()[0][:90])
    finally:
        p.write_text(src)
