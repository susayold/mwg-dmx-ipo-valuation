# Official data scope and SOTP perimeter

**Cut-off:** 13 July 2026, Asia/Ho_Chi_Minh.

**Primary sources:** DMX Investor Relations, MWG Investor Relations and the State Securities Commission of Vietnam (SSC).
**Registry:** [`data/source_registry.csv`](../data/source_registry.csv).

This document defines what belongs in the MWG–DMX analysis, which official files are canonical, and the controls needed to avoid double-counting after the DMX restructuring and IPO. It records source facts; it does not provide investment advice.

## 1. Post-restructuring perimeter

The canonical ownership diagram is page 3 of the official [DMX IPO Presentation](https://cdnv2-tmdt.tgdd.vn/mwgvn/investorrelations/files/posts/2026/6/5005889/4a/f4/4af4a4152a74661a28063a23b4d6747f.pdf), labelled **“MWG Post-Restructuring”** and dated **31 May 2026**.

| MWG branch at 31 May 2026 | Ownership shown in the official diagram | Operating perimeter | SOTP treatment |
|---|---:|---|---|
| DMX JSC | MWG 98.95% before the IPO | Thế Giới Di Động, Điện Máy Xanh, TopZone, Super App, 99.99% Thợ DMX JSC and 45.00% of PT Era Blu Elektronik (EraBlue) | Value as the DMX block, then multiply by MWG's post-IPO ownership. Do not add EraBlue a second time at MWG stub level. |
| BHX Tech & Investment | MWG 94.99% | 99.95% of BHX Trading / Bách Hóa Xanh | Separate MWG-stub block. |
| An Nhi Investment | MWG 100% | 100% of AvaKids Trading | Separate MWG-stub block. |
| Thiên Tâm Investment | MWG 100% | 100% of Thiên Tâm Trading, which owns 99.99% of An Khang Pharma | Separate MWG-stub block. |

The official [IPO completion announcement](https://www.dmx.vn/eng/news/dien-may-xanh-completes-landmark-ipo-raising-more-than-vnd-13-315-billion-and-lifting-charter-capital-to-vnd-12-677-billion-5002485) states that MWG holds **nearly 86%** of DMX after the IPO. The project must not replace this with a more precise percentage unless it is explicitly labelled as a calculation and reconciled to a post-offering shareholder register or later official disclosure.

### Required SOTP equation

```text
MWG equity value
= MWG post-IPO ownership × DMX equity value
+ MWG economic ownership × BHX equity value
+ MWG economic ownership × AvaKids equity value
+ MWG economic ownership × An Khang equity value
+ other verified net assets at MWG/stub level
- holding-company adjustments supported by source data
```

EraBlue is not an additional line beneath MWG after the DMX block. It is already within the DMX perimeter.

## 2. EraBlue accounting control

The official ownership diagram shows DMX owning **45.00% of PT Era Blu Elektronik**. The Q1 2026 official Excel data pack contains the lines **“Investment in jointly controlled entity”** and **“Share of profit from jointly controlled entity”**. Therefore, treat EraBlue as an equity-accounted joint venture for modelling controls:

- do not add EraBlue operating revenue to DMX consolidated revenue;
- do not add 100% of EraBlue EBITDA or net profit to DMX consolidated results;
- if DMX is valued with a consolidated DCF that already captures the joint-venture contribution, do not add a separate EraBlue valuation;
- if EraBlue is explicitly valued as a separate DMX sub-block, remove the corresponding joint-venture contribution from the core DMX valuation and add only DMX's 45% economic share, with consistent net debt and currency treatment.

Management presentations may show EraBlue revenue and stores as operating KPIs even though those amounts are not consolidated line-by-line into DMX revenue. Store counts are operational disclosures, not evidence of accounting consolidation.

## 3. Reported versus post-restructuring history

DMX's official investor materials state that FY2025 like-for-like consolidated revenue and net profit:

- **exclude** the effects of An Khang and AvaKids; and
- **include** the contribution of Thợ DMX.

This is a comparability adjustment, not permission to overwrite the signed audited statements. Maintain two distinct layers:

| Layer | Purpose | Rule |
|---|---|---|
| `reported` | Audit trail and statement reconciliation | Import the signed consolidated statements exactly as disclosed. |
| `pro_forma_post_restructuring` | Forecasting and year-on-year analysis | Use only adjustments explicitly disclosed by DMX; label every adjustment and retain its source ID. |

Never compare a reported FY2025 DMX figure directly with a post-restructuring 2026 KPI without showing the perimeter basis. Do not estimate an An Khang/AvaKids carve-out by simple subtraction unless the official documents provide all components required for that bridge.

## 4. Canonical document hierarchy

When sources differ, use this priority order:

1. SSC regulatory notice or final DMX resolution for the completed offering.
2. Signed audited consolidated financial statements for reported historical figures.
3. Signed unaudited quarterly financial statements for current-period figures.
4. The official Excel data pack for machine-readable ingestion, always reconciled back to the signed PDF.
5. Investor presentations and business-result newsletters for operating KPIs, management guidance and post-restructuring explanations.

Specific canonical choices:

- `DMX_FS_2026Q1_C` is the canonical Q1 2026 consolidated PDF. `DMX_FS_2026Q1_C_ALT` is an official alternate attachment and must not be ingested as another period.
- `DMX_IPO_RESULT_2026` controls final shares issued and post-offering shares outstanding. Initial offer documents describe proposed terms only.
- `DMX_IPO_PROCEEDS_2026` controls the adjusted use of proceeds and the actual gross/net-proceeds bridge.
- `DMX_IPO_PRESENTATION_2026`, page 3, controls the 31 May 2026 post-restructuring SOTP perimeter.

## 5. Period and scope conventions

- Financial year end: 31 December for MWG and DMX documents in this pack.
- Currency: preserve the unit printed in each source. Store normalized monetary values in VND million or VND billion only after recording `source_unit` and `normalization_factor`.
- Financial-scope values must be one of `consolidated`, `separate`, `management_presentation`, `offering`, or `regulatory_notice`.
- Consolidated and separate statements must never be mixed in the same time series.
- Q1 and H1 values are year-to-date unless the source explicitly says otherwise.
- The 6M 2026 business-results file is unaudited management information, not a replacement for Q2/H1 financial statements. At the cut-off date, the DMX site listed Q2 financial statements as a future publication.

## 6. Minimum validation checks

Every normalized statement should pass the checks below before it reaches the model:

1. Assets = liabilities + equity within the disclosed rounding unit.
2. Closing cash in the cash-flow statement reconciles to the balance sheet.
3. Profit attributable to owners and non-controlling interests reconciles to total profit after tax.
4. Consolidated/separate scope and audit status are explicit.
5. Period start, period end and YTD/quarter-only treatment are explicit.
6. Negative signs and parentheses are preserved.
7. The source ID, page/sheet, unit and original label are retained for every imported line item.
8. Duplicate official attachments are detected by source ID and statement period, not only by file hash.
9. Post-IPO share count is taken from `DMX_IPO_RESULT_2026`; proposed shares in earlier documents are not used as actual shares.
10. Any derived ownership percentage is labelled `derived` and linked to its numerator and denominator sources.

## 7. Local files and licensing

Raw documents are stored under `data/raw/` for local verification and are intentionally excluded from Git by `.gitignore`.

- [DMX Terms of Use](https://www.dmx.vn/eng/terms-of-use), effective 6 February 2026, limit downloadable content to personal, non-commercial use and prohibit redistribution, modification, citation or derivative use without prior consent. Do **not** commit DMX PDFs/XLSX files or copied tables to a public repository.
- [MWG Terms of Use](https://mwg.vn/dieu-khoan-su-dung), effective 8 March 2026, allow analytical citation when the source is stated as **“Website Quan hệ cổ đông MWG (mwg.vn)”** together with the citation time; they do not grant unrestricted redistribution of reports.
- The SSC page is linked rather than mirrored because no explicit open-data or redistribution licence was found during this review.

For a public portfolio repository, publish original code, validation logic, source URLs, source IDs and independently written analysis. Keep raw filings local. Before publishing copied tables, document images, logos or substantial extracted datasets, obtain permission from the rights holder or legal review. This licensing note records the website terms and is not legal advice.

## 8. Reproducibility and staleness

- Retrieval timestamp for this pack: `2026-07-13T17:07:18+07:00`.
- SHA-256 hashes and direct URLs are recorded in `data/source_registry.csv`.
- Direct CDN links may change. If a link fails, return to the corresponding official source page rather than using a third-party mirror.
- Re-check the DMX shareholder structure, listing status and Q2 2026 financial statements before any later public release. These facts were time-sensitive at the cut-off date.

## 9. Sources not downloadable at the cut-off

- **DMX Q2/H1 2026 financial statements:** not yet published. The official DMX site displayed 29 July 2026 as the planned publication date. The available 6M business-results newsletter is unaudited management information and is not a substitute.
- **HOSE listing/admission decision for DMX:** no official decision was located as of 13 July 2026. DMX's official announcement described August 2026 trading as expected, so the model must not mark the listing as completed.
- **SSC IPO-result web notice:** the official SSC page was verifiable, but it did not expose a separate downloadable attachment in this review and requires JavaScript in some clients. The registry therefore stores the SSC URL, while the DMX-hosted copy of the SSC notice is retained locally as `DMX_SSC_RESULT_COPY_2026`.

All direct DMX and MWG document links recorded with status `downloaded_verified` were downloaded successfully. No third-party mirror was used.
