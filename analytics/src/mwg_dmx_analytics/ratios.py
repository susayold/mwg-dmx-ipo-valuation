from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable

from .types import FinancialFact


@dataclass(frozen=True, slots=True)
class RatioReport:
    entity_code: str
    period_end: date
    prior_period_end: date | None
    period_type: str
    statement_scope: str
    currency: str
    unit: str
    metrics: dict[str, Decimal | None]


def _divide(numerator: Decimal | None, denominator: Decimal | None) -> Decimal | None:
    if numerator is None or denominator in (None, Decimal("0")):
        return None
    return numerator / denominator


def _average(current: Decimal | None, previous: Decimal | None) -> Decimal | None:
    if current is None:
        return None
    if previous is None:
        return current
    return (current + previous) / Decimal("2")


def _value(items: dict[str, Decimal], line_item: str) -> Decimal | None:
    return items.get(line_item)


def calculate_ratios(
    facts: Iterable[FinancialFact],
    *,
    entity_code: str,
    period_end: date | str,
    period_type: str = "FY",
    statement_scope: str = "consolidated",
    currency: str | None = None,
    unit: str | None = None,
) -> RatioReport:
    """Calculate decision-useful ratios from normalized facts.

    Margins and returns are decimal fractions (0.10 = 10%). `free_cash_flow`
    retains the reported amount unit. Expenses and capex are expected to be
    stored as negative numbers.
    """

    facts = list(facts)
    if isinstance(period_end, str):
        period_end = date.fromisoformat(period_end)

    candidates = [
        fact
        for fact in facts
        if fact.entity_code == entity_code
        and fact.period_end == period_end
        and fact.period_type == period_type
        and fact.statement_scope == statement_scope
        and (currency is None or fact.currency == currency)
        and (unit is None or fact.unit == unit)
    ]
    if not candidates:
        raise ValueError(
            f"No facts for entity={entity_code}, period_end={period_end}, "
            f"period_type={period_type}, scope={statement_scope}"
        )

    combinations = {(fact.currency, fact.unit) for fact in candidates}
    if len(combinations) != 1:
        raise ValueError(
            "Ratio calculation requires one currency/unit combination; "
            f"found {sorted(combinations)}"
        )
    selected_currency, selected_unit = combinations.pop()
    current = {fact.line_item: fact.value for fact in candidates}

    prior_dates = sorted(
        {
            fact.period_end
            for fact in facts
            if fact.entity_code == entity_code
            and fact.period_end < period_end
            and fact.period_type == period_type
            and fact.statement_scope == statement_scope
            and fact.currency == selected_currency
            and fact.unit == selected_unit
        }
    )
    prior_period_end = prior_dates[-1] if prior_dates else None
    previous = {
        fact.line_item: fact.value
        for fact in facts
        if prior_period_end is not None
        and fact.entity_code == entity_code
        and fact.period_end == prior_period_end
        and fact.period_type == period_type
        and fact.statement_scope == statement_scope
        and fact.currency == selected_currency
        and fact.unit == selected_unit
    }

    revenue = _value(current, "revenue")
    previous_revenue = _value(previous, "revenue")
    gross_profit = _value(current, "gross_profit")
    ebitda = _value(current, "ebitda")
    ebit = _value(current, "ebit")
    net_income = _value(current, "net_income")
    cogs = _value(current, "cogs")
    interest_expense = _value(current, "interest_expense")
    pretax_income = _value(current, "pretax_income")
    tax_expense = _value(current, "tax_expense")
    total_assets = _value(current, "total_assets")
    total_equity = _value(current, "total_equity")
    total_debt = _value(current, "total_debt")
    cash = _value(current, "cash")
    current_assets = _value(current, "current_assets")
    current_liabilities = _value(current, "current_liabilities")
    inventory = _value(current, "inventory")
    receivables = _value(current, "receivables")
    payables = _value(current, "payables")
    operating_cash_flow = _value(current, "operating_cash_flow")
    capex = _value(current, "capex")

    average_assets = _average(total_assets, _value(previous, "total_assets"))
    average_equity = _average(total_equity, _value(previous, "total_equity"))
    average_inventory = _average(inventory, _value(previous, "inventory"))
    average_receivables = _average(receivables, _value(previous, "receivables"))
    average_payables = _average(payables, _value(previous, "payables"))

    current_invested_capital = None
    if total_debt is not None and total_equity is not None and cash is not None:
        current_invested_capital = total_debt + total_equity - cash
    previous_invested_capital = None
    if all(item in previous for item in ("total_debt", "total_equity", "cash")):
        previous_invested_capital = (
            previous["total_debt"] + previous["total_equity"] - previous["cash"]
        )
    average_invested_capital = _average(
        current_invested_capital, previous_invested_capital
    )

    effective_tax_rate = None
    if pretax_income is not None and pretax_income > 0 and tax_expense is not None:
        effective_tax_rate = abs(tax_expense) / pretax_income
    nopat = None
    if ebit is not None:
        tax_rate_for_nopat = effective_tax_rate if effective_tax_rate is not None else Decimal("0")
        nopat = ebit * (Decimal("1") - tax_rate_for_nopat)

    net_debt = None
    if total_debt is not None and cash is not None:
        net_debt = total_debt - cash
    free_cash_flow = None
    if operating_cash_flow is not None and capex is not None:
        free_cash_flow = operating_cash_flow + capex

    period_days = {
        "FY": Decimal("365"),
        "LTM": Decimal("365"),
        "H1": Decimal("182"),
        "9M": Decimal("274"),
        "Q1": Decimal("91"),
        "Q2": Decimal("91"),
        "Q3": Decimal("92"),
        "Q4": Decimal("91"),
    }.get(period_type, Decimal("365"))

    dso = _divide(average_receivables, revenue)
    dio = _divide(average_inventory, abs(cogs) if cogs is not None else None)
    dpo = _divide(average_payables, abs(cogs) if cogs is not None else None)
    if dso is not None:
        dso *= period_days
    if dio is not None:
        dio *= period_days
    if dpo is not None:
        dpo *= period_days
    cash_conversion_cycle = None
    if dso is not None and dio is not None and dpo is not None:
        cash_conversion_cycle = dso + dio - dpo

    revenue_growth = None
    if revenue is not None and previous_revenue not in (None, Decimal("0")):
        revenue_growth = revenue / previous_revenue - Decimal("1")

    quick_assets = None
    if current_assets is not None and inventory is not None:
        quick_assets = current_assets - inventory

    metrics = {
        "revenue_growth": revenue_growth,
        "gross_margin": _divide(gross_profit, revenue),
        "ebitda_margin": _divide(ebitda, revenue),
        "ebit_margin": _divide(ebit, revenue),
        "net_margin": _divide(net_income, revenue),
        "effective_tax_rate": effective_tax_rate,
        "return_on_assets": _divide(net_income, average_assets),
        "return_on_equity": _divide(net_income, average_equity),
        "return_on_invested_capital": _divide(nopat, average_invested_capital),
        "current_ratio": _divide(current_assets, current_liabilities),
        "quick_ratio": _divide(quick_assets, current_liabilities),
        "debt_to_equity": _divide(total_debt, total_equity),
        "net_debt_to_ebitda": _divide(net_debt, ebitda),
        "interest_coverage": _divide(
            ebit, abs(interest_expense) if interest_expense is not None else None
        ),
        "cfo_to_net_income": _divide(operating_cash_flow, net_income),
        "free_cash_flow": free_cash_flow,
        "free_cash_flow_margin": _divide(free_cash_flow, revenue),
        "days_sales_outstanding": dso,
        "days_inventory_outstanding": dio,
        "days_payables_outstanding": dpo,
        "cash_conversion_cycle": cash_conversion_cycle,
    }

    return RatioReport(
        entity_code=entity_code,
        period_end=period_end,
        prior_period_end=prior_period_end,
        period_type=period_type,
        statement_scope=statement_scope,
        currency=selected_currency,
        unit=selected_unit,
        metrics=metrics,
    )
