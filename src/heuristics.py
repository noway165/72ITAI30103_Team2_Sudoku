"""Variable/value ordering heuristics for the Sudoku CSP (AIMA 6.3.1).

Expects a `csp` object exposing:
    variables  -- list of (row, col)
    domains    -- dict (row, col) -> iterable of int
    neighbors  -- dict (row, col) -> iterable of (row, col)
and `assignment` as dict (row, col) -> int.
"""


def legal_values(csp, var, assignment):
    used = {assignment[n] for n in csp.neighbors[var] if n in assignment}
    return [v for v in csp.domains[var] if v not in used]


def mrv(csp, assignment):
    """Minimum Remaining Values: pick the unassigned variable with the fewest legal values."""
    unassigned = [v for v in csp.variables if v not in assignment]
    return min(unassigned, key=lambda v: len(legal_values(csp, v, assignment)))
