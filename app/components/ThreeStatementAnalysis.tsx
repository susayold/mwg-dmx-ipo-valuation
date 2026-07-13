import { threeStatementAnalysis } from "../data/case-data";

const formatBn = (value: number | null | undefined, digits = 0) => {
  if (value == null) return "N/D";

  const absolute = new Intl.NumberFormat("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(Math.abs(value));

  return value < 0 ? "(" + absolute + ")" : absolute;
};

const formatPct = (value: number | null | undefined, digits = 1) =>
  value == null ? "N/D" : (value * 100).toFixed(digits) + "%";

const formatDays = (value: number | null | undefined) =>
  value == null ? "N/D" : value.toFixed(1) + "d";

const humanize = (value: string) => value.replaceAll("_", " ");

const statementRows = [
  { key: "revenue", label: "Net revenue", group: "Income statement" },
  { key: "gross_profit", label: "Gross profit", group: "Income statement" },
  {
    key: "operating_profit",
    label: "Operating profit",
    group: "Income statement",
  },
  { key: "net_income", label: "NPAT", group: "Income statement" },
  { key: "total_assets", label: "Total assets", group: "Balance sheet" },
  { key: "inventory", label: "Net inventory", group: "Balance sheet" },
  { key: "total_debt", label: "Total debt", group: "Balance sheet" },
  { key: "total_equity", label: "Total equity", group: "Balance sheet" },
  {
    key: "operating_cash_flow",
    label: "Cash flow from operations",
    group: "Cash flow statement",
  },
  {
    key: "capex",
    label: "CapEx (cash outflow)",
    group: "Cash flow statement",
  },
] as const;

type BridgeComponent = {
  amount_vnd_bn: number;
  label: string;
};

function BridgeCard({
  title,
  subtitle,
  components,
  totalLabel,
  total,
  passed,
}: {
  title: string;
  subtitle: string;
  components: BridgeComponent[];
  totalLabel: string;
  total: number;
  passed: boolean;
}) {
  return (
    <article className="bridge-card">
      <div className="bridge-card-head">
        <div>
          <span>{subtitle}</span>
          <h3>{title}</h3>
        </div>
        <b className={passed ? "check-pass" : "check-fail"}>
          {passed ? "RECONCILED" : "REVIEW"}
        </b>
      </div>
      <div className="bridge-table-wrap">
        <table className="bridge-table">
          <caption className="sr-only">{title} reconciliation</caption>
          <tbody>
            {components.map((component, index) => (
              <tr key={[component.label, index].join("-")}>
                <th scope="row">{component.label}</th>
                <td>{formatBn(component.amount_vnd_bn, 1)}</td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr>
              <th scope="row">{totalLabel}</th>
              <td>{formatBn(total, 1)}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </article>
  );
}

export function ThreeStatementAnalysis() {
  const statements = threeStatementAnalysis.statements.filter(
    (statement) => statement.period !== "Q1 2025A",
  );
  const latestStatement = statements.find(
    (statement) => statement.period === "Q1 2026A",
  );
  const fy2023Statement = statements.find(
    (statement) => statement.period === "FY2023A",
  );
  const fy2025Statement = statements.find(
    (statement) => statement.period === "FY2025A",
  );
  const npatBridge = threeStatementAnalysis.bridges.npat_to_cfo.find(
    (bridge) => bridge.period === "Q1 2026A",
  );
  const cashBridge = threeStatementAnalysis.bridges.cash.find(
    (bridge) => bridge.period === "Q1 2026A",
  );
  const retainedEarningsBridge =
    threeStatementAnalysis.bridges.retained_earnings.find(
      (bridge) => bridge.period === "Q1 2026A",
    );
  const fy2024WorkingCapital = threeStatementAnalysis.working_capital.find(
    (period) => period.period === "FY2024A",
  );
  const fy2025WorkingCapital = threeStatementAnalysis.working_capital.find(
    (period) => period.period === "FY2025A",
  );
  const q1WorkingCapital = threeStatementAnalysis.working_capital.find(
    (period) => period.period === "Q1 2026A",
  );

  if (
    !latestStatement ||
    !fy2023Statement ||
    !fy2025Statement ||
    !npatBridge ||
    !cashBridge ||
    !retainedEarningsBridge ||
    !fy2024WorkingCapital ||
    !fy2025WorkingCapital ||
    !q1WorkingCapital
  ) {
    throw new Error("Generated three-statement payload is missing a required period.");
  }

  const cccImprovement =
    fy2024WorkingCapital.cash_conversion_cycle -
    fy2025WorkingCapital.cash_conversion_cycle;

  return (
    <>
      <section className="section financials-section" id="financials">
        <div className="section-heading">
          <span className="eyebrow">04 / Three-statement history</span>
          <h2>Three years. One connected financial system.</h2>
          <p>
            Statutory income statement, balance sheet and cash-flow lines are
            compared from FY2023 to FY2025, with Q1 2026 used only as a current
            trend update. Values are reported VND bn.
          </p>
        </div>

        <div className="coverage-strip" aria-label="Financial statement coverage">
          {threeStatementAnalysis.coverage.map((item) => (
            <div key={item.period}>
              <span>{item.period}</span>
              <strong>{item.status}</strong>
              <small>{item.source_id}</small>
            </div>
          ))}
        </div>

        <div className="statement-table-wrap">
          <table className="statement-table">
            <caption>
              Comparative DMX consolidated financial statements — VND bn
            </caption>
            <thead>
              <tr>
                <th scope="col">Reported line item</th>
                {statements.map((statement) => (
                  <th scope="col" key={statement.period}>
                    {statement.period}
                    <small>{statement.audit_status}</small>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {statementRows.map((row, index) => {
                const isNewGroup =
                  index === 0 || statementRows[index - 1].group !== row.group;

                return (
                  <tr className={isNewGroup ? "group-start" : ""} key={row.key}>
                    <th scope="row">
                      {isNewGroup && <small>{row.group}</small>}
                      {row.label}
                    </th>
                    {statements.map((statement) => (
                      <td key={statement.period}>
                        {formatBn(statement.values_vnd_bn[row.key], 1)}
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="financial-readout">
          <article>
            <span>FY23 → FY25 revenue CAGR</span>
            <strong>
              {formatPct(
                Math.pow(
                  fy2025Statement.values_vnd_bn.revenue /
                    fy2023Statement.values_vnd_bn.revenue,
                  1 / 2,
                ) - 1,
              )}
            </strong>
            <p>Calculated from statutory reported revenue, not LFL figures.</p>
          </article>
          <article>
            <span>FY25 CFO / NPAT</span>
            <strong>{formatPct(fy2025WorkingCapital.cfo_to_npat)}</strong>
            <p>Below one, after strong conversion in FY2024.</p>
          </article>
          <article>
            <span>Q1 2026 gross margin</span>
            <strong>{formatPct(latestStatement.ratios.gross_margin)}</strong>
            <p>Quarterly result; mix and seasonality still require testing.</p>
          </article>
        </div>

        <p className="data-boundary-note">
          <strong>Evidence boundary:</strong> FY2023 is an unaudited comparative
          in the FY2024 filing; FY2024–FY2025 are audited; Q1 2026 is unaudited.
          H1 2026 was an operating update only at the data cut-off, so no H1
          balance-sheet or cash-flow statement is inferred.
        </p>
      </section>

      <section className="section bridges-section" id="bridges">
        <div className="section-heading">
          <span className="eyebrow light">05 / Accounting bridges</span>
          <h2>The statements reconcile before the story begins.</h2>
          <p>
            These Q1 2026 bridges show how profit converts into operating cash,
            how cash rolls forward and how retained earnings connect to equity.
          </p>
        </div>

        <div className="bridge-grid">
          <BridgeCard
            title="NPAT → CFO"
            subtitle={npatBridge.period}
            components={npatBridge.components}
            totalLabel="Reported CFO"
            total={npatBridge.reported_cfo_vnd_bn}
            passed={npatBridge.passed}
          />
          <BridgeCard
            title="Opening → closing cash"
            subtitle={cashBridge.period}
            components={cashBridge.components}
            totalLabel="Reported closing cash"
            total={cashBridge.reported_ending_cash_vnd_bn}
            passed={cashBridge.passed}
          />
          <BridgeCard
            title="Retained earnings roll"
            subtitle={retainedEarningsBridge.period}
            components={retainedEarningsBridge.components}
            totalLabel="Reported closing retained earnings"
            total={
              retainedEarningsBridge.reported_closing_retained_earnings_vnd_bn
            }
            passed={retainedEarningsBridge.passed}
          />
        </div>

        <div className="checks-banner">
          <div>
            <span>Automated accounting controls</span>
            <strong>
              {threeStatementAnalysis.check_summary.passed}/
              {threeStatementAnalysis.check_summary.checks} passed
            </strong>
          </div>
          <p>
            Balance sheet, gross-profit, tax, inventory, cash-flow and bridge
            checks all reconcile within the generated dataset. A passing check
            confirms arithmetic consistency—not the absence of business risk.
          </p>
        </div>
      </section>

      <section className="section working-capital-section" id="working-capital">
        <div className="section-heading">
          <span className="eyebrow">06 / Working capital</span>
          <h2>Retail cash quality lives in inventory and supplier funding.</h2>
          <p>
            CCC = DIO + DSO − DPO. The schedule uses average opening and closing
            trade balances, net inventory and actual elapsed days.
          </p>
        </div>

        <div className="wc-callouts">
          <article>
            <span>FY2025 cash conversion cycle</span>
            <strong>{formatDays(fy2025WorkingCapital.cash_conversion_cycle)}</strong>
            <p>{cccImprovement.toFixed(1)} days shorter than FY2024.</p>
          </article>
          <article className="warning">
            <span>Q1 2026 CFO / NPAT</span>
            <strong>{formatPct(q1WorkingCapital.cfo_to_npat)}</strong>
            <p>Supplier payables absorbed VND 466bn in the quarter.</p>
          </article>
          <article>
            <span>Q1 inventory provision / gross</span>
            <strong>
              {formatPct(q1WorkingCapital.inventory_provision_to_gross)}
            </strong>
            <p>
              Up from{" "}
              {formatPct(fy2025WorkingCapital.inventory_provision_to_gross)} at
              FY2025.
            </p>
          </article>
        </div>

        <div className="wc-table-wrap">
          <table className="wc-table">
            <caption>Working-capital and cash-conversion schedule</caption>
            <thead>
              <tr>
                <th scope="col">Period</th>
                <th scope="col">DIO</th>
                <th scope="col">DSO</th>
                <th scope="col">DPO</th>
                <th scope="col">CCC</th>
                <th scope="col">CFO / NPAT</th>
                <th scope="col">Inventory provision</th>
                <th scope="col">CapEx / revenue</th>
              </tr>
            </thead>
            <tbody>
              {threeStatementAnalysis.working_capital.map((period) => (
                <tr key={period.period}>
                  <th scope="row">
                    {period.period}
                    {period.q1_seasonality_warning && <small>90-day basis</small>}
                  </th>
                  <td>{formatDays(period.days_inventory_outstanding)}</td>
                  <td>{formatDays(period.days_sales_outstanding)}</td>
                  <td>{formatDays(period.days_payables_outstanding)}</td>
                  <td className="key-cell">
                    {formatDays(period.cash_conversion_cycle)}
                  </td>
                  <td>{formatPct(period.cfo_to_npat)}</td>
                  <td>{formatPct(period.inventory_provision_to_gross)}</td>
                  <td>{formatPct(period.capex_to_revenue)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="table-note">
          Q1 metrics are calculated on a 90-day YTD basis and should not be
          annualized mechanically. A shorter quarterly CCC does not by itself
          prove structural improvement.
        </p>
      </section>

      <section className="section quality-section" id="quality-of-earnings">
        <div className="section-heading">
          <span className="eyebrow">07 / Earnings quality</span>
          <h2>Separate the observation from the interpretation.</h2>
          <p>
            Each signal is presented with its analytical read-through and the
            risk that could invalidate it. Normalization is applied only where a
            disclosed comparator exists.
          </p>
        </div>

        <div className="qoe-grid">
          {threeStatementAnalysis.quality_of_earnings.map((item) => (
            <article key={item.indicator}>
              <span>{item.indicator}</span>
              <h3>{item.observation}</h3>
              <dl>
                <div>
                  <dt>Interpretation</dt>
                  <dd>{item.interpretation}</dd>
                </div>
                <div>
                  <dt>Risk / next test</dt>
                  <dd>{item.risk}</dd>
                </div>
              </dl>
            </article>
          ))}
        </div>

        <div className="normalization-panel">
          <div className="normalization-copy">
            <span className="card-label">Normalization discipline</span>
            <h3>No evidence, no adjustment.</h3>
            <p>
              Management LFL figures are retained as separate comparators. They
              do not overwrite statutory statements, and missing detail is
              shown as not determined rather than back-solved.
            </p>
            <ul>
              {threeStatementAnalysis.senior_readthroughs.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <div className="normalization-table-wrap">
            <table className="normalization-table">
              <caption>FY2025 normalization register — VND bn</caption>
              <thead>
                <tr>
                  <th scope="col">Metric</th>
                  <th scope="col">Reported</th>
                  <th scope="col">Adjustment</th>
                  <th scope="col">Normalized</th>
                  <th scope="col">Treatment</th>
                </tr>
              </thead>
              <tbody>
                {threeStatementAnalysis.normalization.map((item) => (
                  <tr key={item.metric}>
                    <th scope="row">
                      {item.metric}
                      <small>{item.reason}</small>
                    </th>
                    <td>{formatBn(item.reported_value_vnd_bn, 1)}</td>
                    <td>{formatBn(item.adjustment_vnd_bn, 1)}</td>
                    <td>{formatBn(item.normalized_value_vnd_bn, 1)}</td>
                    <td>{humanize(item.treatment)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <p className="data-version">
          Generated dataset: {threeStatementAnalysis.metadata.data_version} ·
          Cut-off {threeStatementAnalysis.metadata.data_cutoff} ·{" "}
          {threeStatementAnalysis.metadata.forecast_boundary}
        </p>
      </section>
    </>
  );
}
