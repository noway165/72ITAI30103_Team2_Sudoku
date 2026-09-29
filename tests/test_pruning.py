import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from backtracking import BacktrackingSolver  # noqa: E402
from core import CSP, read_sudoku  # noqa: E402
from heuristics import legal_values, mrv  # noqa: E402
from pruning import ac3, ac3_inference, forward_checking, propagate_clues, revise  # noqa: E402

PUZZLES = sorted((ROOT / "data").glob("*.txt"))
EASY = ROOT / "data" / "easy_01.txt"


def unsolvable_grid():
    """Clues are consistent, but cells (0, 0) and (0, 1) would both have to be 9."""
    grid = [[0] * 9 for _ in range(9)]
    grid[0] = [0, 0, 1, 2, 3, 4, 5, 6, 7]
    grid[3][0] = 8
    grid[6][1] = 8
    return grid


def assert_valid(test, csp, clues, solution):
    test.assertIsNotNone(solution)
    test.assertTrue(csp.is_complete(solution))
    test.assertTrue(clues.items() <= solution.items())
    for var, value in solution.items():
        for n in csp.neighbors(var):
            test.assertNotEqual(value, solution[n])


class ForwardCheckingTest(unittest.TestCase):
    def test_removes_value_from_unassigned_neighbors_only(self):
        csp = CSP(read_sudoku(str(EASY)))
        assignment = csp.initial_assignment()
        var = next(v for v in csp.variables if v not in assignment)
        assignment[var] = 7
        removals = forward_checking(csp, var, 7, assignment)
        self.assertTrue(removals)
        for cell, value in removals:
            self.assertEqual(value, 7)
            self.assertIn(cell, csp.neighbors(var))
            self.assertNotIn(cell, assignment)
            self.assertNotIn(7, csp.domains[cell])

    def test_wipeout_leaves_an_empty_domain_in_removals(self):
        grid = [[0] * 9 for _ in range(9)]
        csp = CSP(grid)
        csp.domains[(0, 1)] = {5}
        removals = forward_checking(csp, (0, 0), 5, {(0, 0): 5})
        self.assertIn(((0, 1), 5), removals)
        self.assertEqual(csp.domains[(0, 1)], set())

    def test_solves_every_puzzle(self):
        for path in PUZZLES:
            with self.subTest(puzzle=path.name):
                csp = CSP(read_sudoku(str(path)))
                clues = csp.initial_assignment()
                solver = BacktrackingSolver(
                    csp, select_var=mrv, order_values=legal_values, inference=forward_checking
                )
                assert_valid(self, csp, clues, solver.solve())


class Ac3Test(unittest.TestCase):
    def test_revise_removes_value_fixed_in_neighbor(self):
        csp = CSP([[0] * 9 for _ in range(9)])
        csp.domains[(0, 1)] = {4}
        removals = []
        self.assertTrue(revise(csp, (0, 0), (0, 1), removals))
        self.assertEqual(removals, [((0, 0), 4)])
        self.assertNotIn(4, csp.domains[(0, 0)])

    def test_revise_keeps_domain_when_neighbor_has_two_values(self):
        csp = CSP([[0] * 9 for _ in range(9)])
        csp.domains[(0, 1)] = {4, 5}
        self.assertFalse(revise(csp, (0, 0), (0, 1), []))
        self.assertEqual(csp.domains[(0, 0)], set(range(1, 10)))

    def test_ac3_preprocessing_shrinks_domains_and_keeps_solution(self):
        csp = CSP(read_sudoku(str(EASY)))
        before = sum(len(d) for d in csp.domains.values())
        clues = csp.initial_assignment()
        self.assertTrue(ac3(csp))
        self.assertLess(sum(len(d) for d in csp.domains.values()), before)
        assert_valid(self, csp, clues, BacktrackingSolver(csp, inference=ac3_inference).solve())

    def test_ac3_detects_unsolvable_puzzle(self):
        self.assertFalse(ac3(CSP(unsolvable_grid())))

    def test_solves_every_puzzle_with_and_without_preprocessing(self):
        for path in PUZZLES:
            for pre in (False, True):
                with self.subTest(puzzle=path.name, preprocess=pre):
                    csp = CSP(read_sudoku(str(path)))
                    clues = csp.initial_assignment()
                    if pre:
                        self.assertTrue(ac3(csp))
                    solver = BacktrackingSolver(
                        csp, select_var=mrv, order_values=legal_values, inference=ac3_inference
                    )
                    assert_valid(self, csp, clues, solver.solve())


class RestoreTest(unittest.TestCase):
    def test_domains_unchanged_after_failed_search(self):
        for hook in (forward_checking, ac3_inference):
            with self.subTest(hook=hook.__name__):
                csp = CSP(unsolvable_grid())
                before = copy.deepcopy(csp.domains)
                self.assertIsNone(BacktrackingSolver(csp, inference=hook).solve())
                self.assertEqual(csp.domains, before)

    def test_propagate_clues_on_valid_puzzle(self):
        self.assertTrue(propagate_clues(CSP(read_sudoku(str(EASY)))))


if __name__ == "__main__":
    unittest.main()
