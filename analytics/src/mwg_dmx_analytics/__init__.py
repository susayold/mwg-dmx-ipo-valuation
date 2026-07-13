"""Financial analytics engine for the MWG–DMX portfolio case study."""

from .ratios import calculate_ratios
from .validation import validate_dataset
from .valuation import run_scenario_config

__all__ = ["calculate_ratios", "run_scenario_config", "validate_dataset"]
__version__ = "0.1.0"
