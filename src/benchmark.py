import argparse
import csv
import statistics
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional

from backtracking import BacktrackingSolver
from core import CSP, read_sudoku
from heuristics import legal_values, mrv
from pruning import ac3, ac3_inference, forward_checking, propagate_clues

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
DIFFICULTIES = ["easy", "medium", "hard"]


def _baseline(csp: CSP) -> BacktrackingSolver:
    return BacktrackingSolver(csp)


def _mrv(csp: CSP) -> BacktrackingSolver:
    return BacktrackingSolver(csp, select_var=mrv, order_values=legal_values)


def _mrv_fc(csp: CSP) -> Optional[BacktrackingSolver]:
    # Forward checking only helps if the clues are propagated first
    if not propagate_clues(csp):
        return None
    return BacktrackingSolver(csp, select_var=mrv, order_values=legal_values, inference=forward_checking)


def _mrv_ac3(csp: CSP) -> Optional[BacktrackingSolver]:
    # Full AC-3 once before solving, then maintain arc consistency during search
    if not ac3(csp):
        return None
    return BacktrackingSolver(csp, select_var=mrv, order_values=legal_values, inference=ac3_inference)


# Each configuration builds a solver from a fresh CSP (preprocessing included).
CONFIGS: Dict[str, Callable[[CSP], Optional[BacktrackingSolver]]] = {
    "Backtracking": _baseline,
    "MRV": _mrv,
    "MRV+FC": _mrv_fc,
    "MRV+AC3": _mrv_ac3,
}


def is_valid_solution(csp: CSP, clues: Dict, solution: Optional[Dict]) -> bool:
    if solution is None or not csp.is_complete(solution):
        return False
    if any(solution[cell] != value for cell, value in clues.items()):
        return False
    return all(solution[v] != solution[n] for v in solution for n in csp.neighbors(v))


def run_once(puzzle: Path, build: Callable[[CSP], Optional[BacktrackingSolver]]) -> Dict:
    """Solve one puzzle with one configuration. Time includes preprocessing."""
    csp = CSP(read_sudoku(str(puzzle)))
    clues = csp.initial_assignment()
    start = time.perf_counter()
    solver = build(csp)
    solution = solver.solve() if solver is not None else None
    elapsed = time.perf_counter() - start
    return {
        "nodes": solver.nodes_explored if solver else 0,
        "backtracks": solver.backtracks if solver else 0,
        "time": elapsed,
        "success": is_valid_solution(csp, clues, solution),
    }


def run_benchmark(puzzles: List[Path], repeats: int = 3) -> List[Dict]:
    """Run every configuration on every puzzle. Time is the median of `repeats` runs
    (node and backtrack counts are deterministic)."""
    rows = []
    for puzzle in puzzles:
        difficulty = puzzle.stem.split("_")[0]
        for name, build in CONFIGS.items():
            runs = [run_once(puzzle, build) for _ in range(repeats)]
            rows.append({
                "puzzle": puzzle.stem,
                "difficulty": difficulty,
                "config": name,
                "nodes": runs[0]["nodes"],
                "backtracks": runs[0]["backtracks"],
                "time_s": round(statistics.median(r["time"] for r in runs), 6),
                "success": all(r["success"] for r in runs),
            })
    return rows


def summarize(rows: List[Dict]) -> List[Dict]:
    """Average nodes / backtracks / time per difficulty and configuration."""
    summary = []
    for difficulty in DIFFICULTIES:
        for name in CONFIGS:
            group = [r for r in rows if r["difficulty"] == difficulty and r["config"] == name]
            if not group:
                continue
            summary.append({
                "difficulty": difficulty,
                "config": name,
                "puzzles": len(group),
                "avg_nodes": round(statistics.mean(r["nodes"] for r in group), 1),
                "avg_backtracks": round(statistics.mean(r["backtracks"] for r in group), 1),
                "avg_time_s": round(statistics.mean(r["time_s"] for r in group), 6),
                "success_rate": round(sum(r["success"] for r in group) / len(group), 2),
            })
    return summary


def write_csv(rows: List[Dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_summary(summary: List[Dict], path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    configs = list(CONFIGS)
    difficulties = [d for d in DIFFICULTIES if any(s["difficulty"] == d for s in summary)]
    width = 0.8 / len(configs)

    fig, ax = plt.subplots(figsize=(9, 5))
    for i, name in enumerate(configs):
        values = [
            next(s["avg_nodes"] for s in summary if s["difficulty"] == d and s["config"] == name)
            for d in difficulties
        ]
        positions = [x + (i - (len(configs) - 1) / 2) * width for x in range(len(difficulties))]
        bars = ax.bar(positions, [max(v, 1) for v in values], width, label=name)
        for bar, v in zip(bars, values):
            ax.annotate(f"{v:,.0f}", (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        ha="center", va="bottom", fontsize=8)

    ax.set_yscale("log")
    ax.set_xticks(range(len(difficulties)))
    ax.set_xticklabels([d.capitalize() for d in difficulties])
    ax.set_ylabel("Average nodes explored (log scale)")
    ax.set_title("Sudoku CSP: average nodes explored by configuration")
    ax.legend()
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def print_summary(summary: List[Dict]) -> None:
    print(f"{'Difficulty':<10} {'Config':<13} {'Avg nodes':>12} {'Avg time (s)':>13} {'Success':>8}")
    for s in summary:
        print(f"{s['difficulty']:<10} {s['config']:<13} {s['avg_nodes']:>12,.1f} "
              f"{s['avg_time_s']:>13.4f} {s['success_rate']:>8.0%}")


def main():
    parser = argparse.ArgumentParser(description="Benchmark Sudoku CSP solver configurations.")
    parser.add_argument("--data", default=str(DATA_DIR), help="Folder with puzzle .txt files")
    parser.add_argument("--out", default=str(RESULTS_DIR), help="Folder to write results into")
    parser.add_argument("--repeats", type=int, default=3, help="Runs per puzzle/config for timing")
    args = parser.parse_args()

    puzzles = sorted(Path(args.data).glob("*.txt"))
    rows = run_benchmark(puzzles, repeats=args.repeats)
    summary = summarize(rows)

    out = Path(args.out)
    write_csv(rows, out / "benchmark.csv")
    write_csv(summary, out / "summary.csv")
    plot_summary(summary, out / "nodes_by_difficulty.png")

    print_summary(summary)
    print(f"\nSaved: {out / 'benchmark.csv'}, {out / 'summary.csv'}, {out / 'nodes_by_difficulty.png'}")


if __name__ == "__main__":
    main()
