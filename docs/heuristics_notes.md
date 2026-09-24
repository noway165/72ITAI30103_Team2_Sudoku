# Ghi chú Heuristics (MRV, Degree, LCV) — Giang

Tham khảo: AIMA chương 6, mục 6.3.1 *Variable and value ordering*.

Backtracking thuần chọn ô theo thứ tự cố định (hàng → cột) và thử giá trị 1 → 9. Heuristics thay hai lựa chọn đó:

| Câu hỏi | Heuristic | Ý tưởng |
|---|---|---|
| Gán ô nào tiếp theo? | **MRV** | Chọn ô có ít giá trị hợp lệ nhất ("fail-first": nếu nhánh sai thì phát hiện sớm) |
| Nếu MRV hoà? | **Degree** | Chọn ô ràng buộc với nhiều ô *chưa gán* nhất |
| Thử giá trị nào trước? | **LCV** | Thử giá trị loại bỏ ít lựa chọn nhất của các ô hàng xóm ("succeed-first") |

## Áp dụng vào thiết kế Sudoku-CSP (docs/design.md)

- **Giá trị hợp lệ** của ô `(r, c)` = domain của ô trừ đi các giá trị đã gán ở 20 ô hàng xóm. Tính theo cách này nên MRV chạy được cả khi có lẫn không có Forward Checking/AC-3 (nếu Khoa đã prune domain thì kết quả chỉ nhỏ hơn).
- **Ô cho sẵn** nằm trong `assignment` ngay từ đầu nên MRV/Degree không bao giờ chọn lại chúng.
- **Degree** trong Sudoku: ban đầu mọi ô đều có 20 hàng xóm, nên Degree chỉ có tác dụng khi đếm hàng xóm *chưa gán*, và chủ yếu dùng để phá hoà cho MRV.

## Interface đang giả định với core.py

`heuristics.py` hiện chỉ cần một object `csp` có 3 thuộc tính, và `assignment` là dict:

```python
csp.variables   # list[(row, col)]            — 81 biến
csp.domains     # dict[(row, col)] -> iterable — domain hiện tại
csp.neighbors   # dict[(row, col)] -> iterable — 20 ô hàng xóm
assignment      # dict[(row, col)] -> int
```

**Cần xác nhận với Lâm** khi `core.py` lên repo; nếu tên thuộc tính khác thì chỉ cần sửa trong `legal_values` và `mrv`.

## Pseudocode

```
MRV(csp, assignment):
    return argmin over unassigned var of |LEGAL-VALUES(var)|

LEGAL-VALUES(var):
    return { x in domain(var) : no assigned neighbor of var has value x }
```

Phác thảo cho phần sẽ code sau Proposal (lịch: Degree 02–03/10, LCV 05–08/10):

```
DEGREE(var):
    return number of unassigned neighbors of var

MRV-DEGREE(csp, assignment):
    return argmin over unassigned var of ( |LEGAL-VALUES(var)|, -DEGREE(var) )

LCV(var):
    for each x in LEGAL-VALUES(var):
        cost(x) = number of unassigned neighbors n with x in LEGAL-VALUES(n)
    return LEGAL-VALUES(var) sorted by cost ascending
```

## Kết quả thử sơ bộ (MRV, 24/09)

Node = số lần gán một giá trị hợp lệ. Cả hai cách đều dùng backtracking giống nhau, chỉ khác cách chọn ô.

| Đề | Ô cho sẵn | Backtracking thuần | + MRV |
|---|---|---|---|
| easy_01 → 04 | 40 | 45 – 321 node | 41 node (không phải quay lui) |
| medium_01 → 04 | 32 | 133 – 4 166 node | 49 – 76 node |
| hard_01 → 04 | 26 | 825 – 71 503 node | 55 – 256 node |
| hard_05 (Arto Inkala) | 21 | 49 558 node · 0,24 s | 10 101 node · 1,03 s |

Nhận xét cho essay/Oral:

1. MRV giảm số node rất mạnh trên đề khó (hard_03: 71 503 → 55).
2. **Ít node hơn chưa chắc nhanh hơn**: ở hard_05, MRV duyệt ít node hơn gần 5 lần nhưng chạy chậm hơn, vì mỗi node phải quét lại 81 ô × 20 hàng xóm. Cần đo cả node lẫn thời gian.
3. **Số ô cho sẵn không phản ánh đúng độ khó**: hard_02 (26 ô cho sẵn) chỉ cần 825 node ở backtracking thuần, ít hơn medium_04 (4 166 node).

## Bộ đề trong /data

- 12 đề (easy/medium/hard 01–04) sinh ngẫu nhiên với seed 2026, xoá dần ô cho đến khi còn 40 / 32 / 26 ô cho sẵn, **mỗi đề đã kiểm tra có đúng 1 nghiệm**.
- hard_05 là đề của Arto Inkala (2012), thường được gọi là "đề Sudoku khó nhất thế giới".
- Nhãn độ khó dựa trên số ô cho sẵn (xem nhận xét 3 ở trên).
