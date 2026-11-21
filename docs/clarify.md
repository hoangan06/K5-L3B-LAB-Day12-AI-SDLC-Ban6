# Clarify — câu hỏi và câu trả lời (PO ghi, cả nhóm dùng chung)

| # | Ngày giờ | Câu hỏi | Trả lời / giả định | Ai quyết |
|---|---|---|---|---|
| P1-Q01 | 2026-11-21 | ID khách tự sinh? | Nhóm dùng C1, C2…; reserve ID fixture và nối sau hậu tố lớn nhất, không tái dùng. | Quy ước nhóm, tổng hợp theo yêu cầu Ân |
| P1-Q02 | 2026-11-21 | base_price/tip customer trước phục vụ? | Vắng cả hai khóa; giá đã chốt của đơn assigned nằm trong payload món. Khi served/eating mới có giá và tip (tip có thể 0). | Quy ước nhóm |
| P1-Q03 | 2026-11-21 | Khách eating hết ca có thêm customer_left? | Chỉ paid rồi xóa. Ăn vừa xong: finished_eating; còn timer hoặc vừa phục vụ: closing. | Suy luận thứ tự F, chốt nhóm |
| P1-Q04 | 2026-11-21 | Fixture reserved không khai giữ và thiếu kho? | Tạm chốt mã 2 trước output; không cấp thiếu/không tự thành unfulfillable. Thứ tự cấp không chứng minh cơ chế đổi trạng thái. Cần PO xác nhận. | Giả định nhóm, chưa có trả lời giảng viên |
| P1-Q05 | 2026-11-21 | waiting + served hợp lệ? | Tạm chốt mã 2, served đi với eating; không tự suy timer/giá. Cần PO xác nhận vì PRD chỉ viết tường minh một chiều. | Giả định nhóm, chưa có trả lời giảng viên |
| P1-Q06 | 2026-11-21 | order_tick tương lai và patience=0? | Cho order_tick nguyên không âm, không coi là lịch sinh fixture; khách hiện tick 0. Cho waiting patience=0, xử lý interact rồi rời ở bước đầu. Không xử lý rời trong constructor. | Quy ước fixture; chưa có trả lời giảng viên về order_tick tương lai |
| P1-Q07 | 2026-11-21 | Giảm uy tín có kẹp? | Có, kẹp reputation_min/max; closing không phạt. Event dùng giá trị sau kẹp. | Quy ước nhóm theo miền uy tín |
| P1-Q08 | 2026-11-21 | Giá món fixture khác menu/timer nấu vượt chuẩn? | Cho phép nếu đúng kiểu/miền/trạng thái/liên kết; không thêm điều kiện bằng giá menu hoặc trần cook timer. Dùng nguyên giá payload khi phục vụ và thu tiền. Runtime nấu mới vẫn theo tuning. | Quy ước fixture theo ràng buộc đã nêu, không phải xác nhận giảng viên |

Chi tiết thực thi và test cần làm: [giao diện bản 1.2, mục 11](contracts/phase-1-interfaces.md#11-quyết-định-bổ-sung-cho-câu-hỏi-của-trung--bản-12). Các dòng trên là quyết định/giả định nhóm để triển khai thống nhất, không giả nhận đã hỏi trợ giảng hoặc đã có bằng chứng test. Khi có trả lời chính thức, ghi thêm nguồn và cập nhật validator, caller, test cùng lúc.
