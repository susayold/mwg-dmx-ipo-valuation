# Public data layer

Only redistributable project metadata and curated facts are committed here.

| Path | Purpose |
| --- | --- |
| `source_registry.csv` | 29 source records with issuer, period, scope, audit status, official URL, retrieval time and SHA-256 |
| `processed/dmx_q1_2026_financial_facts.csv` | 210 source-tagged facts extracted from the allowlisted balance sheet, income statement and cash-flow statement |
| `raw/` | Local-only official filings; deliberately excluded from Git |

Curated facts do not replace the original filing. Review source rights and reconcile the registry hash before using downloaded documents.
