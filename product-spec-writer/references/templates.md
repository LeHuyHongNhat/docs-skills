# Templates đặc tả sản phẩm

Mục lục: [BRD](#brd) · [PRD](#prd) · [SRS](#srs) · [User story](#user-story) · [Use case](#use-case) · [Metric definition](#metric)

Quy ước chung cho mọi template:
- Header metadata ở đầu: tên tài liệu, phiên bản, ngày (ISO 8601), tác giả/owner, trạng thái (`Draft` / `In review` / `Approved`).
- Mục không áp dụng: giữ heading và ghi "Không áp dụng — <lý do>" thay vì xóa, để người review biết đã cân nhắc.
- Bảng thay cho đoạn văn khi dữ liệu có ≥ 3 thuộc tính lặp lại.
- Mục Open Questions và Assumptions luôn có ở cuối (trừ khi rỗng — khi đó ghi "Không có").

---

<a id="brd"></a>
## BRD — Business Requirements Document

```markdown
# BRD: <Tên dự án>
| Phiên bản | Ngày | Owner | Trạng thái |
|---|---|---|---|

## 1. Bối cảnh & vấn đề kinh doanh
<Hiện trạng, nỗi đau, bằng chứng định lượng nếu có (số liệu, nguồn).>

## 2. Mục tiêu kinh doanh
| ID | Mục tiêu | Chỉ số đo | Baseline | Target | Thời hạn |
|---|---|---|---|---|---|
| BO-001 | | | | | |

## 3. Phạm vi
### 3.1 Trong phạm vi
### 3.2 Ngoài phạm vi

## 4. Stakeholders
| Vai trò | Tên/Bộ phận | Quan tâm chính | Mức ảnh hưởng (Cao/TB/Thấp) |

## 5. Yêu cầu nghiệp vụ
| ID | Yêu cầu | Lý do / mục tiêu liên quan (BO-xxx) | Độ ưu tiên (MoSCoW) |
| BR-001 | | | Must |

## 6. Quy trình nghiệp vụ (As-is / To-be)
<Mô tả bước + diagram Mermaid nếu có.>

## 7. Ràng buộc (pháp lý, ngân sách, thời gian, công nghệ)
## 8. Rủi ro
| ID | Rủi ro | Xác suất | Ảnh hưởng | Giảm thiểu |
## 9. Assumptions
## 10. Open Questions
| ID | Câu hỏi | Ảnh hưởng nếu chưa trả lời | Người trả lời |
```

---

<a id="prd"></a>
## PRD — Product Requirements Document

```markdown
# PRD: <Tên tính năng>
| Phiên bản | Ngày | PM/PO | Trạng thái |

## 1. Tóm tắt
<3–5 câu: vấn đề, đối tượng, giải pháp, kết quả mong đợi.>

## 2. Vấn đề & bằng chứng
## 3. Mục tiêu & chỉ số thành công
| Metric | Định nghĩa (tham chiếu metric spec nếu có) | Baseline | Target | Cách đo |
### Non-goals

## 4. Đối tượng người dùng & persona
## 5. Phạm vi
### Trong phạm vi (release này)
### Ngoài phạm vi

## 6. Business rules
| ID | Quy tắc | Nguồn |

## 7. User stories & Acceptance Criteria
### US-001: <tên ngắn>
**Là** <vai trò>, **tôi muốn** <hành động>, **để** <giá trị>.
Độ ưu tiên: Must | Liên quan: BR-xxx
**Acceptance Criteria**
- AC-001.1 — Given … When … Then …
- AC-001.2 — (nhánh lỗi)
- AC-001.3 — (biên ngưỡng)

## 8. Functional requirements (bổ sung ngoài user story, nếu cần)
## 9. Non-functional requirements
| ID | Loại (performance/security/availability/usability/compliance) | Yêu cầu đo được | Điều kiện đo |

## 10. UX / luồng màn hình
<Liên kết design; mô tả trạng thái rỗng, loading, lỗi.>

## 11. Analytics / tracking
| Event | Trigger | Properties |

## 12. Dependencies & rủi ro
## 13. Release plan / rollout
## 14. Assumptions
## 15. Open Questions
## 16. Phê duyệt (chỉ khi tài liệu gửi duyệt)
| Vai trò | Họ tên | Quyết định | Ngày |
|---|---|---|---|
```

---

<a id="srs"></a>
## SRS / FRD — Software Requirements Specification

```markdown
# SRS: <Hệ thống/Module>
## 1. Giới thiệu
### 1.1 Mục đích  ### 1.2 Phạm vi  ### 1.3 Định nghĩa & từ viết tắt  ### 1.4 Tài liệu tham chiếu
### 1.5 Quy ước: phải = MUST, không được = MUST NOT, nên = SHOULD, được phép = MAY
## 2. Mô tả tổng quan
### 2.1 Bối cảnh hệ thống (context diagram)  ### 2.2 Actors  ### 2.3 Ràng buộc  ### 2.4 Giả định & phụ thuộc
## 3. Yêu cầu chức năng
### 3.x <Nhóm chức năng>
| ID | Yêu cầu (EARS) | Ưu tiên | Nguồn | Tiêu chí kiểm chứng |
## 4. Yêu cầu dữ liệu
| Thực thể | Trường | Kiểu | Bắt buộc | Ràng buộc/validation | Ví dụ |
## 5. Yêu cầu giao tiếp (UI/API/hệ thống ngoài)
## 6. Yêu cầu phi chức năng
## 7. Ma trận truy vết (Traceability)
| BR | FR | AC/Test |
## 8. Open Questions
```

---

<a id="user-story"></a>
## User story + Acceptance Criteria

```markdown
### US-<id>: <tên ngắn, động từ + đối tượng>
**Là** <vai trò cụ thể>, **tôi muốn** <mục đích hành động>, **để** <giá trị kinh doanh/người dùng>.

- Độ ưu tiên: <Must/Should/Could>  · Story point: <nếu có>  · Liên quan: <BR/FR/Design link>
- Điều kiện tiên quyết: <...>

**Acceptance Criteria**
| ID | Given | When | Then |
|---|---|---|---|
| AC-<id>.1 | | | |

**Ngoài phạm vi story này:** <...>
**Definition of Done bổ sung:** <tracking event, log, tài liệu...>
```

Kiểm INVEST: Independent, Negotiable, Valuable, Estimable, Small, Testable. Story lớn hơn 1 sprint → tách theo luồng (happy/lỗi), theo rule, hoặc theo loại dữ liệu.

Danh sách nhánh AC thường bị bỏ sót (xét từng mục xem có áp dụng không):
- Dữ liệu rỗng / không tồn tại / định dạng sai
- Đúng ngưỡng, dưới ngưỡng, trên ngưỡng (mọi số trong rule)
- Hết hạn / timeout / mất kết nối giữa chừng
- Thao tác lặp (double submit, retry), đồng thời (2 thiết bị)
- Quyền: actor không đủ quyền
- Trạng thái trước đó không hợp lệ (vd hủy đơn đã giao)

---

<a id="use-case"></a>
## Use case specification

```markdown
### UC-<id>: <Tên use case>
| Thuộc tính | Nội dung |
|---|---|
| Actor chính | |
| Actor phụ / hệ thống ngoài | |
| Mục tiêu | |
| Trigger | |
| Tiền điều kiện | |
| Hậu điều kiện (thành công) | |
| Hậu điều kiện (thất bại) | |

**Luồng chính**
1. <Actor> <hành động>.
2. Hệ thống <phản hồi>.

**Luồng thay thế**
- A1 (tại bước 2): <điều kiện> → <các bước> → quay lại bước <n> / kết thúc.

**Luồng ngoại lệ**
- E1 (tại bước 3): <lỗi> → <xử lý> → kết thúc với hậu điều kiện thất bại.

**Business rules áp dụng:** BR-xxx
```

Mỗi bước một hành động của một chủ thể. Luồng thay thế/ngoại lệ luôn ghi rõ phân nhánh ở bước nào và quay về đâu.

---

<a id="metric"></a>
## Metric / KPI definition (cho DA, PM)

Mỗi metric một bảng. Mục tiêu: hai analyst tính độc lập ra cùng một con số.

```markdown
### <Tên metric> (`metric_key`)
| Thuộc tính | Định nghĩa |
|---|---|
| Mô tả nghiệp vụ | Metric trả lời câu hỏi gì |
| Công thức | Tử số / mẫu số, viết tường minh |
| Đơn vị & định dạng | %, VND, số người; số chữ số thập phân |
| Grain | Theo ngày / tuần ISO / tháng dương lịch; theo user / account / device |
| Múi giờ | vd Asia/Ho_Chi_Minh |
| Nguồn dữ liệu | Bảng/event cụ thể, cột |
| Bộ lọc (include) | |
| Loại trừ (exclude) | Test account, nhân viên nội bộ, bot, giao dịch hoàn tiền... |
| Định nghĩa "active"/"chuyển đổi" | Event nào, điều kiện nào |
| Xử lý dữ liệu đến muộn | Cửa sổ tính lại (vd tính lại D-3) |
| Owner | |
| SQL/pseudo-code tham chiếu | |
| Ví dụ tính tay | Bộ dữ liệu nhỏ + kết quả |
| Cạm bẫy diễn giải | vd retention cohort nhỏ dao động mạnh |
```

Retention có ba biến thể hay bị gọi chung một tên — định nghĩa tách bạch, chốt một biến thể chuẩn, đặt tên riêng cho hai biến thể còn lại nếu vẫn cần dùng:

| Biến thể | User được tính "giữ chân ở DN" khi | Ghi chú |
|---|---|---|
| Classic / bounded (đúng ngày N) | active đúng ngày D0+N | thấp nhất, dao động theo thứ trong tuần |
| Window (trong cửa sổ D1..DN) | active ít nhất một ngày trong D0+1 … D0+N | cao hơn classic |
| Unbounded / rolling (từ ngày N trở đi) | active vào bất kỳ ngày nào ≥ D0+N (tính đến hôm nay) | cao nhất, thay đổi khi dữ liệu mới về |

Các điểm hay gây hiểu khác nhau, phải chốt rõ: ngày bắt đầu cohort (D0) tính theo sự kiện nào; "trong 7 ngày" là D7 đúng ngày thứ 7 hay bất kỳ ngày nào từ D1–D7 (rolling vs. bounded/unbounded retention); user ẩn danh và đã đăng nhập có gộp không; đếm distinct theo id nào.
