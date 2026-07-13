from __future__ import annotations

from collections import Counter, defaultdict
from decimal import Decimal
from typing import Iterable

from .constants import (
    CANONICAL_LINE_ITEMS,
    DATA_STATUSES,
    EXTRACTION_METHODS,
    NON_NEGATIVE_LINE_ITEMS,
    NON_POSITIVE_LINE_ITEMS,
    PERIOD_TYPES,
    STATEMENT_SCOPES,
    UNITS,
)
from .types import FinancialFact, SourceDocument, ValidationResult


def _result(
    code: str,
    passed: bool,
    message: str,
    *,
    severity: str = "error",
    fact: FinancialFact | None = None,
    context: dict | None = None,
) -> ValidationResult:
    return ValidationResult(
        check_code=code,
        severity=severity,
        passed=passed,
        message=message,
        entity_code=fact.entity_code if fact else None,
        period_end=fact.period_end if fact else None,
        context=context or {},
    )


def _within_tolerance(actual: Decimal, expected: Decimal, scale: Decimal) -> bool:
    absolute_tolerance = Decimal("1")
    relative_tolerance = abs(scale) * Decimal("0.0001")
    return abs(actual - expected) <= max(absolute_tolerance, relative_tolerance)


def validate_dataset(
    facts: Iterable[FinancialFact], sources: Iterable[SourceDocument]
) -> list[ValidationResult]:
    """Validate normalized facts and their document lineage.

    Passing checks are retained because a portfolio model should show what was
    tested, not only what failed. Warning-level sign and taxonomy checks do not
    block a pipeline build; error-level failures do.
    """

    facts = list(facts)
    sources = list(sources)
    results: list[ValidationResult] = []

    results.append(
        _result(
            "DATASET_NOT_EMPTY",
            bool(facts),
            f"Dataset contains {len(facts)} financial facts",
        )
    )

    source_counts = Counter(source.source_document_id for source in sources)
    duplicate_source_ids = sorted(key for key, count in source_counts.items() if count > 1)
    results.append(
        _result(
            "SOURCE_ID_UNIQUE",
            not duplicate_source_ids,
            "Source document identifiers are unique"
            if not duplicate_source_ids
            else f"Duplicate source identifiers: {duplicate_source_ids}",
            context={"duplicates": duplicate_source_ids},
        )
    )

    fact_counts = Counter(fact.natural_key for fact in facts)
    duplicate_fact_keys = [key for key, count in fact_counts.items() if count > 1]
    results.append(
        _result(
            "FACT_NATURAL_KEY_UNIQUE",
            not duplicate_fact_keys,
            "Every financial fact has a unique natural key"
            if not duplicate_fact_keys
            else f"Found {len(duplicate_fact_keys)} duplicate fact keys",
            context={"duplicate_count": len(duplicate_fact_keys)},
        )
    )

    source_map = {source.source_document_id: source for source in sources}
    missing_lineage = sorted(
        {fact.source_document_id for fact in facts if fact.source_document_id not in source_map}
    )
    results.append(
        _result(
            "SOURCE_LINEAGE_COMPLETE",
            not missing_lineage,
            "Every fact links to a registered source document"
            if not missing_lineage
            else f"Unregistered source identifiers: {missing_lineage}",
            context={"missing_source_ids": missing_lineage},
        )
    )

    for source in sources:
        status_valid = source.data_status in DATA_STATUSES
        results.append(
            ValidationResult(
                check_code="SOURCE_STATUS_VALID",
                severity="error",
                passed=status_valid,
                message=f"Source {source.source_document_id} status is {source.data_status!r}",
                entity_code=source.entity_code,
                period_end=source.period_end,
            )
        )
        if source.data_status == "official":
            sha_valid = len(source.sha256) == 64 and all(
                character in "0123456789abcdef" for character in source.sha256
            )
            complete = bool(source.source_url and source.retrieved_at and sha_valid)
            results.append(
                ValidationResult(
                    check_code="OFFICIAL_SOURCE_AUDIT_TRAIL",
                    severity="error",
                    passed=complete,
                    message=(
                        f"Official source {source.source_document_id} has URL, retrieval time and hash"
                        if complete
                        else f"Official source {source.source_document_id} lacks URL, retrieval time or valid SHA-256"
                    ),
                    entity_code=source.entity_code,
                    period_end=source.period_end,
                )
            )
        if source.data_status == "synthetic":
            clearly_labeled = source.source_document_id.startswith("SYNTHETIC-") and any(
                token in (source.document_title + " " + source.notes).lower()
                for token in ("synthetic", "illustrative", "fixture")
            )
            results.append(
                ValidationResult(
                    check_code="SYNTHETIC_SOURCE_LABEL",
                    severity="error",
                    passed=clearly_labeled,
                    message=(
                        f"Synthetic source {source.source_document_id} is clearly labeled"
                        if clearly_labeled
                        else f"Synthetic source {source.source_document_id} is not clearly labeled"
                    ),
                    entity_code=source.entity_code,
                    period_end=source.period_end,
                )
            )

    for fact in facts:
        enum_errors: list[str] = []
        if fact.period_type not in PERIOD_TYPES:
            enum_errors.append(f"period_type={fact.period_type!r}")
        if fact.statement_scope not in STATEMENT_SCOPES:
            enum_errors.append(f"statement_scope={fact.statement_scope!r}")
        if fact.unit not in UNITS:
            enum_errors.append(f"unit={fact.unit!r}")
        if fact.data_status not in DATA_STATUSES:
            enum_errors.append(f"data_status={fact.data_status!r}")
        if fact.extraction_method not in EXTRACTION_METHODS:
            enum_errors.append(f"extraction_method={fact.extraction_method!r}")
        if not fact.entity_code or not fact.currency or not fact.line_item:
            enum_errors.append("blank identifier/currency/line_item")
        if enum_errors:
            results.append(
                _result(
                    "FACT_DOMAIN_VALUES",
                    False,
                    f"Invalid fact domain values: {', '.join(enum_errors)}",
                    fact=fact,
                    context={"line_item": fact.line_item},
                )
            )

        if fact.line_item not in CANONICAL_LINE_ITEMS:
            results.append(
                _result(
                    "CANONICAL_TAXONOMY",
                    False,
                    f"Unknown canonical line item: {fact.line_item}",
                    severity="warning",
                    fact=fact,
                )
            )

        source = source_map.get(fact.source_document_id)
        if source:
            aligned = source.entity_code == fact.entity_code
            if not aligned:
                results.append(
                    _result(
                        "SOURCE_ENTITY_MATCH",
                        False,
                        f"Fact entity {fact.entity_code} does not match source entity {source.entity_code}",
                        fact=fact,
                    )
                )
            status_compatible = fact.data_status == source.data_status or (
                fact.data_status == "derived" and source.data_status in {"official", "synthetic"}
            )
            if not status_compatible:
                results.append(
                    _result(
                        "SOURCE_STATUS_COMPATIBLE",
                        False,
                        f"Fact status {fact.data_status} is incompatible with source status {source.data_status}",
                        fact=fact,
                    )
                )

        if fact.data_status == "synthetic":
            labeled = fact.source_document_id.startswith("SYNTHETIC-") and any(
                token in fact.notes.lower() for token in ("synthetic", "illustrative", "fixture")
            )
            if not labeled:
                results.append(
                    _result(
                        "SYNTHETIC_FACT_LABEL",
                        False,
                        "Synthetic fact must use a SYNTHETIC-* source and an explicit note",
                        fact=fact,
                    )
                )

        if fact.line_item in NON_NEGATIVE_LINE_ITEMS and fact.value < 0:
            results.append(
                _result(
                    "EXPECTED_SIGN",
                    False,
                    f"{fact.line_item} is negative ({fact.value})",
                    severity="warning",
                    fact=fact,
                )
            )
        if fact.line_item in NON_POSITIVE_LINE_ITEMS and fact.value > 0:
            results.append(
                _result(
                    "EXPECTED_SIGN",
                    False,
                    f"{fact.line_item} is positive ({fact.value}); expected an outflow/expense sign",
                    severity="warning",
                    fact=fact,
                )
            )

    period_groups: dict[tuple, dict[str, FinancialFact]] = defaultdict(dict)
    for fact in facts:
        period_groups[fact.period_key][fact.line_item] = fact

    for _, items in period_groups.items():
        reference = next(iter(items.values()))

        if {"total_assets", "total_liabilities", "total_equity"} <= items.keys():
            assets = items["total_assets"].value
            expected_assets = items["total_liabilities"].value + items["total_equity"].value
            passed = _within_tolerance(assets, expected_assets, assets)
            results.append(
                _result(
                    "BALANCE_SHEET_EQUATION",
                    passed,
                    "Assets reconcile to liabilities plus equity"
                    if passed
                    else f"Balance sheet does not reconcile; difference={assets - expected_assets}",
                    fact=reference,
                    context={
                        "assets": assets,
                        "liabilities_plus_equity": expected_assets,
                        "difference": assets - expected_assets,
                    },
                )
            )

        if {"revenue", "cogs", "gross_profit"} <= items.keys():
            gross_profit = items["gross_profit"].value
            expected_gross_profit = items["revenue"].value + items["cogs"].value
            passed = _within_tolerance(
                gross_profit, expected_gross_profit, items["revenue"].value
            )
            results.append(
                _result(
                    "GROSS_PROFIT_RECONCILIATION",
                    passed,
                    "Gross profit reconciles to revenue plus signed COGS"
                    if passed
                    else f"Gross profit does not reconcile; difference={gross_profit - expected_gross_profit}",
                    fact=reference,
                    context={
                        "reported_gross_profit": gross_profit,
                        "calculated_gross_profit": expected_gross_profit,
                    },
                )
            )

        cash_bridge_items = {
            "opening_cash",
            "operating_cash_flow",
            "investing_cash_flow",
            "financing_cash_flow",
            "fx_cash_effect",
            "ending_cash",
        }
        if cash_bridge_items <= items.keys():
            expected_ending_cash = sum(
                (
                    items[item].value
                    for item in (
                        "opening_cash",
                        "operating_cash_flow",
                        "investing_cash_flow",
                        "financing_cash_flow",
                        "fx_cash_effect",
                    )
                ),
                Decimal("0"),
            )
            ending_cash = items["ending_cash"].value
            passed = _within_tolerance(ending_cash, expected_ending_cash, ending_cash)
            results.append(
                _result(
                    "CASH_FLOW_BRIDGE",
                    passed,
                    "Cash-flow movements reconcile opening to ending cash"
                    if passed
                    else f"Cash bridge does not reconcile; difference={ending_cash - expected_ending_cash}",
                    fact=reference,
                    context={
                        "ending_cash": ending_cash,
                        "calculated_ending_cash": expected_ending_cash,
                    },
                )
            )

        if {"cash", "ending_cash"} <= items.keys():
            cash = items["cash"].value
            ending_cash = items["ending_cash"].value
            passed = _within_tolerance(cash, ending_cash, cash)
            results.append(
                _result(
                    "ENDING_CASH_BALANCE_MATCH",
                    passed,
                    "Cash-flow ending cash matches the balance-sheet cash value"
                    if passed
                    else f"Ending cash differs from balance-sheet cash by {ending_cash - cash}",
                    fact=reference,
                )
            )

    results.append(
        _result(
            "FACT_DOMAIN_VALUES",
            not any(r.check_code == "FACT_DOMAIN_VALUES" and not r.passed for r in results),
            "All fact domain values are valid"
            if not any(r.check_code == "FACT_DOMAIN_VALUES" and not r.passed for r in results)
            else "One or more fact domain values are invalid",
        )
    )
    results.append(
        _result(
            "SYNTHETIC_LABELING",
            not any(
                r.check_code in {"SYNTHETIC_FACT_LABEL", "SYNTHETIC_SOURCE_LABEL"}
                and not r.passed
                for r in results
            ),
            "Synthetic observations are explicitly labeled"
            if not any(
                r.check_code in {"SYNTHETIC_FACT_LABEL", "SYNTHETIC_SOURCE_LABEL"}
                and not r.passed
                for r in results
            )
            else "One or more synthetic observations are ambiguously labeled",
        )
    )
    return results


def has_blocking_errors(results: Iterable[ValidationResult]) -> bool:
    return any(result.severity == "error" and not result.passed for result in results)


def validation_summary(results: Iterable[ValidationResult]) -> dict[str, int | bool]:
    results = list(results)
    return {
        "checks": len(results),
        "passed": sum(result.passed for result in results),
        "failed_errors": sum(
            result.severity == "error" and not result.passed for result in results
        ),
        "failed_warnings": sum(
            result.severity == "warning" and not result.passed for result in results
        ),
        "is_valid": not has_blocking_errors(results),
    }
