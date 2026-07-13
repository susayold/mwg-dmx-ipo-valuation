from __future__ import annotations

import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class PortfolioProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with (ROOT / "data" / "source_registry.csv").open(
            "r", encoding="utf-8-sig", newline=""
        ) as handle:
            cls.registry = {row["source_id"]: row for row in csv.DictReader(handle)}
        cls.case_data = (ROOT / "app" / "data" / "case-data.ts").read_text(
            encoding="utf-8"
        )
        cls.memo = (ROOT / "reports" / "RESEARCH_REPORT.md").read_text(
            encoding="utf-8"
        )
        cls.index_html = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_public_primary_links_are_registered_canonical_urls(self) -> None:
        source_ids = [
            "DMX_IPO_RESULT_2026",
            "DMX_DATA_2026Q1",
            "DMX_RESULTS_2026H1",
            "DMX_IPO_PRESENTATION_2026",
            "MWG_AR_2025",
        ]
        for source_id in source_ids:
            with self.subTest(source_id=source_id):
                row = self.registry[source_id]
                self.assertIn(source_id, self.case_data)
                self.assertIn(row["direct_url"], self.case_data)
                self.assertIn(row["direct_url"], self.memo)
                self.assertIn(row["direct_url"], self.index_html)

    def test_ownership_and_lfl_labels_are_explicit(self) -> None:
        self.assertIn('mwgOwnershipDisclosure: "nearly 86%"', self.case_data)
        self.assertIn("mwgOwnershipModelApproxPct", self.case_data)
        self.assertIn("management_lfl_actual", self.case_data)
        self.assertIn("issuer operating update; unaudited", self.case_data)
        self.assertIn("stated like-for-like basis", self.case_data)
        self.assertNotIn("~85.9%", self.case_data)
        self.assertIn("nearly 86%", self.index_html)
        self.assertIn("~86% model approximation", self.index_html)
        self.assertIn("issuer operating update; unaudited", self.index_html)
        self.assertIn("management-adjusted like-for-like", self.index_html)
        self.assertNotIn("85.9%", self.index_html)


if __name__ == "__main__":
    unittest.main()
