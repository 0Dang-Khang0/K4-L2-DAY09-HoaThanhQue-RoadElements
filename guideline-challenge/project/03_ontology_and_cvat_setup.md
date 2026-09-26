# Ontology + CVAT setup

Bảng ontology là **source of truth** cho schema CVAT: `03_cvat_labels.json` phải khớp từng dòng ở đây. Thay mọi
placeholder mới là xong (gate G2).

## Ontology table

| Name | Geometry | Type (class / attribute) | Allowed values | Default | Mutable? | Rationale |
|---|---|---|---|---|---|---|
| `speed_limit_sign` | rectangle | class | | | | Biển giới hạn tốc độ tối đa mặt trước |
| `speed_value` | | attribute | `__undefined__`, `10`, `20`, `30`, `40`, `50`, `60`, `70`, `80`, `90`, `100`, `110`, `120`, `130`, `unreadable` | `__undefined__` | false | Con số đọc được trên biển |
| `applies_to_ego` | | attribute | `__undefined__`, `yes`, `no`, `unknown` | `__undefined__` | false | Xác định biển có áp dụng cho ego hay không |
| `panel_type` | | attribute | `__undefined__`, `none`, `direction`, `time`, `distance`, `vehicle_type`, `multiple`, `unreadable` | `__undefined__` | false | Loại biển phụ ở dưới biển tốc độ |
| `needs_review` | | attribute | `false`, `true` | `false` | false | Yêu cầu review khi không chắc chắn |
| `no_speed_sign` | tag | class | | | | Không có biển giới hạn tốc độ nào trong ảnh |
| `image_escalate` | tag | class | | | | Không quyết định được ảnh có biển không |

## Class hay attribute

- **`speed_limit_sign`** là class (dùng để vẽ box quanh thực thể vật lý). 
- **`no_speed_sign`** và **`image_escalate`** là class (kiểu tag cho ảnh, không đi kèm box).
- **`speed_value`, `applies_to_ego`, `panel_type`, `needs_review`** là attribute vì chúng thuộc về cùng một đối tượng `speed_limit_sign` và mô tả thêm chi tiết cho box đó. 
- Default là `__undefined__` để buộc annotator phải chọn, tránh trường hợp quên đổi giá trị default dẫn tới bias.

## CVAT

- **Phiên bản CVAT** (`make cvat-status`): CVAT 2.4.6
- **Tên task calibration** (có version guideline, ví dụ `team07-calib-v1`): `HoaThanhQue-calib-v2`
- **Guide của task đã dán `02_guideline.md`?** Có
- **Nhóm dùng Track hay Shape, vì sao:** Dùng Shape. Vì bài này yêu cầu label độc lập từng ảnh tĩnh (image), không có tính liên tục thời gian (temporal).

## Setup test

Một thành viên **chưa tham gia setup** mở task và trả lời: label gì, dùng tool nào, gán attribute nào, khi nào
escalate. Ghi lại ai test và chỗ họ vấp:

- **Người test:** Phan Tấn Đạt
- **Label:** Vẽ `speed_limit_sign` nếu có biển, gán tag `no_speed_sign` nếu không có.
- **Tool:** Draw new rectangle (Shape).
- **Attribute:** Chọn `speed_value`, `applies_to_ego`, `panel_type`, check `needs_review`.
- **Khi nào escalate:** Gắn `image_escalate` khi ảnh quá tối/nhoè không xác định nổi có biển không; tích `needs_review=true` khi box có `unknown` hoặc `unreadable`.
- **Chỗ vấp:** Quên gắn thẻ `no_speed_sign` cho những ảnh không có biển và thỉnh thoảng quên tick `needs_review` khi để trạng thái `unknown`.
