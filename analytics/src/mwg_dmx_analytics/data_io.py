from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable

from .constants import FACT_REQUIRED_COLUMNS, SOURCE_REQUIRED_COLUMNS
from .types import FinancialFact, SourceDocument


class DataFormatError(ValueError):
    """Raised when an input cannot be parsed into the data contract."""


def _parse_date(value: str, field: str, row_number: int, optional: bool = False) -> date | None:
    value = value.strip()
    if optional and not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise DataFormatError(f"Row {row_number}: invalid {field} ISO date {value!r}") from exc


def _parse_datetime(value: str, field: str, row_number: int) -> datetime | None:
    value = value.strip()
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise DataFormatError(f"Row {row_number}: invalid {field} timestamp {value!r}") from exc


def _read_rows(path: str | Path, required_columns: set[str]) -> list[dict[str, str]]:
    path = Path(path)
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            columns = set(reader.fieldnames or [])
            missing = required_columns - columns
            if missing:
                raise DataFormatError(f"{path}: missing required columns: {sorted(missing)}")
            return [{key: (value or "").strip() for key, value in row.items()} for row in reader]
    except OSError as exc:
        raise DataFormatError(f"Cannot read {path}: {exc}") from exc


def load_financial_facts(path: str | Path) -> list[FinancialFact]:
    rows = _read_rows(path, FACT_REQUIRED_COLUMNS)
    facts: list[FinancialFact] = []
    for row_number, row in enumerate(rows, start=2):
        try:
            value = Decimal(row["value"])
        except Exception as exc:
            raise DataFormatError(
                f"Row {row_number}: invalid numeric value {row['value']!r}"
            ) from exc
        facts.append(
            FinancialFact(
                entity_code=row["entity_code"],
                period_end=_parse_date(row["period_end"], "period_end", row_number),  # type: ignore[arg-type]
                period_type=row["period_type"],
                statement_scope=row["statement_scope"],
                currency=row["currency"],
                unit=row["unit"],
                line_item=row["line_item"],
                value=value,
                data_status=row["data_status"],
                source_document_id=row["source_document_id"],
                source_page=row["source_page"],
                extraction_method=row["extraction_method"],
                notes=row["notes"],
            )
        )
    return facts


def load_source_documents(path: str | Path) -> list[SourceDocument]:
    rows = _read_rows(path, SOURCE_REQUIRED_COLUMNS)
    sources: list[SourceDocument] = []
    for row_number, row in enumerate(rows, start=2):
        sources.append(
            SourceDocument(
                source_document_id=row["source_document_id"],
                entity_code=row["entity_code"],
                document_title=row["document_title"],
                document_type=row["document_type"],
                period_end=_parse_date(row["period_end"], "period_end", row_number, optional=True),
                published_date=_parse_date(
                    row["published_date"], "published_date", row_number, optional=True
                ),
                source_url=row["source_url"],
                retrieved_at=_parse_datetime(row["retrieved_at"], "retrieved_at", row_number),
                sha256=row["sha256"].lower(),
                data_status=row["data_status"],
                notes=row["notes"],
            )
        )
    return sources


def load_json(path: str | Path) -> dict[str, Any]:
    try:
        with Path(path).open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise DataFormatError(f"Cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise DataFormatError(f"{path}: root JSON value must be an object")
    return value


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def to_jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if is_dataclass(value):
        return {key: to_jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_jsonable(item) for item in value]
    return value


def write_json(path: str | Path, value: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(to_jsonable(value), handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")


def write_csv(path: str | Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: to_jsonable(row.get(key)) for key in fieldnames})
