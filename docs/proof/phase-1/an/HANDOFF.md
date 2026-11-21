# Bàn giao phần Ân — Phase 1

Ngày thực hiện: 21/11/2026 (Asia/Saigon). Nhánh: `p1/an`.
Base commit: `dd568c3c40f6405f789f9620a107ba4b78cab9bf`.
Các kết quả bên dưới chạy trên working tree chưa commit, không phải bằng chứng của tag phase-1. `source-sha256.txt` ghi hash file code/test/command tương ứng.

## Đã triển khai

- gather.py: oxy theo độ sâu cuối bước, hồi ở mặt nước và kẹp tối đa; dive/surface với bản sao vị trí; oxygen_empty chỉ lúc từ dương xuống 0.
- Đếm ngạt gồm bước vừa hết oxy; choke trừ máu đúng interval; nổi lên đúng bước ngạt không mất máu và reset ngạt.
- Máu 0: mất giỏ theo LIFO, phát choke → faint → gather_end, kho rỗng, dừng trước cập bến/bắt cá/hết giờ. Không phát kết thúc lần nữa khi gọi sim.step sau done.
- Giữ nguyên schema snapshot, CLI, preset và đường ghi kho của runner.
- 15 test riêng trong tests/test_p1_an.py, gồm CLI thật kiểm ngất dừng sớm và ghi kho rỗng.
- Command tools/check_determinism.py: chạy headless gather/quan hai lần và so byte JSONL; probe gather bắt buộc ngất và so kho rỗng. Command thất bại nếu subprocess lỗi, thiếu end/kho hoặc byte khác nhau. Đây là kiểm tất định, không xác nhận đầy đủ luật quán/thu hoạch.

## Kết quả kiểm chứng

| Kiểm tra | Kết quả | Bằng chứng |
|---|---|---|
| 15 test riêng Ân | PASS | Nằm trong test-results-utf8.txt |
| Toàn bộ test công khai + test Ân | 47/47 PASS | test-results-utf8.txt |
| Live HTTP / input / dừng server | PASS ngoài sandbox | test-results-utf8.txt |
| Hai lần gather/quan giống byte; kho ngất giống byte | PASS | determinism-results.txt |

Lần đầu full suite trong sandbox: 46 pass, 1 lỗi quyền socket localhost WinError 10013 (`test-results.txt`). Chạy ngoài sandbox lần tiếp theo 47 pass nhưng có lỗi decode stderr do CP1252/UTF-8 (`test-results-unsandboxed.txt`). Kết quả cuối cùng dùng PYTHONUTF8=1 và PYTHONIOENCODING=utf-8, 47 pass, không lỗi decode (`test-results-utf8.txt`). Giữ log cũ để thể hiện các lần thử thật.

## Cách chạy lại

Máy có python3 hoạt động:

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
python3 tools/check_determinism.py
```

Trên máy Windows hiện tại, `python`/`python3` là WindowsApps alias không chạy được. Đã dùng Python 3.12.14 đi kèm Codex, không cài package mới và không sửa headless_cmd/test nguồn để hợp máy này.

PowerShell, từ gốc repo:

```powershell
$anPython = 'C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1119-907-0_26.1119.907.0_x64__3k8sg7r9htsxt/dependencies/python/python.exe'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
& $anPython -B -m unittest discover -s tests -p test_p1_an.py -v
& $anPython -B tools/check_determinism.py --python $anPython
```

Full suite trên máy này dùng adapter **trong tiến trình chạy test**: giữ nguyên các argument headless trong contract, chỉ thay interpreter python3 bằng sys.executable. Không thay hàm test/assertion và không sửa tests/helpers.py. Đây không phải kiểm lệnh python3 native của máy.

```powershell
& $anPython -B -c 'import sys,unittest; sys.path.insert(0,"tests"); import helpers; configured=helpers.headless_cmd(); assert configured[0] == "python3", configured; helpers.headless_cmd=lambda: [sys.executable,*configured[1:]]; print("Local interpreter adapter: python3 -> " + sys.executable, flush=True); suite=unittest.defaultTestLoader.discover("tests"); result=unittest.TextTestRunner(verbosity=2).run(suite); sys.exit(not result.wasSuccessful())'
```

Nếu môi trường chặn localhost, cần chạy với quyền cho phép socket để xác minh test_live; không bỏ test rồi báo tất cả pass. Ở máy khác, dùng Python của máy đó, không chép đường dẫn cài Codex ở trên.

## Phần chờ tích hợp — không tính là hoàn thành

`gather_actions.py` của Duy chưa có tại thời điểm làm phần Ân. Hai TODO hái/bắt của starter vẫn được giữ; chưa import module vắng mặt, không viết stub hoặc làm thay luật của Duy.

Sau khi nhận helper thật, Ân thêm import:

```python
from .gather_actions import gather_node, catch_fish
```

Trong step, thay TODO hái sau nhánh bến bằng `gather_node(self, events)`; thay pass của catch bằng `catch_fish(self, events)`. Giữ nguyên cạnh input và thứ tự oxy/ngất → bến/hái → catch → hết giờ. Chạy lại test mọi lát và smoke kho trước khi merge main/tag.

- Command smoke kho thứ hai do Duy làm, chưa có trong nhánh này.
- Chưa tích hợp khách/bếp của Trung/Đức; test xanh không đồng nghĩa game Phase 1 đã đủ luật.
- TEAM.md, mã nhóm/game.contract.json và thông tin tài khoản để người dùng tự điền theo yêu cầu; không tự đặt GitHub handle hay kênh liên lạc.
- Chưa commit, push, merge main hoặc gắn tag. Chưa kiểm demo bằng mắt trên trình duyệt; test live chỉ xác minh server/input.

## Nhật ký AI gửi Trung tập hợp

Phase 1 | Ân | Codex | Viết oxy/ngạt/ngất, test biên, command tất định và bằng chứng; rà contract 1.1 | Token/chi phí: chưa đo | Ban đầu python alias không chạy; tìm runtime Python thật. Test localhost bị sandbox chặn; chạy lại ngoài sandbox. Bật UTF-8 để sửa môi trường log/test, không sửa test cho xanh. Người dùng cần tự đọc/review code trước bàn giao.
