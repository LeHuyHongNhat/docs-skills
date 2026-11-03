# Writing Standards — chuẩn câu chữ cho tài liệu sản phẩm & kỹ thuật

File này dùng chung cho cả bộ skill. Đọc toàn bộ trước khi viết hoặc review tài liệu.

## Mục lục
1. Nguyên tắc cốt lõi
2. Ngôn ngữ & thuật ngữ (VI/EN)
3. Modal verb — mức độ bắt buộc
4. Viết một requirement đạt chuẩn
5. Danh sách từ/cụm từ mơ hồ và cách thay thế
6. Định dạng số, đơn vị, thời gian
7. Xử lý thông tin thiếu hoặc mâu thuẫn (+ 7b. Độ dài tương xứng)
8. Checklist tự kiểm trước khi bàn giao

---

## 1. Nguyên tắc cốt lõi

Người đọc tài liệu (dev, QA, stakeholder, auditor) không thể hỏi lại người viết. Vì vậy mỗi câu phải có **đúng một cách hiểu**, và mọi cam kết phải **kiểm chứng được**.

- **Một câu – một ý.** Câu chứa "và", "hoặc" nối hai hành vi độc lập thì tách thành hai câu/hai requirement.
- **Có chủ thể rõ ràng.** Mỗi hành động phải nói *ai* (actor/hệ thống/service nào) làm. Tránh bị động không chủ thể: "Dữ liệu được xử lý" → "Service `billing-worker` xử lý dữ liệu".
- **Định lượng thay vì định tính.** "Nhanh" không kiểm thử được; "p95 latency ≤ 300 ms ở 200 RPS" thì được.
- **Không bịa.** Chỉ viết điều có nguồn (input của người dùng, code, ảnh, tài liệu). Thiếu thông tin thì đánh dấu, không lấp chỗ trống bằng số "nghe hợp lý".
- **Nhất quán thuật ngữ.** Một khái niệm – một từ – suốt tài liệu. Định nghĩa trong Glossary ngay lần đầu xuất hiện nếu dễ hiểu sai.
- **Viết cho người quét nhanh.** Heading rõ, bảng cho dữ liệu có cấu trúc, ID cho mọi requirement để trace.

## 2. Ngôn ngữ & thuật ngữ (VI/EN)

- Viết theo ngôn ngữ người dùng dùng để yêu cầu. Tài liệu tiếng Việt **giữ nguyên thuật ngữ kỹ thuật tiếng Anh** khi đó là từ ngành dùng hằng ngày (API, endpoint, user story, acceptance criteria, backlog, sprint, latency, timeout, retry, cache, payload, token, KPI, funnel, churn, retention). Không dịch gượng ("giao diện lập trình ứng dụng" → dùng "API").
- Lần đầu dùng từ viết tắt ít phổ biến: viết đầy đủ kèm viết tắt — "Service Level Objective (SLO)".
- Không trộn hai từ cho cùng một khái niệm: chọn "người dùng" *hoặc* "khách hàng" *hoặc* "user" — nếu chúng là các actor khác nhau thì định nghĩa rõ sự khác nhau trong Glossary.
- Văn phong: trung tính, khẳng định, không cảm thán, không marketing ("tuyệt vời", "đột phá", "mạnh mẽ" → bỏ).
- Ngôi: dùng tên actor/hệ thống, không dùng "chúng ta", "bạn" trong đặc tả (README/hướng dẫn người dùng được phép dùng "bạn").

Bảng thuật ngữ chuẩn hay gặp:

| Nên dùng | Tránh |
|---|---|
| người dùng / user (chọn 1) | lúc "user", lúc "người sử dụng", lúc "khách" |
| hệ thống trả về lỗi `<mã lỗi>` | hệ thống báo lỗi |
| hiển thị thông báo "<nội dung chính xác>" | hiện thông báo phù hợp |
| trong vòng N giây kể từ <sự kiện> | ngay lập tức, kịp thời |
| tối đa / tối thiểu N | khoảng N, tầm N |
| bắt buộc / không bắt buộc (field) | có thể nhập |
| Acceptance Criteria (AC) | điều kiện chấp nhận (nếu team dùng tiếng Anh) |

## 3. Modal verb — mức độ bắt buộc

Dùng nhất quán theo RFC 2119. Khai báo quy ước này ở đầu tài liệu đặc tả.

| Mức | Tiếng Việt | English | Ý nghĩa |
|---|---|---|---|
| Bắt buộc | **phải** | MUST / SHALL | Không đạt = không nghiệm thu |
| Cấm | **không được** | MUST NOT | Vi phạm = lỗi |
| Khuyến nghị | **nên** | SHOULD | Có thể bỏ qua nếu có lý do ghi nhận |
| Tùy chọn | **được phép** | MAY | Không ảnh hưởng nghiệm thu |

"Có thể" trong tiếng Việt vừa mang nghĩa *khả năng* vừa mang nghĩa *cho phép* → **không dùng "có thể" trong câu requirement**. Dùng "được phép" (permission) hoặc viết lại thành năng lực của hệ thống ("Hệ thống phải cho phép người dùng xuất file CSV").

## 4. Viết một requirement đạt chuẩn

Một requirement tốt có các đặc tính (theo ISO/IEC/IEEE 29148): **cần thiết, đơn nghĩa, kiểm chứng được, đơn lẻ (singular), khả thi, truy vết được, nhất quán**.

Dùng mẫu EARS (Easy Approach to Requirements Syntax):

| Loại | Mẫu VI | Mẫu EN |
|---|---|---|
| Ubiquitous | Hệ thống `<X>` phải `<hành vi>`. | The `<system>` shall `<response>`. |
| Event-driven | Khi `<sự kiện>`, hệ thống `<X>` phải `<hành vi>`. | When `<trigger>`, the `<system>` shall `<response>`. |
| State-driven | Trong khi `<trạng thái>`, hệ thống phải `<hành vi>`. | While `<state>`, the `<system>` shall `<response>`. |
| Unwanted behaviour | Nếu `<điều kiện lỗi>`, thì hệ thống phải `<xử lý>`. | If `<condition>`, then the `<system>` shall `<response>`. |
| Optional feature | Ở nơi `<tính năng được bật>`, hệ thống phải `<hành vi>`. | Where `<feature>`, the `<system>` shall `<response>`. |

Ví dụ:
- ❌ "Hệ thống phải xử lý thanh toán nhanh và thông báo cho người dùng phù hợp."
- ✅ "FR-012. Khi người dùng nhấn **Thanh toán**, hệ thống phải trả kết quả giao dịch trong ≤ 5 giây (p95)."
- ✅ "FR-013. Nếu cổng thanh toán trả mã lỗi `51`, thì hệ thống phải hiển thị thông báo: *"Số dư không đủ. Vui lòng chọn phương thức khác."*"

**ID:** mỗi requirement có ID duy nhất, ổn định: `BR-` (business rule), `FR-` (functional), `NFR-` (non-functional), `US-` (user story), `AC-` (acceptance criterion), `UC-` (use case), `DR-` (data rule). Đánh số 3 chữ số; không tái sử dụng ID đã xóa.

## 5. Từ/cụm từ mơ hồ và cách thay thế

Khi gặp các từ dưới đây trong câu mang tính cam kết, thay bằng tiêu chí đo được hoặc liệt kê đầy đủ. Script `scripts/lint_doc.py` phát hiện tự động phần lớn danh sách này.

| Mơ hồ (VI) | Mơ hồ (EN) | Thay bằng |
|---|---|---|
| nhanh, nhanh chóng, ngay lập tức, kịp thời | fast, quickly, immediately, timely | ngưỡng thời gian + percentile + điều kiện tải |
| dễ dùng, thân thiện, trực quan | user-friendly, intuitive, easy | tiêu chí usability đo được (số bước, task success rate) hoặc bỏ |
| hợp lý, phù hợp, thích hợp | appropriate, reasonable, suitable | quy tắc cụ thể quyết định thế nào là "phù hợp" |
| một số, nhiều, vài, đa số | some, several, many, most | con số hoặc danh sách đầy đủ |
| khoảng, tầm, xấp xỉ | about, approximately, around | giá trị + dung sai (±) hoặc min/max |
| v.v., ..., và các loại khác | etc., and so on | liệt kê đầy đủ; nếu danh sách mở, nói rõ nguồn cấu hình |
| và/hoặc | and/or | tách thành hai câu hoặc nói rõ "ít nhất một trong" |
| nếu cần, khi cần thiết, tùy trường hợp | as needed, if necessary, as appropriate | điều kiện kích hoạt cụ thể |
| tối ưu, hiệu quả, mạnh mẽ, linh hoạt, ổn định | optimal, efficient, robust, flexible, seamless, stable | chỉ số đo được (throughput, uptime %, error rate) |
| hỗ trợ (đứng một mình) | support | hành vi cụ thể hệ thống thực hiện |
| TBD, TODO, ??? | TBD, TBC, TODO | mục Open Questions có owner + deadline |
| nó, điều này, cái đó (đầu câu, không rõ chỉ cái gì) | it, this, that | lặp lại danh từ |
| tương tự, như trên | similar, same as above | viết lại đầy đủ hoặc tham chiếu ID |

So sánh không mốc: "nhanh hơn", "tốt hơn", "ít lỗi hơn" → phải nêu baseline: "giảm thời gian xử lý từ 8 s (bản v1.3) xuống ≤ 4 s".

## 6. Định dạng số, đơn vị, thời gian

- Luôn kèm đơn vị: `30 giây`, `5 MB`, `500.000 VND`. Ghi rõ tiền tệ.
- Tiếng Việt: dấu chấm phân cách hàng nghìn, dấu phẩy thập phân (`1.250.000,50 VND`); tiếng Anh ngược lại. Trong bảng số liệu kỹ thuật/API được phép dùng định dạng máy (`1250000.5`) nhưng phải nhất quán.
- Thời gian: ISO 8601 (`2026-11-03`, `2026-11-03T10:00:00+07:00`), nêu múi giờ khi nghiệp vụ phụ thuộc thời điểm.
- Khoảng giá trị: ghi rõ biên có bao gồm hay không: "từ 50.000.000 VND trở lên" (≥) khác "trên 50.000.000 VND" (>). Đây là nguồn bug số 1 trong rule nghiệp vụ.

## 7. Xử lý thông tin thiếu hoặc mâu thuẫn

Không tự quyết thay stakeholder. Thay vào đó:

1. Viết phần chắc chắn như bình thường.
2. Chỗ thiếu: chèn [CẦN XÁC NHẬN: <câu hỏi cụ thể>] (EN: [TO CONFIRM: ...]) ngay tại vị trí, viết như văn bản thường — **không bọc trong backtick**, để bản PDF/DOCX tô nổi được marker.
3. Chỗ mâu thuẫn giữa các nguồn: nêu cả hai phiên bản và nguồn của từng bản, không chọn ngầm.
4. Gom tất cả vào mục **Open Questions** cuối tài liệu dạng bảng: `ID | Câu hỏi | Ảnh hưởng nếu không trả lời | Người cần trả lời`. Thêm cột `Hạn` chỉ khi input có mốc thời gian thật — một cột toàn [CẦN XÁC NHẬN] là độn.
5. Nếu buộc phải giả định để tiếp tục, ghi vào mục **Assumptions** với ID `AS-xxx` để có thể trace và gỡ sau.
6. Mỗi câu hỏi mở chỉ sống ở **một** nơi (bảng Open Questions); marker tại chỗ chỉ cần trỏ ID: [CẦN XÁC NHẬN: OQ-003]. Không lặp lại danh sách câu hỏi ở phụ lục hay tóm tắt.
7. **Nguyên nhân chưa kiểm chứng luôn là giả thuyết — ở mọi chỗ trong tài liệu**, kể cả tóm tắt, cột "lý do", câu kết. Không viết "nguyên nhân gốc là…", "không bên nào sai", "gần như chắc chắn" khi chưa có dữ liệu chứng minh; viết "giả thuyết H1: … — kiểm chứng bằng …".
8. Giá trị đề xuất (vd "gợi ý 5 phút") để ở cột ghi chú của Open Questions, **không** viết vào câu requirement hay acceptance criteria — nếu không, QA sẽ test theo con số chưa ai duyệt.

## 7b. Độ dài tương xứng với input

Tài liệu dài hơn không chuyên nghiệp hơn. Người đọc phải lội qua phần thừa để tìm phần cần.
- Độ chi tiết tỉ lệ với lượng thông tin thật trong input. Mốc tham khảo:

  | Input | Độ dài đích của tài liệu |
  |---|---|
  | Một đoạn / ≤ 15 dòng chat | ≤ 1.500–2.500 từ |
  | Meeting notes 1 trang | ≤ 3.000–4.000 từ |
  | Nhiều nguồn / hệ thống lớn | theo nhu cầu, nhưng mỗi mục phải có thông tin mới |

  Vượt mốc → cắt trước: AC trùng ý, câu hỏi mở chi tiết vụn (gộp lại), mục đề xuất dài, giải thích lặp.
- Chỉ thêm mục quy ước modal (RFC 2119), Glossary, ma trận truy vết khi tài liệu là SRS/đặc tả lớn hoặc có thuật ngữ thật sự dễ hiểu sai. Không định nghĩa từ hiển nhiên.
- Không lặp cùng một nội dung ở hai mục (vd rủi ro lặp trong "quyết định thiết kế").
- Mục không có nội dung thật thì bỏ hẳn (hoặc ghi một dòng "Không áp dụng — lý do") thay vì độn.

## 8. Checklist tự kiểm trước khi bàn giao

- [ ] Chạy `python scripts/lint_doc.py <file>` — không còn finding mức `high`; mỗi finding `medium` còn lại có lý do giữ.
- [ ] Mọi requirement có ID duy nhất và dùng đúng modal (phải/không được/nên/được phép).
- [ ] Mọi con số có đơn vị; mọi ngưỡng có biên rõ (≥/>).
- [ ] Không có câu bị động thiếu chủ thể ở phần đặc tả hành vi.
- [ ] Thuật ngữ nhất quán với Glossary.
- [ ] Mọi thông tin không có nguồn đã được đánh dấu [CẦN XÁC NHẬN] hoặc đưa vào Assumptions.
- [ ] Mục Open Questions phản ánh đúng mọi mâu thuẫn đã phát hiện trong input.
- [ ] Không có giá trị tự đề xuất nào nằm trong requirement/AC mà không đánh dấu.
- [ ] Không có mục độn hoặc nội dung lặp (xem 7b).
- [ ] Nếu bàn giao PDF/DOCX/XLSX: đã render bằng `scripts/render_doc.py --qa` và xem ảnh trang (xem `references/visual-style.md`).
