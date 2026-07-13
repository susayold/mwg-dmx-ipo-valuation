from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any


@dataclass(frozen=True, slots=True)
class SourceDocument:
    source_document_id: str
    entity_code: str
    document_title: str
    document_type: str
    period_end: date | None
    published_date: date | None
    source_url: str
    retrieved_at: datetime | None
    sha256: str
    data_status: str
    notes: str = ""


@dataclass(frozen=True, slots=True)
class FinancialFact:
    entity_code: str
    period_end: date
    period_type: str
    statement_scope: str
    currency: str
    unit: str
    line_item: str
    value: Decimal
    data_status: str
    source_document_id: str
    source_page: str
    extraction_method: str
    notes: str = ""

    @property
    def natural_key(self) -> tuple[str, date, str, str, str, str, str]:
        return (
            self.entity_code,
            self.period_end,
            self.period_type,
            self.statement_scope,
            self.currency,
            self.unit,
            self.line_item,
        )

    @property
    def period_key(self) -> tuple[str, date, str, str, str, str]:
        return (
            self.entity_code,
            self.period_end,
            self.period_type,
            self.statement_scope,
            self.currency,
            self.unit,
        )


@dataclass(frozen=True, slots=True)
class ValidationResult:
    check_code: str
    severity: str
    passed: bool
    message: str
    entity_code: str | None = None
    period_end: date | None = None
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_code": self.check_code,
            "severity": self.severity,
            "passed": self.passed,
            "message": self.message,
            "entity_code": self.entity_code,
            "period_end": self.period_end,
            "context": self.context,
        }


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
