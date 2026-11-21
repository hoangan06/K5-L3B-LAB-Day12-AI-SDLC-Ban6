# Ma trận truy vết Phase 1

| AC | Cách kiểm chứng | Bằng chứng (link `docs/proof/phase-1/...`) | Kết quả (đạt / chưa đạt — ghi trung thực) |
|---|---|---|---|
| Nội bộ DUY-01: hái/bắt và các biên | `tests/test_p1_duy.py`; test tích hợp sau khi nối helper | `docs/proof/phase-1/duy/results.md` | Test helper đạt; tích hợp chưa kiểm chứng |
| Nội bộ DUY-02: kho gather → quán | `python3 tools/smoke_inventory.py` | `docs/proof/phase-1/duy/results.md` | Đạt smoke với fixture cập bến |
| Nội bộ DUY-03: hồi cây, giữ phím, bến, ngất và tick limit | Test tích hợp sau khi phần Ân hoàn thành | `docs/proof/phase-1/duy/results.md` | Chưa đạt bằng chứng; phụ thuộc tích hợp và runtime |

## Đánh giá ngắn
- Các ID DUY là ID nội bộ, không phải mã chính thức của đề. Test helper và smoke kho đạt; các tình huống tích hợp còn thiếu như ghi ở trên.
- Điều cần chỉnh cho phase sau:
