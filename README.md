# MWG–DMX IPO Valuation Lab

[![CI](https://github.com/susayold/mwg-dmx-ipo-valuation/actions/workflows/ci.yml/badge.svg)](https://github.com/susayold/mwg-dmx-ipo-valuation/actions/workflows/ci.yml)
[![GitHub Pages](https://img.shields.io/badge/Live%20portfolio-GitHub%20Pages-DDFC3B?style=flat&labelColor=0B1714)](https://susayold.github.io/mwg-dmx-ipo-valuation/)
[![License: MIT](https://img.shields.io/badge/Code-MIT-FF5B40.svg)](LICENSE)

An end-to-end financial-analysis portfolio project covering the completed Điện Máy Xanh (DMX) IPO, a FY2023–FY2025 three-statement review, Q1 2026 trend update, financial-statement normalization and a scenario-based sum-of-the-parts valuation of Mobile World Investment Corporation (MWG).

> **Tóm tắt:** Dự án biến nguồn công bố chính thức thành dữ liệu tài chính có thể truy vết, đối chiếu kết quả IPO thực tế, khóa các lỗi double-count trong DCF/SOTP và đóng gói kết quả thành Excel model, investment memo, validation artifacts và website tương tác.

**Data cut-off:** 13 July 2026 · **Currency:** VND billion unless stated otherwise · **Status:** Independent analyst work sample; not investment advice.

![MWG after the DMX IPO](public/og.png)

## Recruiter quick tour

| Start here | What it demonstrates |
| --- | --- |
| [Live portfolio](https://susayold.github.io/mwg-dmx-ipo-valuation/) | Research narrative and interactive Bear/Base/Bull SOTP |
| [Excel financial model](model/MWG_DMX_IPO_SOTP_Model.xlsx) | Three-year statements, accounting bridges, working-capital/QoE schedules, IPO bridge, DCF, SOTP and QA |
| [Research memo](reports/RESEARCH_REPORT.md) | Long-form investment analysis and limitations |
| [Source registry](data/source_registry.csv) | 29 official-source records with scope, audit status, URL and SHA-256 |
| [Three-statement dataset](data/processed/dmx_three_statement_facts.csv) | 320 source-tagged facts covering FY2023–FY2025 and Q1 2026 |
| [Generated analysis payload](data/processed/dmx_three_statement_analysis.json) | Statements, bridges, WC/CCC, QoE, normalization and 35 accounting checks |
| [Curated Q1 facts](data/processed/dmx_q1_2026_financial_facts.csv) | 210 source-tagged Q1 facts from allowlisted statements |
| [Validation report](public/downloads/validation_report.html) | Accounting and data-quality checks |
| [Analytics engine](analytics/) | Python/SQLite normalization, ratios, validation and valuation logic |

The root [`index.html`](index.html) is intentionally standalone: it opens directly without Node.js or Python and is the exact entry point deployed by GitHub Pages.

## Why this case?

The completed DMX primary offering creates a visible transaction anchor inside MWG, but it does not answer whether MWG is attractively valued. The post-IPO question is:

```text
MWG equity value
= value of MWG's DMX stake
+ value of the non-DMX stub
+ parent-level adjustments
```

This case combines four problems normally handled separately:

1. Normalize financial statements while preserving source lineage.
2. Reconcile planned offer terms with the actual transaction close.
3. Prove the post-restructuring perimeter before applying DCF/SOTP.
4. Productize the analysis as auditable code, Excel, memo and web outputs.

The key perimeter control is EraBlue: the equity-accounted joint venture sits inside DMX and is valued once. It is never added again to the MWG stub.

## What I built

This repository is designed to show the work of a financial analyst, not only the final valuation number. The contribution includes:

- building a source registry with document hashes, audit status, statement scope and page/sheet locators;
- standardizing 320 financial facts from three annual periods and the latest available quarter;
- reconciling NPAT to CFO, opening cash to closing cash, and retained earnings across periods;
- calculating DIO, DSO, DPO, cash conversion cycle, CFO/NPAT, inventory-provision coverage and CapEx/revenue;
- separating statutory reported results, management like-for-like comparators, guidance and analyst assumptions;
- implementing an IPO proceeds bridge and controls against double-counting cash or EraBlue;
- packaging the analysis into a reproducible Excel model, research memo, validation artifacts and portfolio website.

In a CV or interview, the project can be described as: **“Built an auditable three-statement and SOTP analysis for the DMX IPO using official filings; normalized 320 financial facts, automated 35 accounting checks, analyzed working-capital and earnings quality, and delivered the result through Python, Excel and an interactive web portfolio.”** This describes the work product; it does not imply employment by MWG, DMX or a securities firm.

## Verified transaction snapshot

| Metric | Actual close |
| --- | ---: |
| IPO offer price | VND 80,000/share |
| Successfully issued shares | 166,438,500 |
| Post-offer shares | 1,267,722,000 |
| Gross proceeds | VND 13,315.080bn |
| Estimated issue costs | VND 100.000bn |
| Estimated net proceeds | VND 13,215.080bn |
| Post-money value at the offer price | VND 101,417.760bn |
| MWG ownership disclosure | “Nearly 86%” |

The model uses the final allocation, not the planned 179.5 million-share maximum. The 13.1 million unallocated shares are excluded from post-offer capital. Resolution 15 discloses estimated net proceeds of VND 13,215.080bn—gross proceeds of VND 13,315.080bn less VND 100.000bn of estimated issuance costs—and a plan to use that amount to repay debt during 2026. The valuation treats this as a **pro forma transaction adjustment**, not evidence that repayment had already been disbursed at the data cut-off. “Nearly 86%” remains a rounded disclosure; calculations labelled `~86%` are model approximations, not an exact shareholder-register result.

## Operating evidence

| Q1 metric | 2025 | 2026 | Change |
| --- | ---: | ---: | ---: |
| Revenue | 25,153.56 | 32,541.95 | +29.4% |
| Gross profit | 4,526.17 | 6,241.22 | +37.9% |
| Gross margin | 17.99% | 19.18% | +118 bps |
| NPAT | 1,478.38 | 2,218.57 | +50.1% |
| CFO | 2,477.05 | 863.69 | CFO/NPAT = 38.9% |

The earnings signal is constructive, but cash conversion is the main watchpoint. The analysis therefore reads margin expansion together with inventory, supplier funding, receivables and seasonality rather than treating NPAT growth as a complete conclusion.

The issuer's six-month update reported VND 65,279bn of revenue, 32% same-store sales growth and 53% completion of annual revenue guidance. These figures remain labelled as an unaudited issuer operating update, not a complete H1 financial-statement set.

## Three-statement analysis

### Coverage and assurance

| Period | Income statement | Balance sheet | Cash flow | Status |
| --- | --- | --- | --- | --- |
| FY2023 | Full year | 31 Dec 2023 | Full year | Comparative column in the FY2024 filing; expressly unaudited |
| FY2024 | Full year | 31 Dec 2024 | Full year | Audited consolidated statements |
| FY2025 | Full year | 31 Dec 2025 | Full year | Audited consolidated statements |
| Q1 2026 | Three months | 31 Mar 2026 | Three months YTD | Unaudited consolidated data pack |
| H1 2026 | Operating KPIs only | — | — | No complete H1 statements available at the cut-off |

Q1 is used only as a latest-trend update. It is not treated as a substitute for a full year when evaluating seasonality, inventory cycles, margin durability, CapEx/depreciation or debt policy.

### Linked-statement controls

The module proves that the statements work as one accounting system through three explicit bridges:

```text
NPAT + non-cash items ± working-capital movements − interest/tax paid = CFO
Opening cash + CFO + CFI + CFF + FX = Closing cash
Opening retained earnings + NPAT - dividends +/- residual equity movements = Closing retained earnings
```

All 35 generated accounting checks pass. The retained-earnings schedule is deliberately labelled as a **residual reconciliation**, not an independent statement-of-changes-in-equity rebuild. The FY2025 bridge separately identifies VND 6,542.278bn of capitalisation/other equity movements; it is not recast as an operating adjustment.

### Working capital and earnings quality

| Metric | FY2024 | FY2025 | Q1 2026 YTD |
| --- | ---: | ---: | ---: |
| DIO | 88.0 days | 83.6 days | 78.4 days |
| DSO | 1.1 days | 1.1 days | 1.0 days |
| DPO | 28.3 days | 32.5 days | 31.3 days |
| Cash conversion cycle | 60.8 days | 52.1 days | 48.0 days |
| CFO / NPAT | 168.0% | 86.5% | 38.9% |
| Inventory provision / gross inventory | 2.24% | 2.61% | 3.15% |
| CapEx / revenue | 0.08% | 0.12% | 0.36% |

The Q1 day metrics use average opening/closing balances and the actual 90-day period. They are **not annual forecasts** and should not be compared mechanically with full-year ratios. The most important Q1 cash-flow signal is the VND 465.977bn cash outflow from lower payables, reversing the supplier-funding contribution seen in Q1 2025. This explains more of the CFO/NPAT deterioration than receivables alone.

The normalization policy is deliberately conservative. Reported FY2025 revenue and NPAT remain intact; management's VND 107,000bn revenue and VND 6,075bn NPAT are stored as separate LFL comparators. Operating profit, excess cash and adjusted net debt remain unadjusted where disclosure is insufficient.

## Valuation framework

The public case deliberately separates:

- **Official actuals:** reported figures are not altered to fit a forecast.
- **Issuer operating updates:** LFL operating evidence is kept separate from statutory statements.
- **Management projections:** the 2026–2030 path is not relabelled as an analyst forecast.
- **Analyst assumptions:** WACC, terminal growth, multiples, stub values and discounts remain editable scenarios.

The Excel model includes:

- a planned-versus-actual IPO bridge;
- FY2023–FY2025 comparative statements and Q1 2026 actuals;
- NPAT-to-CFO, cash-roll and retained-earnings residual bridges;
- working-capital, cash-conversion and quality-of-earnings schedules;
- a documented normalization table that permits `not adjusted` where evidence is insufficient;
- management revenue, NPAT and gross-margin references;
- an illustrative FCFF DCF with mid-year convention;
- an equity-level MWG SOTP;
- Bear/Base/Bull cases and sensitivity matrices;
- 21 QA/publication controls, including a check that Base scenario DMX equity value matches the active Base DCF bridge.

No target price, upside/downside or investment rating is published because same-date market price, exact diluted share count and exact post-IPO ownership are not all verified on one basis.

### Illustrative website P/E scenario output

| Scenario | DMX NPAT | P/E | DMX equity value | MWG share at ~86% | Non-DMX stub | Parent adjustments | Illustrative MWG equity value |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Bear | 6,700 | 10.0x | 67,000 | 57,620 | 28,000 | (8,000) | 77,620 |
| Base | 7,350 | 12.3x | 90,405 | 77,748.3 | 45,000 | (5,000) | 117,748.3 |
| Bull | 8,000 | 14.0x | 112,000 | 96,320 | 65,000 | (3,000) | 158,320 |

These are editable VND billion scenarios, not a target price, rating or market-based upside/downside conclusion.

### Illustrative FCFF DCF output

| Scenario | Enterprise value | Equity value | Value per share | Terminal value / EV |
| --- | ---: | ---: | ---: | ---: |
| Bear | 77,784.4 | 99,908.5 | 78,809 | 65.8% |
| Base | 131,814.8 | 154,438.9 | 121,824 | 72.7% |
| Bull | 198,485.9 | 221,610.0 | 174,810 | 77.7% |

The FCFF DCF bridge uses pre-IPO Q1 2026 cash/debt and adds the estimated VND 13,215.080bn net IPO proceeds once through `IPO_Bridge!D20`. The website P/E scenario above is a separate lightweight SOTP illustration.

## Data architecture

```text
DMX / MWG / SSC official disclosures
                │
                ▼
data/source_registry.csv
URL · period · scope · audit status · retrieval time · SHA-256
                │
                ├── data/raw/                         local only; git-ignored
                │
                ▼
Allowlisted Excel extractor
Balance Sheet · Income Statement · Cash Flow Statement
                │
                ▼
Source-tagged curated facts
                │
                ├── three-year statements and latest-quarter update
                ├── NPAT→CFO, cash-roll and retained-earnings residual bridges
                ├── working-capital, CCC and earnings-quality schedules
                ├── accounting and lineage validation
                ├── ratios and SQLite audit trail
                ├── DCF/SOTP scenario engine
                ├── generated Excel and research artifacts
                └── standalone and React web presentations
```

Core controls include:

- assets = liabilities + equity;
- revenue + signed COGS = gross profit;
- opening cash + movements + FX = ending cash;
- opening retained earnings + NPAT - dividends + residual equity movements = ending retained earnings;
- duplicate natural keys and missing source references;
- consolidated versus separate-statement scope;
- IPO share/proceeds identities;
- unique SOTP double-count buckets;
- WACC greater than terminal growth;
- IPO cash included once;
- market-conclusion publication gate.

## Repository structure

```text
.
├── index.html                    # GitHub Pages entry point and interactive SOTP
├── README.md                     # Project overview and reproduction guide
├── LICENSE                       # MIT license for original code/content
├── CONTRIBUTING.md               # Source, model and review conventions
├── .github/workflows/
│   ├── ci.yml                    # Web/Python tests and artifact rebuild
│   └── pages.yml                 # Standalone portfolio deployment
├── app/                          # React/Vinext research application
│   ├── components/               # Interactive valuation component
│   └── data/                     # Typed public case data
├── analytics/                    # Installable Python analytics package
│   ├── src/                      # Validation, ratios, database and valuation
│   ├── tests/                    # Unit/integration tests, including three-statement checks
│   ├── data/sample/              # Clearly labelled synthetic fixtures
│   └── sql/                      # SQLite schema
├── data/
│   ├── source_registry.csv       # Source manifest and document hashes
│   └── processed/                # Curated facts, normalization table and generated 3S payload
├── docs/                         # Data scope, methodology and model contract
├── model/                        # Generated auditable Excel workbook
├── public/
│   ├── downloads/                # Model, memo, facts and validation artifacts
│   ├── favicon.svg
│   └── og.png
├── reports/                      # Long-form research memo
├── scripts/
│   ├── fetch_sources.py          # HTTPS download and SHA-256 verification
│   ├── build_three_statement_analysis.py # Generate statements, bridges, WC/QoE and checks
│   ├── build_financial_model.py  # Reproducible Excel builder
│   └── build_reports.py          # PDF/HTML/manifest builder
├── tests/                        # Rendered and standalone web tests
└── worker/                       # Cloudflare-compatible React entry point
```

The main analysis-facing folders contain short README files describing their public purpose and review path.

## Reproduce locally

### Requirements

- Node.js `>=24.0.0`
- Python `>=3.11` (CI uses Python 3.12)

### Open the portfolio without installing anything

Open [`index.html`](index.html) in a browser.

### Build and test the React application

```bash
npm ci
npm test
npm run lint
```

### Run the analytics engine

```bash
python -m venv .venv
# PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e "analytics[xlsx]"
python -m unittest discover -s analytics/tests -v
```

### Validate the source-download plan

```bash
python scripts/fetch_sources.py --dry-run
```

The downloader accepts HTTPS only, writes only inside ignored `data/raw/`, enforces a size limit and publishes a file only after its SHA-256 matches the registry. Review the source owner's terms before downloading or using any filing.

### Rebuild the Excel model and reports

```bash
python -m pip install -r requirements-artifacts.txt
python scripts/build_three_statement_analysis.py
python scripts/build_financial_model.py
python scripts/build_reports.py
```

Generated outputs:

- `model/MWG_DMX_IPO_SOTP_Model.xlsx`
- `public/downloads/MWG_DMX_IPO_SOTP_Model.xlsx`
- `public/downloads/Investment_Memo_EN.pdf`
- `public/downloads/validation_report.html`
- `public/downloads/dmx_q1_2026_financial_facts.csv`
- `public/downloads/dmx_three_statement_analysis.json`
- `public/downloads/dmx_three_statement_facts.csv`
- `public/downloads/dmx_normalization_adjustments.csv`
- `public/downloads/three_statement_manifest.json`
- `public/downloads/artifacts_manifest.json`

## Tests and continuous integration

The current public suite contains:

- Python tests for extraction boundaries, validation, ratios, SQLite, valuation and three-statement bridges;
- **4 web/static tests** for rendered research content, standalone JavaScript and local artifact links;
- workbook build checks for required sheets, formula integrity, comments and external links;
- **35 generated three-statement accounting checks** with zero failures in the committed payload;
- report validation and SHA-256 artifact manifests.

GitHub Actions runs tests, linting, source-plan validation, model/report rebuild and required-artifact checks. A separate Pages workflow publishes only the recruiter-facing HTML/assets/downloads.

## Known limitations

- Data is frozen at 13 July 2026 and must be refreshed for later use.
- Exact MWG ownership is not inferred from the rounded “nearly 86%” announcement.
- The 2026–2030 figures are management projections, not independent forecasts.
- The public case does not claim a fully integrated three-statement segment forecast.
- Q1 2026 is a 90-day unaudited update; its CCC and cash-conversion ratios are seasonal observations, not full-year run rates.
- FY2023 appears as an expressly unaudited comparative column in the FY2024 filing.
- Resolution 15's net-proceeds use is modelled pro forma; the project does not claim the planned debt repayment had been completed at the cut-off.
- Non-DMX businesses need deeper standalone forecasts and same-date peer inputs.
- The valuation outputs are scenario illustrations, not target prices or recommendations.
- Raw issuer filings are intentionally excluded from Git and must be obtained from their official owners.

## Primary official sources

- [DMX Investor Relations — reports](https://www.dmx.vn/eng/reports)
- [DMX — completed IPO announcement](https://www.dmx.vn/eng/news/dien-may-xanh-completes-landmark-ipo-raising-more-than-vnd-13-315-billion-and-lifting-charter-capital-to-vnd-12-677-billion-5002485)
- [DMX — offering documents and prospectus](https://www.dmx.vn/cong-bo-thong-tin/cbtt-thong-bao-chao-ban-co-phieu-ra-cong-chung-va-cac-tai-lieu-lien-quan-cua-ctcp-dau-tu-dien-may-xanh-5005813)
- [DMX — Resolution 15 on estimated net proceeds and use of proceeds](https://cdnv2-tmdt.tgdd.vn/mwgvn/investorrelations/files/posts/2026/7/0/38/65/38651afbcd5d099f0e968015b88da8ee.pdf)
- [DMX — FY2024 audited consolidated financial statements](https://cdnv2-tmdt.tgdd.vn/mwgvn/investorrelations/files/posts/2026/5/0/93/e5/93e558113d3fa242567df336db5e4af6.pdf)
- [DMX — FY2025 audited consolidated financial statements](https://cdnv2-tmdt.tgdd.vn/mwgvn/investorrelations/files/posts/2026/5/0/08/af/08af79013e9b9bdb210eb476e2fa7b95.pdf)
- [DMX — Q1 2026 consolidated financial data pack](https://cdnv2-tmdt.tgdd.vn/mwgvn/investorrelations/files/posts/2026/6/0/6b/e5/6be50a510e272451464dae07771401ca.xlsx)
- [MWG Investor Relations — reports](https://mwg.vn/bao-cao)
- [State Securities Commission — IPO result notice](https://ssc.gov.vn/webcenter/portal/ubck/pages_r/l/chitit?dDocName=APPSSCGOVVN1620168640)

The complete inventory, including direct URLs, periods, scope, audit status, retrieval timestamps, size and SHA-256, is in [`data/source_registry.csv`](data/source_registry.csv).

## License and data rights

Original source code and original repository content are released under the [MIT License](LICENSE). The MIT License does **not** relicense MWG, DMX, SSC or other third-party filings, trademarks, reports or data.

Raw filings remain outside Git. Users are responsible for obtaining documents from official sources and complying with the owners' terms and applicable law before reuse or redistribution. See [`docs/data_scope.md`](docs/data_scope.md).
