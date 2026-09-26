# QA plan + quality gates

Không được viết "reviewer kiểm tra lại". Phải có sampling, metric, threshold và action khi fail. Thay mọi placeholder
mới là xong (gate G6).

## Flow

Guideline → Calibration → Production → Self-QC → Review → Rework → Quality Gate. Ghi cụ thể cho project của nhóm:

- **Ai review, review bao nhiêu:** QA owner (Phan Tấn Đạt) review 100% các task có `needs_review=true` hoặc tag `image_escalate`. Với các box và ảnh còn lại, lấy random sample 20% để review.
- **Chọn sample theo rule nào** (random, theo tag rủi ro, theo annotator mới…): Lấy 100% dựa theo thuộc tính rủi ro (`needs_review=true`, `image_escalate`). Sau đó chọn ngẫu nhiên 20% từ phần còn lại.
- **Issue được ghi ở đâu, đóng thế nào:** Issue được ghi vào file csv issue_log, kèm screenshot và sample_id. Đóng issue sau khi annotator vào CVAT sửa lỗi và báo Done.
- **Khi phát hiện guideline gap thì update và version ra sao:** Cập nhật ngay vào `08_revision_log.md`, ghi rõ nguyên nhân và action, tăng version (ví dụ từ v2 lên v3) ở file guideline và apply rule mới cho các lô dữ liệu sau.

## Defect severity

Nhóm được đổi mapping nếu downstream contract khác, nhưng phải giải thích và chốt trước khi QA.

| Severity | Định nghĩa cho project này | Ví dụ | Action mặc định |
|---|---|---|---|
| Critical | Sai sót trực tiếp ảnh hưởng đến cảnh báo quá tốc độ của mô hình | Bỏ sót không vẽ `speed_limit_sign`, gán sai `applies_to_ego` (đáng ra `yes` lại ghi `no`), hoặc đọc sai con số. | REWORK toàn bộ batch |
| Major | Gây ra cảnh báo thừa, sai phân loại biển phụ | Gán `yes` cho biển không áp dụng, gán sai `panel_type`. | REWORK các lỗi được point ra |
| Minor | Sai lệch hình học nhưng không ảnh hưởng bản chất | Box lệch mép biển trên 3px hoặc vẽ dính một chút vào cột. | Fix lỗi, nhắc nhở |
| Question | Mơ hồ do ảnh hoặc chưa có trong guideline | Gặp biển mới hoặc ảnh mờ không thấy số. | Update guideline & escalate |

## Metrics

| Metric | Cách tính | Vì sao phù hợp với bài toán |
|---|---|---|
| Decision Accuracy | Số decision đúng (label, thuộc tính) / tổng số decision | Đánh giá trực tiếp chất lượng quyết định logic, vì bài toán cần phân tích logic rẽ/đi thẳng. |
| Critical Escape Rate | Số lượng critical defect lọt lưới / tổng sample | Cực kỳ quan trọng vì miss biển tốc độ có thể gây tai nạn giao thông, ảnh hưởng trực tiếp tới hệ thống. |
| Geometry Accuracy | Số box đạt chuẩn (sai số <= 3px) / tổng số box | Đảm bảo box đủ tốt cho model detection. |

Metric high-risk tách riêng (ví dụ critical defect escape rate): Critical defect escape rate < 5%

## Quality gate

Threshold là đề xuất của nhóm, không phải chuẩn ngành. Giải thích trade-off cost/risk.

```text
PASS if:
  Decision Accuracy >= 90%
  Critical Escape Rate <= 5%
  Geometry Accuracy >= 85%
REWORK if: 
  Decision Accuracy < 90% HOẶC Critical Escape Rate > 5%
REJECT / ESCALATE if: 
  Critical Escape Rate > 15% HOẶC gặp vô số systematic error chưa được guideline nhắc tới.
```

Trade-off: Đặt ngưỡng Critical Escape Rate cực khắt khe (<=5%) khiến tốn nhiều cost review và rework, nhưng risk của dự án lái xe tự động (ADAS) là rất cao (gây tai nạn, bị phạt do quá tốc độ). Do đó chấp nhận cost QA cao để đảm bảo an toàn.
