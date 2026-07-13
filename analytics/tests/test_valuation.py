from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path

ANALYTICS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ANALYTICS_ROOT / "src"))

from mwg_dmx_analytics.data_io import load_json
from mwg_dmx_analytics.valuation import (
    ValuationInputError,
    dcf_sensitivity_matrix,
    run_scenario_config,
    value_dcf_unit,
    value_multiple_unit,
)


class ValuationTests(unittest.TestCase):
    def test_multiple_equity_bridge_and_ownership(self) -> None:
        result = value_multiple_unit(
            {
                "code": "UNIT",
                "name": "Unit",
                "metric_value": 100,
                "valuation_multiple": 5,
                "net_debt": 50,
                "ownership_pct": 0.8,
            }
        )
        self.assertEqual(result.enterprise_value, Decimal("500"))
        self.assertEqual(result.equity_value, Decimal("450"))
        self.assertEqual(result.attributable_equity_value, Decimal("360.0"))

    def test_dcf_defaults_to_mid_year_convention(self) -> None:
        result = value_dcf_unit(
            {
                "code": "DCF",
                "cash_flows": [100, 100],
                "discount_rate": 0.10,
                "terminal_growth": 0,
            }
        )
        self.assertAlmostEqual(
            float(result.enterprise_value), 1048.8088481701516, places=8
        )
        self.assertEqual(result.assumptions["timing_convention"], "mid_year")
        self.assertEqual(
            result.assumptions["discount_periods"],
            [Decimal("0.5"), Decimal("1.5")],
        )

    def test_dcf_can_use_explicit_year_end_convention(self) -> None:
        result = value_dcf_unit(
            {
                "code": "DCF",
                "cash_flows": [100, 100],
                "discount_rate": 0.10,
                "terminal_growth": 0,
                "mid_year_convention": False,
            }
        )
        self.assertAlmostEqual(float(result.enterprise_value), 1000.0, places=8)
        self.assertEqual(result.assumptions["timing_convention"], "year_end")

    def test_dcf_supports_auditable_custom_stub_timing(self) -> None:
        result = value_dcf_unit(
            {
                "code": "DCF",
                "cash_flows": [100, 110],
                "discount_rate": 0.10,
                "terminal_growth": 0.02,
                "discount_periods": [0.25, 1.25],
                "terminal_discount_period": 1.5,
            }
        )
        rate = Decimal("1.1")
        expected = (
            Decimal("100") / rate ** Decimal("0.25")
            + Decimal("110") / rate ** Decimal("1.25")
            + (Decimal("110") * Decimal("1.02") / Decimal("0.08"))
            / rate ** Decimal("1.5")
        )
        self.assertAlmostEqual(float(result.enterprise_value), float(expected), places=8)
        self.assertEqual(result.assumptions["timing_convention"], "custom")
        self.assertEqual(
            result.assumptions["terminal_discount_period"], Decimal("1.5")
        )

    def test_invalid_dcf_timing_is_rejected(self) -> None:
        invalid_timing = [
            {"mid_year_convention": "yes"},
            {"discount_periods": [0.5]},
            {"discount_periods": [0.5, 0.5]},
            {"discount_periods": [0.5, 1.5], "terminal_discount_period": 1.0},
        ]
        for timing in invalid_timing:
            with self.subTest(timing=timing), self.assertRaises(ValuationInputError):
                value_dcf_unit(
                    {
                        "code": "DCF",
                        "cash_flows": [100, 100],
                        "discount_rate": 0.10,
                        "terminal_growth": 0,
                        **timing,
                    }
                )

    def test_invalid_terminal_growth_is_rejected(self) -> None:
        with self.assertRaises(ValuationInputError):
            value_dcf_unit(
                {
                    "code": "DCF",
                    "cash_flows": [100],
                    "discount_rate": 0.10,
                    "terminal_growth": 0.10,
                }
            )

    def test_sample_scenarios_are_monotonic(self) -> None:
        config = load_json(
            ANALYTICS_ROOT / "data" / "sample" / "sotp_scenarios_sample.json"
        )
        output = run_scenario_config(config)
        values = {
            scenario["name"]: scenario["equity_value_after_discount"]
            for scenario in output["scenarios"]
        }
        self.assertLess(values["bear"], values["base"])
        self.assertLess(values["base"], values["bull"])

    def test_sensitivity_matrix_has_expected_shape(self) -> None:
        matrix = dcf_sensitivity_matrix([100, 110], [0.10, 0.12], [0.02, 0.03])
        self.assertEqual(set(matrix), {"0.1", "0.12"})
        self.assertEqual(set(matrix["0.1"]), {"0.02", "0.03"})


if __name__ == "__main__":
    unittest.main()
