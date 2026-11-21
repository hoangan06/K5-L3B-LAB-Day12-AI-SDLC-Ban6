# Ý tưởng sáng tạo (đề xuất của Trung)

> Ý tưởng gốc của Trung; AI tra nguồn và mở rộng. Chưa code. Mục "Sáng tạo của nhóm" trong README do Đức giữ:
> nhóm chọn ý nào thì Đức chép sang đó. Chỉ giữ thông tin văn hóa **có nguồn**; chỗ không chắc đã bỏ.

## 0. Ràng buộc (PRD-0, TICKET-02) và quyết định của Trung

- PRD-0 §1 và TICKET-02 §3: giữ luật lõi, số chuẩn và Test Contract. **Mọi phần thêm tắt ở headless.** Làm lõi đúng trước.
- **Phase 2 đã có quái lõi: Cá Sấu Năm Chèo** (M1, từ Ngày 3 thêm M2). Chạm làm mất 1 Máu, rơi nửa giỏ, bất tử 90 tick. Vì vậy phần sáng tạo **không làm lại Năm Chèo** và không đổi luật chạm, chỉ thêm thẻ truyền thuyết cho con lõi.
- Quyết định "quái gây ngạt, không trừ Máu" *(Trung chốt)* nay chỉ áp cho **quái sáng tạo** (Mãng Xà Vương), không đụng Cá Sấu lõi.
- **Thắp hương tốn thời gian, không tốn tiền.** Tiền là luật lõi; đổi tiền lấy phước dễ phản cảm với tín ngưỡng đang được thờ thật. *(Trung chốt)*
- Phần sáng tạo **không trái đề thì làm** *(Trung chốt)*. Không đổi những gì TICKET-02 ghi bằng số: lịch khách, thực đơn 6 món, kế hoạch D1–D5, bố trí và luật Cá Sấu, giá Shop.
- Ngẫu nhiên sáng tạo dùng luồng `Streams` riêng (ví dụ `creative_monster`), chỉ bật trong `chonoi.live`, không chạm luồng của luật lõi.
- PRD-0 §3 yêu cầu tôn trọng văn hóa địa phương: thần được thờ chỉ làm đền (hình ảnh trang nghiêm), không làm quái.
- Mở rộng **Rắn Hổ Mây (snake)** của TICKET-02 cũng là rắn. Nếu nhóm làm mở rộng này thì bỏ Mãng Xà Vương để khỏi trùng.

## 1. Quái buổi sáng

| Quái | Cơ chế | Gốc truyền thuyết |
|---|---|---|
| **Cá Sấu Năm Chèo** (lõi Phase 2) | Giữ nguyên luật TICKET-02. Sáng tạo chỉ thêm dấu **?** và thẻ truyền thuyết | Thủy quái sông Vàm Nao (An Giang), tương truyền là con sấu đỏ 5 chân. Vàm Nao nối sông Tiền với sông Hậu nên nước xoáy dễ làm chìm ghe; dân gian cho rằng dòng xiết là do ông thở mạnh. Ghe đi ngang thường thắp hương khấn vái [1][2][3] |
| **Mãng Xà Vương** (sáng tạo, chỉ live; tên do nhóm đặt) | Quấn người chơi: không bơi được, oxy vẫn giảm theo luật ngạt lõi, không trừ Máu trực tiếp | Lấy cảm hứng từ chuyện rắn khổng lồ ở Thất Sơn: người sóc Tà Đéc (xã An Hảo, Tịnh Biên) kể có cặp rắn bò từ núi Bà Đội Om sang núi Cấm [4][5] |

**Thoát khi bị Mãng Xà quấn: chuỗi mũi tên** (ý của Trung, chỉ live; không áp cho Cá Sấu lõi vì cú chạm lõi xử lý ngay trong một bước)

- Bị quấn: Út Sen đứng yên, oxy **vẫn giảm như thường**. Trên đầu nhân vật hiện chuỗi 6 mũi tên ↑↓←→.
- Bấm đúng thứ tự thì thoát, kèm 2 giây không bị quấn lại. Bấm sai thì làm lại từ đầu. Hết giờ chuỗi thì bị siết thêm một lượt, rồi chuỗi mới hiện ra.
- Luck của đền Bà Thủy bớt 1 phím.
- Kỹ thuật: chuỗi sinh từ luồng `creative_monster`. Đọc phím bằng **cạnh lên của hướng `move`**. Không thêm nút mới vào inputs, vì Test Contract báo mã 2 với nút lạ.
- Hình ảnh tự thiết kế theo chủ đề sông nước (mũi tên vẽ như mái chèo hoặc vảy cá), không sao chép giao diện game nào.

**Bảng "ngất vì…"** (ý của Trung): khi ngất, live hiện 2–3 câu truyền thuyết theo nguyên nhân, kèm nguồn. Headless vẫn phát `faint` đúng contract v1.1: `cause: "choke"` hoặc `cause: "monster"` (Cá Sấu).

## 2. Đền thờ (thắp hương: đứng ở đền vài giây, mất thời gian ca sáng → luck tăng)

| Đền | Tác dụng (chỉ live) | Gốc tín ngưỡng |
|---|---|---|
| **Bà Thủy Long** | Mãng Xà ít xuất hiện hơn, chuỗi thoát bớt 1 phím. Không đổi Cá Sấu lõi | Thủy Long Thánh Mẫu ("Bà Thủy"), nữ thần sông nước, thường thờ ở ngã ba sông, phù hộ dân chài [6][7] |
| **Cá Ông** | Khi ngất được roll xúc xắc, ra 6 thì hồi sinh, "được cá Ông đưa về" (ý của Trung). Tắt ở headless | Cá Ông là cá voi, ngư dân xem là thần Nam Hải cứu người gặp nạn trên biển; miền Tây Nam Bộ cúng giỗ vào ngày cá Ông lụy [8][9] |
| **Bà Chúa Xứ** (đề xuất thêm) | Chỉ hình ảnh và thẻ truyền thuyết. Bỏ ý "đông khách hơn" vì lịch khách đã cố định trong TICKET-02 | Nữ thần tài lộc ở núi Sam, Châu Đốc; lễ hội Vía Bà được UNESCO ghi danh năm 2024 [10][11] |
| **Neak Ta / Ông Tà** (đề xuất thêm) | Chỉ hình ảnh: vài khách mặc trang phục Khmer. Không đổi món khách gọi | Thần giữ phum sóc của người Khmer, gắn với cầu mưa, giữ ruộng; lễ Đom Lơng Neak Ta (Trà Vinh) là di sản phi vật thể quốc gia năm 2024 [12] |

## 3. Món và chuyện kể

TICKET-02 cố định 6 món lõi. Món ngoài danh sách **không cho khách gọi** (sẽ đổi thực đơn và kế hoạch ngày), chỉ làm thẻ chữ hoặc cảnh trang trí.

| Món | Chuyện kể / gốc | Trong game |
|---|---|---|
| **Cá lóc nướng trui** (lõi) | Món của thời di dân khẩn hoang, không có ở quê gốc miền Trung (theo nhà nghiên cứu Nguyễn Đình Tư, SGGP dẫn). Thời đó thiếu nồi niêu, bắt cá là nướng ngay [13] | Dấu **?** trên món |
| **Lẩu mắm miền Tây** (lõi `lau_mam`, từ Ngày 4) | Sơn Nam cho là gốc ở Châu Đốc, có nguồn khác cho là gốc Khmer (nguồn mâu thuẫn, ghi rõ trên thẻ). Nấu từ mắm cá linh, mắm cá sặc; cá linh theo nước lũ về [16] | Dấu **?** trên món |
| **Bún nước lèo** | Đặc sản Sóc Trăng – Trà Vinh, hòa vị ba dân tộc Kinh, Hoa, Khmer [14][15]. Gốc Sóc Trăng hay Trà Vinh còn tranh cãi [15] | Chỉ thẻ chữ, ghép với đền Neak Ta |
| **Cháo trắng lá dứa** | Món bình dân phổ biến khắp miền Tây, ăn kèm nước cốt dừa và đồ mặn [17] | Cảnh Má Tư nấu cháo ở DayIntro; không kể chuyện lịch sử vì không có nguồn |

Chưa có nguồn cho gỏi bông súng, canh chua cá lóc, cá kèo nướng, kèo nèo nên chưa làm thẻ. Đã bỏ vì không có nguồn: giai thoại "lộc trời" của lẩu mắm, lịch sử cháo lá dứa, ma da.

## 3b. Thẻ lore thêm (chỉ chữ, chỉ live, không gắn luật)

Subagent đã mở và đọc nguồn gốc của từng mục dưới đây. Mục nào nguồn yếu hoặc chỉ có một blog thì đã bỏ phần đó.

| Thẻ | Nội dung (diễn đạt lại) | Gắn ở đâu |
|---|---|---|
| **Cây bẹo** | Ghe chợ nổi cắm sào trước mũi, treo gì bán nấy; treo tàu lá/tấm lợp là muốn bán chính chiếc ghe [18][19][20] | Ghe trang trí ngoài bè |
| **Kiêng kỵ thương hồ** | Kiêng nói "úp, lật, rớt"; mong "người mở hàng có duyên" buổi sáng [20] | Khi Út Sen mở quán; không thưởng/phạt |
| **Tên Cái Răng** | Một giả thuyết (Vương Hồng Sển, ĐH Cần Thơ dẫn): từ "karan", lò cà ràng người Khmer chở ghe xuống bán [21] | Lò cà ràng trang trí ở bếp (vẫn một bếp) |
| **Cá linh** | Có nhiều chuyện kể về tên cá: điềm báo cho Nguyễn Ánh, hoặc cá "có tánh linh". Ghi rõ là truyện truyền miệng [22][23] | Mùa nước nổi, khi bắt cá linh |
| **Sông Cổ Chiên** | Truyền thuyết trống chiêng rớt xuống sông giữa bão; nhà sử học cho rằng tên có thể từ "Koh Chin" [24] | Đêm sương nghe tiếng chiêng xa; không phải quái |
| **Cửu Long** | Chín cửa sông ví như chín rồng; là cách giải thích của nhà nghiên cứu, không phải truyện dân gian [25] | Một dòng ở màn hình tải |
| **Ok Om Bok** | Lễ cúng trăng của người Khmer, rằm tháng 10 âm lịch, di sản phi vật thể quốc gia 2014; thả đèn nước, đua ghe ngo [26] | Đèn nước trôi ban đêm, thẻ viết tôn kính; không thưởng, không đua |
| **Bác Ba Phi** | Nghệ nhân kể chuyện có thật ở U Minh; truyện là chuyện tiếu lâm, "thằng Đậu" do nhà văn Anh Động nghĩ ra [27] | Thẻ hài cạnh cá lóc, ghi "truyện kể vui" |

**Cách hiện thẻ (ý của Trung):** mỗi vật phẩm, món, đền hay quái có truyền thuyết thì có một dấu **?** nhỏ phía trên. Bấm vào **?** để mở thẻ truyền thuyết (tên, chuyện kể ngắn, nhãn "truyền thuyết / giả thuyết / truyện kể vui", nguồn). Bấm ra ngoài hoặc Esc để đóng. Bảng "ngất vì…" khi ngất vẫn tự hiện như mục 1.
- Chỉ ở client live (`chonoi/web/`). Cú bấm chuột là việc của giao diện, không đi vào `inputs` của sim, nên headless và JSONL không đổi.
- Dữ liệu thẻ để riêng một file (ví dụ `chonoi/web/lore.json`: id vật → nội dung + nguồn), không trộn vào `game.contract.json`.
- Mở thẻ thì gửi cạnh `pause` (nút lõi của v1.1), đóng thẻ thì gửi `pause` lần nữa để `resumed`. Đồng hồ và timer đứng yên đúng TICKET-02 §4.2.

Đã bỏ: điên điển cứu đói (không nguồn gốc), mốc thời gian hủ tiếu Mỹ Tho (các nguồn mâu thuẫn), "bốn quy ước" cây bẹo (chỉ một blog), cá sấu đặt tên Cái Răng, bánh xèo, cơm tấm, mắm Châu Đốc, ma da.

## 4. Thứ tự làm đề xuất

1. **Gói 1 (nhỏ, chỉ giao diện):** dấu **?** + thẻ truyền thuyết cho Cá Sấu Năm Chèo, 6 món lõi có nguồn và các thẻ mục 3b; bảng "ngất vì…". Dùng `pause` lõi, không đổi luật nào.
2. **Gói 2:** đền Bà Thủy + Mãng Xà Vương + chuỗi mũi tên; đền cá Ông (xúc xắc hồi sinh). Cần cờ `creative` trong live và luồng RNG riêng.
3. **Gói 3:** Bà Chúa Xứ, Neak Ta, cảnh cháo của Má Tư. Làm khi lõi các phase sau đã ổn.

Mỗi gói cần có bằng chứng "lõi vẫn đúng": test headless chạy giống hệt khi bật/tắt cờ `creative` (PRD-0 §1, DoD).

## Nguồn

Nguồn 1–17: AI mới đọc phần trích trong kết quả tìm kiếm, chưa mở toàn văn từng bài. Nguồn 18–27: subagent đã mở và đọc trang. Trước khi đưa câu chữ vào game, cần mở link kiểm lại.

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
18. mia.vn — Tìm hiểu cây bẹo miền Tây: https://mia.vn/cam-nang-du-lich/tim-hieu-cay-beo-mien-tay-21138
19. Tạp chí Công Thương — Chợ nổi, nét duyên miền sông nước: https://tapchicongthuong.vn/cho-noi-net-duyen-mien-song-nuoc-62931.htm
20. Võ Văn Sơn, Tạp chí Khoa học Yersin (2016) — Chợ nổi Tây Nam Bộ: https://hcmussh.edu.vn/static/document/ChonoiTayNamBo.pdf
21. Tạp chí Khoa học ĐH Cần Thơ (2011): https://sss.ctu.edu.vn/images/upload/NCKH/dulich/2011_19_.pdf
22. Tiền Phong — Mùa bông điên điển, cá linh: https://tienphong.vn/Van-Hoa/564273/Mua-bong-dien-dien-ca-linh-tpp.html
23. VOH — Cá linh, món quà từ mùa nước nổi: https://voh.com.vn/am-thuc/ca-linh-mon-qua-tu-mua-nuoc-noi-449103.html
24. Tuổi Trẻ — Cổ Chiên, tên lạ của Trường Giang: https://tuoitre.vn/co-chien-ten-la-cua-truong-giang-20230905002512204.htm
25. VTC News — Vì sao gọi là sông Cửu Long: https://vtcnews.vn/vi-sao-goi-la-song-cuu-long-ar1031692.html
26. VietnamPlus — Lễ hội Ok Om Bok: https://www.vietnamplus.vn/le-hoi-ok-om-bok-khi-con-nguoi-hoa-minh-voi-thien-nhien-post1145360.vnp
27. Tuổi Trẻ — Bác Ba Phi, giai thoại và sự thật: https://tuoitre.vn/bac-ba-phi-giai-thoai-su-that-thang-dau-la-ai-642745.htm
