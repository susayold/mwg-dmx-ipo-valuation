from __future__ import annotations

import csv
from calendar import isleap
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Iterable

from .types import FinancialFact


class ThreeStatementAnalysisError(ValueError):
    """Raised when the historical statements cannot support a required control."""


ZERO = Decimal("0")
ONE = Decimal("1")
TOLERANCE = Decimal("0.001")  # VND 1 million when the dataset unit is VND bn.

PERIOD_LABELS = {
    (date(2023, 12, 31), "FY"): "FY2023A",
    (date(2024, 12, 31), "FY"): "FY2024A",
    (date(2025, 12, 31), "FY"): "FY2025A",
    (date(2025, 3, 31), "Q1"): "Q1 2025A",
    (date(2026, 3, 31), "Q1"): "Q1 2026A",
}

HEADLINE_ITEMS = (
    "revenue",
    "cogs",
    "gross_profit",
    "financial_income",
    "financial_expense",
    "interest_expense",
    "share_of_jv_profit",
    "selling_expense",
    "general_admin_expense",
    "operating_profit",
    "pretax_income",
    "tax_expense",
    "net_income",
    "current_assets",
    "cash",
    "short_term_investments",
    "current_receivables",
    "receivables",
    "inventory_gross",
    "inventory_provision",
    "inventory",
    "fixed_assets",
    "jv_investment",
    "long_term_deposits",
    "payables",
    "short_term_debt",
    "long_term_debt",
    "total_debt",
    "total_assets",
    "current_liabilities",
    "total_liabilities",
    "total_equity",
    "retained_earnings",
    "depreciation_amortization",
    "operating_profit_before_working_capital",
    "change_receivables",
    "change_inventory",
    "change_payables",
    "change_prepaids",
    "interest_paid",
    "tax_paid",
    "operating_cash_flow",
    "capex",
    "investing_cash_flow",
    "financing_cash_flow",
)

NPAT_TO_CFO_COMPONENTS = (
    ("net_income", "Net profit after tax"),
    ("tax_addback", "Add: P&L income-tax expense"),
    ("depreciation_amortization", "Depreciation and amortization"),
    ("provisions", "Provisions / reversals"),
    ("fx_revaluation_adjustment", "Non-cash FX revaluation"),
    ("investing_profit_adjustment", "Remove investing profit"),
    ("interest_expense_adjustment", "Add back interest expense"),
    ("change_receivables", "Change in receivables"),
    ("change_inventory", "Change in inventory"),
    ("change_payables", "Change in payables"),
    ("change_prepaids", "Change in prepayments"),
    ("interest_paid", "Interest paid"),
    ("tax_paid", "Corporate income tax paid"),
)


def _period_key(fact: FinancialFact) -> tuple[date, str]:
    return fact.period_end, fact.period_type


def _index_facts(facts: Iterable[FinancialFact]) -> dict[tuple[date, str], dict[str, Decimal]]:
    index: dict[tuple[date, str], dict[str, Decimal]] = {}
    for fact in facts:
        if fact.entity_code != "DMX" or fact.statement_scope != "consolidated":
            raise ThreeStatementAnalysisError(
                "Three-statement history must contain DMX consolidated facts only"
            )
        bucket = index.setdefault(_period_key(fact), {})
        if fact.line_item in bucket:
            raise ThreeStatementAnalysisError(
                f"Duplicate line item {fact.line_item} for {fact.period_end}/{fact.period_type}"
            )
        bucket[fact.line_item] = fact.value
    return index


def _value(items: dict[str, Decimal], line_item: str) -> Decimal | None:
    return items.get(line_item)


def _divide(numerator: Decimal | None, denominator: Decimal | None) -> Decimal | None:
    if numerator is None or denominator in (None, ZERO):
        return None
    return numerator / denominator


def _period_days(period_end: date, period_type: str) -> Decimal:
    if period_type == "FY":
        return Decimal("366" if isleap(period_end.year) else "365")
    if period_type == "Q1":
        return Decimal(str((period_end - date(period_end.year, 1, 1)).days + 1))
    raise ThreeStatementAnalysisError(f"Unsupported period-day convention: {period_type}")


def _period_sort_key(key: tuple[date, str]) -> tuple[date, int]:
    return key[0], 0 if key[1] == "FY" else 1


def _line(label: str, amount: Decimal) -> dict[str, Decimal | str]:
    return {"label": label, "amount_vnd_bn": amount}


def _bridge_check(calculated: Decimal, reported: Decimal) -> tuple[bool, Decimal]:
    difference = reported - calculated
    return abs(difference) <= TOLERANCE, difference


def build_statement_summary(
    facts: Iterable[FinancialFact],
) -> list[dict[str, object]]:
    index = _index_facts(facts)
    output: list[dict[str, object]] = []
    ordered_keys = sorted(index, key=_period_sort_key)
    for key in ordered_keys:
        period_end, period_type = key
        items = index[key]
        revenue = _value(items, "revenue")
        gross_profit = _value(items, "gross_profit")
        operating_profit = _value(items, "operating_profit")
        net_income = _value(items, "net_income")
        cfo = _value(items, "operating_cash_flow")
        capex = _value(items, "capex")
        fcf = cfo + capex if cfo is not None and capex is not None else None
        output.append(
            {
                "period": PERIOD_LABELS.get(key, f"{period_type} {period_end.year}"),
                "period_end": period_end,
                "period_type": period_type,
                "period_days": _period_days(period_end, period_type),
                "audit_status": (
                    "comparative unaudited"
                    if key == (date(2023, 12, 31), "FY")
                    else "audited"
                    if period_type == "FY"
                    else "unaudited"
                ),
                "scope": "DMX consolidated statutory reported",
                "values_vnd_bn": {
                    item: items.get(item) for item in HEADLINE_ITEMS
                },
                "ratios": {
                    "gross_margin": _divide(gross_profit, revenue),
                    "operating_margin": _divide(operating_profit, revenue),
                    "net_margin": _divide(net_income, revenue),
                    "cfo_to_npat": _divide(cfo, net_income),
                    "capex_to_revenue": _divide(
                        abs(capex) if capex is not None else None, revenue
                    ),
                    "free_cash_flow_vnd_bn": fcf,
                    "accrual_gap_vnd_bn": (
                        net_income - cfo
                        if net_income is not None and cfo is not None
                        else None
                    ),
                },
            }
        )
    return output


def build_working_capital_schedule(
    facts: Iterable[FinancialFact],
) -> list[dict[str, object]]:
    index = _index_facts(facts)
    comparisons = (
        ((date(2024, 12, 31), "FY"), (date(2023, 12, 31), "FY")),
        ((date(2025, 12, 31), "FY"), (date(2024, 12, 31), "FY")),
        ((date(2026, 3, 31), "Q1"), (date(2025, 12, 31), "FY")),
    )
    output: list[dict[str, object]] = []
    for current_key, opening_key in comparisons:
        current = index[current_key]
        opening = index[opening_key]
        required = ("revenue", "cogs", "receivables", "inventory", "payables")
        missing = [item for item in required if item not in current or item not in opening]
        if missing:
            raise ThreeStatementAnalysisError(
                f"Missing working-capital inputs for {current_key}: {sorted(set(missing))}"
            )
        days = _period_days(*current_key)
        average_receivables = (current["receivables"] + opening["receivables"]) / Decimal("2")
        average_inventory = (current["inventory"] + opening["inventory"]) / Decimal("2")
        average_payables = (current["payables"] + opening["payables"]) / Decimal("2")
        dso = average_receivables / current["revenue"] * days
        dio = average_inventory / abs(current["cogs"]) * days
        dpo = average_payables / abs(current["cogs"]) * days
        output.append(
            {
                "period": PERIOD_LABELS[current_key],
                "opening_balance_date": opening_key[0],
                "period_days": days,
                "basis": "Average opening/closing trade balances; net inventory; actual elapsed days",
                "q1_seasonality_warning": current_key[1] == "Q1",
                "days_inventory_outstanding": dio,
                "days_sales_outstanding": dso,
                "days_payables_outstanding": dpo,
                "cash_conversion_cycle": dio + dso - dpo,
                "cfo_to_npat": current["operating_cash_flow"] / current["net_income"],
                "capex_to_revenue": abs(current["capex"]) / current["revenue"],
                "inventory_provision_to_gross": abs(current["inventory_provision"])
                / current["inventory_gross"],
                "free_cash_flow_vnd_bn": current["operating_cash_flow"] + current["capex"],
            }
        )
    return output


def build_npat_to_cfo_bridges(
    facts: Iterable[FinancialFact],
) -> list[dict[str, object]]:
    index = _index_facts(facts)
    output: list[dict[str, object]] = []
    for key in sorted(index, key=_period_sort_key):
        items = index[key]
        if not {"net_income", "tax_expense", "operating_cash_flow"} <= items.keys():
            continue
        amounts = dict(items)
        amounts["tax_addback"] = -items["tax_expense"]
        missing = [code for code, _ in NPAT_TO_CFO_COMPONENTS if code not in amounts]
        if missing:
            raise ThreeStatementAnalysisError(
                f"Missing NPAT-to-CFO bridge inputs for {key}: {missing}"
            )
        components = [_line(label, amounts[code]) for code, label in NPAT_TO_CFO_COMPONENTS]
        calculated = sum((line["amount_vnd_bn"] for line in components), ZERO)  # type: ignore[arg-type]
        reported = items["operating_cash_flow"]
        passed, difference = _bridge_check(calculated, reported)
        output.append(
            {
                "period": PERIOD_LABELS[key],
                "components": components,
                "calculated_cfo_vnd_bn": calculated,
                "reported_cfo_vnd_bn": reported,
                "difference_vnd_bn": difference,
                "passed": passed,
            }
        )
    return output


def build_cash_bridges(facts: Iterable[FinancialFact]) -> list[dict[str, object]]:
    index = _index_facts(facts)
    output: list[dict[str, object]] = []
    for key in sorted(index, key=_period_sort_key):
        items = index[key]
        required = {
            "opening_cash",
            "operating_cash_flow",
            "investing_cash_flow",
            "financing_cash_flow",
            "fx_cash_effect",
            "ending_cash",
        }
        if not required <= items.keys():
            continue
        components = [
            _line("Opening cash", items["opening_cash"]),
            _line("Cash flow from operations", items["operating_cash_flow"]),
            _line("Cash flow from investing", items["investing_cash_flow"]),
            _line("Cash flow from financing", items["financing_cash_flow"]),
            _line("FX effect", items["fx_cash_effect"]),
        ]
        calculated = sum((line["amount_vnd_bn"] for line in components), ZERO)  # type: ignore[arg-type]
        reported = items["ending_cash"]
        passed, difference = _bridge_check(calculated, reported)
        output.append(
            {
                "period": PERIOD_LABELS[key],
                "components": components,
                "calculated_ending_cash_vnd_bn": calculated,
                "reported_ending_cash_vnd_bn": reported,
                "difference_vnd_bn": difference,
                "passed": passed,
            }
        )
    return output


def build_retained_earnings_bridges(
    facts: Iterable[FinancialFact],
) -> list[dict[str, object]]:
    index = _index_facts(facts)
    comparisons = (
        ((date(2024, 12, 31), "FY"), (date(2023, 12, 31), "FY")),
        ((date(2025, 12, 31), "FY"), (date(2024, 12, 31), "FY")),
        ((date(2026, 3, 31), "Q1"), (date(2025, 12, 31), "FY")),
    )
    output: list[dict[str, object]] = []
    for current_key, opening_key in comparisons:
        current = index[current_key]
        opening = index[opening_key]
        opening_re = opening["retained_earnings"]
        net_income = current["net_income_parent"]
        dividends = current.get("dividends_paid", ZERO)
        closing_re = current["retained_earnings"]
        other_equity_movements = closing_re - opening_re - net_income - dividends
        components = [
            _line("Opening retained earnings", opening_re),
            _line("NPAT attributable to parent", net_income),
            _line("Dividends paid", dividends),
            _line("Residual: capitalisation / other equity movements", other_equity_movements),
        ]
        calculated = sum((line["amount_vnd_bn"] for line in components), ZERO)  # type: ignore[arg-type]
        passed, difference = _bridge_check(calculated, closing_re)
        output.append(
            {
                "period": PERIOD_LABELS[current_key],
                "bridge_type": "retained_earnings_residual_reconciliation",
                "components": components,
                "calculated_closing_retained_earnings_vnd_bn": calculated,
                "reported_closing_retained_earnings_vnd_bn": closing_re,
                "difference_vnd_bn": difference,
                "passed": passed,
                "independent_reconstruction_available": False,
                "note": (
                    "Residual reconciliation only: detailed statement-of-changes-in-equity lines are not fully available in the public case set. FY2025 residual captures the disclosed capital restructuring and other equity movements; it is not treated as an operating adjustment."
                    if current_key == (date(2025, 12, 31), "FY")
                    else "Residual reconciliation only; no unsupported normalization is introduced."
                ),
            }
        )
    return output


def load_normalization_schedule(path: str | Path) -> list[dict[str, object]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    output: list[dict[str, object]] = []
    for row in rows:
        converted: dict[str, object] = dict(row)
        for field in (
            "reported_value_vnd_bn",
            "adjustment_vnd_bn",
            "normalized_value_vnd_bn",
        ):
            value = (row.get(field) or "").strip()
            converted[field] = Decimal(value) if value else None
        output.append(converted)
    return output


def build_accounting_checks(facts: Iterable[FinancialFact]) -> list[dict[str, object]]:
    index = _index_facts(facts)
    checks: list[dict[str, object]] = []

    def add(code: str, key: tuple[date, str], calculated: Decimal, reported: Decimal) -> None:
        passed, difference = _bridge_check(calculated, reported)
        checks.append(
            {
                "check_code": code,
                "period": PERIOD_LABELS[key],
                "passed": passed,
                "difference_vnd_bn": difference,
            }
        )

    for key, items in sorted(index.items(), key=lambda entry: _period_sort_key(entry[0])):
        required_income = {"revenue", "cogs", "gross_profit", "pretax_income", "tax_expense", "net_income"}
        if required_income <= items.keys():
            add("CHK_GROSS_PROFIT", key, items["revenue"] + items["cogs"], items["gross_profit"])
            add("CHK_PBT_NPAT_TAX", key, items["pretax_income"] + items["tax_expense"], items["net_income"])
        required_balance = {"total_assets", "total_liabilities", "total_equity"}
        if required_balance <= items.keys():
            add("CHK_BALANCE_SHEET", key, items["total_liabilities"] + items["total_equity"], items["total_assets"])
        required_inventory = {"inventory_gross", "inventory_provision", "inventory"}
        if required_inventory <= items.keys():
            add("CHK_INVENTORY_NET", key, items["inventory_gross"] + items["inventory_provision"], items["inventory"])
        if {"ending_cash", "cash"} <= items.keys():
            add("CHK_CFS_TO_BS_CASH", key, items["ending_cash"], items["cash"])

    for bridge in build_npat_to_cfo_bridges(facts):
        checks.append(
            {
                "check_code": "CHK_CFO_INDIRECT_BRIDGE",
                "period": bridge["period"],
                "passed": bridge["passed"],
                "difference_vnd_bn": bridge["difference_vnd_bn"],
            }
        )
    for bridge in build_cash_bridges(facts):
        checks.append(
            {
                "check_code": "CHK_CASH_ROLL",
                "period": bridge["period"],
                "passed": bridge["passed"],
                "difference_vnd_bn": bridge["difference_vnd_bn"],
            }
        )
    for bridge in build_retained_earnings_bridges(facts):
        checks.append(
            {
                "check_code": "CHK_RETAINED_EARNINGS_RESIDUAL_RECONCILIATION",
                "period": bridge["period"],
                "passed": bridge["passed"],
                "difference_vnd_bn": bridge["difference_vnd_bn"],
                "validation_basis": "residual_reconciliation_not_independent_socie_rebuild",
            }
        )

    failed = [check for check in checks if not check["passed"]]
    if failed:
        raise ThreeStatementAnalysisError(f"Accounting controls failed: {failed}")
    return checks


def build_quality_of_earnings(facts: Iterable[FinancialFact]) -> list[dict[str, object]]:
    index = _index_facts(facts)
    q1 = index[(date(2026, 3, 31), "Q1")]
    prior_q1 = index[(date(2025, 3, 31), "Q1")]
    fy2025 = index[(date(2025, 12, 31), "FY")]
    return [
        {
            "indicator": "Revenue growth",
            "value": q1["revenue"] / prior_q1["revenue"] - ONE,
            "observation": "Q1 2026 revenue grew strongly year on year.",
            "interpretation": "Operating momentum is broad enough to warrant a full-year follow-through test.",
            "risk": "A single quarter does not establish sustainability or remove seasonality.",
        },
        {
            "indicator": "Gross-margin change",
            "value": q1["gross_profit"] / q1["revenue"]
            - prior_q1["gross_profit"] / prior_q1["revenue"],
            "observation": "Gross margin expanded by approximately 119 bps year on year.",
            "interpretation": "Mix, pricing and operating leverage appear more supportive than pure volume growth.",
            "risk": "Category mix, promotions and vendor support may normalize.",
        },
        {
            "indicator": "CFO / NPAT",
            "value": q1["operating_cash_flow"] / q1["net_income"],
            "prior_value": prior_q1["operating_cash_flow"] / prior_q1["net_income"],
            "observation": "Quarterly cash conversion fell to about 39% from about 168%.",
            "interpretation": "The main swing is working capital, especially supplier funding, plus tax payments.",
            "risk": "Do not infer earnings manipulation without seasonal and H1 statement evidence.",
        },
        {
            "indicator": "Payables contribution to CFO",
            "value_vnd_bn": q1["change_payables"],
            "prior_value_vnd_bn": prior_q1["change_payables"],
            "observation": "Payables absorbed cash in Q1 2026 after providing material funding in Q1 2025.",
            "interpretation": "Supplier financing explains more of the CFO gap than receivables or inventory alone.",
            "risk": "A sustained decline in supplier funding would pressure liquidity.",
        },
        {
            "indicator": "Inventory provision coverage",
            "value": abs(q1["inventory_provision"]) / q1["inventory_gross"],
            "prior_value": abs(fy2025["inventory_provision"]) / fy2025["inventory_gross"],
            "observation": "Provision coverage rose from the FY2025 year-end level.",
            "interpretation": "The balance sheet recognizes more inventory risk as stock expands.",
            "risk": "Ageing, markdowns and category-level obsolescence remain undisclosed.",
        },
        {
            "indicator": "Net finance contribution / PBT",
            "value": (q1["financial_income"] + q1["financial_expense"]) / q1["pretax_income"],
            "observation": "Net finance income contributes to reported profit but is not the primary growth driver.",
            "interpretation": "Core and treasury earnings should remain separately visible.",
            "risk": "Deposit income may change after IPO proceeds are used to repay debt.",
        },
    ]


def build_three_statement_analysis(
    facts: Iterable[FinancialFact],
    *,
    normalization_path: str | Path,
) -> dict[str, object]:
    facts = list(facts)
    checks = build_accounting_checks(facts)
    return {
        "metadata": {
            "data_version": "three-statement-v1.0.0",
            "data_cutoff": "2026-07-13",
            "entity": "Dien May Xanh Investment JSC",
            "scope": "consolidated",
            "currency": "VND",
            "unit": "VND_bn",
            "fact_count": len(facts),
            "forecast_boundary": "Historical analysis only; no fully integrated three-statement forecast is claimed.",
        },
        "coverage": [
            {"period": "FY2023A", "status": "comparative unaudited", "source_id": "DMX_FS_2024_C"},
            {"period": "FY2024A", "status": "audited", "source_id": "DMX_FS_2024_C"},
            {"period": "FY2025A", "status": "audited", "source_id": "DMX_FS_2025_C"},
            {"period": "Q1 2026A", "status": "unaudited", "source_id": "DMX_DATA_2026Q1"},
            {"period": "H1 2026", "status": "operating update only; no H1 statements at cut-off", "source_id": "DMX_RESULTS_2026H1"},
        ],
        "statements": build_statement_summary(facts),
        "working_capital": build_working_capital_schedule(facts),
        "bridges": {
            "npat_to_cfo": build_npat_to_cfo_bridges(facts),
            "cash": build_cash_bridges(facts),
            "retained_earnings": build_retained_earnings_bridges(facts),
        },
        "normalization": load_normalization_schedule(normalization_path),
        "quality_of_earnings": build_quality_of_earnings(facts),
        "senior_readthroughs": [
            "IPO proceeds are primary capital of DMX, not cash received by MWG.",
            "Resolution 15 discloses VND 13,215.08bn estimated net proceeds earmarked for debt repayment; this remains pro forma until disbursement is evidenced.",
            "Cash plus deposits less debt is a liquidity indicator, not automatically distributable excess cash.",
            "Financed-sales mix does not prove DMX bears customer credit risk; lender and risk-transfer terms must be verified.",
            "EraBlue is equity-accounted and must be included once under a method-consistent valuation treatment.",
            "Management LFL FY2025 is a comparator, not a replacement for statutory reported statements.",
        ],
        "accounting_checks": checks,
        "check_summary": {
            "checks": len(checks),
            "passed": sum(bool(check["passed"]) for check in checks),
            "failed": sum(not bool(check["passed"]) for check in checks),
        },
    }
