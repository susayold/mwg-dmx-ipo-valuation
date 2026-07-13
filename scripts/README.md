# Reproducible build scripts

| Script | Responsibility |
| --- | --- |
| `fetch_sources.py` | Validate the source plan, download HTTPS filings into ignored `data/raw/` and verify SHA-256 |
| `build_financial_model.py` | Generate the auditable Excel workbook and copy the public model artifact |
| `build_reports.py` | Generate the memo PDF, validation HTML, curated-data copy and artifact manifest |

Run scripts from the repository root. Build outputs are deterministic with respect to the committed facts and assumptions, subject to generated timestamps documented in the manifest.
