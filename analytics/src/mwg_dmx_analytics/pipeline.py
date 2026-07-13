from __future__ import annotations

import os
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .data_io import (
    file_sha256,
    load_financial_facts,
    load_json,
    load_source_documents,
    to_jsonable,
    write_csv,
    write_json,
)
from .database import (
    complete_run,
    initialize_database,
    insert_facts,
    insert_sources,
    insert_validation_results,
    insert_valuation_results,
    start_run,
)
from .ratios import calculate_ratios
from .validation import has_blocking_errors, validate_dataset, validation_summary
from .valuation import run_scenario_config


@dataclass(frozen=True, slots=True)
class BuildResult:
    run_id: str
    output_dir: Path
    database_path: Path
    validation_summary: dict
    ratios_count: int
    scenarios_count: int


class PipelineValidationError(ValueError):
    def __init__(self, results: list):
        self.results = results
        summary = validation_summary(results)
        super().__init__(
            f"Input validation failed with {summary['failed_errors']} blocking error(s)"
        )


def _default_schema_path() -> Path:
    return Path(__file__).resolve().parents[2] / "sql" / "schema.sql"


def _validation_csv_rows(results: list) -> list[dict]:
    return [
        {
            "check_code": result.check_code,
            "severity": result.severity,
            "passed": str(result.passed).lower(),
            "message": result.message,
            "entity_code": result.entity_code or "",
            "period_end": result.period_end.isoformat() if result.period_end else "",
            "context": str(to_jsonable(result.context)),
        }
        for result in results
    ]


def _ratio_reports(facts: list) -> list:
    keys = sorted(
        {
            (
                fact.entity_code,
                fact.period_end,
                fact.period_type,
                fact.statement_scope,
                fact.currency,
                fact.unit,
            )
            for fact in facts
            if fact.line_item == "revenue"
        }
    )
    return [
        calculate_ratios(
            facts,
            entity_code=entity_code,
            period_end=period_end,
            period_type=period_type,
            statement_scope=scope,
            currency=currency,
            unit=unit,
        )
        for entity_code, period_end, period_type, scope, currency, unit in keys
    ]


def build_analytics(
    *,
    facts_path: str | Path,
    sources_path: str | Path,
    scenarios_path: str | Path,
    output_dir: str | Path,
    schema_path: str | Path | None = None,
    allow_validation_errors: bool = False,
) -> BuildResult:
    facts_path = Path(facts_path).resolve()
    sources_path = Path(sources_path).resolve()
    scenarios_path = Path(scenarios_path).resolve()
    output_dir = Path(output_dir).resolve()
    schema_path = Path(schema_path).resolve() if schema_path else _default_schema_path()

    facts = load_financial_facts(facts_path)
    sources = load_source_documents(sources_path)
    scenario_config = load_json(scenarios_path)
    validations = validate_dataset(facts, sources)
    if has_blocking_errors(validations) and not allow_validation_errors:
        raise PipelineValidationError(validations)

    ratio_reports = _ratio_reports(facts)
    scenario_output = run_scenario_config(scenario_config)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    output_dir.mkdir(parents=True, exist_ok=True)

    validation_path = output_dir / "validation_results.csv"
    ratios_path = output_dir / "ratios.json"
    sotp_path = output_dir / "sotp_results.json"
    database_path = output_dir / "analytics.sqlite"
    manifest_path = output_dir / "run_manifest.json"

    write_csv(
        validation_path,
        _validation_csv_rows(validations),
        [
            "check_code",
            "severity",
            "passed",
            "message",
            "entity_code",
            "period_end",
            "context",
        ],
    )
    write_json(ratios_path, ratio_reports)
    write_json(sotp_path, scenario_output)

    temporary = tempfile.NamedTemporaryFile(
        prefix="analytics-", suffix=".sqlite", dir=output_dir, delete=False
    )
    temporary_path = Path(temporary.name)
    temporary.close()
    try:
        connection = initialize_database(temporary_path, schema_path)
        try:
            start_run(
                connection,
                run_id=run_id,
                engine_version=__version__,
                facts_sha256=file_sha256(facts_path),
                sources_sha256=file_sha256(sources_path),
                assumptions_sha256=file_sha256(scenarios_path),
            )
            insert_sources(connection, sources)
            insert_facts(connection, facts)
            insert_validation_results(connection, run_id, validations)
            insert_valuation_results(connection, run_id, scenario_output)
            complete_run(connection, run_id)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        os.replace(temporary_path, database_path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()

    output_files = [database_path, validation_path, ratios_path, sotp_path]
    manifest = {
        "run_id": run_id,
        "engine_version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_notice": scenario_config["metadata"].get("warning", ""),
        "inputs": {
            "financial_facts": {"path": str(facts_path), "sha256": file_sha256(facts_path)},
            "source_documents": {
                "path": str(sources_path),
                "sha256": file_sha256(sources_path),
            },
            "scenario_assumptions": {
                "path": str(scenarios_path),
                "sha256": file_sha256(scenarios_path),
            },
        },
        "outputs": {
            path.name: {"path": str(path), "sha256": file_sha256(path)}
            for path in output_files
        },
        "validation": validation_summary(validations),
    }
    write_json(manifest_path, manifest)

    return BuildResult(
        run_id=run_id,
        output_dir=output_dir,
        database_path=database_path,
        validation_summary=validation_summary(validations),
        ratios_count=len(ratio_reports),
        scenarios_count=len(scenario_output["scenarios"]),
    )
