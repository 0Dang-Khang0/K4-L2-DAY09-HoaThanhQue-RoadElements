# Annotation guideline — Biển giới hạn tốc độ có áp dụng cho xe mình không (GTSDB)

**Version:** v1

> Guideline này là tài liệu duy nhất người gắn nhãn nhận được. Rule nào không có ở đây thì không tồn tại.
> Tên label, attribute và giá trị trong CVAT viết bằng tiếng Anh, **giống hệt** như trong file này.
> Ví dụ chỉ dùng ảnh thuộc split `example` và `calibration`.

---

## 0. Tóm tắt 30 giây

**Câu hỏi của bài:** *Trong ảnh có biển giới hạn tốc độ nào đang áp dụng cho xe mình ở làn hiện tại không?*

Với **mỗi ảnh**, bạn làm đúng một trong hai việc:

1. **Có ít nhất một biển giới hạn tốc độ nhìn thấy mặt trước** → vẽ một `speed_limit_sign` (rectangle) cho **mỗi** biển,
   rồi gán đủ 4 attribute: `speed_value`, `applies_to_ego`, `panel_type`, `needs_review`.
2. **Không có biển giới hạn tốc độ nào** → gắn tag cả ảnh `no_speed_sign`. Không vẽ gì khác.

Nếu không quyết định được ngay cả việc ảnh có biển giới hạn tốc độ hay không → gắn tag `image_escalate` (mục 7).

Không bao giờ để giá trị `__undefined__` trong bài đã Save.

---

## 1. Objective + scope

### 1.1 Mục đích (downstream)

Dữ liệu dùng để huấn luyện và đánh giá chức năng **hỗ trợ giới hạn tốc độ** (Intelligent Speed Assist) trên xe con:
hệ thống phải biết (a) có biển giới hạn tốc độ không, (b) con số là bao nhiêu, và quan trọng nhất
(c) biển đó **có áp dụng cho xe mình** ở làn hiện tại hay không.

Lỗi nặng nhất: **bỏ sót một biển đang áp dụng** hoặc gán `applies_to_ego=no` cho biển thực ra áp dụng — xe sẽ
chạy quá tốc độ cho phép mà không được cảnh báo. Lỗi nhẹ hơn: gán `yes` cho biển không áp dụng — xe bị nhắc giảm
tốc không cần thiết.

### 1.2 "Xe mình" (ego) là gì

- Ego là **xe con (ô tô cá nhân)** gắn camera, đang đi **thẳng theo làn hiện tại**.
- Làn hiện tại = làn nằm ở giữa, phía dưới ảnh, ngay trước nắp capo.
- Giả định ego **đi thẳng**, trừ khi vạch sơn trên làn ego là mũi tên **chỉ** rẽ (không có mũi tên thẳng) — khi đó
  ego đi theo hướng mũi tên.

### 1.3 Trong scope (bắt buộc vẽ)

Biển **giới hạn tốc độ tối đa** kiểu châu Âu:

- Hình tròn, **viền đỏ**, nền trắng (hoặc nền đen chữ trắng/viền đỏ phát sáng ở biển điện tử),
- ở giữa là **một con số** (km/h), ví dụ 30, 50, 100, 120.

### 1.4 Ngoài scope (không vẽ, không tính là biển tốc độ)

| Biển | Nhận dạng | Làm gì |
|---|---|---|
| Hết giới hạn tốc độ | tròn trắng, số màu xám, có các vạch chéo xám/đen | không vẽ |
| Hết cấm vượt / hết mọi lệnh cấm | tròn trắng, vạch chéo, **không có số** | không vẽ |
| Cấm vượt, cấm xe tải vượt | tròn viền đỏ, bên trong là **hình xe**, không có số | không vẽ |
| Cấm đi vào | tròn đỏ, vạch trắng ngang | không vẽ |
| Cấm xe / cấm dừng / cấm đỗ | tròn viền đỏ, không có số | không vẽ |
| Tốc độ tối thiểu | tròn **nền xanh**, số trắng | không vẽ |
| Khu vực tốc độ (Zone 30) | biển **chữ nhật** có vòng tròn 30 bên trong | không vẽ |
| Tốc độ khuyến nghị | vuông xanh | không vẽ |
| Biển phụ (tấm chữ nhật trắng dưới biển tốc độ) | | **không vẽ riêng** — chỉ ghi vào `panel_type` của biển tốc độ phía trên |
| Mặt sau của biển | đĩa tròn xám/kim loại | không vẽ |

Nếu ảnh chỉ có các biển ngoài scope → ảnh đó là `no_speed_sign`.

---

## 2. Annotation unit

- **Đơn vị:** ảnh tĩnh, mỗi ảnh chấm độc lập. Không suy luận từ ảnh khác.
- **Instance:** **mỗi mặt biển giới hạn tốc độ vật lý = một rectangle**.
  - Hai biển giống nhau đặt hai bên đường (ví dụ cùng 50 ở trái và phải) = **2 instance**, 2 rectangle.
  - Hai biển khác số trên cùng một cột = 2 instance.
  - Biển tốc độ + biển phụ bên dưới = **1 instance** (biển phụ là attribute, không phải instance).
  - Biển tốc độ + biển cấm vượt trên cùng cột = 1 instance (chỉ biển tốc độ). Biển cấm vượt ngoài scope.
- **Tag cả ảnh:** `no_speed_sign` và `image_escalate` là tag, gắn tối đa 1 lần mỗi ảnh.
- Trong CVAT dùng **Shape** (không dùng Track), vì đây là ảnh tĩnh.

---

## 3. Geometry rule

- **Tool:** `Draw new rectangle` (box).
- **Box ôm sát mặt biển tròn nhìn thấy được**: 4 cạnh chạm **mép ngoài của viền đỏ**.
- **Không** ôm cột, **không** ôm biển phụ bên dưới, **không** ôm biển khác trên cùng cột (tam giác cảnh báo, biển cấm
  vượt…).
- Biển nghiêng/nhìn chéo (hình elip): box ôm sát elip.
- **Bị che một phần:** box chỉ ôm **phần nhìn thấy** (visible box), không đoán phần bị che (không amodal).
- **Bị cắt ở mép ảnh:** box dừng ở mép ảnh.
- **Tolerance:** mỗi cạnh lệch không quá **3 px** so với mép viền đỏ khi xem ở 100%. Với biển rất nhỏ (< 20 px), box
  không được to hơn gấp đôi mặt biển.
- Không có ngưỡng kích thước tối thiểu: nhận ra được là biển tròn viền đỏ có số thì vẽ, dù nhỏ.
- **Luôn zoom** (cuộn chuột) vào biển khi vẽ; không vẽ ở mức zoom toàn ảnh.

---

## 4. Taxonomy

### 4.1 Label

| Label | Kiểu | Ý nghĩa |
|---|---|---|
| `speed_limit_sign` | rectangle | một biển giới hạn tốc độ tối đa, nhìn thấy mặt trước |
| `no_speed_sign` | tag (cả ảnh) | ảnh không có biển giới hạn tốc độ nào nhìn thấy mặt trước |
| `image_escalate` | tag (cả ảnh) | không quyết định được ảnh có biển giới hạn tốc độ hay không; cần reviewer |

### 4.2 Attribute của `speed_limit_sign` (bắt buộc gán cả 4)

| Attribute | Giá trị cho phép | Default | Khi nào dùng |
|---|---|---|---|
| `speed_value` | `__undefined__`, `10`, `20`, `30`, `40`, `50`, `60`, `70`, `80`, `90`, `100`, `110`, `120`, `130`, `unreadable` | `__undefined__` | con số đọc được trên biển; `unreadable` khi thấy rõ là biển tốc độ nhưng không đọc chắc chắn được số |
| `applies_to_ego` | `__undefined__`, `yes`, `no`, `unknown` | `__undefined__` | theo cây quyết định ở mục 7.2 |
| `panel_type` | `__undefined__`, `none`, `direction`, `time`, `distance`, `vehicle_type`, `multiple`, `unreadable` | `__undefined__` | loại biển phụ **ngay dưới** biển tốc độ (mục 4.3) |
| `needs_review` | checkbox `false` / `true` | `false` | tích khi `applies_to_ego=unknown` hoặc `speed_value=unreadable` hoặc bạn không chắc box có đúng là biển tốc độ |

`__undefined__` chỉ là giá trị "chưa chọn". Còn `__undefined__` trong export = bài chưa xong = lỗi.

### 4.3 Chọn `panel_type`

Biển phụ là **tấm chữ nhật trắng viền đen** gắn **ngay dưới** biển tốc độ, trên cùng cột.

| Giá trị | Biển phụ trông thế nào |
|---|---|
| `none` | không có tấm chữ nhật nào ngay dưới. Biển tròn khác (cấm vượt…) ở dưới **không** phải biển phụ |
| `direction` | mũi tên chỉ hướng rẽ (↱, ↰) — biển chỉ áp dụng cho xe đi theo hướng đó |
| `time` | khung giờ/ngày, ví dụ "7–18 h", "Mo–Fr" |
| `distance` | khoảng cách/đoạn áp dụng, ví dụ "↑ 300 m ↑", "800 m" |
| `vehicle_type` | hình xe tải, xe buýt, xe kéo rơ-moóc… hoặc điều kiện thời tiết ("bei Nässe", hình mưa/tuyết) |
| `multiple` | có **từ 2 tấm** biển phụ trở lên |
| `unreadable` | có tấm biển phụ nhưng không nhìn ra nội dung |

---

## 5. Inclusion / exclusion

### Bắt buộc vẽ

- Mọi biển giới hạn tốc độ tối đa (mục 1.3) **nhìn thấy mặt trước**, ở bất kỳ vị trí nào trong ảnh: lề phải, lề trái,
  dải phân cách, giá trên cao, góc giao lộ, đường nhánh.
- Biển **không áp dụng** cho ego vẫn phải vẽ, gán `applies_to_ego=no`. Không được bỏ qua chỉ vì biển "không liên
  quan".
- Biển rất nhỏ/xa nhưng vẫn nhận ra là biển tròn viền đỏ có số.

### Không vẽ

- Mọi biển trong bảng "Ngoài scope" (mục 1.4).
- Mặt sau biển (thấy đĩa kim loại xám, không thấy viền đỏ và số).
- Biển quay gần như vuông góc với camera (chỉ thấy cạnh mỏng, không thấy mặt biển).
- Biển in trên xe, trên poster quảng cáo, phản chiếu trên kính.

### Tag ảnh

- Có ≥ 1 `speed_limit_sign` → **không** gắn `no_speed_sign`.
- Không có `speed_limit_sign` nào → **bắt buộc** gắn `no_speed_sign` (không được để ảnh trống).
- Một ảnh không bao giờ có cùng lúc `no_speed_sign` và `speed_limit_sign`.

---

## 6. Visibility / occlusion

| Tình huống | Làm gì |
|---|---|
| Bị cây, cột, xe che một phần nhưng **đọc được số** | vẽ box phần nhìn thấy, gán bình thường |
| Bị che, **thấy rõ là biển tốc độ** (viền đỏ, có chữ số) nhưng không đọc chắc số | vẽ, `speed_value=unreadable`, `needs_review=true` |
| Không phân biệt được là biển tốc độ hay biển tròn đỏ khác (cấm vượt, cấm xe…) | vẽ, `speed_value=unreadable`, `needs_review=true` |
| Bị cắt ở mép ảnh, còn đọc được số | vẽ box tới mép ảnh |
| Nhỏ/xa, zoom vẫn đọc được số | vẽ bình thường |
| Ảnh tối/chạng vạng, ngược sáng, loá | zoom và tăng độ sáng (Settings → Image → Brightness trong CVAT) trước khi quyết định; đọc được thì gán bình thường |
| Ảnh nhoè do chuyển động | như trên; không đoán số — không chắc thì `unreadable` |
| Một vùng bị loá/nhoè đến mức **không biết có biển hay không** | gắn tag `image_escalate` (mục 7) |

**Quy tắc đọc số:** chỉ chọn một con số khi bạn chắc chắn. Không chọn số "có vẻ giống". 30 và 80, 50 và 60 dễ nhầm ở
biển nhỏ — không chắc thì `unreadable`.

---

## 7. Ambiguity / escalation

### 7.1 Bốn quyết định và cách thể hiện trong CVAT

| Quyết định | Khi nào | Thể hiện trong CVAT (nhìn thấy trong export) |
|---|---|---|
| **LABEL** | chắc chắn có biển tốc độ và xác định được áp dụng hay không | `speed_limit_sign` + `applies_to_ego=yes` hoặc `no`, `needs_review=false` |
| **IGNORE** | vật thể ngoài scope (mục 1.4, 5) | không vẽ; nếu cả ảnh không có biển tốc độ thì tag `no_speed_sign` |
| **UNKNOWN** | có biển tốc độ nhưng ảnh không đủ bằng chứng để biết nó có áp dụng cho ego không, hoặc không đọc được số | `speed_limit_sign` + `applies_to_ego=unknown` và/hoặc `speed_value=unreadable`, **luôn** `needs_review=true` |
| **ESCALATE** | không quyết định được ngay cả việc ảnh có biển tốc độ hay không | tag cả ảnh `image_escalate` (có thể kèm các box đã chắc chắn) |

Luật cứng: `applies_to_ego=unknown` ⇒ `needs_review=true`. `speed_value=unreadable` ⇒ `needs_review=true`.

### 7.2 Cây quyết định `applies_to_ego`

Đi từ trên xuống, dừng ở bước đầu tiên khớp:

1. **Biển có dành cho chiều ngược lại / đường khác hẳn không?**
   Biển đặt bên kia dải phân cách cứng hoặc lề trái đường hai chiều và quay mặt về phía xe đi ngược chiều → **không
   vẽ** nếu chỉ thấy mặt sau; nếu thấy mặt trước nhưng rõ ràng đặt cho đường cắt ngang/đường song song khác →
   `no`.
2. **Biển có biển phụ không?** (`panel_type`)
   - `direction`: mũi tên trùng hướng đi của ego (mục 1.2) → `yes`; mũi tên chỉ hướng khác → **`no`**.
   - `vehicle_type`: chỉ áp dụng cho xe tải/xe buýt/xe kéo → **`no`** (ego là xe con).
     Điều kiện thời tiết ("khi đường ướt"), không biết trời có ướt không → `unknown`.
   - `time`: ảnh không cho biết giờ chụp → **`unknown`**.
   - `distance`: vẫn áp dụng từ vị trí biển → xét tiếp bước 3.
   - `multiple`: xét từng tấm; có một tấm dẫn tới `no` → `no`; không có `no` nhưng có một tấm dẫn tới `unknown` →
     `unknown`; còn lại xét tiếp bước 3.
   - `unreadable`: không biết điều kiện → **`unknown`**.
   - `none`: xét tiếp bước 3.
3. **Biển có đứng ở vị trí dành cho đường ego đang đi không?** → `yes` khi biển:
   - ở **lề phải** của đường ego, quay mặt về phía ego; hoặc
   - ở **lề trái** của đường một chiều / cao tốc / đường có dải phân cách (bên trái vẫn thuộc chiều của ego); hoặc
   - trên giá/khung **phía trên làn ego**.
4. **Biển ở góc giao lộ, ở điểm tách nhánh, hoặc ở mép một đường nhánh**, và ảnh không cho biết nó dành cho đường ego
   đi tiếp hay đường ego sắp rẽ/cắt qua → **`unknown`** + `needs_review=true`.

Không suy đoán ngoài ảnh (ví dụ "ở Đức trong phố thường là 50"). Chỉ dùng bằng chứng nhìn thấy.

### 7.3 Escalation path

- Mọi box `needs_review=true` và mọi ảnh `image_escalate` được reviewer (QA owner) xem lại ở cỡ gốc.
- Reviewer quyết định cuối; nếu phát hiện rule thiếu thì ghi vào `08_revision_log.md` và tăng version guideline.
- Người gắn nhãn **không** hỏi miệng để chốt; dùng `unknown`/`needs_review`/`image_escalate` rồi đi tiếp.

---

## 8. Temporal rule

Không áp dụng — task ảnh tĩnh. Mỗi ảnh độc lập, dùng Shape, không dùng Track. Mọi attribute `mutable=false`.

---

## 9. Examples

Mở ảnh theo `sample_id` trong thư mục `data/gtsdb/`.

| sample_id | Thấy gì | Expected output | Rule áp dụng |
|---|---|---|---|
| GTS18 | Đường nhỏ, lề phải có cột: tam giác cảnh báo khúc cua, bên dưới là biển tròn **30** | 1 × `speed_limit_sign`: `speed_value=30`, `applies_to_ego=yes`, `panel_type=none`, `needs_review=false`. Box ôm viền đỏ của biển 30, **không** ôm tam giác | 3, 4.3, 7.2 bước 3 |
| GTS01 | Đầu đoạn đường qua rừng; **hai cột, trái và phải**, mỗi cột: tam giác cảnh báo, biển **50**, biển tròn cấm vượt | 2 × `speed_limit_sign` (trái + phải): cả hai `speed_value=50`, `applies_to_ego=yes`, `panel_type=none`. Biển cấm vượt **không** vẽ và **không** phải biển phụ | 2 (2 instance), 1.4, 4.3 |
| GTS15 | Đường phố; biển tròn trắng có **vạch chéo** và hình xe, **không có số** (hết cấm xe tải vượt); nhiều biển chỉ đường | tag `no_speed_sign`. Không vẽ box | 1.4 (look-alike) |
| GTS22 | Đường chui dưới cầu, ngược sáng; phía xa có biển chỉ đường, tam giác nhường đường, biển mũi tên đỏ trắng | tag `no_speed_sign` | 5 (tag ảnh) |
| GTS04 | Cao tốc có sương; biển **120** ở lề trái (cạnh dải phân cách) và lề phải, dưới mỗi biển là biển tròn cấm xe tải vượt | 2 × `speed_limit_sign`: `speed_value=120`, `applies_to_ego=yes`, `panel_type=none`. Biển lề trái vẫn `yes` vì cùng chiều cao tốc | 2, 7.2 bước 3 (lề trái đường có dải phân cách) |
| GTS06 | Lề phải: biển **30**, bên dưới có **2 tấm** biển phụ: "↑ … m ↑" và khung giờ "7–18 h" (chữ mờ) | 1 × `speed_limit_sign`: `speed_value=30`, `panel_type=multiple`, `applies_to_ego=unknown`, `needs_review=true` | 4.3, 7.2 bước 2 (`time` → `unknown`) |
| GTS05 | Xe đang ở giao lộ; biển **30** đứng ở góc vỉa hè **bên kia đường cắt ngang**; bên phải có đĩa tròn xám và tam giác xám (mặt sau biển) | 1 × `speed_limit_sign`: `speed_value=30`, `panel_type=none`, `applies_to_ego=unknown`, `needs_review=true`. Mặt sau biển **không** vẽ | 7.2 bước 4, 5 (mặt sau) |
| GTS17 | Lối vào bãi xe; hai biển **tròn đỏ vạch trắng** (cấm đi vào) | tag `no_speed_sign` | 1.4 (look-alike) |
| GTS26 | Đường quê; chỉ có một biển tam giác cảnh báo nhỏ ở xa | tag `no_speed_sign` (zoom để chắc chắn không có biển tròn nào) | 5 |
| GTS12 | Đường ngoại ô; tam giác cảnh báo + biển chỉ đường vàng ở xa | tag `no_speed_sign` | 5 |

---

## 10. Common mistakes

1. **Vẽ biển cấm vượt / cấm xe tải vượt / cấm đi vào** vì chúng cũng tròn viền đỏ. → Chỉ vẽ khi bên trong là **con
   số**.
2. **Coi biển tròn bên dưới biển tốc độ là biển phụ.** → Biển phụ là **tấm chữ nhật**. Biển tròn bên dưới là biển độc
   lập ngoài scope; `panel_type=none`.
3. **Vẽ một box ôm cả cột** (tam giác + biển tốc độ + biển phụ). → Box chỉ ôm viền đỏ của biển tốc độ.
4. **Chỉ vẽ một biển khi hai bên đường đều có biển.** → Mỗi mặt biển là một instance.
5. **Bỏ qua biển không áp dụng.** → Vẫn vẽ, gán `applies_to_ego=no` hoặc `unknown`.
6. **Gán `yes` cho biển có biển phụ mũi tên rẽ** trong khi làn ego đi thẳng. → Đọc biển phụ trước (7.2 bước 2).
7. **Gán `yes` cho biển có biển phụ khung giờ.** → Ảnh không có giờ chụp → `unknown`.
8. **Nhầm biển hết giới hạn / hết lệnh cấm (vạch chéo) với biển tốc độ.** → Có vạch chéo = ngoài scope.
9. **Quên gắn `no_speed_sign`** cho ảnh không có biển. → Ảnh trống trong export bị tính là chưa làm.
10. **Để `__undefined__`** ở một attribute. → Kiểm tra từng box trước khi Save.
11. **Đoán số** ở biển nhỏ/mờ. → Không chắc thì `unreadable` + `needs_review=true`.
12. **Không zoom** nên bỏ sót biển nhỏ ở hai bên lề, nhất là ảnh cao tốc và ảnh tối. → Quét trái → phải ở mức zoom
    ≥ 200% trước khi kết luận `no_speed_sign`.

### Checklist trước khi Save (Ctrl+S)

- [ ] Đã quét cả hai bên lề, dải phân cách và phía trên đường ở mức zoom lớn.
- [ ] Mỗi biển tốc độ nhìn thấy mặt trước có đúng 1 box, ôm sát viền đỏ.
- [ ] Không box nào ôm biển phụ, cột, hoặc biển khác.
- [ ] Mỗi box: `speed_value`, `applies_to_ego`, `panel_type` đều khác `__undefined__`.
- [ ] Mọi box `unknown` hoặc `unreadable` đều có `needs_review=true`.
- [ ] Ảnh không có box nào → đã gắn `no_speed_sign`.
- [ ] Không có ảnh nào vừa có box vừa có `no_speed_sign`.
