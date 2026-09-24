from typing import Dict, List, Set, Tuple

Cell = Tuple[int, int]  # (row, col), 0-indexed


class CSP:
    """Constraint Satisfaction Problem for a 9x9 Sudoku."""

    def __init__(self, grid: List[List[int]]):
        """
        grid: 9x9 matrix, 0 = empty cell, 1-9 = given value.
        """
        if len(grid) != 9 or any(len(row) != 9 for row in grid):
            raise ValueError("Sudoku grid must be 9x9.")

        self.variables: List[Cell] = [(r, c) for r in range(9) for c in range(9)]

        # Domain: each cell -> set of still-possible values
        self.domains: Dict[Cell, Set[int]] = {}
        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0:
                    self.domains[(r, c)] = set(range(1, 10))
                else:
                    self.domains[(r, c)] = {grid[r][c]}

        # Precompute neighbors (cells sharing an all-different constraint) for each cell
        self._neighbors: Dict[Cell, Set[Cell]] = {
            cell: self._compute_neighbors(cell) for cell in self.variables
        }

    # ---------- Constraints ----------

    @staticmethod
    def _compute_neighbors(cell: Cell) -> Set[Cell]:
        r, c = cell
        neighbors = set()

        # Same row
        neighbors.update((r, cc) for cc in range(9) if cc != c)
        # Same column
        neighbors.update((rr, c) for rr in range(9) if rr != r)
        # Same 3x3 box
        box_r, box_c = (r // 3) * 3, (c // 3) * 3
        for rr in range(box_r, box_r + 3):
            for cc in range(box_c, box_c + 3):
                if (rr, cc) != (r, c):
                    neighbors.add((rr, cc))

        return neighbors

    def neighbors(self, cell: Cell) -> Set[Cell]:
        """Return the cells that share an all-different constraint with `cell`."""
        return self._neighbors[cell]

    def is_consistent(self, cell: Cell, value: int, assignment: Dict[Cell, int]) -> bool:
        """Check whether assigning `cell = value` violates a constraint with already-assigned cells."""
        for neighbor in self._neighbors[cell]:
            if assignment.get(neighbor) == value:
                return False
        return True

    # ---------- Assignment state ----------

    def is_complete(self, assignment: Dict[Cell, int]) -> bool:
        return len(assignment) == len(self.variables)

    def unassigned_variables(self, assignment: Dict[Cell, int]) -> List[Cell]:
        return [v for v in self.variables if v not in assignment]

    # ---------- Utilities ----------

    def to_grid(self, assignment: Dict[Cell, int]) -> List[List[int]]:
        """Convert an assignment (dict) back into a 9x9 matrix for printing/checking."""
        grid = [[0] * 9 for _ in range(9)]
        for (r, c), v in assignment.items():
            grid[r][c] = v
        return grid

    def initial_assignment(self) -> Dict[Cell, int]:
        """Cells with a given value (single-value domain) are treated as already assigned."""
        return {cell: next(iter(domain)) for cell, domain in self.domains.items() if len(domain) == 1}


def read_sudoku(file_path: str) -> List[List[int]]:
    """
    Read a Sudoku puzzle from a text file: 9 lines, 9 digits per line (0 = empty cell).
    Example line: 530070000
    """
    grid = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = [int(ch) for ch in line]
            if len(row) != 9:
                raise ValueError(f"Invalid line (expected 9 characters): {line}")
            grid.append(row)
    if len(grid) != 9:
        raise ValueError(f"File must contain 9 lines, found {len(grid)}.")
    return grid


def print_grid(grid: List[List[int]]) -> None:
    """Print the Sudoku grid to the console in a readable format."""
    for r in range(9):
        if r % 3 == 0 and r != 0:
            print("-" * 21)
        row_str = ""
        for c in range(9):
            if c % 3 == 0 and c != 0:
                row_str += "| "
            row_str += (str(grid[r][c]) if grid[r][c] != 0 else ".") + " "
        print(row_str)
