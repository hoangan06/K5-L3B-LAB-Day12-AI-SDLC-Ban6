# Lát 3 (Trung) — kết quả thật

Nhánh p1/trung, HEAD dd568c3 (giao diện 1.1); code lát 3 chưa commit lúc chạy.

```
$ PYTHONPATH=tests:. python3 -m unittest tests.test_p1_trung -v
test_an_xong_dung_tick_dong_ca_la_finished_eating (tests.test_p1_trung.Departures.test_an_xong_dung_tick_dong_ca_la_finished_eating) ... ok
test_an_xong_tra_tien_roi_ban (tests.test_p1_trung.Departures.test_an_xong_tra_tien_roi_ban) ... ok
test_dong_ca (tests.test_p1_trung.Departures.test_dong_ca) ... ok
test_het_kien_nhan_roi_tru_uy_tin_nha_giu (tests.test_p1_trung.Departures.test_het_kien_nhan_roi_tru_uy_tin_nha_giu) ... ok
test_ban_ban_bo_luot_va_luot_sau (tests.test_p1_trung.Spawn.test_ban_ban_bo_luot_va_luot_sau) ... ok
test_chi_chon_mon_du_nguyen_lieu_kha_dung (tests.test_p1_trung.Spawn.test_chi_chon_mon_du_nguyen_lieu_kha_dung) ... ok
test_cung_seed_cung_mon (tests.test_p1_trung.Spawn.test_cung_seed_cung_mon) ... ok
test_kien_nhan_giam_tu_buoc_sau (tests.test_p1_trung.Spawn.test_kien_nhan_giam_tu_buoc_sau) ... ok
test_lich_khach_theo_phase_tick (tests.test_p1_trung.Spawn.test_lich_khach_theo_phase_tick) ... ok
test_luot_thu_hai_dung_chu_ky (tests.test_p1_trung.Spawn.test_luot_thu_hai_dung_chu_ky) ... ok
test_no_dish_khi_co_ban_ma_thieu_mon (tests.test_p1_trung.Spawn.test_no_dish_khi_co_ban_ma_thieu_mon) ... ok
test_tat_khach_ngau_nhien_va_het_gio (tests.test_p1_trung.Spawn.test_tat_khach_ngau_nhien_va_het_gio) ... ok
test_timer_bep (tests.test_p1_trung.Spawn.test_timer_bep) ... ok
test_kha_dung_tru_giu_cho_khong_doi_ton (tests.test_p1_trung.Stock.test_kha_dung_tru_giu_cho_khong_doi_ton) ... ok
test_fixture_chung_cua_nhom_hop_le_va_khong_bi_sua (tests.test_p1_trung.Validation.test_fixture_chung_cua_nhom_hop_le_va_khong_bi_sua) ... ok
test_fixture_mac_dinh (tests.test_p1_trung.Validation.test_fixture_mac_dinh) ... ok
test_hop_le (tests.test_p1_trung.Validation.test_hop_le) ... ok
test_tu_choi (tests.test_p1_trung.Validation.test_tu_choi) ... ok

----------------------------------------------------------------------
Ran 18 tests in 0.003s

OK

$ python3 docs/proof/phase-1/trung/mutate.py  # làm hỏng từng luật, test phải FAIL (CAUGHT)
CAUGHT  if n > sim.stock.get(k, 0):
CAUGHT  if res != sim.menu[c["dish_id"]]["recipe"]:
CAUGHT  if c["id"] in holders:
CAUGHT  elif c["eat_ticks_left"]:
CAUGHT  if all(avail.get(k, 0) >= n
CAUGHT  if reason == "patience":
CAUGHT  if c["eat_ticks_left"] == 0:
CAUGHT  if sim.phase_tick < first or
CAUGHT  avail = {k: sim.stock.get(k, 0) for k in KINDS_P1}
CAUGHT  for raw in copy.deepcopy(scenario.get("customers", [])):
CAUGHT  if s["state"] == "ready":

$ PYTHONPATH=tests:. python3 -m unittest discover -s tests
Ran 50 tests in 2.725s

OK
```
