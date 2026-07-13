from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Iterable, Mapping


class ValuationInputError(ValueError):
    """Raised when scenario assumptions are incomplete or internally invalid."""


def _decimal(value: Any, field: str) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception as exc:
        raise ValuationInputError(f"{field} must be numeric; received {value!r}") from exc


@dataclass(frozen=True, slots=True)
class UnitValuationResult:
    code: str
    name: str
    method: str
    enterprise_value: Decimal
    net_debt: Decimal
    non_operating_assets: Decimal
    minority_interest: Decimal
    equity_value: Decimal
    ownership_pct: Decimal
    attributable_equity_value: Decimal
    assumptions: dict[str, Any]


def value_multiple_unit(unit: Mapping[str, Any]) -> UnitValuationResult:
    metric_value = _decimal(unit.get("metric_value"), "metric_value")
    valuation_multiple = _decimal(unit.get("valuation_multiple"), "valuation_multiple")
    if metric_value < 0 or valuation_multiple < 0:
        raise ValuationInputError("Multiple valuation requires non-negative metric and multiple")
    enterprise_value = metric_value * valuation_multiple
    return _equity_bridge(unit, "multiple", enterprise_value, {
        "metric_name": unit.get("metric_name", "metric"),
        "metric_value": metric_value,
        "valuation_multiple": valuation_multiple,
    })


def value_dcf_unit(unit: Mapping[str, Any]) -> UnitValuationResult:
    raw_cash_flows = unit.get("cash_flows")
    if not isinstance(raw_cash_flows, list) or not raw_cash_flows:
        raise ValuationInputError("DCF unit requires a non-empty cash_flows list")
    cash_flows = [_decimal(value, "cash_flows") for value in raw_cash_flows]
    discount_rate = _decimal(unit.get("discount_rate"), "discount_rate")
    terminal_growth = _decimal(unit.get("terminal_growth"), "terminal_growth")
    if discount_rate <= terminal_growth:
        raise ValuationInputError("discount_rate must be greater than terminal_growth")
    if discount_rate <= Decimal("-1"):
        raise ValuationInputError("discount_rate must be greater than -100%")

    mid_year_convention = unit.get("mid_year_convention", True)
    if not isinstance(mid_year_convention, bool):
        raise ValuationInputError("mid_year_convention must be true or false")

    raw_discount_periods = unit.get("discount_periods")
    if raw_discount_periods is None:
        offset = Decimal("0.5") if mid_year_convention else Decimal("0")
        discount_periods = [
            Decimal(period) - offset for period in range(1, len(cash_flows) + 1)
        ]
        timing_convention = "mid_year" if mid_year_convention else "year_end"
    else:
        if not isinstance(raw_discount_periods, list):
            raise ValuationInputError("discount_periods must be a list when provided")
        if len(raw_discount_periods) != len(cash_flows):
            raise ValuationInputError(
                "discount_periods must contain one period for each cash flow"
            )
        discount_periods = [
            _decimal(value, "discount_periods") for value in raw_discount_periods
        ]
        if any(period <= 0 for period in discount_periods):
            raise ValuationInputError("discount_periods must be positive")
        if any(
            later <= earlier
            for earlier, later in zip(discount_periods, discount_periods[1:])
        ):
            raise ValuationInputError("discount_periods must be strictly increasing")
        timing_convention = "custom"

    terminal_discount_period = _decimal(
        unit.get("terminal_discount_period", discount_periods[-1]),
        "terminal_discount_period",
    )
    if terminal_discount_period < discount_periods[-1]:
        raise ValuationInputError(
            "terminal_discount_period cannot precede the final explicit cash flow"
        )

    present_value = sum(
        (
            cash_flow / ((Decimal("1") + discount_rate) ** period)
            for cash_flow, period in zip(cash_flows, discount_periods)
        ),
        Decimal("0"),
    )
    terminal_value = (
        cash_flows[-1]
        * (Decimal("1") + terminal_growth)
        / (discount_rate - terminal_growth)
    )
    terminal_present_value = terminal_value / (
        (Decimal("1") + discount_rate) ** terminal_discount_period
    )
    enterprise_value = present_value + terminal_present_value
    return _equity_bridge(
        unit,
        "dcf",
        enterprise_value,
        {
            "cash_flows": cash_flows,
            "discount_rate": discount_rate,
            "terminal_growth": terminal_growth,
            "mid_year_convention": mid_year_convention,
            "timing_convention": timing_convention,
            "discount_periods": discount_periods,
            "terminal_discount_period": terminal_discount_period,
            "explicit_period_pv": present_value,
            "terminal_value_pv": terminal_present_value,
        },
    )


def _equity_bridge(
    unit: Mapping[str, Any],
    method: str,
    enterprise_value: Decimal,
    assumptions: dict[str, Any],
) -> UnitValuationResult:
    code = str(unit.get("code", "")).strip()
    name = str(unit.get("name", code)).strip()
    if not code:
        raise ValuationInputError("Every valuation unit requires a code")
    net_debt = _decimal(unit.get("net_debt", 0), "net_debt")
    non_operating_assets = _decimal(
        unit.get("non_operating_assets", 0), "non_operating_assets"
    )
    minority_interest = _decimal(unit.get("minority_interest", 0), "minority_interest")
    ownership_pct = _decimal(unit.get("ownership_pct", 1), "ownership_pct")
    if not Decimal("0") <= ownership_pct <= Decimal("1"):
        raise ValuationInputError(f"{code}: ownership_pct must be between 0 and 1")
    equity_value = enterprise_value - net_debt + non_operating_assets - minority_interest
    attributable_equity_value = equity_value * ownership_pct
    return UnitValuationResult(
        code=code,
        name=name,
        method=method,
        enterprise_value=enterprise_value,
        net_debt=net_debt,
        non_operating_assets=non_operating_assets,
        minority_interest=minority_interest,
        equity_value=equity_value,
        ownership_pct=ownership_pct,
        attributable_equity_value=attributable_equity_value,
        assumptions=assumptions,
    )


def value_unit(unit: Mapping[str, Any]) -> UnitValuationResult:
    method = str(unit.get("method", "")).lower()
    if method == "multiple":
        return value_multiple_unit(unit)
    if method == "dcf":
        return value_dcf_unit(unit)
    raise ValuationInputError(f"Unsupported valuation method {method!r}")


def value_sotp_scenario(scenario: Mapping[str, Any]) -> dict[str, Any]:
    name = str(scenario.get("name", "")).strip()
    if not name:
        raise ValuationInputError("Scenario requires a name")
    raw_units = scenario.get("units")
    if not isinstance(raw_units, list) or not raw_units:
        raise ValuationInputError(f"Scenario {name} requires at least one business unit")

    unit_results = [value_unit(unit) for unit in raw_units]
    codes = [result.code for result in unit_results]
    if len(codes) != len(set(codes)):
        raise ValuationInputError(f"Scenario {name} contains duplicate unit codes")

    operating_attributable_value = sum(
        (result.attributable_equity_value for result in unit_results), Decimal("0")
    )
    holding_discount_pct = _decimal(
        scenario.get("holding_company_discount_pct", 0), "holding_company_discount_pct"
    )
    if not Decimal("0") <= holding_discount_pct < Decimal("1"):
        raise ValuationInputError("holding_company_discount_pct must be in [0, 1)")
    holding_discount_amount = operating_attributable_value * holding_discount_pct
    parent_net_debt = _decimal(scenario.get("parent_net_debt", 0), "parent_net_debt")
    parent_non_operating_assets = _decimal(
        scenario.get("parent_non_operating_assets", 0), "parent_non_operating_assets"
    )
    shares_outstanding = _decimal(scenario.get("shares_outstanding"), "shares_outstanding")
    if shares_outstanding <= 0:
        raise ValuationInputError("shares_outstanding must be positive")

    equity_value_before_discount = (
        operating_attributable_value + parent_non_operating_assets - parent_net_debt
    )
    equity_value_after_discount = (
        operating_attributable_value
        - holding_discount_amount
        + parent_non_operating_assets
        - parent_net_debt
    )
    implied_value_per_share = equity_value_after_discount / shares_outstanding

    return {
        "name": name,
        "units": unit_results,
        "operating_attributable_value": operating_attributable_value,
        "holding_company_discount_pct": holding_discount_pct,
        "holding_company_discount_amount": holding_discount_amount,
        "parent_non_operating_assets": parent_non_operating_assets,
        "parent_net_debt": parent_net_debt,
        "equity_value_before_discount": equity_value_before_discount,
        "equity_value_after_discount": equity_value_after_discount,
        "shares_outstanding": shares_outstanding,
        "implied_value_per_share": implied_value_per_share,
    }


def run_scenario_config(config: Mapping[str, Any]) -> dict[str, Any]:
    metadata = config.get("metadata")
    if not isinstance(metadata, dict):
        raise ValuationInputError("Scenario config requires a metadata object")
    if metadata.get("data_status") == "synthetic" and not metadata.get("warning"):
        raise ValuationInputError("Synthetic scenario config requires an explicit warning")
    if metadata.get("unit") == "VND_bn" and metadata.get("shares_unit") != "billion_shares":
        raise ValuationInputError(
            "VND_bn scenarios must express shares_outstanding in billion_shares "
            "so the quotient is VND per share"
        )
    scenarios = config.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValuationInputError("Scenario config requires a non-empty scenarios list")
    results = [value_sotp_scenario(scenario) for scenario in scenarios]
    scenario_names = [result["name"] for result in results]
    if len(scenario_names) != len(set(scenario_names)):
        raise ValuationInputError("Scenario names must be unique")
    return {"metadata": dict(metadata), "scenarios": results}


def dcf_sensitivity_matrix(
    cash_flows: Iterable[Decimal | int | float | str],
    discount_rates: Iterable[Decimal | int | float | str],
    terminal_growth_rates: Iterable[Decimal | int | float | str],
    *,
    mid_year_convention: bool = True,
    discount_periods: Iterable[Decimal | int | float | str] | None = None,
    terminal_discount_period: Decimal | int | float | str | None = None,
) -> dict[str, dict[str, Decimal]]:
    """Return an enterprise-value sensitivity matrix for explicit FCFs."""

    cash_flows = [_decimal(value, "cash_flows") for value in cash_flows]
    if not cash_flows:
        raise ValuationInputError("Sensitivity matrix requires explicit cash flows")
    custom_periods = list(discount_periods) if discount_periods is not None else None
    matrix: dict[str, dict[str, Decimal]] = {}
    for discount_rate_value in discount_rates:
        discount_rate = _decimal(discount_rate_value, "discount_rate")
        row: dict[str, Decimal] = {}
        for terminal_growth_value in terminal_growth_rates:
            terminal_growth = _decimal(terminal_growth_value, "terminal_growth")
            result = value_dcf_unit(
                {
                    "code": "SENSITIVITY",
                    "name": "Sensitivity",
                    "cash_flows": cash_flows,
                    "discount_rate": discount_rate,
                    "terminal_growth": terminal_growth,
                    "mid_year_convention": mid_year_convention,
                    **(
                        {"discount_periods": custom_periods}
                        if custom_periods is not None
                        else {}
                    ),
                    **(
                        {"terminal_discount_period": terminal_discount_period}
                        if terminal_discount_period is not None
                        else {}
                    ),
                }
            )
            row[str(terminal_growth)] = result.enterprise_value
        matrix[str(discount_rate)] = row
    return matrix
