from __future__ import annotations

import sys
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

ANALYTICS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ANALYTICS_ROOT / "src"))

from mwg_dmx_analytics.data_io import load_financial_facts, load_source_documents
from mwg_dmx_analytics.validation import has_blocking_errors, validate_dataset


class ValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.facts = load_financial_facts(
            ANALYTICS_ROOT / "data" / "sample" / "financial_facts_sample.csv"
        )
        cls.sources = load_source_documents(
            ANALYTICS_ROOT / "data" / "sample" / "source_documents_sample.csv"
        )

    def test_sample_dataset_passes_blocking_checks(self) -> None:
        results = validate_dataset(self.facts, self.sources)
        self.assertFalse(has_blocking_errors(results))
        self.assertTrue(
            all(
                result.passed
                for result in results
                if result.check_code
                in {
                    "BALANCE_SHEET_EQUATION",
                    "GROSS_PROFIT_RECONCILIATION",
                    "CASH_FLOW_BRIDGE",
                    "ENDING_CASH_BALANCE_MATCH",
                }
            )
        )

    def test_balance_sheet_mismatch_is_blocking(self) -> None:
        changed = [
            replace(fact, value=Decimal("99999"))
            if fact.period_end.isoformat() == "2025-12-31" and fact.line_item == "total_assets"
            else fact
            for fact in self.facts
        ]
        failures = [
            result
            for result in validate_dataset(changed, self.sources)
            if result.check_code == "BALANCE_SHEET_EQUATION" and not result.passed
        ]
        self.assertEqual(len(failures), 1)
        self.assertTrue(has_blocking_errors(failures))

    def test_duplicate_fact_is_blocking(self) -> None:
        results = validate_dataset([*self.facts, self.facts[0]], self.sources)
        duplicate_check = next(
            result for result in results if result.check_code == "FACT_NATURAL_KEY_UNIQUE"
        )
        self.assertFalse(duplicate_check.passed)

    def test_synthetic_fact_must_be_explicitly_labeled(self) -> None:
        changed = [replace(self.facts[0], notes=""), *self.facts[1:]]
        results = validate_dataset(changed, self.sources)
        self.assertTrue(
            any(
                result.check_code == "SYNTHETIC_FACT_LABEL" and not result.passed
                for result in results
            )
        )


if __name__ == "__main__":
    unittest.main()
