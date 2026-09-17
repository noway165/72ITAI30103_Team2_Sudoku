# Sudoku CSP Solver

Final Project — Nhập môn Trí tuệ Nhân tạo (261_72ITSE30303_01)
Giảng viên: Dr. Huy T. Nguyen

Giải bài toán Sudoku bằng cách mô hình hoá dưới dạng **Constraint Satisfaction Problem (CSP)**, so sánh hiệu quả của nhiều chiến lược giải: Backtracking thuần, Heuristics (MRV/Degree/LCV), Pruning (Forward Checking/AC-3), và Local Search (Min-Conflicts).

## Mục tiêu

1. Hiểu và áp dụng chắc lý thuyết CSP vào một bài toán thực tế.
2. Rèn kỹ năng lập trình Python thông qua việc cài đặt nhiều thuật toán search.
3. So sánh định lượng hiệu quả (số node duyệt, thời gian chạy, tỉ lệ thành công) giữa các chiến lược giải khác nhau.

## Thành viên nhóm

| Tên | Vai trò | Phụ trách |
|---|---|---|
| **Lâm** | Leader | Quản lý dự án, biểu diễn Sudoku-CSP, Backtracking Search (baseline) |
| **Giang** | Thành viên | Heuristics: MRV, Degree, LCV |
| **Khoa** | Thành viên | Pruning: Forward Checking, AC-3 |
| **Quang** | Thành viên | Local Search: Min-Conflicts, Benchmark & thực nghiệm |

## Cấu trúc thư mục

```
sudoku-csp-solver/
├── src/                # Toàn bộ source code
│   ├── core.py         # Biểu diễn CSP: Variable, Domain, Constraint
│   ├── backtracking.py # Backtracking Search (baseline) — Lâm
│   ├── heuristics.py   # MRV, Degree, LCV — Giang
│   ├── pruning.py      # Forward Checking, AC-3 — Khoa
│   ├── local_search.py # Min-Conflicts — Quang
│   ├── benchmark.py    # Đo & so sánh hiệu năng — Quang
│   └── main.py         # Entry point chạy solver
├── data/                # Bộ đề Sudoku test (độ khó khác nhau)
├── results/             # Số liệu benchmark, biểu đồ so sánh
├── docs/                # Slide, essay, tài liệu tham khảo
├── requirements.txt
└── README.md
```

## Cài đặt môi trường

Yêu cầu Python 3.10+.

```bash
# Clone repo
git clone <repo-url>
cd sudoku-csp-solver

# Tạo virtual environment
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows

# Cài thư viện
pip install -r requirements.txt
```

## Cách chạy

```bash
python src/main.py --input data/easy_01.txt --method backtracking
python src/main.py --input data/hard_01.txt --method min_conflicts
```

Các giá trị `--method` hỗ trợ: `backtracking`, `mrv_lcv`, `forward_checking`, `ac3`, `min_conflicts` *(cập nhật khi từng module hoàn thiện)*.

## Định dạng dữ liệu đầu vào

File `.txt` trong `data/`, 9 dòng, mỗi dòng 9 ký tự số (0 = ô trống):

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

## Quy trình làm việc (Git)

- Nhánh `main` luôn giữ code chạy được, không push trực tiếp.
- Mỗi người làm trên nhánh riêng: `feature/backtracking`, `feature/heuristics`, `feature/pruning`, `feature/local-search`.
- Mở Pull Request để Lâm review & merge vào `main`.
- Commit message ngắn gọn, rõ ràng (ví dụ: `add MRV heuristic`, `fix AC-3 domain check`).

## Lộ trình (tóm tắt)

| Mốc | Ngày |
|---|---|
| Thuyết trình Proposal | 02/10/2026 |
| Thuyết trình Logical Agents (môn học) | 22/10/2026 |
| Buổi học cuối — Final ready | 12/11/2026 |
| Thuyết trình Oral | 19/11/2026 |
| Hạn nộp ETC | 22/11/2026 |

Chi tiết lịch trình từng tuần: xem `docs/lich_trinh.docx`.

## Deliverables

1. Report (essay 10 trang, double-spaced)
2. Source code
3. Executable file chạy trên Windows
