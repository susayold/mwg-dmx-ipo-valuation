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

- Dùng BCTC hợp nhất kiểm toán/công bố chính thức làm nguồn actual. Presentation, sales kit và phát biểu quản trị chỉ là nguồn KPI, guidance hoặc giả định.
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
| Tỷ lệ phân phối | 100,00% giả định | 92,72% | `actual_issued / offered` |
| Tỷ trọng cổ phần mới/post-money | 14,01% | 13,13% | `new_shares / post_shares` |
| Post-money market cap tại giá IPO | 102.462,712 tỷ VND | 101.417,760 tỷ VND | `post_shares × offer_price` |

Nghị quyết 14 ghi nhận 166.438.500 cổ phần được phân phối thành công; 13.061.900 cổ phần còn lại bị hủy, không tính vào vốn điều lệ. Đây là số dùng cho actual case.

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

Nếu ngày bắt đầu định giá là trước ngày hoàn tất IPO:

```text
Cash_post      = Cash_pre + Gross_proceeds - Issue_costs - Debt_repaid - Other_use
Debt_post      = Debt_pre - Debt_repaid + New_debt
Net_debt_post  = Debt_post - Cash_post
```

Việc dùng tiền trả nợ hay giữ tiền đều làm net debt giảm bằng tiền thu ròng, trước các uses khác. Không được vừa pro forma cash/net debt vừa cộng `net proceeds` lần nữa trong equity bridge.

EPS năm phát hành dùng cổ phần bình quân gia quyền theo ngày thực tế:

```text
Weighted_average_shares = Σ(shares_outstanding_i × days_i / days_in_year)
Basic_EPS                = NPAT_MI / Weighted_average_shares
```

Sales kit giả định cổ phần mới lưu hành sáu tháng cho EPS minh họa; actual model phải dùng ngày hoàn tất/đủ điều kiện ghi nhận theo tài liệu chính thức.

Sau IPO, nếu MWG vẫn kiểm soát DMX, DMX tiếp tục hợp nhất vào MWG và nhà đầu tư ngoài MWG là NCI. Phân bổ lợi nhuận dùng effective ownership, không dùng tỷ lệ cổ phần mới phát hành như một proxy.

## 5. DMX standalone driver model

### 5.1 Kỳ mô hình

- Historical: 2024A, 2025A, quý gần nhất được công bố tại valuation date.
- Pro forma comparator: 2025 LFL, trình bày bridge riêng từ reported.
- Forecast: 2026E–2030E.
- 2026E phải là `actual YTD + forecast remaining months`, không annualize máy móc một quý.

### 5.2 Revenue build

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

### 5.3 Biên lợi nhuận và chi phí

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

### 5.4 Working capital, capex và ba báo cáo

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

## 6. DCF DMX

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

## 7. Trading comparables

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

## 8. SOTP MWG

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

## 9. Stub value và implied BHX value

### 9.1 Market-implied stub

Khi có giá đóng cửa cùng ngày cho cả MWG và DMX:

```text
MWG_market_cap       = MWG_price × MWG_diluted_shares
DMX_market_cap       = DMX_price × DMX_diluted_shares
DMX_value_to_MWG     = theta_DMX × DMX_market_cap
Observed_stub_equity = MWG_market_cap - DMX_value_to_MWG
```

Trước khi DMX giao dịch, thay `DMX_price` bằng giá IPO hoặc DCF phải gắn nhãn `IPO-price-implied stub` hoặc `DCF-implied stub`, không gọi là market stub.

Stub không đồng nghĩa với BHX: nó còn chứa An Khang, AVAKids, tài sản/nghĩa vụ công ty mẹ, thuế, chi phí holding và discount kỳ vọng.

### 9.2 Implied standalone equity value của BHX

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

## 10. Base/Bull/Bear

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

## 11. Kiểm tra bắt buộc

Mô hình không được xuất kết quả khi một check critical khác 0 hoặc thiếu nguồn:

1. `Assets - Liabilities - Equity = 0`.
2. Cash flow closing cash = balance-sheet cash.
3. Debt, PPE, retained earnings và JV investment roll-forward bằng 0.
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
14. Bull/Base/Bear mapping đúng scenario và không có hard-code vào output.
15. Mỗi actual có source URL/page; mỗi assumption có owner/rationale.

## 12. Giới hạn và cách trình bày trung thực

- Lịch sử DMX standalone ngắn và chịu ảnh hưởng tái cấu trúc cuối 2025; LFL do doanh nghiệp cung cấp không thay thế BCTC kiểm toán.
- Sales kit chứa forward-looking statements và giả định hậu IPO; dùng làm benchmark, không làm forecast mặc định.
- Giá IPO là giá giao dịch sơ cấp; trước ngày niêm yết chưa có price discovery liên tục.
- Exact MWG ownership phải được lấy từ nguồn cổ đông chính thức; cụm “gần 86%” chỉ là kiểm tra định tính.
- Phân bổ corporate costs, transfer pricing và working capital giữa DMX/MWG có thể hạn chế tính so sánh lịch sử.
- Peer CE/ICT khu vực khác biệt về mix, chuẩn kế toán, lease và geography; comps là range, không là điểm chính xác.
- DCF nhạy với WACC, terminal growth, working capital và biên lợi nhuận; phải công bố sensitivity.
- Stub/implied BHX là residual phụ thuộc toàn bộ giả định khác, không phải appraisal độc lập.
- Website phải dùng các nhãn `Actual`, `Company guidance`, `Analyst assumption`, `Illustrative` rõ ràng.

## 13. Nguồn chính thức ưu tiên

1. [DMX Investor Relations](https://www.dmx.vn/eng) — BCTC, data pack, reports, disclosure; truy cập 2026-07-13.
2. [Hồ sơ chào bán IPO và BCTC đính kèm](https://www.dmx.vn/cong-bo-thong-tin/cbtt-thong-bao-chao-ban-co-phieu-ra-cong-chung-va-cac-tai-lieu-lien-quan-cua-ctcp-dau-tu-dien-may-xanh-5005813) — truy cập 2026-07-13.
3. [DMX IPO sales kit](https://cdnv2-tmdt.tgdd.vn/mwgvn/investorrelations/files/posts/2026/5/5005818/d8/6b/d86b5d707c2c0b5baea9dbcffafaaa50.pdf) — planned transaction và valuation illustration; truy cập 2026-07-13.
4. [Nghị quyết 14 về kết quả IPO](https://cdnv2-tmdt.tgdd.vn/mwgvn/investorrelations/files/posts/2026/7/0/f1/08/f108ca2a7399d9a70674915a4b2cf651.pdf) — actual shares/proceeds/charter capital; truy cập 2026-07-13.
5. [Công bố hoàn tất IPO](https://www.dmx.vn/eng/news/dien-may-xanh-completes-landmark-ipo-raising-more-than-vnd-13-315-billion-and-lifting-charter-capital-to-vnd-12-677-billion-5002485) — ownership gần 86% và business update; truy cập 2026-07-13.
6. [MWG Investor Relations](https://mwg.vn/) và [MWG disclosures](https://mwg.vn/cong-bo-thong-tin) — BCTC MWG, cổ phần, tài liệu ĐHĐCĐ; truy cập 2026-07-13.
7. [MWG: EraBlue là liên doanh](https://mwg.vn/tin-tuc/erablue-buoc-chuyen-minh-cua-the-gioi-di-dong-o-quoc-gia-dong-dan-nhat-asean-179) — kiểm tra perimeter/accounting; truy cập 2026-07-13.

Theo điều khoản của MWG/DMX, mọi trích dẫn lại từ website phải ghi rõ nguồn IR và thời điểm trích dẫn. Repository chỉ nên lưu derived data được phép sử dụng và source manifest; không re-host toàn bộ PDF nếu chưa kiểm tra quyền phân phối.
