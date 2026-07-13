from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .data_io import to_jsonable
from .types import FinancialFact, SourceDocument, ValidationResult


def initialize_database(database_path: str | Path, schema_path: str | Path) -> sqlite3.Connection:
    database_path = Path(database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    with Path(schema_path).open("r", encoding="utf-8") as handle:
        connection.executescript(handle.read())
    return connection


def insert_sources(
    connection: sqlite3.Connection, sources: Iterable[SourceDocument]
) -> None:
    connection.executemany(
        """
        INSERT INTO source_documents (
            source_document_id, entity_code, document_title, document_type,
            period_end, published_date, source_url, retrieved_at, sha256,
            data_status, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                source.source_document_id,
                source.entity_code,
                source.document_title,
                source.document_type,
                source.period_end.isoformat() if source.period_end else None,
                source.published_date.isoformat() if source.published_date else None,
                source.source_url or None,
                source.retrieved_at.isoformat() if source.retrieved_at else None,
                source.sha256 or None,
                source.data_status,
                source.notes,
            )
            for source in sources
        ],
    )


def insert_facts(connection: sqlite3.Connection, facts: Iterable[FinancialFact]) -> None:
    loaded_at = datetime.now(timezone.utc).isoformat()
    connection.executemany(
        """
        INSERT INTO financial_facts (
            entity_code, period_end, period_type, statement_scope, currency,
            unit, line_item, value, data_status, source_document_id, source_page,
            extraction_method, notes, loaded_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                fact.entity_code,
                fact.period_end.isoformat(),
                fact.period_type,
                fact.statement_scope,
                fact.currency,
                fact.unit,
                fact.line_item,
                str(fact.value),
                fact.data_status,
                fact.source_document_id,
                fact.source_page or None,
                fact.extraction_method,
                fact.notes,
                loaded_at,
            )
            for fact in facts
        ],
    )


def insert_validation_results(
    connection: sqlite3.Connection,
    run_id: str,
    results: Iterable[ValidationResult],
) -> None:
    checked_at = datetime.now(timezone.utc).isoformat()
    connection.executemany(
        """
        INSERT INTO validation_results (
            run_id, check_code, severity, passed, message, entity_code,
            period_end, context_json, checked_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                run_id,
                result.check_code,
                result.severity,
                int(result.passed),
                result.message,
                result.entity_code,
                result.period_end.isoformat() if result.period_end else None,
                json.dumps(to_jsonable(result.context), sort_keys=True),
                checked_at,
            )
            for result in results
        ],
    )


def start_run(
    connection: sqlite3.Connection,
    *,
    run_id: str,
    engine_version: str,
    facts_sha256: str,
    sources_sha256: str,
    assumptions_sha256: str | None,
) -> None:
    connection.execute(
        """
        INSERT INTO analytics_runs (
            run_id, engine_version, started_at, status, facts_sha256,
            sources_sha256, assumptions_sha256
        ) VALUES (?, ?, ?, 'running', ?, ?, ?)
        """,
        (
            run_id,
            engine_version,
            datetime.now(timezone.utc).isoformat(),
            facts_sha256,
            sources_sha256,
            assumptions_sha256,
        ),
    )


def complete_run(connection: sqlite3.Connection, run_id: str, status: str = "completed") -> None:
    connection.execute(
        "UPDATE analytics_runs SET status = ?, completed_at = ? WHERE run_id = ?",
        (status, datetime.now(timezone.utc).isoformat(), run_id),
    )


def insert_valuation_results(
    connection: sqlite3.Connection,
    run_id: str,
    scenario_output: dict,
) -> None:
    metadata = scenario_output["metadata"]
    currency = str(metadata["currency"])
    unit = str(metadata["unit"])
    per_share_unit = str(metadata.get("per_share_unit", f"{currency}_per_share"))
    rows: list[tuple] = []
    for scenario in scenario_output["scenarios"]:
        name = scenario["name"]
        for unit_result in scenario["units"]:
            rows.extend(
                [
                    (
                        run_id,
                        name,
                        unit_result.code,
                        "enterprise_value",
                        str(unit_result.enterprise_value),
                        currency,
                        unit,
                        json.dumps(to_jsonable(unit_result.assumptions), sort_keys=True),
                    ),
                    (
                        run_id,
                        name,
                        unit_result.code,
                        "attributable_equity_value",
                        str(unit_result.attributable_equity_value),
                        currency,
                        unit,
                        json.dumps(
                            to_jsonable(
                                {
                                    "ownership_pct": unit_result.ownership_pct,
                                    "net_debt": unit_result.net_debt,
                                    "non_operating_assets": unit_result.non_operating_assets,
                                    "minority_interest": unit_result.minority_interest,
                                }
                            ),
                            sort_keys=True,
                        ),
                    ),
                ]
            )
        summary_assumptions = {
            "holding_company_discount_pct": scenario["holding_company_discount_pct"],
            "parent_net_debt": scenario["parent_net_debt"],
            "parent_non_operating_assets": scenario["parent_non_operating_assets"],
            "shares_outstanding": scenario["shares_outstanding"],
        }
        rows.append(
            (
                run_id,
                name,
                None,
                "equity_value_after_discount",
                str(scenario["equity_value_after_discount"]),
                currency,
                unit,
                json.dumps(to_jsonable(summary_assumptions), sort_keys=True),
            )
        )
        rows.append(
            (
                run_id,
                name,
                None,
                "implied_value_per_share",
                str(scenario["implied_value_per_share"]),
                currency,
                per_share_unit,
                json.dumps(to_jsonable(summary_assumptions), sort_keys=True),
            )
        )
    connection.executemany(
        """
        INSERT INTO valuation_results (
            run_id, scenario_name, unit_code, result_type, amount, currency,
            unit, assumptions_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
