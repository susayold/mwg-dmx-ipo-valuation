"""Financial analytics engine for the MWG–DMX portfolio case study."""

from .ratios import calculate_ratios
from .three_statement import build_three_statement_analysis
from .validation import validate_dataset
from .valuation import run_scenario_config

__all__ = [
    "build_three_statement_analysis",
    "calculate_ratios",
    "run_scenario_config",
    "validate_dataset",
]
__version__ = "0.2.0"
