from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path

ANALYTICS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ANALYTICS_ROOT / "src"))

from mwg_dmx_analytics.data_io import load_financial_facts
from mwg_dmx_analytics.ratios import calculate_ratios


class RatioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.facts = load_financial_facts(
            ANALYTICS_ROOT / "data" / "sample" / "financial_facts_sample.csv"
        )

    def test_growth_margins_and_cash_flow(self) -> None:
        report = calculate_ratios(
            self.facts,
            entity_code="SYNTH_MWG_GROUP",
            period_end="2025-12-31",
        )
        self.assertEqual(report.prior_period_end.isoformat(), "2024-12-31")
        self.assertEqual(report.metrics["revenue_growth"], Decimal("0.15"))
        self.assertEqual(report.metrics["gross_margin"], Decimal("0.23"))
        self.assertEqual(report.metrics["free_cash_flow"], Decimal("5000"))
        self.assertEqual(
            report.metrics["free_cash_flow_margin"], Decimal("5000") / Decimal("115000")
        )

    def test_returns_use_average_balance_sheet_values(self) -> None:
        report = calculate_ratios(
            self.facts,
            entity_code="SYNTH_MWG_GROUP",
            period_end="2025-12-31",
        )
        expected_roe = Decimal("5720") / Decimal("33000")
        expected_roa = Decimal("5720") / Decimal("85000")
        self.assertEqual(report.metrics["return_on_equity"], expected_roe)
        self.assertEqual(report.metrics["return_on_assets"], expected_roa)

    def test_working_capital_cycle_is_reconciled(self) -> None:
        report = calculate_ratios(
            self.facts,
            entity_code="SYNTH_MWG_GROUP",
            period_end="2025-12-31",
        )
        expected = (
            report.metrics["days_sales_outstanding"]
            + report.metrics["days_inventory_outstanding"]
            - report.metrics["days_payables_outstanding"]
        )
        self.assertEqual(report.metrics["cash_conversion_cycle"], expected)

    def test_unknown_entity_raises(self) -> None:
        with self.assertRaises(ValueError):
            calculate_ratios(
                self.facts,
                entity_code="NOT_FOUND",
                period_end="2025-12-31",
            )


if __name__ == "__main__":
    unittest.main()
