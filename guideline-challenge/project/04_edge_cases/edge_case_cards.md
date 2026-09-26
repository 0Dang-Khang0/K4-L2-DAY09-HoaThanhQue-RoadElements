# Edge-case library

Tối thiểu **8 card**, khuyến nghị 10–12. Một edge case tốt là case mà hai annotator hợp lý có thể làm khác nhau nếu
guideline chưa rõ. Tám ảnh dễ có label rõ ràng không được tính là edge-case library.

Cần có đủ độ đa dạng: occlusion / truncation / small-far · ambiguous semantics · conflicting road elements · **một case
critical-risk** · **một case guideline cho phép escalation**.

File này là kho nội bộ của nhóm, **không gửi cho peer**. Card dùng ảnh example/calibration thì chép rule + ví dụ sang
`02_guideline.md` (mục 7 và 9) để peer đọc được. Card về ảnh blind chỉ nằm ở đây, và decision của nó phải có trong
`gold_decisions.csv` trước `make freeze`.

---

CASE ID: EC-01
Sample: GTS18
Scene: Đường nhỏ, lề phải có cột tam giác và biển 30
Observation: Thấy tam giác cảnh báo và biển tốc độ 30 trên cùng 1 cột
Decision: LABEL
Expected: 1 x `speed_limit_sign`: `speed_value=30`, `applies_to_ego=yes`, `panel_type=none`, `needs_review=false`. geometry ôm sát mặt biển tròn.
Rationale: Tam giác không phải biển phụ và không nằm trong scope. Biển tốc độ lề phải áp dụng cho ego.
Common mistake: Ôm box cả cột hoặc cho tam giác là biển phụ.
Diversity: conflicting road elements

---

CASE ID: EC-02
Sample: GTS01
Scene: Đường qua rừng, hai cột trái phải
Observation: Hai biển 50 và hai biển cấm vượt ở 2 cột
Decision: LABEL
Expected: 2 x `speed_limit_sign`: `speed_value=50`, `applies_to_ego=yes`, `panel_type=none`.
Rationale: Mỗi biển tốc độ 50 là một instance riêng. Biển cấm vượt nằm ngoài scope.
Common mistake: Chỉ vẽ 1 box hoặc vẽ luôn biển cấm vượt.
Diversity: normal

---

CASE ID: EC-03
Sample: GTS15
Scene: Đường phố
Observation: Có biển tròn trắng vạch chéo hình xe (hết cấm xe tải vượt)
Decision: IGNORE
Expected: tag `no_speed_sign`
Rationale: Biển có vạch chéo và không có số là ngoài scope.
Common mistake: Nhầm thành biển tốc độ vì có viền đỏ tròn.
Diversity: negative

---

CASE ID: EC-04
Sample: GTS04
Scene: Cao tốc có sương
Observation: Biển 120 lề trái và phải cạnh dải phân cách
Decision: LABEL
Expected: 2 x `speed_limit_sign`: `speed_value=120`, `applies_to_ego=yes`, `panel_type=none`.
Rationale: Đường cao tốc, biển lề trái vẫn áp dụng.
Common mistake: Bỏ qua biển lề trái.
Diversity: small_far

---

CASE ID: EC-05
Sample: GTS06
Scene: Lề phải
Observation: Biển 30 với 2 biển phụ bên dưới
Decision: UNKNOWN
Expected: 1 x `speed_limit_sign`: `speed_value=30`, `panel_type=multiple`, `applies_to_ego=unknown`, `needs_review=true`
Rationale: Biển phụ thời gian không xác định được trong ảnh tĩnh.
Common mistake: Gán applies_to_ego=yes
Diversity: ambiguity

---

CASE ID: EC-06
Sample: GTS05
Scene: Giao lộ
Observation: Biển 30 góc vỉa hè bên kia đường, có mặt sau biển
Decision: UNKNOWN
Expected: 1 x `speed_limit_sign`: `speed_value=30`, `panel_type=none`, `applies_to_ego=unknown`, `needs_review=true`
Rationale: Góc giao lộ không biết đường dành cho chiều nào
Common mistake: Gán applies_to_ego=yes hoặc vẽ cả mặt sau
Diversity: escalation

---

CASE ID: EC-07
Sample: GTS17
Scene: Bãi xe
Observation: Biển tròn đỏ vạch trắng (cấm đi vào)
Decision: IGNORE
Expected: tag `no_speed_sign`
Rationale: Biển không có số
Common mistake: Vẽ nhầm thành speed_limit_sign
Diversity: negative

---

CASE ID: EC-08
Sample: GTS11 (blind)
Scene: Đường hẹp
Observation: Biển tốc độ bị cành cây che lấp một phần lớn nhưng vẫn thấy số
Decision: LABEL
Expected: 1 x `speed_limit_sign`: `speed_value=unreadable`, `applies_to_ego=yes`, `panel_type=none`, `needs_review=true`
Rationale: Bị che lấp nên không tự bịa số được, phải nhờ reviewer hỗ trợ
Common mistake: Tự đoán số
Diversity: critical
