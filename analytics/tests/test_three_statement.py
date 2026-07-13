from __future__ import annotations

import sys
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

ANALYTICS_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ANALYTICS_ROOT.parent
sys.path.insert(0, str(ANALYTICS_ROOT / "src"))

from mwg_dmx_analytics.data_io import load_financial_facts, load_source_documents
from mwg_dmx_analytics.three_statement import (
    ThreeStatementAnalysisError,
    build_three_statement_analysis,
)
from mwg_dmx_analytics.validation import validate_dataset, validation_summary


class ThreeStatementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.facts = load_financial_facts(
            REPO_ROOT / "data" / "processed" / "dmx_three_statement_facts.csv"
        )
        cls.sources = load_source_documents(
            REPO_ROOT / "data" / "processed" / "dmx_three_statement_sources.csv"
        )
        cls.analysis = build_three_statement_analysis(
            cls.facts,
            normalization_path=REPO_ROOT
            / "data"
            / "processed"
            / "dmx_normalization_adjustments.csv",
        )

    def test_source_lineage_and_generic_validation_are_clean(self) -> None:
        summary = validation_summary(validate_dataset(self.facts, self.sources))
        self.assertTrue(summary["is_valid"])
        self.assertEqual(summary["failed_errors"], 0)
        self.assertEqual(summary["failed_warnings"], 0)

    def test_all_mandatory_accounting_controls_exist_and_pass(self) -> None:
        summary = self.analysis["check_summary"]
        self.assertGreaterEqual(summary["checks"], 30)
        self.assertEqual(summary["checks"], summary["passed"])
        self.assertEqual(summary["failed"], 0)
        codes = {check["check_code"] for check in self.analysis["accounting_checks"]}
        self.assertTrue(
            {
                "CHK_BALANCE_SHEET",
                "CHK_GROSS_PROFIT",
                "CHK_PBT_NPAT_TAX",
                "CHK_CFO_INDIRECT_BRIDGE",
                "CHK_CASH_ROLL",
                "CHK_CFS_TO_BS_CASH",
                "CHK_INVENTORY_NET",
                "CHK_RETAINED_EARNINGS_RESIDUAL_RECONCILIATION",
            }
            <= codes
        )

    def test_period_day_convention_uses_actual_calendar_days(self) -> None:
        schedule = {row["period"]: row for row in self.analysis["working_capital"]}
        self.assertEqual(schedule["FY2024A"]["period_days"], Decimal("366"))
        self.assertEqual(schedule["FY2025A"]["period_days"], Decimal("365"))
        self.assertEqual(schedule["Q1 2026A"]["period_days"], Decimal("90"))
        self.assertTrue(schedule["Q1 2026A"]["q1_seasonality_warning"])

    def test_working_capital_schedule_uses_trade_balances_and_average_dates(self) -> None:
        schedule = {row["period"]: row for row in self.analysis["working_capital"]}
        self.assertEqual(schedule["FY2025A"]["opening_balance_date"], date(2024, 12, 31))
        self.assertLess(
            schedule["FY2025A"]["cash_conversion_cycle"],
            schedule["FY2024A"]["cash_conversion_cycle"],
        )
        self.assertAlmostEqual(
            float(schedule["Q1 2026A"]["cash_conversion_cycle"]), 48.03, places=2
        )

    def test_q1_npat_to_cfo_bridge_exposes_supplier_funding_swing(self) -> None:
        bridges = {row["period"]: row for row in self.analysis["bridges"]["npat_to_cfo"]}
        q1 = bridges["Q1 2026A"]
        components = {row["label"]: row["amount_vnd_bn"] for row in q1["components"]}
        self.assertEqual(components["Change in payables"], Decimal("-465.976745678"))
        self.assertEqual(q1["reported_cfo_vnd_bn"], Decimal("863.686766977"))
        self.assertTrue(q1["passed"])

    def test_retained_earnings_bridge_does_not_hide_2025_restructuring(self) -> None:
        bridges = {
            row["period"]: row for row in self.analysis["bridges"]["retained_earnings"]
        }
        components = {
            row["label"]: row["amount_vnd_bn"]
            for row in bridges["FY2025A"]["components"]
        }
        self.assertEqual(
            bridges["FY2025A"]["bridge_type"],
            "retained_earnings_residual_reconciliation",
        )
        self.assertFalse(bridges["FY2025A"]["independent_reconstruction_available"])
        self.assertLess(
            components["Residual: capitalisation / other equity movements"], 0
        )
        self.assertIn("Residual reconciliation only", bridges["FY2025A"]["note"])
        self.assertIn("capital restructuring", bridges["FY2025A"]["note"])

    def test_normalization_schedule_preserves_missing_evidence_as_null(self) -> None:
        rows = {row["metric"]: row for row in self.analysis["normalization"]}
        self.assertEqual(
            rows["NPAT attributable to parent"]["normalized_value_vnd_bn"],
            Decimal("6075.000000000"),
        )
        self.assertIsNone(rows["Cash and cash equivalents"]["adjustment_vnd_bn"])
        self.assertIsNone(rows["Total debt"]["normalized_value_vnd_bn"])

    def test_missing_bridge_line_is_a_blocking_error(self) -> None:
        incomplete = [
            fact
            for fact in self.facts
            if not (
                fact.period_end == date(2026, 3, 31)
                and fact.period_type == "Q1"
                and fact.line_item == "change_payables"
            )
        ]
        with self.assertRaises(ThreeStatementAnalysisError):
            build_three_statement_analysis(
                incomplete,
                normalization_path=REPO_ROOT
                / "data"
                / "processed"
                / "dmx_normalization_adjustments.csv",
            )


if __name__ == "__main__":
    unittest.main()
