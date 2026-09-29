"""Pruning (constraint propagation) for the Sudoku CSP (AIMA 6.2) - Khoa.

Two inference hooks that plug into `BacktrackingSolver(..., inference=...)`:

    forward_checking(csp, var, value, assignment)
    ac3_inference(csp, var, value, assignment)      # a.k.a. MAC (maintaining arc consistency)

Hook contract (see backtracking.py): after `var = value` is assigned, the hook
removes values from domains and returns the list of (cell, removed_value) it
removed. The solver restores them on backtracking and treats any emptied domain
as a dead end, so a hook that hits a wipe-out simply returns the removals so far.

Also provided (optional, permanent, run once before solving):

    ac3(csp)  ->  bool     # full AC-3 over all arcs; False if some domain became empty
"""

from collections import deque
from typing import Dict, Iterable, List, Optional, Tuple

from core import CSP, Cell

Assignment = Dict[Cell, int]
Removals = List[Tuple[Cell, int]]
Arc = Tuple[Cell, Cell]


# ---------------------------------------------------------------- Forward Checking

def forward_checking(csp: CSP, var: Cell, value: int, assignment: Assignment) -> Removals:
    """After `var = value`, delete `value` from the domain of every unassigned neighbor.

    Stops early on a wipe-out (a neighbor left with an empty domain); the solver
    detects the empty domain in the returned removals and backtracks.
    """
    removals: Removals = []
    for neighbor in csp.neighbors(var):
        if neighbor in assignment:
            continue
        domain = csp.domains[neighbor]
        if value in domain:
            domain.discard(value)
            removals.append((neighbor, value))
            if not domain:
                break
    return removals


# ---------------------------------------------------------------------------- AC-3

def revise(csp: CSP, xi: Cell, xj: Cell, removals: Removals) -> bool:
    """Make xi arc-consistent with xj for the all-different constraint.

    A value x in D(xi) has no support iff D(xj) contains nothing other than x,
    so with |D(xj)| == 1 only that single value can be removed.
    Removed values are appended to `removals`. Returns True if D(xi) changed.
    """
    dj = csp.domains[xj]
    if len(dj) > 1:  # any x has a different y in D(xj): nothing to remove
        return False
    di = csp.domains[xi]
    unsupported = [x for x in di if not any(y != x for y in dj)]
    for x in unsupported:
        di.discard(x)
        removals.append((xi, x))
    return bool(unsupported)


def _propagate(csp: CSP, queue: "deque[Arc]", removals: Removals) -> bool:
    """AC-3 main loop. Returns False on wipe-out (removals hold everything removed so far)."""
    while queue:
        xi, xj = queue.popleft()
        if revise(csp, xi, xj, removals):
            if not csp.domains[xi]:
                return False
            for xk in csp.neighbors(xi):
                if xk != xj:
                    queue.append((xk, xi))
    return True


def ac3_inference(csp: CSP, var: Cell, value: int, assignment: Assignment) -> Removals:
    """MAC: fix D(var) = {value}, then propagate arc consistency from var's neighbors."""
    removals: Removals = []
    for other in list(csp.domains[var]):
        if other != value:
            csp.domains[var].discard(other)
            removals.append((var, other))
    if value not in csp.domains[var]:  # value was not even in the domain -> dead end
        return removals
    queue: "deque[Arc]" = deque((n, var) for n in csp.neighbors(var))
    _propagate(csp, queue, removals)
    return removals


def ac3(csp: CSP, arcs: Optional[Iterable[Arc]] = None) -> bool:
    """Full AC-3 (AIMA Fig. 6.3) as a one-off preprocessing step; changes domains permanently.

    Returns False if some domain becomes empty (puzzle has no solution).
    """
    if arcs is None:
        arcs = [(xi, xj) for xi in csp.variables for xj in csp.neighbors(xi)]
    return _propagate(csp, deque(arcs), [])


# --------------------------------------------------------------------- convenience

def propagate_clues(csp: CSP) -> bool:
    """Forward-check every given clue once (permanent). Returns False on wipe-out.

    The solver never calls `inference` for the initial clues, so run this before
    solving if you want forward checking to also use the clues.
    """
    clues = csp.initial_assignment()
    for cell, value in clues.items():
        for neighbor in csp.neighbors(cell):
            if neighbor not in clues:
                csp.domains[neighbor].discard(value)
                if not csp.domains[neighbor]:
                    return False
    return True
