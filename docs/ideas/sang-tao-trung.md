# Ý tưởng sáng tạo (đề xuất của Trung)

> Ý tưởng gốc của Trung; AI tra nguồn và mở rộng. Chưa code. Mục "Sáng tạo của nhóm" trong README do Đức giữ:
> nhóm chọn ý nào thì Đức chép sang đó. Chỉ giữ thông tin văn hóa **có nguồn**; chỗ không chắc đã bỏ.

## 0. Ràng buộc (PRD-0) và quyết định của Trung

- PRD-0 §1: giữ luật lõi, số chuẩn và Test Contract. **Mọi phần thêm tắt ở headless.** Làm lõi đúng trước.
- Luật lõi "3 Máu, chỉ mất do ngạt" → **quái không trừ Máu, quái gây ngạt (choke)**. *(Trung chốt)*
- **Thắp hương tốn thời gian, không tốn tiền.** Tiền là luật lõi; đổi tiền lấy phước dễ phản cảm với tín ngưỡng đang được thờ thật. *(Trung chốt)*
- Phần sáng tạo **không trái đề thì làm**: có thể đổi trải nghiệm ở chế độ live (hồi sinh, thêm khách, món phụ) khi tắt hoàn toàn ở headless. *(Trung chốt)*
- Ngẫu nhiên sáng tạo dùng luồng `Streams` riêng (ví dụ `creative_monster`), chỉ bật trong `chonoi.live`, không chạm luồng của luật lõi.
- PRD-0 §3 yêu cầu tôn trọng văn hóa địa phương: thần được thờ chỉ làm đền (hình ảnh trang nghiêm), không làm quái.
- Rủi ro (suy luận, chưa kiểm chứng): commit `5ffca8c` của giảng viên ("bỏ nhắc sớm về sinh vật của phase sau") gợi ý phase sau có sinh vật chính thức. Vì vậy quái làm thành lớp dữ liệu riêng, dễ tắt hoặc thay.

## 1. Quái buổi sáng (chỉ live)

| Quái | Cơ chế (gây ngạt, không trừ Máu) | Gốc truyền thuyết |
|---|---|---|
| **Ông Năm Chèo** | Hiện ngẫu nhiên ở vùng sâu, tạo **nước xoáy** kéo Út Sen xuống và làm oxy tụt nhanh. | Thủy quái sông Vàm Nao (An Giang), tương truyền là con sấu đỏ 5 chân. Vàm Nao nối sông Tiền với sông Hậu nên nước xoáy dễ làm chìm ghe; dân gian cho rằng dòng xiết là do ông thở mạnh. Ghe đi ngang thường thắp hương khấn vái [1][2][3] |
| **Mãng Xà Vương** (tên game do nhóm đặt) | Quấn người chơi vài giây, không bơi được, oxy vẫn giảm; bấm E liên tục để thoát. | Lấy cảm hứng từ chuyện rắn khổng lồ ở Thất Sơn: người sóc Tà Đéc (xã An Hảo, Tịnh Biên) kể có cặp rắn bò từ núi Bà Đội Om sang núi Cấm [4][5] |

**Bảng "ngạt vì…"** (ý của Trung): khi ngất, cửa sổ live hiện 2–3 câu về truyền thuyết của quái gây ra, kèm nguồn. Headless vẫn phát `faint` với `cause: "choke"` đúng contract.

## 2. Đền thờ (thắp hương: đứng ở đền vài giây → luck tăng)

| Đền | Tác dụng (chỉ live) | Gốc tín ngưỡng |
|---|---|---|
| **Bà Thủy Long** | Buổi sáng ít gặp quái hơn | Thủy Long Thánh Mẫu ("Bà Thủy"), nữ thần sông nước, thường thờ ở ngã ba sông, phù hộ dân chài [6][7] |
| **Cá Ông** | Khi ngất được roll xúc xắc, ra 6 thì hồi sinh, "được cá Ông đưa về" (ý của Trung) | Cá Ông là cá voi, ngư dân xem là thần Nam Hải cứu người gặp nạn trên biển; miền Tây Nam Bộ cúng giỗ vào ngày cá Ông lụy [8][9] |
| **Bà Chúa Xứ** (đề xuất thêm) | Buổi tối đông khách hơn | Nữ thần tài lộc ở núi Sam, Châu Đốc; lễ hội Vía Bà được UNESCO ghi danh năm 2024 [10][11] |
| **Neak Ta / Ông Tà** (đề xuất thêm) | Ghép với bún nước lèo: khách Khmer ghé quán | Thần giữ phum sóc của người Khmer, gắn với cầu mưa, giữ ruộng; lễ Đom Lơng Neak Ta (Trà Vinh) là di sản phi vật thể quốc gia năm 2024 [12] |

## 3. Món và chuyện kể

| Món | Chuyện kể / gốc | Trong game |
|---|---|---|
| **Cá lóc nướng trui** (menu lõi) | Món của thời di dân khẩn hoang, không có ở quê gốc miền Trung (theo nhà nghiên cứu Nguyễn Đình Tư, SGGP dẫn). Thời đó thiếu nồi niêu, bắt cá là nướng ngay [13] | Giữ công thức lõi; thẻ món ở live kể chuyện này |
| **Bún nước lèo** | Đặc sản Sóc Trăng – Trà Vinh, hòa vị ba dân tộc Kinh, Hoa, Khmer [14][15]. Gốc Sóc Trăng hay Trà Vinh còn tranh cãi [15] | Món phụ chỉ ở live (PRD cố định 3 món) |
| **Lẩu mắm** | Sơn Nam cho là gốc ở Châu Đốc, có nguồn khác cho là gốc Khmer (nguồn mâu thuẫn). Nấu từ mắm cá linh, mắm cá sặc; cá linh theo nước lũ về [16] | Món phụ live, gắn với "mùa nước nổi" và cá linh có sẵn |
| **Cháo trắng lá dứa** | Món bình dân phổ biến khắp miền Tây, ăn kèm nước cốt dừa và đồ mặn [17] | Món ăn sáng trước khi lặn (live); không kể chuyện lịch sử vì không có nguồn |

Đã bỏ vì không có nguồn: giai thoại "lộc trời" của lẩu mắm, lịch sử cháo lá dứa, ma da (nguồn yếu).

## 4. Thứ tự làm đề xuất

1. **Gói 1 (nhỏ, không đổi luật lõi):** Ông Năm Chèo + đền Bà Thủy + bảng "ngạt vì…". Dùng lại oxy/ngạt có sẵn, không đụng tiền và uy tín. Cần một cờ `creative` trong live, một luồng RNG riêng và một khung hiển thị.
2. **Gói 2:** Mãng Xà Vương, đền cá Ông (xúc xắc hồi sinh), thẻ món.
3. **Gói 3:** Bà Chúa Xứ, Neak Ta, món phụ. Làm khi lõi các phase sau đã ổn.

Mỗi gói cần có bằng chứng "lõi vẫn đúng": test headless chạy giống hệt khi bật/tắt cờ `creative` (PRD-0 §1, DoD).

## Nguồn

AI mới đọc phần trích trong kết quả tìm kiếm, chưa mở toàn văn từng bài. Trước khi đưa câu chữ vào game, cần mở link kiểm lại.

1. VTC News — Thủy quái Vàm Nao và giai thoại cá sấu 5 chân: https://vtcnews.vn/thuy-quai-vam-nao-va-giai-thoai-thu-vi-ve-ca-sau-5-chan-thanh-tinh-ar400798.html
2. Tuổi Trẻ — Huyền thoại đánh bắt "quái ngư" Vàm Nao: https://tuoitre.vn/huyen-thoai-danh-bat-quai-ngu-vam-nao-20180530140302313.htm
3. Báo Cần Thơ — Truyện "Ông Năm Chèo" trong đời sống dân gian Nam Bộ: https://baocantho.com.vn/truyen-ong-nam-cheo-trong-doi-song-dan-gian-nam-bo-a99831.html
4. Báo Bắc Ninh — Chuyện ly kỳ về rắn khổng lồ ở núi Cấm: https://baobacninhtv.vn/chuyen-ly-ky-ve-ran-khong-lo-nang-300-400-kg-o-nui-cam-postid291595.bbg
5. Tiền Phong — Chuyện ly kỳ về rắn khổng lồ nặng 300–400 kg: https://tienphong.vn/xa-hoi/517620/Chuyen-ly-ky-ve-ran-khong-lo-nang-300---400-kg.html
6. Wikipedia — Thủy Long Thánh Mẫu: https://vi.wikipedia.org/wiki/Th%E1%BB%A7y_Long_Th%C3%A1nh_M%E1%BA%ABu
7. Hội An Heritage — Tín ngưỡng thờ bà Thủy Long: https://hoianheritage.net/vi/trao-doi-chuyen-nganh/chuyen-de-nghien-cuu-trao-doi/tin-nguong-tho-ba-thuy-long-o-hoi-an-1277.html
8. Wikipedia — Tục thờ cá Ông: https://vi.wikipedia.org/wiki/T%E1%BB%A5c_th%E1%BB%9D_c%C3%A1_%C3%94ng
9. Thư viện Cần Thơ — Tục thờ cá Ông ở miền Tây Nam Bộ: http://www.cantholib.org.vn:84/View.aspx?p=16A6074627B95A75553716A6E73647C92A95554737E6B64648C92A956677
10. UNESCO — Festival of Bà Chúa Xứ goddess at Sam mountain: https://ich.unesco.org/en/RL/festival-of-ba-chua-xu-goddess-at-sam-mountain-01999
11. Wikipedia — Bà Chúa Xứ: https://en.wikipedia.org/wiki/B%C3%A0_Ch%C3%BAa_X%E1%BB%A9
12. Quản lý Nhà nước — Tín ngưỡng thờ Neak Ta của người Khmer Nam Bộ tại Trà Vinh: https://www.quanlynhanuoc.vn/2024/09/05/phat-huy-gia-tri-tin-nguong-tho-neak-ta-cua-nguoi-khmer-nam-bo-tai-tinh-tra-vinh
13. SGGP — Nhớ cá lóc đồng nướng trui: https://www.sggp.org.vn/nho-ca-loc-dong-nuong-trui-post702292.html
14. VietnamPlus — Bún nước lèo Sóc Trăng: https://www.vietnamplus.vn/bun-nuoc-leo-mon-dac-san-nhat-dinh-phai-thu-khi-co-dip-den-soc-trang-post914536.vnp
15. Người Việt — Bún nước lèo Sóc Trăng hay Trà Vinh là chính gốc?: https://www.nguoi-viet.com/doi-song/bun-nuoc-leo-soc-trang-hay-tra-vinh-la-chinh-goc/
16. VnExpress — Lẩu mắm, "bản hòa tấu" của rau: https://vnexpress.net/lau-mam-ban-hoa-tau-cua-rau-2342858.html
17. VnExpress — Cháo buffet bình dân ở miền Tây: https://vnexpress.net/chao-buffet-binh-dan-o-mien-tay-4175916.html
