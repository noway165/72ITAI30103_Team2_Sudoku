import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from backtracking import BacktrackingSolver  # noqa: E402
from core import CSP, read_sudoku  # noqa: E402
from heuristics import legal_values, mrv  # noqa: E402

PUZZLES = sorted((ROOT / "data").glob("*.txt"))


def assert_valid_solution(test, csp, clues, solution):
    test.assertIsNotNone(solution)
    test.assertTrue(csp.is_complete(solution))
    test.assertTrue(clues.items() <= solution.items())
    for var, value in solution.items():
        for n in csp.neighbors(var):
            test.assertNotEqual(value, solution[n])


def simple_forward_checking(csp, var, value, assignment):
    """Minimal inference hook used only to test the solver's hook contract."""
    removals = []
    for n in csp.neighbors(var):
        if n not in assignment and value in csp.domains[n]:
            csp.domains[n].discard(value)
            removals.append((n, value))
    return removals


def unsolvable_grid():
    """Clues are consistent, but cells (0, 0) and (0, 1) would both have to be 9."""
    grid = [[0] * 9 for _ in range(9)]
    grid[0] = [0, 0, 1, 2, 3, 4, 5, 6, 7]
    grid[3][0] = 8
    grid[6][1] = 8
    return grid


class BaselineTest(unittest.TestCase):
    def test_solves_every_puzzle_in_data(self):
        self.assertTrue(PUZZLES)
        for path in PUZZLES:
            with self.subTest(puzzle=path.name):
                csp = CSP(read_sudoku(str(path)))
                clues = csp.initial_assignment()
                solver = BacktrackingSolver(csp)
                assert_valid_solution(self, csp, clues, solver.solve())
                self.assertGreater(solver.nodes_explored, 0)

    def test_returns_none_for_unsolvable_puzzle(self):
        csp = CSP(unsolvable_grid())
        self.assertIsNone(BacktrackingSolver(csp).solve())

    def test_returns_none_when_clues_conflict(self):
        grid = [[0] * 9 for _ in range(9)]
        grid[0][0] = 1
        grid[1][1] = 1  # two 1s in the same 3x3 box
        self.assertIsNone(BacktrackingSolver(CSP(grid)).solve())


class HookTest(unittest.TestCase):
    def test_works_with_mrv_from_heuristics(self):
        for path in PUZZLES:
            with self.subTest(puzzle=path.name):
                csp = CSP(read_sudoku(str(path)))
                clues = csp.initial_assignment()
                solver = BacktrackingSolver(csp, select_var=mrv, order_values=legal_values)
                assert_valid_solution(self, csp, clues, solver.solve())

    def test_inference_hook_solves_and_restores_domains_on_failure(self):
        for path in PUZZLES:
            with self.subTest(puzzle=path.name):
                csp = CSP(read_sudoku(str(path)))
                clues = csp.initial_assignment()
                solver = BacktrackingSolver(csp, inference=simple_forward_checking)
                assert_valid_solution(self, csp, clues, solver.solve())

    def test_domains_unchanged_after_failed_search(self):
        csp = CSP(unsolvable_grid())
        before = copy.deepcopy(csp.domains)
        self.assertIsNone(BacktrackingSolver(csp, inference=simple_forward_checking).solve())
        self.assertEqual(csp.domains, before)


if __name__ == "__main__":
    unittest.main()
