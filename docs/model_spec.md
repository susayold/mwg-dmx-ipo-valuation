# Model specification — MWG/DMX IPO valuation

Tài liệu này là contract giữa data pipeline, finance model và presentation website. Công thức chi tiết và rationale nằm tại [`financial_methodology.md`](./financial_methodology.md).

## 1. Model controls

### 1.1 Control inputs bắt buộc

| Field | Type | Unit/example | Rule |
|---|---|---|---|
| `valuation_date` | date | `YYYY-MM-DD` | Không được sau ngày dữ liệu mới nhất |
| `scenario` | enum | `bear/base/bull` | Một scenario active |
| `currency` | enum | `VND` | DCF nominal VND |
| `display_scale` | enum | `VND_bn` | Báo cáo tài chính dùng tỷ VND |
| `mwg_price` | number/null | VND/share | Null nếu không có price/date |
| `mwg_price_date` | date/null | `YYYY-MM-DD` | Bắt buộc nếu có price |
| `dmx_price` | number/null | VND/share | Null trước ngày giao dịch |
| `dmx_price_date` | date/null | `YYYY-MM-DD` | Bắt buộc nếu có price |
| `ipo_offer_price` | number | VND/share | 80.000 actual |
| `use_actual_ipo` | boolean | `true` | Public output mặc định actual close |
| `holdco_discount` | number | decimal | Chỉ dùng sensitivity/conclusion có nhãn |
| `mid_year_convention` | boolean | `true/false` | DCF timing phải nhất quán |
| `lease_convention` | enum | `pre_lease/post_lease` | Áp dụng xuyên EBITDA, debt, FCFF |

Nếu giá hoặc ngày giá thiếu, các field `market_cap`, `upside_downside`, `observed_stub` và `market_holdco_discount` trả `null`, không trả 0.

### 1.2 Chuẩn đơn vị

- P&L/BS/CF/valuation: tỷ VND.
- Share count: triệu cổ phần trong model view; raw source lưu nguyên cổ phần.
- Price: VND/cổ phần.
- Ratios: decimal trong storage/calculation, percent chỉ ở presentation.
- FX: VND trên một đơn vị ngoại tệ; lưu `average` và `closing` riêng.
- Date: ISO `YYYY-MM-DD`.

Không cộng trực tiếp `VND_bn × shares_mn`; mọi bridge phải dùng helper chuyển đổi đơn vị có test.

## 2. Source and data contracts

### 2.1 Source registry

Mỗi tài liệu có tối thiểu:

```text
source_id
issuer                 # DMX/MWG/BHX/peer
document_type          # audited_fs, interim_fs, prospectus, resolution, deck...
title
period_start
period_end
published_date
retrieved_at
url
language
audit_status            # audited/reviewed/unaudited/na
scope                   # consolidated/separate/pro_forma
sha256                  # nếu lưu local artifact
notes
```

### 2.2 Financial fact

```text
entity
statement               # IS/BS/CF/KPI/OWNERSHIP
line_item
period_start
period_end
value
unit
currency
scope
basis                   # reported/LFL/pro_forma
status                  # actual/guidance/assumption/forecast
source_id
source_locator           # page/table/note/section; dùng N/A chỉ khi tài liệu không có locator
extraction_method       # manual/xlsx/pdf/api
review_status           # unreviewed/reviewed/approved
note
```

Một actual không có `source_id` hoặc `source_locator` hợp lệ phải bị loại khỏi published output.

### 2.3 Assumption

```text
assumption_id
entity
driver
period
scenario
value
unit
rationale
evidence_source_id      # nullable, nhưng rationale bắt buộc
owner
updated_at
```

## 3. Workbook/module map

Nếu triển khai Excel, dùng đúng tab order; nếu triển khai Python/SQL, dùng tên module/table tương đương.

| Tab/module | Vai trò | Input chính | Output chính |
|---|---|---|---|
| `Cover` | Hướng dẫn/version/disclaimer | — | Model map |
| `Sources` | Source registry | URLs/metadata | Provenance |
| `IPO_Bridge` | Planned vs actual + pro forma use of proceeds | Resolutions/sales kit | Shares, proceeds, dilution, net-proceeds basis |
| `Q1_Actuals` | Latest reported facts | Q1 data pack | Q1 2025/Q1 2026 comparison |
| `3Y_Statements` | FY2023–FY2025 + Q1 update | Audited/unaudited filings | Comparative IS/BS/CF |
| `3S_Bridges` | Linked-statement reconciliations | Normalized facts | NPAT→CFO, cash and retained-earnings bridges |
| `WC_QoE` | Working capital and earnings quality | Average trade balances + flow data | DIO/DSO/DPO/CCC, QoE, normalization |
| `Mgmt_Forecast` | Issuer reference case | Official management materials | Clearly labelled company guidance |
| `Assumptions` | Analyst scenario inputs | User inputs | WACC, growth, multiples and bridge assumptions |
| `DMX_Valuation` | FCFF/earnings valuation | Actuals + assumptions | EV/equity illustration |
| `MWG_SOTP` | Parent SOTP | DMX/stub/parent inputs | MWG illustrative equity value |
| `Scenarios` | Bear/Base/Bull/sensitivities | Driver matrix | Output matrix |
| `Checks` | Model QA | All modules | PASS/FAIL/error count |

Actuals nên trái sang phải, forecast bắt đầu sau một cột ngăn; màu/formula convention nếu dùng Excel: blue hard-code input, black formula, green cross-sheet link, red error only.

## 4. IPO bridge specification

### 4.1 Required fields

```text
offer_price
shares_pre
shares_offered
shares_registered
shares_successfully_allocated
shares_cancelled
shares_post
par_value
gross_proceeds
issue_costs
net_proceeds
mwg_shares_pre
mwg_shares_subscribed
mwg_shares_post
mwg_ownership_pre
mwg_ownership_post
completion_date
```

### 4.2 Seed actuals (official, as known 2026-07-13)

```text
offer_price                   = 80_000 VND/share
shares_pre                    = 1_101_283_500
shares_offered                =   179_500_400
shares_registered             =   166_485_800
shares_successfully_allocated =   166_438_500
shares_cancelled              =    13_061_900
shares_post                   = 1_267_722_000
par_value                     =        10_000 VND/share
gross_proceeds                =    13_315.080 VND_bn
estimated_issue_costs         =       100.000 VND_bn
estimated_net_proceeds        =    13_215.080 VND_bn
planned_debt_repayment        =    13_215.080 VND_bn
completion_resolution_date    = 2026-06-30
use_of_proceeds_resolution    = 2026-07-07
```

VND 100 tỷ là **estimated issue costs** theo Nghị quyết 15, không được đổi nhãn thành actual costs paid. Tương tự, VND 13.215,080 tỷ là estimated net proceeds và planned debt repayment; không ghi nhận actual disbursement nếu chưa có BCTC/bank evidence hậu giao dịch. Exact `mwg_shares_pre/post` và accounting recognition date vẫn giữ `null` tới khi có nguồn chính thức đủ chính xác. Công bố “gần 86%” chỉ dùng cho approximate check range.

### 4.3 Formula and validation

```text
shares_post_calc        = shares_pre + shares_successfully_allocated
gross_proceeds_calc     = shares_successfully_allocated × offer_price / 1e9
subscription_rate       = shares_successfully_allocated / shares_offered
new_shares_post_pct     = shares_successfully_allocated / shares_post
pre_money_value_bn      = shares_pre × offer_price / 1e9
post_money_value_bn     = shares_post × offer_price / 1e9
net_proceeds_bn         = gross_proceeds_bn - issue_costs_bn

mwg_shares_post         = mwg_shares_pre + mwg_shares_subscribed
mwg_ownership_pre       = mwg_shares_pre / shares_pre
mwg_ownership_post      = mwg_shares_post / shares_post
dilution_bps            = (mwg_ownership_pre - mwg_ownership_post) × 10_000
```

Checks:

```text
CHK_IPO_01 = shares_post_calc - shares_post                         # = 0
CHK_IPO_02 = gross_proceeds_calc - gross_proceeds_reported          # <= 0.001 bn
CHK_IPO_03 = shares_offered - shares_successfully_allocated
             - shares_cancelled                                     # = 0
CHK_IPO_04 = pre_money_value + gross_proceeds - post_money_value     # = 0
CHK_IPO_05 = abs(mwg_ownership_post - disclosed_approx_86pct)        # warning only
CHK_IPO_06 = gross_proceeds - estimated_issue_costs
             - estimated_net_proceeds                               # = 0
CHK_IPO_07 = planned_debt_repayment - estimated_net_proceeds         # = 0, plan basis
```

`CHK_IPO_05` không được dùng để tạo exact ownership.

## 5. Historical and LFL specification

### 5.0 Required coverage

| Period | Required statements | Audit flag | Use |
|---|---|---|---|
| FY2023 | IS/BS/CF comparative | `comparative_unaudited` | Three-year trend; never labelled audited |
| FY2024 | IS/BS/CF | `audited` | Statutory historical |
| FY2025 | IS/BS/CF | `audited` | Statutory historical and LFL bridge anchor |
| Q1 2026 | IS/BS/CF YTD | `unaudited` | Latest trend and WC/QoE update |
| H1 2026 | KPI update only | `management_update` | Do not populate missing H1 statements |

The committed normalized dataset is `data/processed/dmx_three_statement_facts.csv`; the generated analysis contract is `data/processed/dmx_three_statement_analysis.json`. Every actual retains a `source_id`, page/sheet locator, scope, period type and audit note.

### 5.1 Required P&L lines

```text
revenue
cogs
gross_profit
selling_expense
g_and_a_expense
ebitda_derived
depreciation_amortization
ebit
interest_income
interest_expense
share_of_jv_associate_profit
other_income_expense
pbt
income_tax
npat
npat_nci
npat_mi
```

### 5.2 Required BS/CF lines

```text
cash_and_equivalents
short_term_investments
receivables
inventory
other_operating_current_assets
ppe_net
right_of_use_assets_if_any
jv_associate_investment
other_non_operating_assets
payables
other_operating_current_liabilities
short_term_debt
long_term_debt
lease_liabilities_if_any
other_claims
share_capital
share_premium
retained_earnings
nci

cfo_reported
capex
acquisitions_investments
debt_drawdown
debt_repayment
dividends_paid
equity_issuance_proceeds
issue_costs_paid
fx_effect
cash_open
cash_close
```

### 5.3 2025 LFL bridge

```text
reported_2025
less_An_Khang
less_AVAKids
plus_Tho_DMX
other_perimeter_adjustments
= LFL_2025
```

Mỗi adjustment phải có nguồn; chỉ NPAT LFL được công bố không cho phép tự tạo LFL line-by-line. Các dòng không đủ disclosure phải `null` hoặc ghi rõ `analyst_estimate`, không phân bổ pro-rata ngầm.

Required committed normalization rows:

| Metric | Reported FY2025 | Adjustment | Management LFL comparator | Treatment |
|---|---:|---:|---:|---|
| Net revenue | 109,479.188 | (2,479.188) | 107,000.000 | `management_lfl_comparator` |
| NPAT attributable to parent | 5,801.785 | +273.215 | 6,075.000 | `management_lfl_comparator` |
| Operating profit | 7,240.396 | `null` | `null` | `not_adjusted` — insufficient disclosure |
| Cash and cash equivalents | 3,578.155 | `null` | `null` | `not_adjusted` — minimum cash unknown |
| Total debt | 23,429.114 | `null` | `null` | `not_adjusted` — lease/debt basis unsupported |

`not_adjusted` is a valid reviewed conclusion. The model must never replace `null` with zero, because zero would assert that the analyst tested and rejected an adjustment rather than lacking evidence.

## 6. Driver and three-statement specification

Current implemented scope:

- **implemented:** FY2023–FY2025 historical three-statement analysis, Q1 2026 update, statement bridges, working-capital and QoE schedules;
- **not claimed:** a fully integrated 2026E–2030E balance-sheet/cash-flow forecast with debt circularity.

The driver/forecast rules below define the extension path. They do not convert management guidance into an analyst forecast automatically.

### 6.0 Historical reconciliation contract

```text
CFO = NPAT + P&L tax expense + D&A ± other non-cash items
      ± Δreceivables ± Δinventory ± Δpayables ± Δprepayments
      - interest paid - corporate income tax paid

cash_close = cash_open + CFO + CFI + CFF + FX_effect

retained_earnings_close = retained_earnings_open
                          + NPAT attributable to parent
                          - dividends
                          ± capitalisation/other equity movements
```

Required output fields per bridge: `period`, ordered `components`, `calculated_total`, `reported_total`, `difference`, `tolerance`, `passed`, `note`. A balancing residual cannot be recast as a normalization adjustment without source evidence.

### 6.1 Chain driver table

Một row cho mỗi `chain × year × scenario`:

```text
opening_stores
openings
closures
ending_stores
average_stores
monthly_sales_per_store
sssg
revenue
gross_margin
variable_opex_rate
fixed_opex
capex_new_store
maintenance_capex
```

Formula:

```text
ending_stores  = opening_stores + openings - closures
average_stores = opening_stores + 0.5 × (openings - closures)
revenue        = average_stores × monthly_sales_per_store × 12
```

Nếu actual store timing có theo tháng, thay 0,5 bằng month-weighted average.

### 6.2 Working-capital schedule

Historical analysis uses average trade balances and actual elapsed days:

```text
historical_dio = average(net_inventory_open, net_inventory_close)
                 / abs(cogs) × elapsed_days
historical_dso = average(trade_receivables_open, trade_receivables_close)
                 / revenue × elapsed_days
historical_dpo = average(trade_payables_open, trade_payables_close)
                 / abs(cogs) × elapsed_days
historical_ccc = historical_dio + historical_dso - historical_dpo
```

FY2024 uses 366 days, FY2025 uses 365 days and Q1 2026 uses 90 days. Q1 output must carry `q1_seasonality_warning=true`. Forecast balances, if later implemented, follow the driver equations below:

```text
receivables = revenue × dso / 365
inventory   = cogs × dio / 365
payables    = cogs × dpo / 365
other_op_ca = revenue × other_op_ca_pct
other_op_cl = revenue × other_op_cl_pct
nwc         = receivables + inventory + other_op_ca
            - payables - other_op_cl
delta_nwc   = nwc_t - nwc_t_minus_1
```

Sử dụng 366 ngày cho leap year nếu model dùng date-exact convention; nếu dùng 365 cho mọi năm phải ghi rõ.

Additional QoE outputs:

```text
cfo_to_npat = CFO / NPAT
inventory_provision_to_gross = abs(inventory_provision) / gross_inventory
capex_to_revenue = abs(capex) / revenue
free_cash_flow = CFO + capex              # capex stored with cash-flow sign
```

The analysis must present the Q1 2026 payables contribution (approximately VND -465.977bn) beside Q1 2025 (approximately VND +2,104.879bn); it may not attribute the entire CFO gap to inventory or receivables.

### 6.3 Fixed asset, debt and equity schedules

```text
ppe_close = ppe_open + capex - depreciation - disposals
debt_close = debt_open + drawdown - repayment + fx_change
average_debt = (debt_open + debt_close) / 2
interest_expense = average_debt × effective_cost_of_debt

jv_close = jv_open + contributions + share_of_profit
           - jv_dividends - impairment + fx_change

retained_earnings_close = retained_earnings_open + npat
                          - dividends - other_equity_movements
```

IPO split:

```text
increase_share_capital = shares_new × par_value
increase_share_premium = gross_proceeds - increase_share_capital - allocated_issue_costs
```

### 6.4 Cash flow and circularity policy

Cash là output của cash flow. Nếu model dùng minimum cash và debt revolver:

1. Tính pre-financing cash.
2. Draw revolver để đạt minimum cash.
3. Tính interest bằng average debt với copy/paste iteration hoặc controlled circularity.
4. Public/code model mặc định dùng iteration có convergence test; không để circular reference không kiểm soát.

```text
cash_close = cash_open + cfo + cfi + cff + fx_effect
```

## 7. EraBlue specification

Required operating fields:

```text
stores_opening
stores_closing
sssg
revenue_idr
ebitda_margin
npat_margin
dmx_effective_ownership
fx_vnd_per_idr_average
share_of_profit_vnd_bn
dividend_to_dmx_vnd_bn
```

Default accounting flag: `equity_accounted`, nhưng phải xác minh theo BCTC tại valuation date.

```text
share_of_profit_vnd_bn = revenue_idr × npat_margin
                       × dmx_effective_ownership
                       × average_fx / 1e9
```

Website được hiển thị EraBlue gross revenue như KPI với nhãn `JV gross revenue`; consolidated DMX revenue không chứa số này nếu flag là equity-accounted.

## 8. DCF specification

### 8.1 Forecast table

```text
ebit
cash_tax_rate
nopat
depreciation_amortization
capex
delta_nwc
fcff
discount_period
discount_factor
pv_fcff
```

```text
nopat = ebit × (1 - cash_tax_rate)
fcff  = nopat + d_and_a - capex - delta_nwc
discount_period = year_index - 0.5  # only when mid-year=true
discount_factor = 1 / (1 + wacc)^discount_period
```

### 8.2 WACC table

Peer beta table cần `levered_beta`, `net_debt_or_debt`, `market_equity`, `tax_rate`, `unlevered_beta`; sau đó median unlevered beta và target leverage. Mọi market input phải có cùng/practically close pricing date.

```text
cost_of_equity = rf + relevered_beta × erp
after_tax_cod  = pretax_cod × (1 - marginal_tax_rate)
wacc           = equity_weight × cost_of_equity
               + debt_weight × after_tax_cod
```

### 8.3 Terminal and equity bridge

```text
terminal_fcff       = fcff_final_year × (1 + terminal_growth)
terminal_value      = terminal_fcff / (wacc - terminal_growth)
pv_terminal         = terminal_value × terminal_discount_factor
enterprise_value    = sum(pv_fcff) + pv_terminal
equity_value        = enterprise_value
                      - gross_debt
                      - lease_liability_if_included
                      - other_claims
                      + excess_cash
                      + fair_value_of_erablue_stake_if_not_in_fcff
                      + non_operating_investments
value_per_share     = equity_value / diluted_post_ipo_shares
terminal_value_pct  = pv_terminal / enterprise_value
```

Khi FCFF dùng EBIT/EBITDA hợp nhất và EraBlue được equity-accounted, `fair_value_of_erablue_stake_if_not_in_fcff` phải được định giá riêng. Khi dùng P/E trên NPAT-MI (đã chứa share of JV profit), hoặc một DMX equity SOTP đã gồm EraBlue, field này bằng 0 để tránh double count.

IPO proceeds policy:

- Valuation balance sheet hậu IPO đã phản ánh giao dịch: dùng actual/pro forma cash và debt; `additional_ipo_proceeds = 0` trong bridge.
- Valuation balance sheet Q1 2026 tiền IPO cùng post-IPO shares: `additional_ipo_proceeds = 13_215.080 VND_bn`, bằng gross VND 13,315.080bn trừ estimated costs VND 100.000bn; cộng đúng một lần.
- Planned debt repayment of VND 13,215.080bn reduces debt in the pro forma schedule but remains `planned`, not `actual_disbursed`, until later evidence confirms execution.
- Nếu net proceeds đã nằm trong ending cash hoặc debt balance, không cộng lại tại equity bridge.

## 9. Comparable-company specification

Required columns:

```text
ticker
company
country
pricing_date
price
diluted_shares
market_cap
gross_debt
lease_liability
cash
minority_interest
associates_nonop
enterprise_value
revenue_ltm/fy1
ebitda_ltm/fy1
npat_mi_ltm/fy1
ev_sales
ev_ebitda
pe
accounting_notes
source_ids
include_flag
exclusion_reason
```

Peer statistics: median và quartiles trên `include_flag=true`. Không winsorize hoặc loại outlier mà thiếu `exclusion_reason`.

## 10. MWG SOTP and stub specification

### 10.1 SOTP table

```text
asset
valuation_method
metric
multiple_or_dcf_value
equity_value_100pct
mwg_effective_ownership
value_attributable_to_mwg
source_or_model_ref
double_count_bucket
```

Rows tối thiểu:

```text
DMX
BHX
An_Khang
AVAKids
Other_investments
Parent_non_operating_assets
Parent_only_net_debt
Parent_provisions
```

```text
gav = sum(positive attributable asset values) + parent_non_operating_assets
nav_pre_discount = gav - parent_only_net_debt - parent_provisions
nav_post_discount = nav_pre_discount × (1 - holdco_discount)
value_per_mwg_share = nav_post_discount / mwg_diluted_shares
```

`double_count_bucket` phải unique. Ví dụ EraBlue dùng `DMX_DCF`; không có row EraBlue riêng ở MWG SOTP nếu đã nằm trong DMX.

### 10.2 Observed stub

```text
mwg_market_cap = mwg_price × mwg_diluted_shares / 1e9
dmx_market_cap = dmx_price × dmx_diluted_shares / 1e9
dmx_to_mwg     = dmx_market_cap × mwg_ownership_post
stub_value     = mwg_market_cap - dmx_to_mwg
```

Required statuses:

- `MARKET`: MWG và DMX có closing price cùng ngày.
- `MIXED_DATE_WARNING`: price dates khác nhau.
- `IPO_PROXY`: dùng DMX IPO price.
- `DCF_PROXY`: dùng DCF equity value.
- `UNAVAILABLE`: thiếu input.

### 10.3 Implied BHX

```text
implied_bhx_100pct = (
    mwg_market_cap / (1 - holdco_discount)
    - dmx_to_mwg
    - other_subsidiary_values_attributable
    - parent_non_operating_assets
    + parent_only_net_debt
    + parent_provisions
) / mwg_ownership_bhx
```

Output luôn kèm assumption `holdco_discount`, DMX value type và valuation date. Không floor âm.

## 11. Scenario specification

### 11.1 Operating scenarios

Scenario switch phải điều khiển các driver row, không điều khiển trực tiếp revenue/EBITDA/valuation output:

```text
domestic_sssg
net_store_openings
sales_per_store
gross_margin
variable_opex_rate
fixed_opex_growth
dio
dso
dpo
maintenance_capex
growth_capex
erablue_stores
erablue_sssg
erablue_npat_margin
```

### 11.2 Valuation sensitivities

Tối thiểu:

1. DCF `WACC × terminal_growth` (5×5).
2. DCF `steady_state_gross_margin × SSSG` (5×5).
3. MWG `DMX_equity_value × holdco_discount` (5×4).
4. Implied BHX `DMX_value_case × holdco_discount`.

Operating scenario và valuation sensitivity là hai chiều độc lập.

The public earnings-anchor illustration must reconcile as follows (VND billion):

| Scenario | DMX equity | MWG share at ~86% | Stub | Parent adjustments | Total illustrative MWG equity |
|---|---:|---:|---:|---:|---:|
| Bear | 67,000 | 57,620 | 28,000 | (8,000) | 77,620 |
| Base | 90,405 | 77,748.3 | 45,000 | (5,000) | 117,748.3 |
| Bull | 112,000 | 96,320 | 65,000 | (3,000) | 158,320 |

These totals are scenario checks, not target prices. `~86%` remains an approximate ownership input until an exact post-IPO shareholder record is available.

## 12. QA checks and publication gate

### 12.1 Tolerances

```text
statement_tolerance_bn   = 0.5        # hoặc nhỏ hơn materiality do analyst đặt
share_tolerance          = 0
ownership_tolerance      = 0.000001
valuation_tolerance_bn   = 0.01
percent_tolerance        = 0.000001
```

### 12.2 Critical checks

```text
CHK_3S_BS_BALANCE
CHK_3S_CASH_ROLL
CHK_3S_DEBT_ROLL
CHK_3S_PPE_ROLL
CHK_3S_EQUITY_ROLL
CHK_3S_JV_ROLL
CHK_3S_NPAT_TO_CFO
CHK_3S_RETAINED_EARNINGS
CHK_3S_PERIOD_DAYS
CHK_3S_SOURCE_COVERAGE
CHK_NORM_NO_UNSUPPORTED_ADJUSTMENT
CHK_IPO_SHARES
CHK_IPO_PROCEEDS
CHK_IPO_NET_PROCEEDS
CHK_IPO_VALUATION_IDENTITY
CHK_OWNERSHIP_SUM
CHK_EPS_WEIGHTED_SHARES
CHK_DCF_WACC_GT_G
CHK_DCF_BRIDGE
CHK_DCF_NO_DOUBLE_COUNT_IPO
CHK_SOTP_NO_DUPLICATE_BUCKET
CHK_SOTP_EQUITY_BRIDGE
CHK_STUB_SAME_PRICE_DATE
CHK_PERIMETER_UNIQUE
CHK_PERIOD_NO_OVERLAP
CHK_ACTUAL_SOURCE_COMPLETE
CHK_SCENARIO_LINKS
```

The generated historical module currently publishes 35 accounting checks; committed output must have `failed = 0`. This count is separate from the broader workbook publication-gate checks.

### 12.3 Publication gate

```text
publishable = (
  critical_error_count == 0
  and actual_source_coverage == 100%
  and valuation_date is not null
  and disclaimer_present == true
)
```

Upside/downside và investment-language gate cần thêm:

```text
market_conclusion_allowed = publishable
  and mwg_price is not null
  and mwg_price_date == valuation_date
  and mwg_diluted_shares is not null
```

Không đạt gate thì website chỉ hiển thị methodology/scenario illustration và câu “market conclusion unavailable”.

## 13. Website output contract

Website có thể đọc một JSON đã version hóa:

```text
meta: valuation_date, generated_at, scenario, units, version, disclaimer
ipo: planned, actual, ownership, checks
dmx: historical, three_statement_bridges, working_capital, quality_of_earnings,
     normalization, lfl_bridge, forecast, kpis
valuation: dcf, comps, sensitivity
mwg: sotp, stub, implied_bhx
qa: critical_errors, warnings, source_coverage
sources: source_id, title, url, published_date, retrieved_at
```

Mỗi chart/table phải có:

- `status`: Actual/Company guidance/Analyst assumption/Forecast/Illustrative.
- `as_of` hoặc `period_end`.
- `unit`.
- `source_ids`.
- `scenario` nếu là forecast.

Website không được dùng số demo làm actual. Placeholder phải là `null` và render `N/A`, không dùng `0`.

Website scenario output may show total illustrative equity value in VND billion. It must not show target price, premium/upside or an investment rating until `market_conclusion_allowed=true`.

## 14. Versioning and sign-off

- Thay nguồn actual: bump data version.
- Thay công thức/methodology: bump model version.
- Thay assumption: bump scenario version.
- Lưu `generated_at`, commit hash và check summary trong output artifact.
- Finance review ký `perimeter`, IPO bridge, DCF bridge, SOTP double count và limitations trước khi publish.
