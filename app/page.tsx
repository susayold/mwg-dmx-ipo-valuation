import { ValuationLab } from "./components/ValuationLab";
import { ThreeStatementAnalysis } from "./components/ThreeStatementAnalysis";
import {
  analyticalChecks,
  dataCutoff,
  ipoFacts,
  managementForecast,
  modelBoundary,
  officialSources,
  q1Facts,
  sixMonthFacts,
} from "./data/case-data";

const number = (value: number, digits = 0) =>
  new Intl.NumberFormat("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value);

const revenueGrowth =
  q1Facts.revenue2026VndBn / q1Facts.revenue2025VndBn - 1;
const npatGrowth = q1Facts.npat2026VndBn / q1Facts.npat2025VndBn - 1;
const grossMargin2026 =
  q1Facts.grossProfit2026VndBn / q1Facts.revenue2026VndBn;
const grossMargin2025 =
  q1Facts.grossProfit2025VndBn / q1Facts.revenue2025VndBn;
const netMargin2026 = q1Facts.npat2026VndBn / q1Facts.revenue2026VndBn;
const cfoConversion = q1Facts.cfo2026VndBn / q1Facts.npat2026VndBn;
const netCashLike =
  q1Facts.cashVndBn +
  q1Facts.termDepositsVndBn -
  q1Facts.shortTermDebtVndBn;

export default function Home() {
  return (
    <main>
      <header className="site-header">
        <a className="wordmark" href="#top" aria-label="Go to top">
          <span>MWG</span>
          <i>/</i>
          <span>DMX</span>
          <small>IPO LAB</small>
        </a>
        <nav aria-label="Primary navigation">
          <a href="#financials">Financials</a>
          <a href="#bridges">Bridges</a>
          <a href="#working-capital">Working capital</a>
          <a href="#valuation">Valuation lab</a>
        </nav>
        <a className="header-cta" href="/downloads/MWG_DMX_IPO_SOTP_Model.xlsx">
          Download model
        </a>
      </header>

      <section className="hero" id="top">
        <div className="hero-grid">
          <div className="hero-copy">
            <div className="hero-kicker">
              <span className="live-dot" />
              Event-driven valuation case · Data cut-off {dataCutoff}
            </div>
            <h1>
              MWG after the
              <span> DMX IPO.</span>
            </h1>
            <p className="hero-lede">
              A source-traceable model that separates the listed-electronics
              engine from the remaining MWG stub—and makes every valuation
              assumption visible.
            </p>
            <div className="hero-actions">
              <a className="button primary" href="#valuation">
                Open valuation lab
              </a>
              <a className="button text" href="#case">
                Read the case <span aria-hidden="true">↓</span>
              </a>
            </div>
            <div className="hero-meta">
              <div>
                <span>Deliverable</span>
                <strong>Independent analyst work sample</strong>
              </div>
              <div>
                <span>Methods</span>
                <strong>IPO bridge · SOTP · scenarios</strong>
              </div>
            </div>
          </div>

          <aside className="ipo-ticket" aria-label="DMX IPO facts">
            <div className="ticket-top">
              <span>Transaction snapshot</span>
              <span>ACTUAL</span>
            </div>
            <div className="ticket-value">
              <strong>{number(ipoFacts.grossProceedsVndBn / 1_000, 1)}</strong>
              <div>
                <span>VND</span>
                <span>trillion</span>
              </div>
            </div>
            <p>Gross proceeds from the completed primary offering.</p>
            <div className="ticket-grid">
              <div>
                <span>Offer price</span>
                <strong>{number(ipoFacts.offerPriceVnd / 1_000)}k</strong>
              </div>
              <div>
                <span>Shares issued</span>
                <strong>{number(ipoFacts.sharesIssuedMillion, 1)}m</strong>
              </div>
              <div>
                <span>Post shares</span>
                <strong>{number(ipoFacts.postOfferSharesMillion, 1)}m</strong>
              </div>
              <div>
                <span>MWG ownership</span>
                <strong>{ipoFacts.mwgOwnershipDisclosure}</strong>
              </div>
            </div>
            <div className="ticket-foot">
              <span>Primary source</span>
              <a href={officialSources[0].url} target="_blank" rel="noreferrer">
                IPO result ↗
              </a>
            </div>
          </aside>
        </div>
        <div className="hero-stripe" aria-hidden="true">
          <span>PUBLIC FILINGS</span>
          <span>NO BLACK BOX</span>
          <span>FORMULAS INCLUDED</span>
          <span>SOURCE → CONTROL → DECISION</span>
        </div>
      </section>

      <section className="section case-section" id="case">
        <div className="section-heading">
          <span className="eyebrow">01 / The decision</span>
          <h2>Do not value MWG as one undifferentiated retailer.</h2>
          <p>
            The IPO creates an observable valuation anchor for DMX. The harder
            question is what remains at MWG—and whether the stub is being valued
            consistently without double-counting EraBlue or the IPO cash.
          </p>
        </div>

        <div className="decision-grid">
          <article className="question-card">
            <span>Core question</span>
            <blockquote>
              After valuing MWG&apos;s post-IPO stake in DMX, what value is
              attributable to Bach Hoa Xanh, An Khang, AvaKids and parent-level
              adjustments?
            </blockquote>
            <div className="formula">
              <span>MWG equity</span>
              <b>=</b>
              <span>DMX stake</span>
              <b>+</b>
              <span>Non-DMX stub</span>
              <b>±</b>
              <span>Parent adjustments</span>
            </div>
          </article>

          <article className="signal-card">
            <div className="signal-index">A</div>
            <div>
              <span className="card-label">Transaction</span>
              <h3>Value crystallisation</h3>
              <p>
                The completed offer establishes a transparent post-money anchor
                of approximately VND {number(ipoFacts.postMoneyEquityVndBn / 1_000, 1)}tn
                at the IPO price.
              </p>
            </div>
          </article>
          <article className="signal-card">
            <div className="signal-index">B</div>
            <div>
              <span className="card-label">Operations</span>
              <h3>Margin expansion</h3>
              <p>
                Q1 gross margin expanded by{" "}
                {number((grossMargin2026 - grossMargin2025) * 10_000)} bps while
                reported revenue grew {number(revenueGrowth * 100, 1)}%.
              </p>
            </div>
          </article>
          <article className="signal-card risk">
            <div className="signal-index">C</div>
            <div>
              <span className="card-label">Watchpoint</span>
              <h3>Cash conversion</h3>
              <p>
                Q1 CFO covered only {number(cfoConversion * 100)}% of NPAT,
                making working capital a necessary stress-test—not a footnote.
              </p>
            </div>
          </article>
        </div>
      </section>

      <section className="section boundary-section">
        <div className="section-heading compact">
          <span className="eyebrow">02 / Model boundary</span>
          <h2>One map prevents the biggest SOTP error.</h2>
          <p>
            EraBlue is an equity-accounted joint venture inside DMX. It must not
            reappear in the MWG stub.
          </p>
        </div>

        <div className="ownership-map">
          <div className="map-parent">
            <span>HOSE: MWG</span>
            <strong>Mobile World Investment Corporation</strong>
          </div>
          <div className="map-branches">
            <article className="map-card dmx">
              <div className="map-card-head">
                <span>DMX perimeter</span>
                <strong>Nearly 86% disclosed</strong>
              </div>
              <ul>
                {modelBoundary.insideDmx.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
              <p>EraBlue value enters once through DMX earnings or JV value.</p>
            </article>
            <article className="map-card stub">
              <div className="map-card-head">
                <span>MWG stub</span>
                <strong>Value separately</strong>
              </div>
              <ul>
                {modelBoundary.mwgStub.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
              <p>Apply parent net debt, cash and holding-company adjustments.</p>
            </article>
          </div>
        </div>
      </section>

      <section className="section performance-section">
        <div className="section-heading compact">
          <span className="eyebrow">03 / Current evidence</span>
          <h2>Growth is visible. Cash quality still needs watching.</h2>
        </div>

        <div className="metric-row">
          <article>
            <span>1Q26 revenue</span>
            <strong>{number(q1Facts.revenue2026VndBn / 1_000, 1)}tn</strong>
            <i>+{number(revenueGrowth * 100, 1)}% YoY</i>
          </article>
          <article>
            <span>1Q26 NPAT</span>
            <strong>{number(q1Facts.npat2026VndBn / 1_000, 2)}tn</strong>
            <i>+{number(npatGrowth * 100, 1)}% YoY</i>
          </article>
          <article>
            <span>Net margin</span>
            <strong>{number(netMargin2026 * 100, 1)}%</strong>
            <i>Reported financials</i>
          </article>
          <article>
            <span>Cash + deposits − debt</span>
            <strong>{number(netCashLike / 1_000, 1)}tn</strong>
            <i>31 March 2026</i>
          </article>
        </div>

        <div className="evidence-grid">
          <article className="evidence-card chart-card">
            <div className="card-heading">
              <div>
                <span>6M26 operating pulse</span>
                <h3>Revenue at 53% of guidance</h3>
              </div>
              <strong>{number(sixMonthFacts.revenueVndBn / 1_000, 1)}tn</strong>
            </div>
            <div className="progress-track" aria-label="53 percent of guidance">
              <span style={{ width: sixMonthFacts.revenueGuidanceCompletionPct + "%" }} />
            </div>
            <div className="mini-metrics">
              <div>
                <span>Revenue growth</span>
                <strong>+{sixMonthFacts.revenueGrowthPct}%</strong>
              </div>
              <div>
                <span>SSSG</span>
                <strong>+{sixMonthFacts.sameStoreSalesGrowthPct}%</strong>
              </div>
              <div>
                <span>Financed sales</span>
                <strong>{sixMonthFacts.financedSalesMixPct}% mix</strong>
              </div>
              <div>
                <span>EraBlue</span>
                <strong>{sixMonthFacts.erablueStores} stores</strong>
              </div>
            </div>
            <p>
              Issuer operating update; unaudited. The +31% revenue growth is on
              the company&apos;s stated like-for-like basis ({sixMonthFacts.sourceId}).
            </p>
          </article>

          <article className="evidence-card cash-card">
            <div className="card-heading">
              <div>
                <span>1Q26 earnings quality</span>
                <h3>NPAT to cash bridge</h3>
              </div>
              <strong>{number(cfoConversion * 100)}%</strong>
            </div>
            <div className="cash-bars" role="img" aria-label="NPAT versus operating cash flow">
              <div>
                <span style={{ height: "100%" }} />
                <b>NPAT</b>
                <strong>{number(q1Facts.npat2026VndBn)}bn</strong>
              </div>
              <div>
                <span style={{ height: cfoConversion * 100 + "%" }} />
                <b>CFO</b>
                <strong>{number(q1Facts.cfo2026VndBn)}bn</strong>
              </div>
            </div>
            <p>
              Inventory and supplier-payable movements explain why a profitable
              quarter did not convert one-for-one into operating cash.
            </p>
          </article>
        </div>
      </section>

      <ThreeStatementAnalysis />

      <section className="section forecast-section" id="forecast">
        <div className="section-heading">
          <span className="eyebrow">08 / Forecast evidence</span>
          <h2>Management&apos;s case is a benchmark—not the answer.</h2>
          <p>
            The model stores management guidance separately from Bear, Base and
            Bull assumptions. This prevents a presentation target from becoming
            an unchallenged analyst forecast.
          </p>
        </div>

        <div className="forecast-panel">
          <div className="forecast-chart" role="img" aria-label="DMX revenue and net profit forecast">
            {managementForecast.map((point) => (
              <div className="forecast-column" key={point.year}>
                <div className="bar-space">
                  <span
                    className={
                      point.status === "management_lfl_actual" ? "actual" : ""
                    }
                    style={{ height: (point.revenue / 182_000) * 100 + "%" }}
                  >
                    <i>{number(point.revenue / 1_000)}</i>
                  </span>
                </div>
                <strong>{point.year}</strong>
              </div>
            ))}
          </div>
          <div className="forecast-table-wrap">
            <table>
              <thead>
                <tr>
                  <th>VND bn</th>
                  {managementForecast.map((point) => (
                    <th key={point.year}>{point.year}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th>Revenue</th>
                  {managementForecast.map((point) => (
                    <td key={point.year}>{number(point.revenue)}</td>
                  ))}
                </tr>
                <tr>
                  <th>NPAT</th>
                  {managementForecast.map((point) => (
                    <td key={point.year}>{number(point.npat)}</td>
                  ))}
                </tr>
                <tr>
                  <th>Gross margin</th>
                  {managementForecast.map((point) => (
                    <td key={point.year}>{number(point.grossMargin, 1)}%</td>
                  ))}
                </tr>
              </tbody>
            </table>
            <p>
              2025A is the company&apos;s like-for-like reference; 2026F–2030F
              are management projections. Reported and LFL values are not mixed.
            </p>
          </div>
        </div>
      </section>

      <section className="section valuation-section" id="valuation">
        <ValuationLab />
      </section>

      <section className="section methodology-section" id="methodology">
        <div className="section-heading">
          <span className="eyebrow light">09 / Audit trail</span>
          <h2>Built to be reviewed and challenged.</h2>
          <p>
            The repository keeps official facts, management guidance and analyst
            assumptions in separate layers. Every number can be traced back to
            a source or an assumptions register.
          </p>
        </div>

        <div className="pipeline" aria-label="Data pipeline">
          {["Official filing", "Allowlisted extraction", "QA checks", "Curated facts", "Model & website"].map(
            (step, index) => (
              <div key={step}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <strong>{step}</strong>
              </div>
            ),
          )}
        </div>

        <div className="method-grid">
          <article>
            <span className="card-label">Controls</span>
            <h3>Six non-negotiable checks</h3>
            <ul className="check-list">
              {analyticalChecks.map((check) => (
                <li key={check}>{check}</li>
              ))}
            </ul>
          </article>
          <article>
            <span className="card-label">Artifacts</span>
            <h3>Everything a recruiter can inspect</h3>
            <div className="artifact-list">
              <a href="/downloads/MWG_DMX_IPO_SOTP_Model.xlsx">
                <span>Excel financial model</span>
                <b>XLSX ↗</b>
              </a>
              <a href="/downloads/Investment_Memo_EN.pdf">
                <span>Investment memo</span>
                <b>PDF ↗</b>
              </a>
              <a href="/downloads/validation_report.html">
                <span>Validation report</span>
                <b>HTML ↗</b>
              </a>
              <a href="/downloads/dmx_three_statement_analysis.json">
                <span>Three-statement dataset</span>
                <b>JSON ↗</b>
              </a>
              <a href="#sources">
                <span>Source register</span>
                <b>WEB ↓</b>
              </a>
            </div>
          </article>
        </div>
      </section>

      <section className="section sources-section" id="sources">
        <div className="section-heading compact">
          <span className="eyebrow">10 / Sources</span>
          <h2>Primary documents, not scraped summaries.</h2>
        </div>
        <div className="source-list">
          {officialSources.map((source, index) => (
            <a href={source.url} target="_blank" rel="noreferrer" key={source.id}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <div>
                <strong>{source.title}</strong>
                <p>{source.detail}</p>
              </div>
              <b>{source.id} ↗</b>
            </a>
          ))}
        </div>
      </section>

      <footer>
        <div>
          <span className="wordmark footer-mark">
            <span>MWG</span>
            <i>/</i>
            <span>DMX</span>
          </span>
          <p>
            Independent portfolio project. Public information only. Not
            investment advice.
          </p>
        </div>
        <div>
          <span>Data cut-off</span>
          <strong>{dataCutoff}</strong>
        </div>
        <a href="#top">Back to top ↑</a>
      </footer>
    </main>
  );
}
