import argparse
import time
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from core import CSP, Cell, print_grid, read_sudoku

Assignment = Dict[Cell, int]

# Hook signatures (so heuristics / pruning can be plugged in without changing the solver):
#   select_var(csp, assignment) -> Cell
#   order_values(csp, var, assignment) -> Iterable[int]
#   inference(csp, var, value, assignment) -> list of (cell, removed_value) it removed from domains.
#       The solver restores these values when backtracking and treats an emptied domain as a dead end.
#       Returning None also means failure (the hook must then leave the domains unchanged).
SelectVar = Callable[[CSP, Assignment], Cell]
OrderValues = Callable[[CSP, Cell, Assignment], Iterable[int]]
Inference = Callable[[CSP, Cell, int, Assignment], Optional[List[Tuple[Cell, int]]]]


def first_unassigned(csp: CSP, assignment: Assignment) -> Cell:
    """Baseline: pick the first unassigned cell in fixed (row, col) order."""
    for var in csp.variables:
        if var not in assignment:
            return var
    raise RuntimeError("No unassigned variable left.")


def ascending_values(csp: CSP, var: Cell, assignment: Assignment) -> Iterable[int]:
    """Baseline: try values of the current domain in ascending order."""
    return sorted(csp.domains[var])


class BacktrackingSolver:
    """Backtracking search for the Sudoku CSP.

    Statistics collected after solve() (used by the benchmark):
        nodes_explored: number of consistent assignments made (search tree nodes)
        backtracks:     number of assignments that had to be undone
        elapsed:        wall-clock solving time in seconds
    """

    def __init__(
        self,
        csp: CSP,
        select_var: SelectVar = first_unassigned,
        order_values: OrderValues = ascending_values,
        inference: Optional[Inference] = None,
    ):
        self.csp = csp
        self.select_var = select_var
        self.order_values = order_values
        self.inference = inference
        self.nodes_explored = 0
        self.backtracks = 0
        self.elapsed = 0.0

    def solve(self) -> Optional[Assignment]:
        """Return a complete assignment, or None if the puzzle has no solution."""
        self.nodes_explored = 0
        self.backtracks = 0
        start = time.perf_counter()
        clues = self.csp.initial_assignment()
        result = self._backtrack(clues) if self._clues_consistent(clues) else None
        self.elapsed = time.perf_counter() - start
        return result

    def _clues_consistent(self, clues: Assignment) -> bool:
        """Given values must not conflict with each other (e.g. two 5s in one row)."""
        return all(
            clues.get(n) != value for var, value in clues.items() for n in self.csp.neighbors(var)
        )

    def _backtrack(self, assignment: Assignment) -> Optional[Assignment]:
        if self.csp.is_complete(assignment):
            return assignment

        var = self.select_var(self.csp, assignment)

        for value in list(self.order_values(self.csp, var, assignment)):
            if not self.csp.is_consistent(var, value, assignment):
                continue

            assignment[var] = value
            self.nodes_explored += 1

            removals: Optional[List[Tuple[Cell, int]]] = []
            if self.inference is not None:
                removals = self.inference(self.csp, var, value, assignment)

            if removals is not None:
                dead_end = any(not self.csp.domains[cell] for cell, _ in removals)
                if not dead_end:
                    result = self._backtrack(assignment)
                    if result is not None:
                        return result
                self._restore(removals)

            # Undo this assignment and try the next value
            del assignment[var]
            self.backtracks += 1

        return None

    def _restore(self, removals: List[Tuple[Cell, int]]) -> None:
        """Put back domain values removed by the inference step."""
        for cell, value in removals:
            self.csp.domains[cell].add(value)


def main():
    parser = argparse.ArgumentParser(description="Solve a Sudoku with baseline backtracking search.")
    parser.add_argument("--input", required=True, help="Path to a Sudoku puzzle file (.txt)")
    args = parser.parse_args()

    grid = read_sudoku(args.input)
    print("Puzzle:")
    print_grid(grid)

    csp = CSP(grid)
    solver = BacktrackingSolver(csp)
    solution = solver.solve()

    print("\nResult:")
    if solution is None:
        print("No solution found.")
    else:
        print_grid(csp.to_grid(solution))

    print(f"\nNodes explored: {solver.nodes_explored}")
    print(f"Backtracks:     {solver.backtracks}")
    print(f"Time:           {solver.elapsed:.4f} s")


if __name__ == "__main__":
    main()
