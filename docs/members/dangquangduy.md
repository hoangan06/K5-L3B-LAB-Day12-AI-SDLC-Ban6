# Đặng Quang Duy — duydang2k4

- Tôi đã làm (kèm link commit): Phụ trách `gather_fish`, `gather_actions`, dữ liệu và validation kho/scenario; bổ sung kiểm thử cá, độ tươi, bể cá và soak. Các thay đổi đã được tích hợp trong [bản phát hành v1.0.0](https://github.com/hoangan06/K5-L3B-LAB-Day12-AI-SDLC-Ban6/commit/b9a704e). [Bằng chứng Phase 4](../proof/phase-4/duy/results.md).
- Tôi đã review (kèm link): Rà pipeline Gather → file kho → Quán, test tích hợp và luật bể cá live; đối chiếu thêm [bằng chứng tích hợp Phase 1](../proof/phase-1/an/INTEGRATION-DUY.md) và [kiểm tra bể cá](../proof/phase-4/duy/live-fish-tank.md).
- AI sai ở đâu và tôi phát hiện thế nào: Không coi test helper hoặc fixture là bằng chứng runtime đã tích hợp; các ghi nhận Phase 1–3 chỉ rõ helper, manifest và caller còn chưa nối. Tôi kiểm tra lại bằng smoke, test tích hợp và soak hai lượt cùng seed.
- Điều tôi học được: Phải phân biệt kiểm thử đơn vị, fixture và luồng chạy thật; khi thay đổi contract hoặc tuning, cần kiểm tra cả tính tất định, dữ liệu biên và đường bàn giao giữa các module.
