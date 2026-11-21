# Phase 2 — Trung: kết quả chạy thật

Nhánh `p2/trung`, chạy trên cây làm việc của HEAD `71dcdd2` + thay đổi QuanSim(context) chưa commit lúc ghi. Ngày 2026-11-21.

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
test_context_allowed_dishes_must_be_menu_ids (tests.test_p2_trung.QuanSimContext.test_context_allowed_dishes_must_be_menu_ids) ... ok
test_context_filters_spawned_dishes (tests.test_p2_trung.QuanSimContext.test_context_filters_spawned_dishes) ... ok
test_context_fixture_checked_against_real_stock (tests.test_p2_trung.QuanSimContext.test_context_fixture_checked_against_real_stock) ... ok
test_context_fixture_dish_outside_plan_rejected (tests.test_p2_trung.QuanSimContext.test_context_fixture_dish_outside_plan_rejected) ... ok
test_context_rejects_template_stock_and_reputation (tests.test_p2_trung.QuanSimContext.test_context_rejects_template_stock_and_reputation) ... ok
test_context_sets_working_state_and_is_not_mutated (tests.test_p2_trung.QuanSimContext.test_context_sets_working_state_and_is_not_mutated) ... ok
test_payment_adds_to_context_money_and_earned (tests.test_p2_trung.QuanSimContext.test_payment_adds_to_context_money_and_earned) ... ok
test_quan_end_reports_cross_day_totals (tests.test_p2_trung.QuanSimContext.test_quan_end_reports_cross_day_totals) ... ok
test_standalone_defaults (tests.test_p2_trung.QuanSimContext.test_standalone_defaults) ... ok
test_template_not_mutated (tests.test_p2_trung.QuanSimContext.test_template_not_mutated) ... ok

----------------------------------------------------------------------
Ran 25 tests in 0.350s

OK
```

## Toàn bộ test
```
Ran 105 tests in 8.566s

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
CAUGHT  chonoi/sim/quan.py | for key in ("stock", "reputation"):
CAUGHT  chonoi/sim/quan.py | if not isinstance(allowed, list) or not all(
CAUGHT  chonoi/sim/quan.py | self.money, self.earned = context["money"], context["earned"]
CAUGHT  chonoi/sim/quan.py | self.reputation = context["reputation"]
CAUGHT  chonoi/sim/quan.py | self.allowed_dishes = list(context["allowed_dishes"])
```

## Tất định (`python3 tools/check_determinism.py`, exit 0)
```
PASS gather: JSONL sha256=e75f8606372ba7bd86f0039a8a136d03f74adad1940ab017c61c4c81d7b9fd70
PASS gather inventory: sha256=599e112e7a4c3a048f918b031713b47de4ed62e3aa6fa3299099b3566144fcd5
PASS quan: JSONL sha256=0e851ebc46e11b49a37691000134db999139fdc797239342b565258443920228
PASS: repeated outputs match byte-for-byte (not proof of all gameplay rules)
```

## Phạm vi và chưa làm

- Có: `day_plan.resolve_day_plans`; `QuanSim(..., *, context=None)` (tiền/earned/uy tín lấy từ context, lọc `allowed_dishes`, cấm `quan.stock`/`quan.reputation` khi có context, kiểm fixture trên kho bàn giao); 6 kind theo công thức thực đơn; 2 bếp/4 bàn theo dữ liệu.
- Dữ liệu test: `docs/contracts/phase-2-tuning.sample.json` (giao diện P2 §9). Manifest runtime vẫn v1.0, nên headless chưa chạy 6 món.
- Chưa: test hộp đen headless cho quán P2 (cần manifest 1.1 của Duy và DaySim của Đức).
- `docs/proof/phase-1/trung/mutate.py` có một mục trỏ tới dòng `KINDS_P1` cũ; đó là bằng chứng của commit P1, không chạy lại trên nhánh này.
