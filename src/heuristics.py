"""Variable/value ordering heuristics for the Sudoku CSP (AIMA 6.3.1).

Works on `core.CSP` and an assignment dict (row, col) -> int.
"""


def legal_values(csp, var, assignment):
    used = {assignment[n] for n in csp.neighbors(var) if n in assignment}
    return [v for v in csp.domains[var] if v not in used]


def mrv(csp, assignment):
    """Minimum Remaining Values: pick the unassigned variable with the fewest legal values."""
    return min(
        csp.unassigned_variables(assignment),
        key=lambda v: len(legal_values(csp, v, assignment)),
    )
