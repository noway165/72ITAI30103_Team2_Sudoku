# Ghi chú Pruning (Forward Checking, AC-3) — Khoa

Tham khảo: AIMA chương 6, mục 6.2 *Constraint propagation and inference*.

Backtracking chỉ phát hiện nhánh sai khi đã gán tới ô bị kẹt. Pruning **loại bớt giá trị không thể** khỏi domain của các ô chưa gán ngay sau mỗi lần gán, nên nhánh sai bị cắt sớm.

| Kỹ thuật | Ý tưởng | Trong Sudoku |
|---|---|---|
| **Forward Checking (FC)** | Gán `X = v` → xoá `v` khỏi domain 20 ô hàng xóm chưa gán. Domain rỗng → quay lui. | Nhẹ, chỉ nhìn 1 bước |
| **AC-3** | Duy trì arc consistency: mỗi giá trị `x` của `Xi` phải còn "chỗ dựa" `y ≠ x` trong domain của `Xj`. Xoá được giá trị thì đẩy tiếp các cung liên quan vào queue. | Lan truyền nhiều bước (vd: ô chỉ còn 1 giá trị → loại giá trị đó khỏi hàng xóm → có ô khác chỉ còn 1 giá trị...) |

## Interface (theo hook `inference` của backtracking.py)

```python
BacktrackingSolver(csp, select_var=mrv, order_values=legal_values, inference=forward_checking)
BacktrackingSolver(csp, select_var=mrv, order_values=legal_values, inference=ac3_inference)
```

Hook trả về danh sách `(ô, giá_trị_đã_xoá)`; solver tự khôi phục khi quay lui. Nếu domain rỗng thì hook trả về phần đã xoá và solver coi là ngõ cụt.

Ngoài ra: `ac3(csp)` chạy AC-3 toàn bộ một lần trước khi giải (tiền xử lý, thay đổi domain vĩnh viễn, trả `False` nếu đề vô nghiệm); `propagate_clues(csp)` làm FC cho các ô cho sẵn.

## Số node đã đo (13 đề trong data/, số node duyệt)

| Đề | Baseline | MRV | MRV + FC | MRV + AC-3 (có tiền xử lý) |
|---|---|---|---|---|
| easy_01 | 69 | 41 | 41 | 0 |
| medium_04 | 4166 | 76 | 55 | 50 |
| hard_01 | 6188 | 149 | 155 | 72 |
| hard_03 | 71503 | 55 | 55 | 41 |
| hard_05 | 49558 | 10101 | 12694 | 4389 |

## Nhận xét (để dùng cho slide/essay)

- Solver của Lâm đã kiểm tra `is_consistent` và `legal_values` của MRV đã loại giá trị của hàng xóm đã gán, nên FC **khi đi kèm MRV gần như không giảm thêm node** (đôi khi cao hơn chút vì thứ tự chọn khác). FC chủ yếu cắt nhánh sớm hơn khi dùng với thứ tự cố định.
- AC-3 (cộng tiền xử lý) là kỹ thuật giảm node rõ nhất: đề dễ/trung bình gần như giải xong ngay khi tiền xử lý.
- `hard_05` là đề khó nhất cho mọi cấu hình, phù hợp để làm ca kiểm thử trong benchmark.
