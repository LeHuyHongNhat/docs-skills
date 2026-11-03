"""Sinh thư mục evals/<case>/ cho từng skill theo schema của skill-creator / `claude plugin eval`."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path("/home/claude/doc-skills")
FX = Path("/home/claude/fixtures")

SETTINGS = """---
tags: [skill-creator, doc-skills]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

"""

CASES: dict[str, list[dict]] = {
    "product-spec-writer": [
        {
            "name": "prd-referral-docx",
            "prompt": "Đây là đoạn chat nhóm growth về tính năng giới thiệu bạn bè (notes_gioi_thieu_ban.md). Viết PRD và xuất file Word "
                      "prd_gioi_thieu_ban.docx để mình gửi sếp duyệt (giữ cả bản .md).",
            "files": [FX / "text/notes_gioi_thieu_ban.md"],
            "outcome": "PRD ngắn gọn tương xứng input, file Word trình bày chuyên nghiệp: heading dùng style Heading, bảng full ngang có header nổi bật, marker cần xác nhận được tô; các rule 50.000 VND, 10 lượt/tháng, 7 ngày, 30 ngày, 1 lần/thiết bị có ID; câu hỏi hủy đơn đầu tiên ở Open Questions.",
            "assertions": [
                "prd_gioi_thieu_ban.docx tồn tại và các tiêu đề dùng paragraph style Heading 1/Heading 2 (điều hướng được bằng Navigation Pane của Word)",
                "Bảng trong DOCX trải full chiều ngang trang, hàng header được tô nền hoặc in đậm",
                "Marker cần xác nhận trong DOCX được định dạng nổi bật (character style riêng, tô nền hoặc màu), không nằm trong font code",
                "Khi chuyển DOCX sang PDF và xem ảnh trang, không có bảng tràn lề hoặc chữ trong ô bị gãy giữa từ ngắn (như 'Không', mã ID)",
                "Các rule 50.000 VND cho cả hai bên, tối đa 10 lượt mời thành công/tháng, đặt đơn đầu tiên trong 7 ngày kể từ đăng ký, thưởng hạn 30 ngày chỉ trừ vào đơn, 1 lần nhận thưởng/thiết bị đều thành business rule có ID",
                "Câu hỏi hủy đơn đầu tiên có thu hồi thưởng không nằm trong Open Questions, không bị tự quyết",
                "Biên 7 ngày (tính theo giờ hay ngày lịch, có bao gồm đúng thời điểm 7×24h) được đánh dấu cần xác nhận hoặc có AC kiểm biên",
                "Độ dài tương xứng input 9 dòng chat: prd_gioi_thieu_ban.md không quá 2.500 từ",
            ],
        },
        {
            "name": "prd-loyalty-from-meeting-notes",
            "prompt": "Mình là PO. Đây là note họp sprint planning về tính năng đổi điểm lấy voucher (file meeting_notes_doi_diem.md). "
                      "Viết giúp mình bản PRD chuẩn để gửi team dev + QA review, lưu thành file prd_doi_diem.md.",
            "files": [FX / "text/meeting_notes_doi_diem.md"],
            "outcome": "PRD tiếng Việt đầy đủ mục tiêu/metric, scope + out of scope, business rules có ID, user story + AC Given/When/Then có kiểm tra biên, NFR đo được; mâu thuẫn hạn điểm 6 vs 12 tháng và câu hỏi hủy phòng dùng voucher nằm trong Open Questions, không bị tự quyết.",
            "assertions": [
                "prd_doi_diem.md có mục Out of scope (hoặc Ngoài phạm vi) nêu rõ đổi điểm ra tiền mặt và chuyển điểm cho người khác không thuộc đợt này",
                "Quy tắc quy đổi 100 điểm = 10.000 VND, tối thiểu 500 điểm/lần và bội số 100 được ghi thành business rule có ID (BR-xxx hoặc tương đương)",
                "Mâu thuẫn hạn điểm 12 tháng (PM) và 6 tháng (Marketing) được nêu trong mục Open Questions/câu hỏi mở với cả hai giá trị, và phần đặc tả không âm thầm chọn một giá trị như đã chốt",
                "Câu hỏi về việc hủy phòng đã thanh toán bằng voucher được đưa vào Open Questions",
                "Có ít nhất một acceptance criterion kiểm tra biên tối thiểu 500 điểm (ví dụ 499 điểm bị chặn, 500 điểm được đổi)",
                "Có acceptance criterion hoặc requirement chống trừ điểm hai lần khi người dùng bấm liên tục (idempotency/double submit)",
                "Yêu cầu hiệu năng dùng ngưỡng lấy từ input (≤ 3 giây) thay vì 'tầm 2-3s' hay 'nhanh', và không có percentile/tải tự chế nằm trong requirement hoặc AC mà không đánh dấu cần xác nhận",
                "Rule voucher độc quyền 1.000.000 VND cho hạng Gold trở lên, tối đa 1 lần/tháng được đặc tả, và điểm chưa rõ (vd tháng dương lịch hay 30 ngày cuốn chiếu, 'Gold trở lên' gồm hạng nào) được đánh dấu cần xác nhận hoặc đưa vào Open Questions",
                "Mọi giá trị tự suy ra (vd số điểm cần cho voucher 1.000.000 VND, 'mỗi tháng' là tháng dương lịch hay 30 ngày) đều được đánh dấu giả định/cần xác nhận, không nằm trong requirement/AC như đã chốt",
                "lint_doc.py báo 0 finding mức high trên prd_doi_diem.md",
            ],
        },
        {
            "name": "metric-definition-dau-retention",
            "prompt": "Team data của mình với team marketing đang tính DAU và Retention D7 ra số khác nhau (bối cảnh trong metric_context.md). "
                      "Viết tài liệu định nghĩa metric chuẩn cho DAU, Retention D1/D7/D30 để cả công ty dùng chung, lưu ra metric_definitions.md. "
                      "Giải thích luôn vì sao 2 team ra số khác nhau.",
            "files": [FX / "text/metric_context.md"],
            "outcome": "Tài liệu định nghĩa metric với công thức tường minh, grain, múi giờ, nguồn bảng, định nghĩa active, loại trừ internal, chiến lược distinct id, loại retention, SQL tham chiếu, ví dụ tính tay; giải thích nguyên nhân chênh lệch (push_received, UTC vs giờ VN, anonymous_id, internal) dưới dạng giả thuyết cần kiểm chứng.",
            "assertions": [
                "Định nghĩa DAU nêu rõ event nào tính là 'active' và loại trừ push_received (event tự động, không phản ánh user hoạt động)",
                "Tài liệu chốt rõ múi giờ dùng để cắt ngày (ví dụ Asia/Ho_Chi_Minh) và nêu event_ts đang lưu UTC",
                "Tài liệu nêu cách xử lý user chưa đăng nhập: đếm theo user_id, anonymous_id, hay hợp nhất — và đây được nêu là nguồn chênh lệch tiềm năng",
                "Định nghĩa loại trừ tài khoản nội bộ/test qua users.is_internal",
                "Tài liệu định nghĩa riêng từng biến thể retention — đúng ngày N, bất kỳ ngày nào trong cửa sổ D1..DN, và từ ngày N trở đi (unbounded) — chốt một biến thể chuẩn cho D1/D7/D30, kèm định nghĩa cohort D0",
                "Có SQL hoặc pseudo-code tham chiếu dùng đúng tên bảng analytics.events và analytics.users",
                "Có ví dụ tính tay với số liệu nhỏ minh họa công thức, và số liệu trong ví dụ tính đúng",
                "Có test case/edge case cho ranh giới ngày theo giờ Việt Nam (vd event lúc 23:59:59 và 00:00:00 +07, tương ứng 16:59:59 / 17:00:00 UTC)",
                "Trong TOÀN BỘ tài liệu, nguyên nhân chênh lệch 48k vs 61k và 18% vs 27% chỉ được trình bày như giả thuyết cần kiểm chứng; không có câu khẳng định như sự thật điều không thể biết khi chưa có query của hai team (vd 'không bên nào tính sai', 'nguyên nhân gốc là...')",
            ],
        },
    ],
    "codebase-doc-writer": [
        {
            "name": "readme-order-service",
            "prompt": "Repo order-service trong thư mục order-service/ chưa có README. Viết README tiếng Việt cho team dev (lưu thành order-service/README.md), "
                      "để người mới clone về chạy được ngay.",
            "files": [FX / "order-service"],
            "outcome": "README đúng với code: 5 endpoint, 6 env var (kể cả SMTP_HOST chỉ đọc ở worker và không có trong .env.example) với default đúng, lệnh chạy theo Makefile/compose, Python 3.11, có worker + Redis + Postgres; không bịa endpoint/lệnh.",
            "assertions": [
                "README liệt kê đủ 5 endpoint với method đúng: GET /health, POST /api/v1/orders, GET /api/v1/orders, GET /api/v1/orders/{order_id}, POST /api/v1/orders/{order_id}/cancel",
                "README không mô tả endpoint nào không có trong code (ví dụ DELETE, PUT, /login, /auth)",
                "Bảng cấu hình có đủ 6 biến DATABASE_URL, REDIS_URL, JWT_SECRET, ORDER_MAX_ITEMS, LOG_LEVEL, SMTP_HOST",
                "Default ghi đúng: REDIS_URL redis://localhost:6379/0, ORDER_MAX_ITEMS 50, LOG_LEVEL INFO; DATABASE_URL, JWT_SECRET, SMTP_HOST được ghi là bắt buộc/không có default",
                "README nói rõ SMTP_HOST là bắt buộc cho worker và KHÔNG có trong .env.example",
                "README không hướng dẫn đặt SMTP_HOST hoặc LOG_LEVEL vào file .env (Settings của pydantic-settings từ chối biến lạ trong .env → app lỗi khi khởi động)",
                "README nêu `make install` thất bại (setuptools flat-layout vì có hai package app và worker) và đưa cách cài/chạy thay thế đã kiểm chứng",
                "Hướng dẫn chạy dùng lệnh có thật trong repo (make install/run/worker/test, docker compose, hoặc uvicorn app.main:app) và nêu cần chạy worker riêng",
                "Yêu cầu Python 3.11 (từ Dockerfile/pyproject) được nêu đúng",
                "README nêu ít nhất một lỗi phát hiện từ logic code (không chỉ chép TODO/FIXME): ghi DB và push Redis không atomic, race giữa cancel và worker confirm, worker mất message khi crash (BRPOP), hoặc lỗi kết nối SMTP (OSError) không được retry",
            ],
        },
        {
            "name": "architecture-doc-order-service",
            "prompt": "Viết tài liệu kiến trúc (architecture overview) cho service trong order-service/ để onboard 2 dev mới tuần sau. "
                      "Lưu ra file architecture.md. Có diagram thì tốt.",
            "files": [FX / "order-service"],
            "outcome": "Tài liệu kiến trúc mô tả đúng API (FastAPI) → Postgres + Redis queue orders.created → worker xác nhận đơn + gửi email SMTP có retry 3 lần; có Mermaid hợp lệ; trích file path; mục rủi ro dựa trên bằng chứng code.",
            "assertions": [
                "Tài liệu mô tả đúng luồng tạo đơn: API ghi đơn status pending vào Postgres rồi LPUSH vào Redis queue tên orders.created",
                "Tài liệu mô tả worker BRPOP queue orders.created, cập nhật status pending→confirmed và gửi email qua SMTP",
                "Tài liệu nêu cơ chế retry gửi email tối đa 3 lần với backoff (2^attempt giây) và hệ quả khi thất bại (chỉ log, email mất)",
                "Tài liệu có diagram Mermaid và MỌI diagram Mermaid trong tài liệu đều render được bằng mmdc không lỗi",
                "Trích dẫn file:line chính xác cho ít nhất hai fact cụ thể, ví dụ TODO idempotency tại app/services/orders.py:16 và FIXME email tại worker/main.py:23",
                "Mục rủi ro/nợ kỹ thuật nêu ít nhất 2 vấn đề có bằng chứng trong code (ví dụ thiếu idempotency key, email placeholder FIXME, worker tạo engine mới mỗi message, không có dead-letter queue, trạng thái đơn bị confirm dù gửi mail thất bại)",
                "Tài liệu không khẳng định thông tin không có trong repo mà không đánh dấu cần xác nhận — gồm cả chi tiết nhỏ như gọi kết nối client là HTTPS/TLS trong khi repo chỉ chạy HTTP ở port 8000",
            ],
        },
    ],
    "diagram-to-doc": [
        {
            "name": "erd-export-xlsx-pdf",
            "prompt": "Từ ERD này (erd_sales.png) làm data dictionary cho module bán hàng. Team DA muốn file Excel để lọc theo bảng, "
                      "còn sếp muốn bản PDF đọc trên điện thoại. Lưu ra data_dictionary.md, data_dictionary.xlsx và data_dictionary.pdf.",
            "files": [FX / "diagrams/erd_sales.png"],
            "outcome": "Ba file cùng nội dung; XLSX có sheet riêng cho từng bảng (header cố định, lọc được); PDF trình bày gọn gàng, chữ có dấu đúng, diagram là hình, bảng không tràn lề, marker cần xác nhận nổi bật.",
            "assertions": [
                "data_dictionary.xlsx cho phép DA lọc theo bảng — hoặc mỗi bảng trong 5 bảng một sheet, hoặc một sheet phẳng có cột tên bảng và bộ lọc (autofilter) — với header in đậm và được cố định (freeze)",
                "data_dictionary.pdf tồn tại, font được nhúng và chữ tiếng Việt có dấu hiển thị đúng (pdftotext đọc ra được các từ có dấu như 'Khóa', 'bảng')",
                "PDF đọc thoải mái trên điện thoại như yêu cầu (khổ trang/cỡ chữ/bố cục bảng phù hợp màn hình hẹp, không phải bảng A4 nhiều cột thu nhỏ khó đọc)",
                "Diagram trong PDF là hình đã render — văn bản PDF không chứa mã nguồn Mermaid như 'erDiagram' hay '||--o{'",
                "Trên ảnh các trang PDF, không có bảng nào tràn khỏi lề phải hoặc bị cắt chữ, và cột ID/tên cột không gãy giữa từ",
                "Marker cần xác nhận hiển thị nổi bật trong PDF (được tô màu/khung riêng), không phải chữ trong khối code",
                "Nội dung đủ 5 bảng × 25 cột với kiểu dữ liệu, PK/FK đúng như ảnh, và cảnh báo payments.amount dùng FLOAT",
            ],
        },
        {
            "name": "flowchart-purchase-approval",
            "prompt": "Đây là sơ đồ quy trình đề nghị mua hàng của phòng mua sắm (purchase_approval.png). "
                      "Viết giúp mình tài liệu đặc tả quy trình chuẩn để gửi IT làm module phê duyệt, lưu ra dac_ta_quy_trinh_mua_hang.md.",
            "files": [FX / "diagrams/purchase_approval.png"],
            "outcome": "Đặc tả phủ đủ 5 actor, 4 decision với tất cả nhánh (TP có 3 nhánh), ngưỡng 50.000.000 VND, 3 trạng thái kết thúc; phát hiện khoảng trống = 50tr và vòng lặp bổ sung không giới hạn; có Mermaid.",
            "assertions": [
                "Đặc tả nêu đủ 5 actor: Nhân viên, Hệ thống, Trưởng phòng, Giám đốc, Kế toán và gán đúng actor cho các bước chính (vd Kế toán tạo PO, Hệ thống kiểm tra ngân sách)",
                "Quyết định của Trưởng phòng có đủ 3 nhánh: Duyệt, Từ chối, Yêu cầu bổ sung (→ Nhân viên bổ sung chứng từ → quay lại Trưởng phòng)",
                "Nhánh 'Không còn ngân sách' dẫn tới thông báo vượt ngân sách và kết thúc Hủy được mô tả",
                "Ngưỡng 50 triệu được chuẩn hóa thành 50.000.000 VND: > 50tr cần Giám đốc duyệt, < 50tr chuyển thẳng Kế toán tạo PO",
                "Tài liệu chỉ ra khoảng trống: đề nghị có giá trị đúng bằng 50.000.000 VND không thuộc nhánh nào trong diagram",
                "Tài liệu chỉ ra vòng lặp Yêu cầu bổ sung không có giới hạn số lần hoặc thời hạn (hoặc nêu đây là câu hỏi mở)",
                "Có đủ các trạng thái kết thúc: Hoàn tất (sau khi gửi PO cho nhà cung cấp), Hủy (vượt ngân sách), Kết thúc từ chối",
                "Mọi dòng trong bảng luồng/bước/transition truy được về một node hoặc cạnh trong ảnh; hành vi không có trong ảnh (thông báo thêm, retry, field dữ liệu, rule mới) chỉ xuất hiện trong mục đề xuất riêng",
                "Nhãn tại chỗ hai đường cong giao nhau được gán đúng: 'Duyệt' của Trưởng phòng dẫn tới 'Giá trị đề nghị?', 'Từ chối' của Giám đốc dẫn tới 'Thông báo từ chối cho NV'",
                "Có diagram Mermaid trong tài liệu và render được bằng mmdc",
            ],
        },
        {
            "name": "erd-to-data-dictionary",
            "prompt": "Từ ERD này (erd_sales.png) viết data dictionary cho module bán hàng, để DA và dev backend dùng chung. Lưu ra data_dictionary.md.",
            "files": [FX / "diagrams/erd_sales.png"],
            "outcome": "Data dictionary đủ 5 bảng × 25 cột với kiểu, PK/FK/UQ, nullable đúng; 4 quan hệ với cardinality đúng; phát hiện payments.amount dùng FLOAT cho tiền.",
            "assertions": [
                "Có đủ 5 bảng customers, orders, order_items, products, payments và mỗi bảng có đủ 5 cột như trong ảnh (tổng 25 cột, tên chính xác)",
                "Kiểu dữ liệu được chép đúng cho các cột tiền: orders.total_amount DECIMAL(12,2), order_items.unit_price DECIMAL(12,2), products.price DECIMAL(12,2), payments.amount FLOAT",
                "4 khóa ngoại đúng: orders.customer_id→customers.id, order_items.order_id→orders.id, order_items.product_id→products.id, payments.order_id→orders.id",
                "Ràng buộc unique của customers.email và products.sku được ghi nhận; phone và paid_at được ghi là nullable",
                "Cardinality: một customer có 0..N orders; một order có 1..N order_items (ít nhất một); một order có 0..N payments; một product xuất hiện trong 0..N order_items",
                "Tài liệu cảnh báo payments.amount dùng FLOAT là không phù hợp để lưu tiền (sai số làm tròn) và đề xuất DECIMAL",
                "Không có giá trị enum cụ thể nào cho orders.status hoặc payments.method (vd PENDING, PAID, COD) xuất hiện trong bảng đặc tả cột, kể cả cột ví dụ; danh sách giá trị được đánh dấu cần xác nhận",
                "Diagram Mermaid trong tài liệu (nếu có) giữ đúng tham số kiểu như DECIMAL(12,2), VARCHAR(255) hoặc nói rõ đã lược bỏ",
            ],
        },
    ],
    "doc-clarity-review": [
        {
            "name": "review-otp-srs-draft",
            "prompt": "Review giúp mình bản SRS OTP này (srs_otp_draft.md) trước khi gửi dev, chỉ ra chỗ nào mơ hồ/sai và đề xuất sửa. "
                      "Lưu báo cáo review vào review_srs_otp.md và bản đã sửa vào srs_otp_v0.4.md.",
            "files": [FX / "text/srs_otp_draft.md"],
            "outcome": "Báo cáo bắt được phần lớn 13 vấn đề cài sẵn (đặc biệt mâu thuẫn 5 vs 3 phút là Critical), không đánh lỗi nặng FR-001/FR-006 vốn đã tốt, bản sửa không tự bịa số liệu.",
            "assertions": [
                "Báo cáo phát hiện mâu thuẫn hiệu lực OTP 5 phút (mục 2) với 3 phút (AC-001/AC-002) và xếp mức cao nhất (Critical hoặc tương đương)",
                "Báo cáo phát hiện ID FR-004 bị dùng hai lần",
                "Báo cáo phát hiện quy tắc khóa 'nhập sai quá nhiều lần' thiếu số lần và thời gian khóa",
                "Báo cáo phát hiện FR-002 'nhanh chóng' không kiểm thử được",
                "Báo cáo phát hiện danh sách mở 'SMS, Email, Zalo, v.v.' ở FR-003",
                "Báo cáo phát hiện tham chiếu mơ hồ 'nó' và 'thông báo lỗi phù hợp' ở FR-005",
                "Báo cáo phát hiện khẳng định không nguồn 'giảm 40% số tài khoản bị chiếm đoạt'",
                "Báo cáo phát hiện thuật ngữ không nhất quán khách hàng / người dùng / user",
                "Báo cáo nêu thiếu xử lý lỗi khi gửi OTP thất bại (gateway SMS lỗi/không gửi được) hoặc thiếu giới hạn gửi lại OTP",
                "Không có finding Critical/Major nào nhắm vào chính câu chữ của FR-001 hoặc FR-006 (nhắc chúng như ngữ cảnh của một mâu thuẫn ở chỗ khác thì được chấp nhận)",
                "Trong srs_otp_v0.4.md, hiệu lực OTP, số lần nhập sai, thời gian khóa và rate limit không mang giá trị do reviewer tự chọn ở requirement hay AC (dùng ký hiệu + cần xác nhận); giá trị gợi ý, nếu có, chỉ nằm ở ghi chú/Open Questions",
                "FR-004 'Người dùng có thể yêu cầu gửi lại OTP' được viết lại với modal chuẩn (phải/được phép) trong bản sửa",
                "lint_doc.py báo 0 finding mức high trên srs_otp_v0.4.md",
            ],
        },
        {
            "name": "rewrite-export-feature-brief",
            "prompt": "PO bên mình viết mô tả tính năng thế này (feature_brief_export.md), đọc thấy chưa ổn. Viết lại giúp cho chặt chẽ, chuyên nghiệp để đưa vào backlog, lưu ra export_feature_spec.md.",
            "files": [FX / "text/feature_brief_export.md"],
            "outcome": "Bản viết lại giữ đủ mọi fact (Excel, ngưỡng ~10.000 dòng chạy ngầm + email link, phân quyền admin/manager/staff theo chi nhánh, lưu 7 ngày), dùng ID + modal chuẩn, không tự bịa ngưỡng thời gian/danh sách cột, đánh dấu cần xác nhận cho biên 10k và nội dung file.",
            "assertions": [
                "Bản viết lại giữ định dạng file Excel (.xlsx hoặc Excel) cho báo cáo doanh thu",
                "Ngưỡng chuyển sang chạy ngầm khoảng 10.000 dòng được giữ, và biên (đúng 10.000 dòng thuộc nhánh nào / 'tầm' là ước lượng) được đánh dấu cần xác nhận",
                "Luồng chạy ngầm gửi email chứa link tải file được đặc tả",
                "Phân quyền được viết rõ: Admin và Manager export được tất cả chi nhánh, Staff chỉ export được chi nhánh của mình",
                "Thời gian lưu file 7 ngày rồi xóa được giữ, có nêu mốc tính (từ lúc tạo file) hoặc đánh dấu cần xác nhận",
                "Không tự bịa ngưỡng thời gian cụ thể cho 'liền'/'nhanh'/'ổn định' hay danh sách cột của file mà không đánh dấu cần xác nhận",
                "Requirement có ID và dùng modal chuẩn (phải/không được/được phép), không còn văn nói như 'đc', 'nha', 'liền'",
                "Chỉ ra sự lệch giữa 'xem được hết' (Admin/Manager) và 'export được' (Staff) trong brief như một điểm cần PO xác nhận",
                "Không thêm phạm vi chưa ai yêu cầu (mã lỗi HTTP, audit log, retry, NFR bổ sung) như yêu cầu đã chốt; nếu có thì nằm ở mục đề xuất/câu hỏi",
                "Độ dài tương xứng một đoạn brief: export_feature_spec.md không quá 2.000 từ",
                "lint_doc.py báo 0 finding mức high trên export_feature_spec.md",
            ],
        },
    ],
}


def write_case(skill: str, c: dict) -> None:
    d = ROOT / skill / "evals" / c["name"]
    if d.exists():
        shutil.rmtree(d)
    (d / "graders").mkdir(parents=True)
    fnames = [Path(f).name for f in c["files"]]
    prompt = c["prompt"] + ("\n\nInput files: " + ", ".join(fnames) if fnames else "")
    (d / "prompt.md").write_text(SETTINGS + prompt + "\n", encoding="utf-8")
    yaml = (f'schema_version: "1.1"\nname: {c["name"]}\nexpected_outcome: |\n  {c["outcome"]}\n')
    if fnames:
        yaml += "context:\n  scaffold_script: place-files.sh\n"
        (d / "files").mkdir()
        for f in c["files"]:
            f = Path(f)
            dst = d / "files" / f.name
            shutil.copytree(f, dst) if f.is_dir() else shutil.copy(f, dst)
        sh = d / "place-files.sh"
        sh.write_text('#!/usr/bin/env bash\nset -eu\ncp -R "$(dirname "$0")/files/." .\n')
        sh.chmod(0o755)
    (d / "case.yaml").write_text(yaml, encoding="utf-8")
    for i, a in enumerate(c["assertions"], 1):
        (d / "graders" / f"{i:02d}-assert.md").write_text(
            f"---\ntype: llm\nfocus: trace\nweight: 1\n---\n\n{a}\n", encoding="utf-8")


if __name__ == "__main__":
    for skill, cases in CASES.items():
        for c in cases:
            write_case(skill, c)
            print(skill, c["name"], len(c["assertions"]), "assertions")
