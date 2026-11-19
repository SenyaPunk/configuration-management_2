import tempfile
import unittest
from pathlib import Path

from src.dependency_visualizer.source import SourceError, load_test_graph


class SourceTests(unittest.TestCase):
    def test_loads_csv_graph(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "graph.csv"
            path.write_text("A,B,C\nB,D\nC\n", encoding="utf-8")
            self.assertEqual(load_test_graph(path), {
                "A": ["B", "C"], "B": ["D"], "C": [], "D": []
            })

    def test_loads_colon_graph(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "graph.csv"
            path.write_text("A: B,C\n", encoding="utf-8")
            self.assertEqual(load_test_graph(path)["A"], ["B", "C"])

    def test_rejects_lowercase_names(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "graph.csv"
            path.write_text("a,B\n", encoding="utf-8")
            with self.assertRaises(SourceError):
                load_test_graph(path)

    def test_rejects_missing_graph(self):
        with self.assertRaises(SourceError):
            load_test_graph("missing.csv")

    def test_rejects_empty_duplicate_and_malformed_graphs(self):
        cases = (
            ("\n , \n", "граф пуст"),
            ("A,B\nA,C\n", "задан повторно"),
            ("A,B\n,B\n", "строка 2"),
        )
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "graph.csv"
            for text, message in cases:
                with self.subTest(text=text):
                    path.write_text(text, encoding="utf-8")
                    with self.assertRaisesRegex(SourceError, message):
                        load_test_graph(path)

    def test_skips_blank_rows_and_preserves_cycles(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "graph.csv"
            path.write_text("\n , \nA,B\nB,A\n", encoding="utf-8")
            self.assertEqual(load_test_graph(path), {
                "A": ["B"], "B": ["A"]
            })


if __name__ == "__main__":
    unittest.main()
