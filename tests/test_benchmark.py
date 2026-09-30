import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from benchmark import CONFIGS, run_benchmark, summarize, write_csv  # noqa: E402

PUZZLES = sorted((ROOT / "data").glob("*.txt"))


class BenchmarkTest(unittest.TestCase):
    def test_every_config_solves_every_puzzle(self):
        rows = run_benchmark(PUZZLES, repeats=1)
        self.assertEqual(len(rows), len(PUZZLES) * len(CONFIGS))
        for row in rows:
            with self.subTest(puzzle=row["puzzle"], config=row["config"]):
                self.assertTrue(row["success"])

    def test_heuristics_explore_fewer_nodes_than_baseline_on_hard(self):
        summary = summarize(run_benchmark([p for p in PUZZLES if p.stem.startswith("hard")], repeats=1))
        nodes = {s["config"]: s["avg_nodes"] for s in summary}
        self.assertLess(nodes["MRV"], nodes["Backtracking"])
        self.assertLess(nodes["MRV+AC3"], nodes["Backtracking"])

    def test_write_csv(self):
        rows = run_benchmark(PUZZLES[:1], repeats=1)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "out.csv"
            write_csv(rows, path)
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), len(rows) + 1)
            self.assertTrue(lines[0].startswith("puzzle,difficulty,config"))


if __name__ == "__main__":
    unittest.main()
