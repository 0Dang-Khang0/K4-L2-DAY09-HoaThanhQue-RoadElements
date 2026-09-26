# Problem statement + downstream contract

## Bài toán

Với ảnh camera hành trình trên đường Đức (GTSDB), xác định **biển giới hạn tốc độ tối đa nào đang áp dụng cho xe mình
ở làn hiện tại** — khó ở chỗ biển có **biển phụ** (mũi tên hướng, khung giờ, loại xe), biển đặt ở **góc giao lộ /
điểm tách nhánh**, biển **nhỏ/xa/tối**, và các biển tròn viền đỏ **trông giống** (cấm vượt, cấm đi vào, hết lệnh cấm).

## Downstream contract

1. **Downstream task / model / user là ai?** Model nhận dạng biển cho chức năng hỗ trợ giới hạn tốc độ (Intelligent
   Speed Assist) trên xe con: cảnh báo tài xế khi chạy quá tốc độ biển đang áp dụng.
2. **Output annotation nào thực sự cần?** Rectangle `speed_limit_sign` cho mỗi biển nhìn thấy mặt trước, kèm
   attribute `speed_value` (con số), `applies_to_ego` (yes / no / unknown), `panel_type` (loại biển phụ),
   `needs_review`; tag ảnh `no_speed_sign` cho ảnh không có biển tốc độ.
3. **Failure nào gây hậu quả lớn nhất?** (a) **Bỏ sót** một biển đang áp dụng, hoặc gán `applies_to_ego=no` cho biển
   thực ra áp dụng → xe chạy quá tốc độ mà không được cảnh báo. (b) Gán `yes` cho biển chỉ dành cho hướng rẽ / loại
   xe khác → cảnh báo sai, tài xế mất tin tưởng hệ thống. (c) Đọc sai con số.
4. **Khi ambiguity không resolve được, ai / ở đâu là escalation path?** Trên box: `applies_to_ego=unknown` hoặc
   `speed_value=unreadable`, luôn kèm `needs_review=true`. Cả ảnh không quyết định được: tag `image_escalate`. QA
   owner xem lại mọi item này ở cỡ gốc, quyết định cuối và cập nhật guideline nếu thiếu rule.

## Scope

- **Trong scope (bắt buộc label):** biển giới hạn tốc độ **tối đa** — tròn, viền đỏ, có con số, không có vạch chéo —
  nhìn thấy mặt trước, ở mọi vị trí trong ảnh (kể cả biển không áp dụng cho xe mình).
- **Ngoài scope (ignore):** biển tốc độ tối thiểu (nền xanh), hết giới hạn tốc độ / hết lệnh cấm (có vạch chéo), cấm
  vượt, cấm xe tải vượt, cấm đi vào, Zone 30 (biển chữ nhật), mặt sau biển, biển in trên xe/quảng cáo. Biển phụ không
  vẽ riêng — chỉ ghi vào `panel_type`.
- **Geometry tolerance:** box ôm sát mép ngoài viền đỏ của phần biển nhìn thấy, không ôm cột / biển phụ / biển khác
  cùng cột; mỗi cạnh lệch ≤ 3 px khi xem ở 100%.

## Output chấm được

- **LABEL:** số box `speed_limit_sign` mỗi ảnh (ví dụ 2 biển hai bên đường = 2 box), `speed_value`, `panel_type`.
- **Decision critical:** `applies_to_ego` = yes / no trên từng box.
- **UNKNOWN:** `applies_to_ego=unknown` / `speed_value=unreadable` + `needs_review=true`.
- **IGNORE:** ảnh chỉ có biển ngoài scope → tag `no_speed_sign`, không có box.
- **ESCALATE:** tag `image_escalate`.
- **Geometry:** vị trí và độ ôm của box quanh viền đỏ.

Tất cả nằm trong export CVAT for images 1.1 (label, attribute, tag, toạ độ box).

## Dữ liệu và giới hạn

- Nguồn: `data/gtsdb`, 28 ảnh 1360×800 (biển Đức); dùng khoảng 15 ảnh: 4 example, 6 calibration, 5 blind.
- Chỉ 9/28 ảnh có biển giới hạn tốc độ tối đa; không ảnh nào có biển tốc độ tối thiểu hay hết giới hạn tốc độ, nên
  các loại đó để ngoài scope.
- Ảnh tĩnh, không có giờ chụp → biển phụ khung giờ không xác định được áp dụng hay không (`unknown`).
- Ít ảnh ban đêm/thời tiết xấu (chủ yếu ban ngày, 1 ảnh chạng vạng, 1 ảnh sương); biển Đức có thể khác biển Việt Nam
  về hình thức biển phụ và biển hết giới hạn.