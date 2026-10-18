import unittest
from ebook_worker import summarize_scan


class ScannerSummaryTests(unittest.TestCase):
    def test_extracts_counts_without_excerpt_text(self):
        sample = """=== NOT-X-BUT-Y: 18 hits ===
  [CHAPTER ONE#1] ...PRIVATE MANUSCRIPT EXCERPT...
=== CATALOGUED: 11 hits ===
Total paragraphs scanned: 828
"""
        result = summarize_scan(sample)
        self.assertEqual(result["paragraphs_scanned"], 828)
        self.assertEqual(result["heuristic_counts"]["NOT-X-BUT-Y"], 18)
        self.assertNotIn("PRIVATE MANUSCRIPT EXCERPT", str(result))

    def test_rejects_unexpected_scanner_output(self):
        with self.assertRaises(RuntimeError):
            summarize_scan("scanner output changed")


if __name__ == "__main__":
    unittest.main()
