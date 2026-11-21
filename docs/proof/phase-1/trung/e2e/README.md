# Chơi thử hai buổi trên bản tích hợp (headless, hộp đen)

Chạy trên `main` local sau khi gộp `origin/p1/an` + `p2/trung` (2026-11-21). Chỉ giữ dòng event và end; snapshot bỏ cho gọn.

```bash
python3 -m chonoi.headless --mode gather --seed 1 --inputs docs/proof/phase-1/trung/e2e/g_in.json --ticks 3000 --out g.jsonl --inventory-out inv.json
python3 -m chonoi.headless --mode quan --seed 1 --inventory inv.json --inputs docs/proof/phase-1/trung/e2e/q_in.json --ticks 10800 --out q.jsonl
```

Kết quả: cả hai exit 0.
- Sáng: hái N3, N4 (bông súng), cập bến tick 1821 → kho `{"bong_sung": 2}`.
- Tối: khách C1 tới tick 120 gọi gỏi bông súng → nấu tick 126 → chín 366 → bưng 371 → phục vụ 526 (còn 3194 tick kiên nhẫn, boa 8) → trả 48 tick 1126 (`finished_eating`). Hết nguyên liệu: `no_dish` mỗi 900 tick. Kết thúc: money 48, uy tín 3.2, điểm 348.
- Đối chiếu tay: 3600 − (526 − 120) = 3194; boa floor(40 × 0.2) = 8 vì còn ≥ 50% kiên nhẫn; điểm 48 + 100 × floor(3.2) = 348.

Chưa kiểm: chơi trên trình duyệt (`chonoi.live`), bắt cá, ngạt/ngất trong luồng hai buổi.
