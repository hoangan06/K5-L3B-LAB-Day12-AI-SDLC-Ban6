# Ma trận kiểm chứng Phase 2

Các ID dưới đây do nhóm đặt, không phải mã chính thức của đề.

| ID nội bộ | Yêu cầu | Cách kiểm và bằng chứng | Trạng thái |
|---|---|---|---|
| Duy-P2-01 | Cá khởi tạo, bơi, đổi hướng, sinh và tất định | `tests/test_p2_duy.py`; GatherSim đã gọi init/update/snapshot_fish; `docs/proof/phase-2/an/release-tests.txt` | Đạt test và tích hợp, manifest thật khởi tạo 8 đàn |
| Duy-P2-02 | Thu hoạch và kho 6 kind | `docs/proof/phase-2/an/release-six-kind.txt` | Đạt CLI gather → file kho → quan tick 0, đủ 6 kind |
| Duy-P2-03 | Dữ liệu v1.1 và đầu vào | game.contract.json đồng bộ tuning mẫu; release-tests.txt | Đạt kiểm tra hiện có, contract 1.1; chưa bật 1.2 |
| Duy-P2-04 | Hai tiến trình Gather → Quán | `docs/proof/phase-2/an/release-inventory.txt` và release-six-kind.txt | Đạt với manifest 1.1 thật |
| An-P2-05 | Trọn 5 ngày headless | `docs/proof/phase-2/an/day-five-summary.json` | Đạt 111000 tick, days_complete, days_completed=5, 5 Shop đóng |
| An-P2-06 | Live 5 ngày và tổng kết | `docs/proof/phase-2/an/live-five-summary.json`; `tools/check_phase2_live_release.py` | Đạt qua LiveGame/HTTP tăng tốc, giữ nguyên luật/timer, quan sát trang tổng kết đủ 5 ngày trên trình duyệt |
| An-P2-07 | Pause, quái, Shop/nâng cấp và hồi quy | `docs/proof/phase-2/an/release-tests.txt` | 192/192 test đạt; live toàn vòng không input nên chưa là demo chủ động thu hoạch/phục vụ đủ 5 ngày |
| An-P2-08 | Tính tất định | `docs/proof/phase-2/an/release-determinism.txt` | Đạt JSONL gather/quan và kho ngất |

Các kết quả release của Ân chạy trên working tree từ main 26e481a, chưa phải bằng chứng của tag. Chi tiết lệnh, môi trường và lý do sửa test: `docs/proof/phase-2/an/RELEASE-PHASE-2.md`. Headless 5 ngày mất khoảng 3.153 giây trên máy thử, không thay cho số đo máy chấm hoặc FPS đồ họa.
