# Phương pháp tài chính — MWG After the DMX IPO

> **Mục đích:** một case study portfolio về IPO, carve-out và định giá SOTP. Đây không phải báo cáo khuyến nghị đầu tư, không phải chào mua/chào bán chứng khoán.
>
> **Ngày chốt nguồn:** 2026-07-13, múi giờ Asia/Bangkok. Mọi kết quả phụ thuộc giá thị trường phải hiển thị riêng `valuation_date`, nguồn giá và trạng thái dữ liệu.

## 1. Câu hỏi mà mô hình phải trả lời

1. IPO thực tế đã làm số cổ phần, tiền mặt, sở hữu của MWG và lợi ích cổ đông không kiểm soát tại DMX thay đổi thế nào?
2. Giá trị hợp lý của 100% vốn chủ sở hữu DMX là bao nhiêu theo DCF và giao dịch so sánh?
3. Phần giá trị DMX thuộc cổ đông MWG là bao nhiêu sau pha loãng?
4. Sau khi loại phần DMX, vốn hóa MWG đang ngầm định bao nhiêu cho BHX, các tài sản còn lại và nghĩa vụ tại công ty mẹ?
5. Kết quả thay đổi thế nào trong Base/Bull/Bear và các bảng nhạy cảm?

Mô hình phải trả lời bằng **bridge có thể kiểm toán**, không bằng một con số mục tiêu đơn lẻ.

## 2. Nguyên tắc nền tảng

- Dùng BCTC hợp nhất kiểm toán/công bố chính thức làm nguồn actual. FY2023 chỉ là cột so sánh trong BCTC FY2024 và được kiểm toán viên ghi rõ **chưa kiểm toán**; không được gắn nhãn audited. Presentation, sales kit và phát biểu quản trị chỉ là nguồn KPI, guidance hoặc giả định.
- Tách ba lớp dữ liệu: `reported`, `like_for_like/pro_forma`, `forecast`. Không ghi đè actual đã báo cáo bằng số điều chỉnh.
- Tách `planned IPO` khỏi `actual IPO close`. Giá trị sau giao dịch phải dùng kết quả phân phối và thanh toán cuối cùng.
- Chỉ dùng dữ liệu đã biết tại `valuation_date`; một tài liệu công bố sau ngày định giá không được dùng để tạo lợi thế nhìn trước.
- Mỗi input phải có đơn vị, kỳ, phạm vi hợp nhất, ngày công bố và URL/page nguồn.
- Không cộng trùng tiền IPO, EraBlue, tiền/nợ hoặc lợi ích cổ đông không kiểm soát.
- Không trình bày upside/downside hay kết luận đầu tư nếu thiếu đồng thời giá, ngày giá, số cổ phần pha loãng và nguồn giá.

## 3. Phạm vi doanh nghiệp và hàng rào chống double count

Theo trang IR của DMX, perimeter được truyền thông gồm Điện Máy Xanh, thegioididong.com, TopZone, Thợ Điện Máy Xanh và EraBlue. Nguồn chính thức cũng gọi EraBlue là một **joint venture**. Vì vậy:

- Doanh thu gross của EraBlue chỉ là KPI vận hành khi EraBlue được hạch toán theo phương pháp vốn chủ sở hữu.
- P&L DMX khi đó chỉ nhận `share_of_profit_from_JV`; không cộng gross revenue/EBITDA EraBlue vào doanh thu/EBITDA hợp nhất DMX.
- Nếu BCTC mới nhất thay đổi phân loại kế toán, mô hình phải theo BCTC và lưu ngày hiệu lực.
- EraBlue đã nằm trong DCF/SOTP nội bộ của DMX thì **không** được cộng thêm như một dòng tài sản riêng trong SOTP MWG.
- Với FCFF DCF dựa trên EBIT/EBITDA hợp nhất, phần lợi nhuận liên doanh không nằm trong FCFF. Khi đó phải định giá phần sở hữu EraBlue riêng và cộng tại DMX equity bridge. Nếu dùng P/E trên NPAT-MI đã chứa share of JV profit, không cộng EraBlue lần nữa.
- DMX 2025 like-for-like trong sales kit loại An Khang và AVAKids, đồng thời đưa Thợ Điện Máy Xanh vào. An Khang/AVAKids, nếu định giá, chỉ xuất hiện trong phần non-DMX của MWG.

Trước khi chạy model, `perimeter_check` phải xác nhận từng pháp nhân/chuỗi thuộc đúng một bucket.

## 4. IPO bridge: kế hoạch và kết quả thực tế

### 4.1 Dữ liệu giao dịch đã công bố

| Chỉ tiêu | Planned | Actual close | Nguồn/ghi chú |
|---|---:|---:|---|
| Giá chào bán | 80.000 VND/cp | 80.000 VND/cp | Sales kit; Nghị quyết kết quả IPO |
| Cổ phần trước IPO | 1.101.283.500 | 1.101.283.500 | Nghị quyết 14 |
| Cổ phần chào bán | 179.500.400 | 179.500.400 | Sales kit; Nghị quyết 14 |
| Cổ phần phân phối thành công | 179.500.400 giả định | 166.438.500 | Nghị quyết 14 |
| Cổ phần sau IPO | 1.280.783.900 | 1.267.722.000 | Tính toán planned; Nghị quyết 14 actual |
| Gross proceeds | 14.360,032 tỷ VND | 13.315,080 tỷ VND | `shares_issued × 80.000` |
| Chi phí phát hành ước tính | N/D | 100,000 tỷ VND | Nghị quyết 15; đây là estimate |
| Net proceeds ước tính | N/D | 13.215,080 tỷ VND | `gross proceeds - estimated issue costs` |
| Tỷ lệ phân phối | 100,00% giả định | 92,72% | `actual_issued / offered` |
| Tỷ trọng cổ phần mới/post-money | 14,01% | 13,13% | `new_shares / post_shares` |
| Post-money market cap tại giá IPO | 102.462,712 tỷ VND | 101.417,760 tỷ VND | `post_shares × offer_price` |

Nghị quyết 14 ghi nhận 166.438.500 cổ phần được phân phối thành công; 13.061.900 cổ phần còn lại bị hủy, không tính vào vốn điều lệ. Đây là số dùng cho actual case.

Nghị quyết 15 công bố VND 13.315,080 tỷ gross proceeds, VND 100,000 tỷ chi phí phát hành ước tính và VND 13.215,080 tỷ net proceeds ước tính; toàn bộ net proceeds được dự kiến dùng để trả nợ trong năm 2026. Đây là **kế hoạch sử dụng vốn/pro forma assumption**. Tại ngày chốt nguồn, dự án không trình bày khoản trả nợ này như cash disbursement đã thực hiện nếu chưa có sao kê hoặc BCTC hậu giao dịch xác nhận.

### 4.2 Công thức chuẩn

Ký hiệu:

- `S0`: cổ phần DMX trước IPO.
- `S_offer`: cổ phần dự kiến chào bán.
- `S_new`: cổ phần mới thực tế đã phân phối và thanh toán.
- `S1 = S0 + S_new`: cổ phần sau IPO.
- `P0`: giá IPO.
- `C_issue`: chi phí phát hành.
- `G = S_new × P0`: tiền thu gộp.
- `N = G - C_issue`: tiền thu ròng.

Bridge định giá:

```text
Pre-money equity value  = P0 × S0
Post-money equity value = P0 × S1
                       = Pre-money equity value + Gross proceeds
Subscription rate      = S_new / S_offer
Primary dilution       = S_new / S1
```

`Post-money = pre-money + gross proceeds` chỉ là identity tại cùng một giá phát hành, chưa phải bằng chứng IPO tạo ra giá trị kinh tế.

### 4.3 Sở hữu MWG và pha loãng

Ký hiệu thêm:

- `M0`: số cổ phần DMX do MWG sở hữu ngay trước IPO.
- `M_sub`: số cổ phần MWG mua trong đợt phát hành, nếu có.
- `M1 = M0 + M_sub`.
- `theta0 = M0 / S0`.
- `theta1 = M1 / S1`.

```text
Dilution (percentage points) = theta0 - theta1
Dilution (basis points)      = (theta0 - theta1) × 10,000
MWG stake value at price P   = M1 × P
```

Không được đặt `M0 = S0`. DMX có thể đã có cổ đông thiểu số trước IPO. Bài công bố kết quả chỉ nói MWG nắm **gần 86%** sau IPO; đây là số làm tròn để kiểm tra hợp lý, không đủ để back-solve số cổ phần chính xác. Production model phải lấy `M0` từ danh sách cổ đông/bản cáo bạch hoặc công bố hậu IPO.

Vì đây là primary issuance, tiền IPO thuộc DMX. Không coi `G` là tiền mặt MWG nhận được. Nếu MWG không bán cổ phần:

```text
Value of MWG stake at P0 before IPO = M0 × P0
Value of MWG stake at P0 after IPO  = M0 × P0
```

Pha loãng tỷ lệ không tự động làm thay đổi giá trị gross của số cổ phần MWG tại cùng mức giá; giá trị thay đổi về sau phụ thuộc cách DMX sử dụng vốn và hiệu quả sinh lời.

### 4.4 Pro forma balance sheet và EPS

Nếu balance sheet bắt đầu định giá là trước ngày hoàn tất IPO (ví dụ 31/03/2026), dùng bridge sau:

```text
Cash_post      = Cash_pre + Gross_proceeds - Issue_costs - Debt_repaid - Other_use
Debt_post      = Debt_pre - Debt_repaid + New_debt
Net_debt_post  = Debt_post - Cash_post
```

Việc dùng tiền trả nợ hay giữ tiền đều làm net debt giảm bằng tiền thu ròng, trước các uses khác. Không được vừa pro forma cash/net debt vừa cộng `net proceeds` lần nữa trong equity bridge.

Trong case hiện tại:

```text
Gross proceeds                 = 13.315,080
Less: estimated issue costs    =    100,000
Estimated net proceeds         = 13.215,080 tỷ VND
Planned debt repayment         = 13.215,080 tỷ VND
```

Quy tắc chọn basis:

- dùng Q1 2026 cash/debt tiền IPO cùng post-IPO shares: cộng VND 13.215,080 tỷ **một lần** như pro forma net-proceeds adjustment;
- dùng balance sheet hậu IPO đã phản ánh phát hành/trả nợ: `additional_ipo_proceeds = 0`;
- chưa có bằng chứng disbursement: gắn nhãn `planned debt repayment`, không gắn nhãn `actual debt repayment`.

EPS năm phát hành dùng cổ phần bình quân gia quyền theo ngày thực tế:

```text
Weighted_average_shares = Σ(shares_outstanding_i × days_i / days_in_year)
Basic_EPS                = NPAT_MI / Weighted_average_shares
```

Sales kit giả định cổ phần mới lưu hành sáu tháng cho EPS minh họa; actual model phải dùng ngày hoàn tất/đủ điều kiện ghi nhận theo tài liệu chính thức.

Sau IPO, nếu MWG vẫn kiểm soát DMX, DMX tiếp tục hợp nhất vào MWG và nhà đầu tư ngoài MWG là NCI. Phân bổ lợi nhuận dùng effective ownership, không dùng tỷ lệ cổ phần mới phát hành như một proxy.

## 5. Historical three-statement analysis

Đây là module phân tích lịch sử liên kết ba báo cáo, không phải full integrated forecast.

### 5.1 Coverage và audit status

| Kỳ | P&L | Balance sheet | Cash flow | Trạng thái |
|---|---|---|---|---|
| FY2023 | Cả năm | 31/12/2023 | Cả năm | Comparative trong BCTC FY2024; kiểm toán viên ghi rõ chưa kiểm toán |
| FY2024 | Cả năm | 31/12/2024 | Cả năm | Audited consolidated |
| FY2025 | Cả năm | 31/12/2025 | Cả năm | Audited consolidated |
| Q1 2026 | 3 tháng YTD | 31/03/2026 | 3 tháng YTD | Unaudited consolidated |
| H1 2026 | Chỉ operating KPIs | Không có | Không có | Không thay thế BCTC H1 tại cut-off |

Q1 chỉ cập nhật xu hướng mới nhất. Không annualize Q1 để kết luận về seasonality, vòng quay tồn kho cả năm, margin bền vững, CapEx/depreciation hoặc debt policy.

### 5.2 Headline trend

| VND tỷ, trừ tỷ lệ | FY2023 | FY2024 | FY2025 | Q1 2026 |
|---|---:|---:|---:|---:|
| Revenue | 86.822,1 | 93.356,6 | 109.479,2 | 32.542,0 |
| Gross margin | 16,61% | 18,31% | 17,80% | 19,18% |
| Operating margin | 2,31% | 5,45% | 6,61% | 8,52% |
| NPAT attributable to parent | 1.345,5 | 3.716,6 | 5.801,8 | 2.218,6 |
| CFO | 2.357,3 | 6.243,1 | 5.016,7 | 863,7 |
| CFO / NPAT | 175,2% | 168,0% | 86,5% | 38,9% |

Senior readthrough: FY2024–FY2025 cho thấy lợi nhuận vận hành cải thiện rõ hơn doanh thu, nhưng cash conversion suy giảm. Q1 2026 tăng trưởng và margin tốt, song không thể gọi là earnings-quality confirmation khi supplier funding đảo chiều và chưa có BCTC H1.

### 5.3 Ba bridge bắt buộc

```text
NPAT
+ P&L tax expense
+ depreciation and amortization
± provisions / non-cash FX / investing-profit removal
± change in receivables
± change in inventory
± change in payables
± change in prepayments
- interest paid
- corporate income tax paid
= CFO
```

```text
Opening cash + CFO + CFI + CFF + FX effect = Closing cash
```

```text
Opening retained earnings + NPAT - dividends
± residual capitalisation / other equity movements = Closing retained earnings
```

Đây là **retained-earnings residual reconciliation**, chưa phải independent statement-of-changes-in-equity rebuild. Không được nhét balancing residual vào `other` rồi coi là operating adjustment. FY2025 có VND 6.542,278 tỷ capitalisation/other equity movements trong retained-earnings bridge; module trình bày riêng khoản này và không dùng nó để điều chỉnh EBIT hay CFO. Nếu sau này có đủ statement of changes in equity, check nên tách capitalisation, fund transfers, dividends, restructuring và OCI/other equity movements thành source-tagged lines, rồi chỉ để residual gần bằng 0.

### 5.4 Working-capital schedule

```text
DIO = average net inventory / COGS × elapsed days
DSO = average trade receivables / revenue × elapsed days
DPO = average trade payables / COGS × elapsed days
CCC = DIO + DSO - DPO
```

| Chỉ tiêu | FY2024 | FY2025 | Q1 2026 YTD |
|---|---:|---:|---:|
| DIO | 88,0 ngày | 83,6 ngày | 78,4 ngày |
| DSO | 1,1 ngày | 1,1 ngày | 1,0 ngày |
| DPO | 28,3 ngày | 32,5 ngày | 31,3 ngày |
| CCC | 60,8 ngày | 52,1 ngày | 48,0 ngày |
| Inventory provision / gross inventory | 2,24% | 2,61% | 3,15% |
| CFO / NPAT | 168,0% | 86,5% | 38,9% |
| CapEx / revenue | 0,08% | 0,12% | 0,36% |

FY2024 dùng 366 ngày; FY2025 dùng 365 ngày; Q1 2026 dùng 90 ngày thực tế. Vì Q1 là một đoạn mùa vụ ngắn, CCC 48,0 ngày không phải annual forecast. Các ratio dùng average opening/closing trade balances; không dùng closing balance duy nhất để tạo xu hướng giả.

### 5.5 Quality of earnings

| Indicator | Observation | Interpretation | Risk / next evidence |
|---|---|---|---|
| Revenue growth | Q1 2026 +29,4% YoY | Operating momentum đủ mạnh để theo dõi full-year | Một quý không chứng minh sustainability |
| Gross-margin change | +~119 bps YoY | Mix, pricing và operating leverage hỗ trợ | Vendor funding, promotion và category mix có thể normalize |
| CFO / NPAT | 38,9%, từ 167,6% Q1 2025 | Working capital và tax là điểm nghẽn chính | Cần BCTC H1/full-year trước khi kết luận earnings quality |
| Payables contribution | Q1 2026 âm 466,0 tỷ, so với dương 2.104,9 tỷ Q1 2025 | Supplier funding đảo chiều giải thích phần lớn CFO gap | DPO giảm kéo dài sẽ tạo cash pressure |
| Inventory provision | Coverage tăng từ 2,61% lên 3,15% | Balance sheet ghi nhận thêm inventory risk | Không có ageing/category detail để đánh giá obsolescence đầy đủ |
| Net finance contribution / PBT | Khoảng 6,7% Q1 2026 | Treasury income hỗ trợ nhưng không phải growth driver chính | Deposit income có thể giảm khi tiền IPO dùng trả nợ |

Cần phân biệt financed sales với receivables của DMX: tỷ trọng bán trả góp không tự động chứng minh DMX giữ credit risk. Phải kiểm tra lender, recourse và risk-transfer terms trước khi đưa loan losses vào forecast.

### 5.6 Normalization policy

| Reported item FY2025 | Adjustment | Comparator | Treatment / reason |
|---|---:|---:|---|
| Revenue 109.479,188 | (2.479,188) | LFL revenue 107.000,000 | Management LFL excludes An Khang/AvaKids and includes Thợ DMX; do not overwrite statutory actual |
| NPAT parent 5.801,785 | +273,215 | LFL NPAT 6.075,000 | Only the disclosed headline is bridged |
| Operating profit 7.240,396 | N/D | N/D | Insufficient line-by-line disclosure; not adjusted |
| Cash 3.578,155 | N/D | N/D | Minimum operating cash is not disclosed; do not label automatic excess cash |
| Total debt 23.429,114 | N/D | N/D | Lease/debt convention is not sufficiently disclosed; no unsupported adjusted net debt |

Nguyên tắc senior analyst ở đây là biết **khi nào không điều chỉnh**. Không tự tạo one-off, minimum cash, lease adjustment hoặc carve-out allocation nếu nguồn không đủ granularity.

### 5.7 Senior analyst conclusions

1. Lợi nhuận tăng chủ yếu đi cùng operating margin, không chỉ nhờ finance income; tuy vậy treasury contribution vẫn phải tách riêng.
2. FY2025 inventory build được supplier funding bù đáng kể, nhưng Q1 2026 payables giảm VND 465,977 tỷ và làm CFO yếu đi.
3. DSO gần một ngày phản ánh trade receivables thấp; financed-sales mix không đồng nghĩa DMX giữ toàn bộ customer credit exposure.
4. Inventory provision coverage tăng là tín hiệu thận trọng, nhưng thiếu ageing khiến chưa thể kết luận mức dự phòng đã đủ.
5. Cash + deposits - debt là liquidity indicator, không phải distributable excess cash nếu chưa xác định minimum operating cash.
6. Net proceeds IPO là vốn sơ cấp của DMX, không phải tiền MWG nhận; VND 13.215,080 tỷ trả nợ là pro forma plan cho tới khi có evidence thực hiện.

## 6. DMX standalone driver model

### 6.1 Kỳ mô hình

- Historical analysis: FY2023A comparative unaudited, FY2024A, FY2025A và quý gần nhất được công bố tại valuation date.
- Pro forma comparator: 2025 LFL, trình bày bridge riêng từ reported.
- Forecast: 2026E–2030E.
- 2026E phải là `actual YTD + forecast remaining months`, không annualize máy móc một quý.

### 6.2 Revenue build

Phân rã tối thiểu:

1. TGDD + TopZone.
2. Điện Máy Xanh domestic.
3. Thợ Điện Máy Xanh/services.
4. EraBlue operating KPIs và equity-accounted earnings nếu phân loại JV còn hiệu lực.

Với chuỗi cửa hàng `c`:

```text
Average_stores_c,t = Opening_stores_c,t
                   + 0.5 × Net_openings_c,t
Revenue_c,t        = Average_stores_c,t × Monthly_sales_per_store_c,t × 12
Monthly_sales_per_store_c,t
                   = Prior_period × (1 + SSSG_c,t) × FX_or_mix_adjustment
```

Nếu chỉ có SSSG và doanh thu base:

```text
Revenue_growth ≈ (1 + SSSG) × (Average_stores_t / Average_stores_t-1) - 1
```

Services dùng volume × take-rate/fee; không giả định cùng gross margin với bán hàng hóa.

Với EraBlue được equity-account:

```text
EraBlue_revenue_local = Average_stores × sales/store/month × 12
EraBlue_NPAT_local    = Revenue × net_margin
DMX_share_of_profit   = EraBlue_NPAT_local × effective_ownership × FX_average
```

Gross revenue EraBlue chỉ dùng cho operating dashboard, không cộng vào consolidated revenue DMX.

### 6.3 Biên lợi nhuận và chi phí

```text
COGS                  = Revenue × (1 - Gross_margin)
Gross_profit          = Revenue - COGS
Variable_opex         = Revenue × Variable_opex_rate
Fixed_opex            = Prior_fixed_opex × (1 + inflation) + step_costs
EBITDA                = Gross_profit - Variable_opex - Fixed_opex
EBIT                  = EBITDA - D&A
Interest_income       = Average_excess_cash × Cash_yield
Interest_expense      = Average_interest_bearing_debt × Cost_of_debt
PBT                   = EBIT + Net_finance_income + Share_of_JV_profit + Other
Tax                   = PBT × normalized_ETR, adjusted for discrete items/losses
NPAT_MI               = NPAT - NPAT_attributable_to_NCI
```

Gross margin phải được phân tích bởi product mix, vendor funding, service mix và markdown risk; không kéo thẳng một CAGR lợi nhuận từ guidance.

### 6.4 Working capital, capex và ba báo cáo

```text
Receivables = Revenue × DSO / 365
Inventory   = COGS × DIO / 365
Payables    = COGS × DPO / 365
NWC         = Operating_CA - Operating_CL
PPE_close   = PPE_open + Capex - D&A - Disposals
JV_close    = JV_open + Share_of_profit + Contributions - Dividends - Impairment
RE_close    = RE_open + NPAT - Dividends

CFO  = NPAT + Non_cash_items - Change_in_NWC
CFI  = -Capex + Asset_disposals + Other_investing_CF
CFF  = Debt_drawdown - Debt_repayment + Net_IPO_proceeds - Dividends
Cash_close = Cash_open + CFO + CFI + CFF + FX_effect
```

Capex tách maintenance, new stores, refurbishment/IoT/IT. Tồn kho và khoản phải trả là driver trọng yếu của cash conversion; không forecast FCF chỉ bằng EBITDA trừ một tỷ lệ capex.

## 7. DCF DMX

DCF chính dùng FCFF:

```text
NOPAT_t = EBIT_t × (1 - Marginal_cash_tax_rate_t)
FCFF_t  = NOPAT_t + D&A_t - Capex_t - Change_in_NWC_t

Terminal_value_n = FCFF_n × (1 + g) / (WACC - g)
Enterprise_value = Σ[FCFF_t / (1 + WACC)^t]
                 + Terminal_value_n / (1 + WACC)^n
DMX_equity_value = EV - Gross_debt + Excess_cash
                 + Fair_value_of_EraBlue_stake
                 + Other_non_operating_investments - Other_claims
Value_per_share  = DMX_equity_value / Diluted_post_IPO_shares
```

`Fair_value_of_EraBlue_stake` được đưa vào khi FCFF/EBIT chưa chứa cash flow của liên doanh. Nếu DMX DCF được xây theo equity-level SOTP đã gồm EraBlue, dòng này bằng 0 trong bridge cuối. P/E valuation dựa trên NPAT-MI đã chứa share of JV profit cũng không cộng thêm EraBlue.

Nếu dùng mid-year convention, số mũ discount của năm thứ `k` là `k - 0,5`; terminal value được chiết khấu nhất quán tại `n - 0,5` hoặc theo timing được công bố rõ.

```text
WACC = E/(D+E) × Cost_of_equity + D/(D+E) × Pre_tax_cost_of_debt × (1-T)
Cost_of_equity = Risk_free_rate + Relevered_beta × Equity_risk_premium
Unlevered_beta = Levered_beta / [1 + (1-T) × D/E]
Relevered_beta = Median_unlevered_beta × [1 + (1-T) × Target_D/E]
```

Chọn risk-free rate/ERP nhất quán cùng đồng tiền danh nghĩa VND. Không cộng country risk premium hai lần nếu nó đã nằm trong cấu phần rate/ERP. Luôn kiểm tra `WACC > g` và terminal assumptions không vượt logic tăng trưởng dài hạn.

Lease liabilities, EBITDA, capex và net debt phải dùng cùng một convention. Ghi rõ `pre-lease` hoặc `post-lease`; không dùng EBITDA sau lease với debt bridge loại lease một cách tùy ý.

## 8. Trading comparables

Peer set ưu tiên nhà bán lẻ CE/ICT và omnichannel trong khu vực, nhưng từng peer phải có giải thích về geography, growth, margin và accounting. Chỉ dùng dữ liệu có cùng `pricing_date` và cùng forecast period.

```text
EV/EBITDA implied EV      = Peer_multiple × DMX_EBITDA_same_period
EV-based implied equity  = Implied_EV - Net_debt - Other_claims
                           + Non_operating_investments
P/E implied equity       = Peer_PE × DMX_NPAT_MI_same_period
Implied_price            = Implied_equity / Diluted_post_IPO_shares
```

- Loại P/E của doanh nghiệp lỗ hoặc EPS không có ý nghĩa.
- Trình bày median, 25th–75th percentile; không chọn một peer cao nhất làm target.
- Điều chỉnh IFRS 16/lease, lợi ích thiểu số, associates và kỳ tài chính trước khi so sánh.
- IPO price là một datapoint giao dịch, không phải bằng chứng độc lập của fair value.
- Không blend DCF/comps bằng trọng số tùy ý. Nếu dùng weighted conclusion, phải công bố trọng số và lý do.

## 9. SOTP MWG

Khuyến nghị dùng equity-level SOTP để giảm rủi ro NCI/double count:

```text
GAV = theta_DMX × Equity_value_DMX
    + theta_BHX × Equity_value_BHX
    + Σ(theta_j × Equity_value_j)
    + Parent_non_operating_assets

NAV_pre_discount = GAV - Parent_only_net_debt - Parent_provisions
NAV_post_discount = NAV_pre_discount × (1 - Holdco_discount)
MWG_value_per_share = NAV_post_discount / MWG_diluted_shares
```

`Parent_only_net_debt` chỉ gồm tiền/nợ chưa nằm trong equity value của các công ty con. Không lấy consolidated MWG net debt rồi lại dùng equity value của DMX/BHX.

Các bucket tối thiểu:

- DMX: 100% equity value × exact effective ownership sau IPO.
- BHX: DCF hoặc EV/Sales/EV/EBITDA tùy maturity, rồi × ownership.
- An Khang, AVAKids, tài sản khác: phương pháp thận trọng và tách riêng.
- Parent assets/liabilities: chỉ phần chưa phân bổ.

Holdco discount là sensitivity, không phải phép sửa để đạt giá mong muốn. Trình bày NAV trước discount trước khi áp dụng 0%/10%/20%/30% hoặc range có cơ sở thị trường.

## 10. Stub value và implied BHX value

### 10.1 Market-implied stub

Khi có giá đóng cửa cùng ngày cho cả MWG và DMX:

```text
MWG_market_cap       = MWG_price × MWG_diluted_shares
DMX_market_cap       = DMX_price × DMX_diluted_shares
DMX_value_to_MWG     = theta_DMX × DMX_market_cap
Observed_stub_equity = MWG_market_cap - DMX_value_to_MWG
```

Trước khi DMX giao dịch, thay `DMX_price` bằng giá IPO hoặc DCF phải gắn nhãn `IPO-price-implied stub` hoặc `DCF-implied stub`, không gọi là market stub.

Stub không đồng nghĩa với BHX: nó còn chứa An Khang, AVAKids, tài sản/nghĩa vụ công ty mẹ, thuế, chi phí holding và discount kỳ vọng.

### 10.2 Implied standalone equity value của BHX

Nếu muốn giải residual cho 100% BHX:

```text
Implied_BHX_equity = {
  MWG_market_cap / (1 - assumed_holdco_discount)
  - theta_DMX × DMX_equity_value
  - Σ(theta_j × Other_equity_value_j)
  - Parent_non_operating_assets
  + Parent_only_net_debt
  + Parent_provisions
} / theta_BHX
```

Chạy bảng discount 0%/10%/20%/30% và nhiều DMX value cases. Nếu kết quả âm, giữ nguyên và giải thích đây là residual của giả định, không floor về 0.

## 11. Base/Bull/Bear

Scenario phải thay đổi driver kinh tế, không cộng/trừ cơ học 10% vào valuation.

| Driver | Bear | Base | Bull |
|---|---|---|---|
| Domestic SSSG / sales per store | Phục hồi yếu, mix bất lợi | Trung tâm theo evidence | Demand và premium mix tốt hơn |
| Store count | Đóng/không mở | Theo kế hoạch hợp lý | Mở có kỷ luật |
| Gross margin | Markdown/vendor funding bất lợi | Bình thường hóa | Service/premium mix hỗ trợ |
| Opex | Operating leverage thấp | Theo driver | Operating leverage cao |
| DIO/DPO | Cash conversion xấu | Bình thường | Tồn kho tốt, funding ổn định |
| EraBlue | Ramp chậm, margin thấp | Theo lộ trình khả thi | SSSG/mở cửa hàng tốt hơn |
| Capex | Cao hơn/hiệu quả chậm | Theo kế hoạch | Hiệu suất vốn tốt hơn |

WACC/g và exit multiple nằm trong bảng valuation sensitivity riêng. Không dùng đồng thời Bull operations + WACC cực thấp + terminal growth cực cao như một “best case” thiếu kỷ luật.

Current public website P/E illustration (VND tỷ) uses an earnings anchor to make the SOTP bridge easy to audit:

| Scenario | DMX NPAT | P/E | DMX equity | MWG share ~86% | Non-DMX stub | Parent adjustments | MWG equity illustration |
|---|---:|---:|---:|---:|---:|---:|---:|
| Bear | 6.700 | 10,0x | 67.000 | 57.620 | 28.000 | (8.000) | 77.620 |
| Base | 7.350 | 12,3x | 90.405 | 77.748,3 | 45.000 | (5.000) | 117.748,3 |
| Bull | 8.000 | 14,0x | 112.000 | 96.320 | 65.000 | (3.000) | 158.320 |

Đây là `illustrative equity value`, không phải target price. Không chuyển thành price/share hoặc upside/downside trước khi market-conclusion gate đạt yêu cầu.

Illustrative FCFF DCF output (VND tỷ, except value/share):

| Scenario | Enterprise value | Equity value | Value/share | Terminal value / EV |
|---|---:|---:|---:|---:|
| Bear | 77.784,4 | 99.908,5 | 78.809 | 65,8% |
| Base | 131.814,8 | 154.438,9 | 121.824 | 72,7% |
| Bull | 198.485,9 | 221.610,0 | 174.810 | 77,7% |

FCFF DCF dùng Q1 2026 pre-IPO cash/debt và cộng estimated net IPO proceeds VND 13.215,080 tỷ đúng một lần qua `IPO_Bridge!D20`. Website P/E table ở trên là phương pháp minh họa riêng, không phải kết quả chính của FCFF DCF.

## 12. Kiểm tra bắt buộc

Mô hình không được xuất kết quả khi một check critical khác 0 hoặc thiếu nguồn:

1. `Assets - Liabilities - Equity = 0`.
2. Cash flow closing cash = balance-sheet cash.
3. Debt, PPE và JV investment roll-forward bằng 0; retained earnings được trình bày là residual reconciliation nếu thiếu chi tiết statement of changes in equity.
4. `S0 + S_new - S1 = 0` và `S_new × P0 - G = 0`.
5. Tổng tỷ lệ sở hữu sau IPO = 100%; MWG stake dùng exact shares, không dùng rounded 86%.
6. `Pre_money + Gross_proceeds - Post_money = 0` tại cùng giá IPO.
7. Actual IPO close không lấy planned share count.
8. DCF equity bridge không cộng IPO proceeds hai lần.
9. SOTP không cộng EraBlue hoặc net cash/debt hai lần.
10. Reported/LFL/forecast không bị trộn trong cùng một series.
11. LTM không cộng một kỳ YTD với cả năm chứa kỳ đó.
12. Giá MWG và DMX, số cổ phần và FX có cùng ngày/nhãn ngày.
13. `WACC > g`; terminal value share of EV được hiển thị và cảnh báo nếu quá cao.
14. Bull/Base/Bear mapping đúng scenario và không có hard-code vào output; Base scenario DMX equity value khớp DMX_Valuation khi active scenario là Base.
15. Mỗi actual có source URL/page; mỗi assumption có owner/rationale.
16. NPAT-to-CFO bridge, cash roll và retained-earnings residual reconciliation reconcile về reported totals.
17. Working-capital days dùng average balance, đúng period days và có Q1 seasonality warning.
18. Khi starting balance sheet là Q1 pre-IPO, net-proceeds adjustment = VND 13.215,080 tỷ; khi balance sheet đã post-IPO, adjustment = 0.
19. Reported FY2025 và management LFL comparator cùng tồn tại; không overwrite statutory actual.

## 13. Giới hạn và cách trình bày trung thực

- Lịch sử DMX standalone ngắn và chịu ảnh hưởng tái cấu trúc cuối 2025; LFL do doanh nghiệp cung cấp không thay thế BCTC kiểm toán.
- FY2023 là comparative chưa kiểm toán trong BCTC FY2024; không có cùng mức assurance với FY2024–FY2025.
- Q1 2026 chỉ là kỳ 90 ngày chưa kiểm toán. DIO/DSO/DPO/CCC và CFO/NPAT chịu seasonality, không dùng như full-year run rate.
- Module hiện tại là three-statement **analysis** lịch sử; chưa phải fully integrated three-statement forecast. Forecast đầy đủ chỉ nên bổ sung khi scope chuyển mạnh sang FP&A/IB/Equity Research.
- Nghị quyết 15 nêu kế hoạch dùng VND 13.215,080 tỷ net proceeds để trả nợ; chưa có bằng chứng disbursement thì không trình bày là actual repayment.
- Sales kit chứa forward-looking statements và giả định hậu IPO; dùng làm benchmark, không làm forecast mặc định.
- Giá IPO là giá giao dịch sơ cấp; trước ngày niêm yết chưa có price discovery liên tục.
- Exact MWG ownership phải được lấy từ nguồn cổ đông chính thức; cụm “gần 86%” chỉ là kiểm tra định tính.
- Phân bổ corporate costs, transfer pricing và working capital giữa DMX/MWG có thể hạn chế tính so sánh lịch sử.
- Peer CE/ICT khu vực khác biệt về mix, chuẩn kế toán, lease và geography; comps là range, không là điểm chính xác.
- DCF nhạy với WACC, terminal growth, working capital và biên lợi nhuận; phải công bố sensitivity.
- Stub/implied BHX là residual phụ thuộc toàn bộ giả định khác, không phải appraisal độc lập.
- Website phải dùng các nhãn `Actual`, `Company guidance`, `Analyst assumption`, `Illustrative` rõ ràng.

## 14. Nguồn chính thức ưu tiên

1. [DMX Investor Relations](https://www.dmx.vn/eng) — BCTC, data pack, reports, disclosure; truy cập 2026-07-13.
2. [Hồ sơ chào bán IPO và BCTC đính kèm](https://www.dmx.vn/cong-bo-thong-tin/cbtt-thong-bao-chao-ban-co-phieu-ra-cong-chung-va-cac-tai-lieu-lien-quan-cua-ctcp-dau-tu-dien-may-xanh-5005813) — truy cập 2026-07-13.
3. [DMX IPO sales kit](https://cdnv2-tmdt.tgdd.vn/mwgvn/investorrelations/files/posts/2026/5/5005818/d8/6b/d86b5d707c2c0b5baea9dbcffafaaa50.pdf) — planned transaction và valuation illustration; truy cập 2026-07-13.
4. [Nghị quyết 14 về kết quả IPO](https://cdnv2-tmdt.tgdd.vn/mwgvn/investorrelations/files/posts/2026/7/0/f1/08/f108ca2a7399d9a70674915a4b2cf651.pdf) — actual shares/proceeds/charter capital; truy cập 2026-07-13.
5. [Nghị quyết 15 về net proceeds và kế hoạch sử dụng vốn](https://cdnv2-tmdt.tgdd.vn/mwgvn/investorrelations/files/posts/2026/7/0/38/65/38651afbcd5d099f0e968015b88da8ee.pdf) — estimated costs, estimated net proceeds và planned debt repayment; truy cập 2026-07-13.
6. [BCTC hợp nhất FY2024 đã kiểm toán](https://cdnv2-tmdt.tgdd.vn/mwgvn/investorrelations/files/posts/2026/5/0/93/e5/93e558113d3fa242567df336db5e4af6.pdf) — FY2024 actual và FY2023 comparative unaudited; truy cập 2026-07-13.
7. [BCTC hợp nhất FY2025 đã kiểm toán](https://cdnv2-tmdt.tgdd.vn/mwgvn/investorrelations/files/posts/2026/5/0/08/af/08af79013e9b9bdb210eb476e2fa7b95.pdf) — FY2025 actual; truy cập 2026-07-13.
8. [Q1 2026 consolidated data pack](https://cdnv2-tmdt.tgdd.vn/mwgvn/investorrelations/files/posts/2026/6/0/6b/e5/6be50a510e272451464dae07771401ca.xlsx) — unaudited Q1 actual/comparative; truy cập 2026-07-13.
9. [Công bố hoàn tất IPO](https://www.dmx.vn/eng/news/dien-may-xanh-completes-landmark-ipo-raising-more-than-vnd-13-315-billion-and-lifting-charter-capital-to-vnd-12-677-billion-5002485) — ownership gần 86% và business update; truy cập 2026-07-13.
10. [MWG Investor Relations](https://mwg.vn/) và [MWG disclosures](https://mwg.vn/cong-bo-thong-tin) — BCTC MWG, cổ phần, tài liệu ĐHĐCĐ; truy cập 2026-07-13.
11. [MWG: EraBlue là liên doanh](https://mwg.vn/tin-tuc/erablue-buoc-chuyen-minh-cua-the-gioi-di-dong-o-quoc-gia-dong-dan-nhat-asean-179) — kiểm tra perimeter/accounting; truy cập 2026-07-13.

Theo điều khoản của MWG/DMX, mọi trích dẫn lại từ website phải ghi rõ nguồn IR và thời điểm trích dẫn. Repository chỉ nên lưu derived data được phép sử dụng và source manifest; không re-host toàn bộ PDF nếu chưa kiểm tra quyền phân phối.
