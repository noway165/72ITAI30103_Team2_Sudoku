# Thiết kế dữ liệu Sudoku-CSP

Thiết kế đã được cả nhóm thống nhất ngày 23/09/2026, không có thay đổi so với bản đề xuất ban đầu.

## 1. Biến (Variables)

Mỗi ô trên lưới 9x9 là một biến, đặt tên theo tọa độ `(hàng, cột)`, đánh số từ 0 đến 8. Tổng cộng có **81 biến**.

## 2. Miền giá trị (Domain)

- Ô còn trống: domain = `{1, 2, 3, 4, 5, 6, 7, 8, 9}`
- Ô đã có sẵn số (cho trước trong đề bài): domain chỉ có đúng 1 giá trị đó, coi như đã gán sẵn.

## 3. Ràng buộc (Constraints)

Mỗi ô có ràng buộc "tất cả khác nhau" (all-different) với:

- 8 ô còn lại cùng hàng
- 8 ô còn lại cùng cột
- 8 ô còn lại cùng khối 3x3 chứa nó

Mỗi ô có tối đa 20 ô "hàng xóm" (có một số ô trùng nhau giữa 3 nhóm trên nên không phải 24).

## 4. Định dạng file đề đầu vào

File `.txt`, 9 dòng, mỗi dòng 9 ký tự số, `0` = ô trống. Ví dụ:

```
530070000
600195000
098000060
800060003
400803001
700020006
060000280
000419005
000080079
```

## 5. Quy tắc đặt tên file đề

Lưu trong thư mục `/data`, đặt tên theo mẫu `<độ_khó>_<số_thứ_tự>.txt`, ví dụ: `easy_01.txt`, `medium_01.txt`, `hard_01.txt`.

## 6. Ghi chú

Toàn bộ code sau này (baseline, heuristics, pruning, local search) đều phải tuân theo đúng cách biểu diễn này để đảm bảo tương thích khi merge vào `main`.
