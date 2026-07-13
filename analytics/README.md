# MWG–DMX Analytics Engine

This folder contains the reproducible analytics layer for the MWG–DMX IPO and
sum-of-the-parts case study. It is deliberately independent from the web app:
the core engine uses only the Python standard library and SQLite. The official
DMX Excel adapter has one optional dependency (`openpyxl`).

> **Data notice:** every CSV and JSON file committed under `data/sample/` is a
> synthetic fixture for testing the workflow. It is not a company disclosure,
> investment research, or investment advice. Official figures must be added
> with a source document, retrieval timestamp, and document hash.

## What it does

- Stores source documents and normalized financial facts in SQLite.
- Preserves row-level source lineage (`source_document_id`, page and extraction
  method).
- Runs accounting, schema, duplicate, type, and lineage checks.
- Calculates profitability, return, leverage, liquidity, cash-conversion and
  working-capital ratios.
- Runs multiple-based or DCF unit valuations and reconciles a parent SOTP.
- Executes bear/base/bull scenarios from a versioned JSON assumption file.
- Produces machine-readable JSON and CSV artifacts with input hashes.

## Quick start

From this `analytics` directory:

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v

mwg-dmx-analytics validate `
  --facts data/sample/financial_facts_sample.csv `
  --sources data/sample/source_documents_sample.csv

mwg-dmx-analytics ratios `
  --facts data/sample/financial_facts_sample.csv `
  --entity SYNTH_MWG_GROUP `
  --period-end 2025-12-31

mwg-dmx-analytics sotp `
  --config data/sample/sotp_scenarios_sample.json

mwg-dmx-analytics build `
  --facts data/sample/financial_facts_sample.csv `
  --sources data/sample/source_documents_sample.csv `
  --scenarios data/sample/sotp_scenarios_sample.json `
  --output-dir data/curated/demo

# From the repository root, extract the allowlisted official DMX statements.
python -m pip install -e "analytics[xlsx]"
mwg-dmx-analytics extract-dmx `
  --workbook data/raw/dmx/dmx_q1_2026_data_pack.xlsx `
  --output data/processed/dmx_q1_2026_financial_facts.csv
```

On macOS/Linux, replace PowerShell backticks with backslashes or put each
command on one line.

The `build` command stops before publishing outputs if an error-level data
quality check fails. Add `--allow-validation-errors` only while debugging.

## Production data contract

`financial_facts.csv` is long-form. One row represents one normalized line
item for one entity, reporting period, reporting scope and currency/unit.

Required fields:

| Field | Meaning |
| --- | --- |
| `entity_code` | Stable internal entity key, e.g. `MWG` or `DMX` |
| `period_end` | ISO date (`YYYY-MM-DD`) |
| `period_type` | `FY`, `Q1`, `Q2`, `Q3`, `Q4`, `H1`, `9M`, or `LTM` |
| `statement_scope` | `consolidated`, `separate`, or `carve_out` |
| `currency` / `unit` | Reported currency and multiplier (`VND`, `VND_mn`, `VND_bn`) |
| `line_item` | Canonical item from the supported taxonomy |
| `value` | Signed numeric value; outflows remain negative |
| `data_status` | `official`, `derived`, or `synthetic` |
| `source_document_id` | Foreign key to the source manifest |
| `source_page` | Page reference when applicable |
| `extraction_method` | `manual`, `table_extract`, `ocr`, `api`, or `calculated` |

Production loaders should preserve reported values in a raw staging layer and
write only normalized values to `financial_facts`. Never overwrite a restated
period: register the new source and load a new fact version.

## Official-data workflow

1. Download the disclosure from the issuer/HOSE investor-relations page.
2. Record URL, publication date, retrieval time and SHA-256 in the source
   manifest.
3. Extract the consolidated statements without changing signs or units.
4. Map labels to the canonical taxonomy and retain the source page.
5. Run `validate`; investigate every error and document warnings.
6. Lock actuals, version assumptions, then run `build`.

The sample values must never be relabelled `official`. Replace the entire
sample row with a sourced observation instead.

### DMX workbook safety boundary

`extract-dmx` reads only `Balance Sheet`, `Income Statement`, and
`Cash Flow Statement`. The allowlist is a constant in the adapter; `config`,
`notes`, and any future workbook tabs are ignored. The resulting CSV contains
only `statement,line_item,period,value_vnd,source_id`. Float values from Excel
are rounded to the nearest whole VND because the workbook declares VND as its
unit. The `source_id` embeds the full SHA-256 of the raw workbook for
traceability; raw workbooks are excluded from Git.

## Output contract

`build` creates:

- `analytics.sqlite`: normalized source and fact tables plus validation rows.
- `validation_results.csv`: auditable check results.
- `ratios.json`: ratios by entity and period.
- `sotp_results.json`: scenario valuation bridge.
- `run_manifest.json`: engine version, UTC timestamp and SHA-256 for every
  input and output.

Amounts retain their input unit. A valuation scenario must use one consistent
currency and unit across all business units and parent adjustments. In the
sample SOTP, amounts are VND billion and shares are billion shares, so the
quotient is directly VND per share.
