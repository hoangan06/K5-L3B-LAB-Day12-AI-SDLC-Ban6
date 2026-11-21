# Clarify — câu hỏi và câu trả lời (PO ghi, cả nhóm dùng chung)

| # | Ngày giờ | Câu hỏi | Trả lời / giả định | Ai quyết |
|---|---|---|---|---|
| Q1 | 2026-11-21 | Id khách tự sinh dùng tiền tố gì, bắt đầu từ số mấy? PRD chỉ nói `order_id` = id khách và quy tắc nối hậu tố. | CHỜ coach. Nhóm chốt `sim.ids.new("C")` (contract 1.1 §5.1) | Trung hỏi |
| Q2 | 2026-11-21 | Khách chưa được chốt giá: snapshot/fixture để `base_price`, `tip` là vắng, `null` hay `0`? | CHỜ coach. Nhóm chốt vắng trường, không mặc định (contract 1.1 §4.1) | Trung hỏi |
| Q3 | 2026-11-21 | Khách đang ăn lúc hết ca: chỉ phát `paid` (reason `closing`), hay phát thêm `customer_left` (reason `closing`)? | CHỜ coach. Nhóm chốt chỉ `paid` (contract 1.1 §5.1) | Trung hỏi |
| Q4 | 2026-11-21 | Đơn `reserved` thiếu `reserved` mà kho không đủ công thức: mã 2 (quá tồn) hay chuyển `unfulfillable`? PRD nói "cấp theo order_tick rồi id bàn", thứ tự chỉ có nghĩa nếu được phép thiếu. | CHỜ coach. Tạm: mã 2 | Trung hỏi |
| Q5 | 2026-11-21 | Fixture `order_status: served` nhưng `state: waiting` có hợp lệ không? PRD chỉ nói eating ⇒ served. | CHỜ coach. Tạm: không chặn | Trung hỏi |
| Q6 | 2026-11-21 | Fixture có `order_tick` > 0 (tương lai so với phase_tick 0) hoặc `patience_ticks_left: 0` có hợp lệ không? | CHỜ coach. Tạm: chấp nhận | Trung hỏi |
| Q7 | 2026-11-21 | Khách bỏ đi vì hết kiên nhẫn: uy tín có kẹp `reputation_min` không? PRD chỉ ghi kẹp khi cộng boa. | CHỜ coach. Nhóm chốt kẹp [min, max] (contract 1.1 §4.3) | Trung hỏi |
| Q8 | 2026-11-21 | Món trên bếp/tay có `base_price` khác giá menu, hoặc `cook_ticks_left` lớn hơn thời gian nấu: có phải mã 2? | CHỜ coach. Tạm: không chặn | Trung hỏi |
