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
- Rà lại hành động Phase 2 ("nâng manifest/contract ngay đầu phase và đẩy lên main trước"): **làm một phần**. Manifest 1.2 lên main cùng lúc với toàn bộ migration (commit `5f9a0aa`), không lên trước, vì đổi riêng manifest làm gãy code kho đếm (ghi chú §4 của `docs/PHAN-CONG-PHASE-3.md`: "Không merge riêng manifest 1.2 khi gather/adapter/day vẫn dùng count map"). Bù lại: Ân đưa fixture chung và giao diện P3 lên main sớm (`c367e7a`), nên test của Ân/Duy viết song song được.
- Điều tốt: phân quyền file giúp Ân nối runner, Duy nối DaySim/soak, Đức làm UI/bench, Trung migration/docs; regression cuối 278 test đạt. Bot soak đã đi qua hái, nấu, phục vụ và thu tiền thật, không chỉ hết giờ.
- Điều cần sửa: các ma trận/notes ban đầu còn trỏ kết quả nhánh cũ; benchmark tính load từ trang và chưa bỏ intro. Đã đo lại, gắn bằng chứng theo source và ghi rõ kiểm tự động bằng fixture thay vì nhận là chơi tay.
- Số liệu: commit không tính merge trên `origin/main` lúc Trung gom (sau `918ed67`): trungnb 22, hoangan06 12, laitrongduc 12, duydang2k4 4, giảng viên (Hai Duong) 9. Token theo người: UNKNOWN (chưa ai đo). Cách đọc code của nhau: (mỗi người bổ sung)
- Cách đọc code khi tích hợp: Ân đối chiếu Session/DaySim, pipeline LIFO/freshness và serializer bằng test CLI; kiểm benchmark bằng Chrome rồi đọc screenshot cảnh báo. Mutation quán của Trung bổ sung kiểm luật ngoài regression.
- Một lần AI sai và cách phát hiện: test của AI đọc dòng event đầu lượt day như snapshot; CLI thật báo KeyError, sửa test chọn type=snapshot. Không sửa thứ tự JSONL để chiều test.
- Hành động tiếp theo: chốt SHA ứng viên trước khi đo, xuất báo cáo tự động vào ma trận; đổi version phải giữ các gate test P3 chạy; rà giấy phép trước ngày phát hành. Chủ repo hiện chọn chưa công bố giấy phép, đã ghi rõ thay vì tự điền MIT.
- Phản tư cá nhân: đã có Ân, Đức, Trung; file tự phản tư của Duy chưa có tại thời điểm chốt. Giữ trạng thái này để thành viên bổ sung, không viết thay phản tư cá nhân.
