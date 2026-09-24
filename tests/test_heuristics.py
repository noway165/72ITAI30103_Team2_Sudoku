import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

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


# Minimal stand-in for core.py, following docs/design.md.
def build_csp(rows):
    variables = [(r, c) for r in range(9) for c in range(9)]
    neighbors = {}
    for r, c in variables:
        br, bc = r // 3 * 3, c // 3 * 3
        peers = {(r, i) for i in range(9)} | {(i, c) for i in range(9)}
        peers |= {(br + i, bc + j) for i in range(3) for j in range(3)}
        peers.discard((r, c))
        neighbors[(r, c)] = peers
    domains, assignment = {}, {}
    for r, c in variables:
        v = int(rows[r][c])
        domains[(r, c)] = {v} if v else set(range(1, 10))
        if v:
            assignment[(r, c)] = v
    return SimpleNamespace(variables=variables, domains=domains, neighbors=neighbors), assignment


def solve_with_mrv(csp, assignment):
    if len(assignment) == len(csp.variables):
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
        csp, assignment = build_csp(DESIGN_EXAMPLE)
        self.assertEqual(sorted(legal_values(csp, (0, 2), assignment)), [1, 2, 4])


class MRVTest(unittest.TestCase):
    def test_picks_unassigned_variable_with_fewest_legal_values(self):
        csp, assignment = build_csp(DESIGN_EXAMPLE)
        var = mrv(csp, assignment)
        self.assertNotIn(var, assignment)
        fewest = min(
            len(legal_values(csp, v, assignment)) for v in csp.variables if v not in assignment
        )
        self.assertEqual(len(legal_values(csp, var, assignment)), fewest)

    def test_solves_every_puzzle_in_data(self):
        puzzles = sorted((ROOT / "data").glob("*.txt"))
        self.assertTrue(puzzles)
        for path in puzzles:
            with self.subTest(puzzle=path.name):
                rows = path.read_text().split()
                csp, assignment = build_csp(rows)
                clues = dict(assignment)
                solution = solve_with_mrv(csp, assignment)
                self.assertIsNotNone(solution)
                self.assertTrue(clues.items() <= solution.items())
                for var, value in solution.items():
                    for n in csp.neighbors[var]:
                        self.assertNotEqual(value, solution[n])


if __name__ == "__main__":
    unittest.main()
