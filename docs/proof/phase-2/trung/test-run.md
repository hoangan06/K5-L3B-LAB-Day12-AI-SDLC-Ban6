# Phase 2 — Trung: kết quả chạy thật

Nhánh `p2/trung`, base: `p1/trung` + merge `origin/p1/an` (bb1fb50). Ngày 2026-11-21.

## Test riêng
```
test_bad_preset_rejected (tests.test_p2_trung.DayPlan.test_bad_preset_rejected) ... ok
test_override_ingredients_matching_accepted (tests.test_p2_trung.DayPlan.test_override_ingredients_matching_accepted) ... ok
test_override_recomputes_and_keeps_other_days (tests.test_p2_trung.DayPlan.test_override_recomputes_and_keeps_other_days) ... ok
test_override_rejected (tests.test_p2_trung.DayPlan.test_override_rejected) ... ok
test_preset_matches_ticket (tests.test_p2_trung.DayPlan.test_preset_matches_ticket) ... ok
test_returns_copies (tests.test_p2_trung.DayPlan.test_returns_copies) ... ok
test_allowed_but_no_stock_is_no_dish (tests.test_p2_trung.QuanP2.test_allowed_but_no_stock_is_no_dish) ... ok
test_allowed_dishes_filter_before_stock (tests.test_p2_trung.QuanP2.test_allowed_dishes_filter_before_stock) ... ok
test_available_stock_covers_new_kinds (tests.test_p2_trung.QuanP2.test_available_stock_covers_new_kinds) ... ok
test_fixture_dish_outside_plan_rejected (tests.test_p2_trung.QuanP2.test_fixture_dish_outside_plan_rejected) ... ok
test_fixture_on_b2_t4_and_new_kinds_valid (tests.test_p2_trung.QuanP2.test_fixture_on_b2_t4_and_new_kinds_valid) ... ok
test_four_tables_filled_in_id_order_then_skip (tests.test_p2_trung.QuanP2.test_four_tables_filled_in_id_order_then_skip) ... ok
test_no_quota_after_planned_servings (tests.test_p2_trung.QuanP2.test_no_quota_after_planned_servings) ... ok
test_standalone_uses_all_six_dishes (tests.test_p2_trung.QuanP2.test_standalone_uses_all_six_dishes) ... ok
test_unknown_kind_in_reserved_rejected (tests.test_p2_trung.QuanP2.test_unknown_kind_in_reserved_rejected) ... ok

----------------------------------------------------------------------
Ran 15 tests in 0.005s

OK
```

## Toàn bộ test
```
Ran 80 tests in 2.949s

OK
```

## Mutation (`python3 docs/proof/phase-2/trung/mutate.py`)
```
CAUGHT  chonoi/sim/day_plan.py | if "ingredients" in entry and entry["ingredients"] != ingredients:
CAUGHT  chonoi/sim/day_plan.py | if not _pos_int(day) or day not in DAYS:
CAUGHT  chonoi/sim/day_plan.py | if dish not in menu or not _pos_int(n):
CAUGHT  chonoi/sim/day_plan.py | if p["day"] in seen:
CAUGHT  chonoi/sim/day_plan.py | out[kind] = out.get(kind, 0) + k * n
CAUGHT  chonoi/sim/day_plan.py | return {"day": day, "dishes": dict(dishes), "ingredients": ingredients}
CAUGHT  chonoi/sim/day_plan.py | plans[p["day"]] = p
CAUGHT  chonoi/sim/quan_customers.py | if (allowed is None or d in allowed)
CAUGHT  chonoi/sim/quan_customers.py | for k in menu_kinds(sim.menu) | set(sim.stock)
CAUGHT  chonoi/sim/quan_validation.py | if allowed is not None and c["dish_id"] not in allowed:
CAUGHT  chonoi/sim/quan_validation.py | validate_items(c["reserved"], menu_kinds(menu))
```

## Phạm vi và chưa làm

- Có: `chonoi/sim/day_plan.py` (`resolve_day_plans`), lọc `allowed_dishes` khi sinh khách và khi kiểm fixture, kind lấy từ công thức thực đơn (6 kind), 2 bếp/4 bàn theo dữ liệu.
- Dữ liệu test: `docs/contracts/phase-2-tuning.sample.json` (giao diện P2 §9). Manifest runtime vẫn v1.0.
- Chưa: `QuanSim(context=...)` trong `quan.py`, vì Đức chưa bàn giao `quan_kitchen.py` P1. Chưa có test hộp đen headless cho quán P2.
- `docs/proof/phase-1/trung/mutate.py` có một mục trỏ tới dòng `KINDS_P1` cũ; đó là bằng chứng của commit P1, không chạy lại trên nhánh này.
