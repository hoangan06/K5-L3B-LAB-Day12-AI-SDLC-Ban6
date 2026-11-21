"""Phá từng luật P2 một lần; test_p2_trung phải fail (CAUGHT). Chạy: python3 docs/proof/phase-2/trung/mutate.py"""
import subprocess, sys, pathlib
M = [
 ("chonoi/sim/day_plan.py", 'if "ingredients" in entry and entry["ingredients"] != ingredients:', "if False:"),
 ("chonoi/sim/day_plan.py", "if not _pos_int(day) or day not in DAYS:", "if day not in DAYS:"),
 ("chonoi/sim/day_plan.py", "if dish not in menu or not _pos_int(n):", "if dish not in menu:"),
 ("chonoi/sim/day_plan.py", 'if p["day"] in seen:', "if False:"),
 ("chonoi/sim/day_plan.py", "out[kind] = out.get(kind, 0) + k * n", "out[kind] = out.get(kind, 0) + k"),
 ("chonoi/sim/day_plan.py", 'return {"day": day, "dishes": dict(dishes), "ingredients": ingredients}', 'return {"day": day, "dishes": dishes, "ingredients": ingredients}'),
 ("chonoi/sim/day_plan.py", 'plans[p["day"]] = p\n    return', 'plans.setdefault(p["day"], p)\n    return'),
 ("chonoi/sim/quan_customers.py", "if (allowed is None or d in allowed)", "if (True)"),
 ("chonoi/sim/quan_customers.py", "for k in menu_kinds(sim.menu) | set(sim.stock)", "for k in set(sim.stock)"),
 ("chonoi/sim/quan_validation.py", 'if allowed is not None and c["dish_id"] not in allowed:', "if False:"),
 ("chonoi/sim/quan_validation.py", 'validate_items(c["reserved"], menu_kinds(menu))', 'validate_items(c["reserved"])'),
]
for f, a, b in M:
    p = pathlib.Path(f); src = p.read_text()
    assert src.count(a) == 1, a
    p.write_text(src.replace(a, b))
    try:
        r = subprocess.run([sys.executable, "-m", "unittest", "tests.test_p2_trung"], capture_output=True, text=True,
                           env={"PYTHONPATH": "tests:.", "PATH": "/usr/bin:/bin"})
        print("CAUGHT " if r.returncode else "MISSED ", f, "|", a.splitlines()[0])
    finally:
        p.write_text(src)
