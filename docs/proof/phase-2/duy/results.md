# Bàn giao tạm phần Duy — Phase 2

- Base `4229ebf`; các thay đổi hiện chưa commit. Chạy trên Windows, Python `.venv` 3.11.9 ngoài sandbox.
- `$env:PYTHONPATH='tests;.'; .\.venv\Scripts\python.exe -m unittest discover -s tests`: **120 test đạt**, 7.808 giây. Gồm test helper cá, nguyên liệu mới, dữ liệu mẫu và một số scenario.
- `.\.venv\Scripts\python.exe tools/smoke_inventory.py`: **PASS** với manifest P1; kiểm Gather ghi kho và Quán đọc stock tick 0, không chứng minh kho P2 sáu kind.
- `gather_fish.py` cung cấp `init_fish`, `update_fish`, `snapshot_fish`; caller cần dựng `t`, `rng`, `ids`, `phase_tick`, gọi theo giao diện P2. Không sửa `gather.py` của Ân.
- Dữ liệu dự thảo nằm ở `docs/contracts/phase-2-tuning.sample.json`; manifest runtime vẫn P1 vì GatherSim hiện chưa đọc `fish_initial` dạng số. Cần ghép manifest, validator, helper và caller cùng lúc.
- Chưa kiểm đủ validator P2 cho monster/day/shop và context nâng cấp; validator monster/day/shop thuộc các module Ân/Đức chưa có tại base này. Chưa kiểm CLI day, smoke kho 6 kind hai tiến trình, tính tất định pipeline P2 hoặc hiệu năng ngày đầy đủ. Chưa coi Phase 2 đã hoàn thành.
