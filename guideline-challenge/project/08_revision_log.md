# Revision log

Guideline v1 = bản nháp đầu; v2 = sau calibration nội bộ; v3 = sau blind handoff. Mỗi lần tăng `Version` trong
`02_guideline.md`, thêm một hoặc nhiều dòng vào bảng: đổi gì và vì sao, kèm bằng chứng (sample_id, dòng
calibration report, câu hỏi trong clarification log, feedback của peer).

Cột Version ghi dạng `v1`, `v2`, `v3` — `make status` tìm dòng bảng có `v2` và dòng có `v3`.

| Version | Đổi gì | Vì sao | Bằng chứng |
|---|---|---|---|
| v2 | Thêm giải thích rõ về loại biển bị gạch chéo không phải là biển tốc độ tối đa | Annotator nhầm biển hết cấm xe tải vượt với biển 30 | GTS15, dòng 1 calibration report |
| v3 | Bổ sung quy định gán needs_review khi bị khuất cây cối không đoán được số | Tránh tình trạng annotator tự đoán số dẫn tới critical error | Clarification log (peer hỏi có đoán số không) |
