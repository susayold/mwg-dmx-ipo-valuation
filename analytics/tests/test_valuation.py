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

    def test_dcf_terminal_value_is_discounted(self) -> None:
        result = value_dcf_unit(
            {
                "code": "DCF",
                "cash_flows": [100, 100],
                "discount_rate": 0.10,
                "terminal_growth": 0,
            }
        )
        self.assertAlmostEqual(float(result.enterprise_value), 1000.0, places=8)

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
