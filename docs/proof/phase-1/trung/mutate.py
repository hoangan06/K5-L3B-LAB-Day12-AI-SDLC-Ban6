import subprocess, sys, pathlib
M = [
 ("chonoi/sim/quan_validation.py", "if n > sim.stock.get(k, 0):", "if False:"),
 ("chonoi/sim/quan_validation.py", 'if res != sim.menu[c["dish_id"]]["recipe"]:', "if False:"),
 ("chonoi/sim/quan_validation.py", 'if c["id"] in holders:', "if False:"),
 ("chonoi/sim/quan_validation.py", 'elif c["eat_ticks_left"]:', "elif False:"),
 ("chonoi/sim/quan_customers.py", 'if all(avail.get(k, 0) >= n', "if True or all(avail.get(k, 0) >= n"),
 ("chonoi/sim/quan_customers.py", 'if reason == "patience":', "if False:"),
 ("chonoi/sim/quan_customers.py", 'if c["eat_ticks_left"] == 0:', "if closing and False:"),
 ("chonoi/sim/quan_customers.py", "if sim.phase_tick < first or", "if sim.phase_tick < first or (sim.phase_tick - first) % (every + 1) or False or"),
 ("chonoi/sim/quan_customers.py", "avail = {k: sim.stock.get(k, 0) for k in KINDS_P1}", "avail = dict(sim.stock)"),
 ("chonoi/sim/quan_customers.py", 'for raw in copy.deepcopy(scenario.get("customers", [])):', 'for raw in scenario.get("customers", []):'),
 ("chonoi/sim/quan_customers.py", 'if s["state"] == "ready":\n            s["ready_ticks"] += 1', 'if True:\n            s["ready_ticks"] += 1'),
]
for f, a, b in M:
    p = pathlib.Path(f); src = p.read_text()
    assert src.count(a) == 1, a
    p.write_text(src.replace(a, b))
    try:
        r = subprocess.run([sys.executable, "-m", "unittest", "tests.test_p1_trung"], capture_output=True, text=True,
                           env={"PYTHONPATH": "tests:.", "PATH": "/usr/bin:/bin"})
        print("CAUGHT " if r.returncode else "MISSED ", a.splitlines()[0])
    finally:
        p.write_text(src)
