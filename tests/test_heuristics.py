import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from core import CSP, read_sudoku  # noqa: E402
from heuristics import legal_values, mrv  # noqa: E402

DESIGN_EXAMPLE = [
    "530070000",
    "600195000",
    "098000060",
    "800060003",
    "400803001",
    "700020006",
    "060000280",
    "000419005",
    "000080079",
]


def solve_with_mrv(csp, assignment):
    if csp.is_complete(assignment):
        return assignment
    var = mrv(csp, assignment)
    for value in legal_values(csp, var, assignment):
        assignment[var] = value
        if solve_with_mrv(csp, assignment):
            return assignment
        del assignment[var]
    return None


class LegalValuesTest(unittest.TestCase):
    def test_excludes_values_of_assigned_neighbors(self):
        csp = CSP([[int(ch) for ch in row] for row in DESIGN_EXAMPLE])
        self.assertEqual(sorted(legal_values(csp, (0, 2), csp.initial_assignment())), [1, 2, 4])


class MRVTest(unittest.TestCase):
    def test_picks_unassigned_variable_with_fewest_legal_values(self):
        csp = CSP([[int(ch) for ch in row] for row in DESIGN_EXAMPLE])
        assignment = csp.initial_assignment()
        var = mrv(csp, assignment)
        self.assertNotIn(var, assignment)
        fewest = min(
            len(legal_values(csp, v, assignment)) for v in csp.unassigned_variables(assignment)
        )
        self.assertEqual(len(legal_values(csp, var, assignment)), fewest)

    def test_solves_every_puzzle_in_data(self):
        puzzles = sorted((ROOT / "data").glob("*.txt"))
        self.assertTrue(puzzles)
        for path in puzzles:
            with self.subTest(puzzle=path.name):
                csp = CSP(read_sudoku(str(path)))
                clues = csp.initial_assignment()
                solution = solve_with_mrv(csp, dict(clues))
                self.assertIsNotNone(solution)
                self.assertTrue(clues.items() <= solution.items())
                for var, value in solution.items():
                    for n in csp.neighbors(var):
                        self.assertNotEqual(value, solution[n])


if __name__ == "__main__":
    unittest.main()
