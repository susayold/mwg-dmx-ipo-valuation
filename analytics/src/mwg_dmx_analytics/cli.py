from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .data_io import (
    DataFormatError,
    load_financial_facts,
    load_json,
    load_source_documents,
    to_jsonable,
)
from .database import initialize_database
from .dmx_excel import WorkbookFormatError, extract_to_csv
from .pipeline import PipelineValidationError, build_analytics
from .ratios import calculate_ratios
from .validation import has_blocking_errors, validate_dataset, validation_summary
from .valuation import ValuationInputError, run_scenario_config


def _print_json(value: object) -> None:
    print(json.dumps(to_jsonable(value), indent=2, ensure_ascii=False, sort_keys=True))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mwg-dmx-analytics",
        description="Validate financial facts and run ratios/SOTP scenarios",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Run data quality and lineage checks")
    validate.add_argument("--facts", required=True, type=Path)
    validate.add_argument("--sources", required=True, type=Path)

    ratios = subparsers.add_parser("ratios", help="Calculate ratios for one reporting period")
    ratios.add_argument("--facts", required=True, type=Path)
    ratios.add_argument("--entity", required=True)
    ratios.add_argument("--period-end", required=True)
    ratios.add_argument("--period-type", default="FY")
    ratios.add_argument("--scope", default="consolidated")
    ratios.add_argument("--currency")
    ratios.add_argument("--unit")

    sotp = subparsers.add_parser("sotp", help="Run all SOTP scenarios in a JSON config")
    sotp.add_argument("--config", required=True, type=Path)

    build = subparsers.add_parser("build", help="Build the complete curated analytics output")
    build.add_argument("--facts", required=True, type=Path)
    build.add_argument("--sources", required=True, type=Path)
    build.add_argument("--scenarios", required=True, type=Path)
    build.add_argument("--output-dir", required=True, type=Path)
    build.add_argument("--schema", type=Path)
    build.add_argument("--allow-validation-errors", action="store_true")

    init_db = subparsers.add_parser("init-db", help="Create an empty SQLite analytics schema")
    init_db.add_argument("--database", required=True, type=Path)
    init_db.add_argument(
        "--schema", type=Path, default=Path(__file__).resolve().parents[2] / "sql" / "schema.sql"
    )

    extract = subparsers.add_parser(
        "extract-dmx", help="Extract only the three allowlisted DMX financial statement sheets"
    )
    extract.add_argument("--workbook", required=True, type=Path)
    extract.add_argument("--output", required=True, type=Path)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            facts = load_financial_facts(args.facts)
            sources = load_source_documents(args.sources)
            results = validate_dataset(facts, sources)
            _print_json(
                {
                    "summary": validation_summary(results),
                    "results": [result.to_dict() for result in results],
                }
            )
            return 1 if has_blocking_errors(results) else 0

        if args.command == "ratios":
            report = calculate_ratios(
                load_financial_facts(args.facts),
                entity_code=args.entity,
                period_end=args.period_end,
                period_type=args.period_type,
                statement_scope=args.scope,
                currency=args.currency,
                unit=args.unit,
            )
            _print_json(report)
            return 0

        if args.command == "sotp":
            _print_json(run_scenario_config(load_json(args.config)))
            return 0

        if args.command == "build":
            result = build_analytics(
                facts_path=args.facts,
                sources_path=args.sources,
                scenarios_path=args.scenarios,
                output_dir=args.output_dir,
                schema_path=args.schema,
                allow_validation_errors=args.allow_validation_errors,
            )
            _print_json(result)
            return 0

        if args.command == "init-db":
            connection = initialize_database(args.database, args.schema)
            connection.close()
            _print_json({"database": str(args.database.resolve()), "initialized": True})
            return 0

        if args.command == "extract-dmx":
            row_count = extract_to_csv(args.workbook, args.output)
            _print_json(
                {
                    "output": str(args.output.resolve()),
                    "rows": row_count,
                    "sheets_read": [
                        "Balance Sheet",
                        "Income Statement",
                        "Cash Flow Statement",
                    ],
                }
            )
            return 0

    except PipelineValidationError as exc:
        _print_json(
            {
                "error": str(exc),
                "summary": validation_summary(exc.results),
                "failed_checks": [
                    result.to_dict()
                    for result in exc.results
                    if result.severity == "error" and not result.passed
                ],
            }
        )
        return 1
    except (DataFormatError, ValuationInputError, WorkbookFormatError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    parser.error(f"Unsupported command {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
