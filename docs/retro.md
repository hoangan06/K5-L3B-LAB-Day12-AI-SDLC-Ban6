# Retro nhóm

## Phase 2 (nhanh)
> Nháp do Trung gom, cả nhóm bổ sung/sửa.
- Điều tốt:
  - Mỗi người có test riêng, gộp nhánh thường xuyên; sau mỗi lần gộp toàn bộ test vẫn xanh (192 test trên main `26e481a`).
  - Mutation test (`docs/proof/phase-*/trung/mutate.py`) phát hiện test còn sót lỗi nên bổ sung được trước khi bàn giao.
  - Đức thử được luồng 5 ngày trên trình duyệt bằng bộ giả tạm khi chưa có Session thật.
- Điều tệ:
  - Code P2 của từng người lên repo muộn và gần như cùng lúc, nên tích hợp dồn về cuối; chưa có tag `phase-2`.
  - Manifest vẫn `contract_version 1.0`, nên `--mode day` báo mã 2 dù code day/shop/session đã có.
  - Đề xuất 6 câu hỏi clarify không có mâu thuẫn thật trong đề, PO phải bỏ; bot Anh Năm không dùng được (lỗi quyền).
  - TEAM.md còn thiếu một dòng thành viên (`tools/check_team.py` không đạt).
- 1 hành động cho Phase 3: nâng manifest/contract ngay đầu phase và đẩy lên main trước, rồi mới làm luật trên đó.

## Phase 4 (cuối)
- Rà lại hành động Phase 2: đã làm chưa? vì sao?
- Điều tốt / điều tệ:
- Số liệu: số commit theo người, cách đọc code của nhau, token theo người:
- Một lần AI sai và cách nhóm phát hiện:
- Nếu làm lại, đổi gì:
