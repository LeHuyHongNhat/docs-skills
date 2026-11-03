# Checklist trích xuất & cấu trúc output theo loại diagram

Mục lục: [Flowchart/BPMN/Swimlane](#flow) · [State machine](#state) · [Sequence](#sequence) · [ERD](#erd) · [Use case diagram](#usecase) · [Architecture](#arch) · [Wireframe/Mockup](#wireframe)

---

<a id="flow"></a>
## Flowchart / BPMN / Swimlane / Activity

**Trích xuất — đếm và ghi đủ:**
- Start event(s), end event(s) — có thể có nhiều end (thành công, hủy, từ chối).
- Mọi task/activity: nhãn nguyên văn, lane (actor).
- Mọi gateway/decision: câu hỏi + **tất cả** nhánh ra kèm nhãn. BPMN: phân biệt exclusive (X), parallel (+), inclusive (O) — parallel nghĩa là các nhánh chạy đồng thời, không phải "chọn một".
- Message flow giữa các pool (nét đứt), data object, data store, timer event (đồng hồ), error event.
- Vòng lặp (cạnh quay ngược): điều kiện thoát.
- Ghi chú/annotation bên cạnh.

**Bẫy hay gặp:**
- Mũi tên chồng nhau hoặc đi vòng — lần theo từng mũi tên, không suy từ vị trí node.
- Nhãn nhánh đặt gần cạnh khác → xác định nhãn thuộc cạnh nào bằng vị trí đầu mũi tên.
- Đơn vị viết tắt: "tr" = triệu, "k" = nghìn, "ngày LV" = ngày làm việc. Chuẩn hóa nhưng giữ nguyên văn trong inventory.
- Hai nhánh "> X" và "< X" bỏ sót trường hợp "= X". "≥" và ">" khác nhau.

**Output:** cấu trúc mặc định trong SKILL.md. Bảng luồng chính:

| Bước | Actor | Hành động | Điều kiện / Rule | Bước tiếp theo |
|---|---|---|---|---|
| S1 | Nhân viên | Tạo yêu cầu mua hàng trên hệ thống | — | S2 |
| S2 | Hệ thống | Kiểm tra tổng giá trị yêu cầu | BR-001 | S3 nếu > 50.000.000 VND; S4 nếu ngược lại |

---

<a id="state"></a>
## State machine

**Trích xuất:** danh sách state (initial, final); mọi transition `from → to` với event/trigger, guard `[điều kiện]`, action `/ hành động`.

**Output:**
- Bảng state: tên, mô tả, có phải final không.
- **Bảng transition**: `Từ trạng thái | Sự kiện | Guard | Hành động | Đến trạng thái`.
- **Ma trận state × event** khi có ≥ 4 state: ô trống = event không hợp lệ ở state đó → nêu rõ hệ thống xử lý thế nào (bỏ qua hay báo lỗi) hoặc [CẦN XÁC NHẬN]. Đây là chỗ hay sinh bug nhất.

---

<a id="sequence"></a>
## Sequence diagram

**Trích xuất:** participants theo thứ tự trái → phải; message theo thứ tự trên → dưới; kiểu (sync mũi tên đặc, async mũi tên mở, reply nét đứt); fragment `alt/opt/loop/par` + điều kiện; activation, self-call; ghi chú.

**Output:**
- Bảng participant: tên, loại (actor/service/DB/hệ thống ngoài), trách nhiệm.
- Bảng bước: `# | Từ | Đến | Message (method + path/topic) | Đồng bộ? | Dữ liệu chính | Ghi chú`.
- Mỗi fragment `alt/opt` → một luồng thay thế có tên; `loop` → điều kiện lặp và dừng.
- Mục "Xử lý lỗi": message nào có thể lỗi/timeout mà diagram không mô tả → câu hỏi mở.

---

<a id="erd"></a>
## ERD

**Trích xuất:** mọi entity/bảng; mọi cột với kiểu, PK, FK (trỏ tới đâu), NOT NULL/nullable, unique, default nếu ảnh có; relationship + cardinality ở **cả hai đầu** (crow's foot: vạch = 1, vòng tròn = 0, chân gà = nhiều); bảng trung gian của quan hệ N:M.

Đọc crow's foot: ký hiệu **gần entity nào** mô tả số lượng của **entity đó** trong quan hệ. `customers ||——o{ orders`: một order thuộc đúng 1 customer; một customer có 0..N order.

**Output — Data dictionary:**
```markdown
## Bảng `orders` — <mô tả nghiệp vụ một câu>
| Cột | Kiểu | Null | Khóa | Tham chiếu | Mô tả nghiệp vụ |
|---|---|---|---|---|---|
| id | BIGINT | Không | PK | — | Định danh đơn hàng |
| customer_id | BIGINT | Không | FK | customers.id | Khách đặt đơn |
```
Khi người dùng cần Excel để lọc (DA): thêm phụ lục **một bảng phẳng mọi cột** `Bảng | Cột | Kiểu | Null | Khóa | Mô tả` — sau khi render, sheet này lọc được theo bảng bằng autofilter, tiện hơn nhảy giữa nhiều sheet.

Hành vi khi xóa/cập nhật bản ghi cha (ON DELETE/UPDATE), CHECK, default không thể hiện trên ảnh → **không** viết thành ràng buộc trong mục "Ràng buộc toàn vẹn"; đưa vào câu hỏi mở hoặc mục đề xuất.

Sau các bảng: mục **Quan hệ** (`A 1 — 0..N B: <diễn giải bằng lời>`), mục **Ràng buộc toàn vẹn** suy ra trực tiếp từ ảnh (vd xóa customer khi còn order?), mục **Vấn đề phát hiện** (FK không có relationship, bảng không PK, kiểu dữ liệu bất thường như tiền dùng FLOAT).
Mô tả nghiệp vụ của cột không có trong ảnh → viết theo tên cột nếu tên tự giải thích; nếu không → [CẦN XÁC NHẬN].

---

<a id="usecase"></a>
## Use case diagram

**Trích xuất:** actor (người/hệ thống), system boundary, use case, association actor–use case, `<<include>>`, `<<extend>>` (+ extension point), generalization.

**Output:** bảng actor; danh sách use case với ID `UC-xxx`; với mỗi use case dùng template use case spec (xem product-spec-writer nếu có, hoặc: actor, mục tiêu, tiền/hậu điều kiện, luồng chính/thay thế/ngoại lệ). Diagram chỉ cho biết *có* use case, không cho biết luồng — luồng chi tiết không có trong ảnh thì để khung + [CẦN XÁC NHẬN], không bịa.

---

<a id="arch"></a>
## Architecture / deployment diagram

**Trích xuất:** thành phần (service, DB, queue, cache, CDN, bên thứ ba), ranh giới (VPC, cluster, zone), kết nối + giao thức + chiều, công nghệ ghi trên hình.

**Output:** bảng thành phần (tên, loại, công nghệ, trách nhiệm); bảng kết nối (`từ → đến | giao thức | đồng bộ? | dữ liệu`); mục điểm lỗi đơn (SPOF) và phụ thuộc bên ngoài *quan sát được trên hình*; câu hỏi mở về những gì hình không thể hiện (scaling, HA, backup).

---

<a id="wireframe"></a>
## Wireframe / Mockup màn hình

**Trích xuất — đi từ trên xuống, trái sang phải:** tên màn hình; từng vùng (header, form, list, footer); từng element: loại (text field, dropdown, checkbox, button, link, table, label), nhãn nguyên văn, placeholder, giá trị mẫu, trạng thái (disabled, selected), dấu `*` bắt buộc; điều hướng (nút dẫn tới đâu nếu có mũi tên/ghi chú).

**Output — Screen specification:**
```markdown
## Màn hình SCR-01: <tên>
Mục đích · Actor · Điều kiện truy cập
| ID | Element | Loại | Nhãn/Placeholder | Bắt buộc | Validation | Hành vi |
|---|---|---|---|---|---|---|
| E01 | Email | Text field | "Nhập email" | Có | [CẦN XÁC NHẬN: định dạng] | — |
| E05 | Đăng nhập | Button | "Đăng nhập" | — | Disabled khi E01 hoặc E02 rỗng [CẦN XÁC NHẬN] | Gọi API đăng nhập → SCR-02 |
```
Sau bảng: trạng thái màn hình (rỗng, loading, lỗi, thành công) — ảnh tĩnh thường chỉ có một trạng thái, các trạng thái còn lại liệt kê vào câu hỏi mở; thông báo lỗi chỉ ghi nguyên văn nếu có trong ảnh.
