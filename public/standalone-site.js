(() => {
  "use strict";

  const analysis = window.DMX_THREE_STATEMENT_ANALYSIS;
  const periods = ["FY2023A", "FY2024A", "FY2025A", "Q1 2026A"];
  const rows = [
    ["revenue", "Net revenue", "Income statement"],
    ["gross_profit", "Gross profit", "Income statement"],
    ["operating_profit", "Operating profit", "Income statement"],
    ["net_income", "NPAT attributable to parent", "Income statement"],
    ["total_assets", "Total assets", "Balance sheet"],
    ["inventory", "Net inventory", "Balance sheet"],
    ["total_debt", "Total debt", "Balance sheet"],
    ["total_equity", "Total equity", "Balance sheet"],
    ["operating_cash_flow", "Cash flow from operations", "Cash flow statement"],
    ["capex", "CapEx", "Cash flow statement"]
  ];
  const integer = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });
  const decimal = new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1
  });
  const byId = (id) => document.getElementById(id);

  function amount(value, digits = 1) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) return "N/D";
    const formatted = (digits === 0 ? integer : decimal).format(Math.abs(Number(value)));
    return Number(value) < 0 ? "(" + formatted + ")" : formatted;
  }

  function percent(value) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) return "N/D";
    return (Number(value) * 100).toFixed(1) + "%";
  }

  function days(value) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) return "N/D";
    return Number(value).toFixed(1) + "d";
  }

  function cell(row, tagName, text, className) {
    const node = document.createElement(tagName);
    if (className) node.className = className;
    node.textContent = text;
    row.appendChild(node);
    return node;
  }

  function bridgeItem(list, label, value, isTotal = false) {
    const item = document.createElement("div");
    if (isTotal) item.className = "bridge-total";
    cell(item, "dt", label);
    cell(item, "dd", value);
    list.appendChild(item);
  }

  function bridge(listId, checkId, payload, totalLabel, totalKey) {
    const list = byId(listId);
    const check = byId(checkId);
    if (!list || !check || !payload) return;

    list.replaceChildren();
    payload.components.forEach((component) => {
      bridgeItem(list, component.label, amount(component.amount_vnd_bn) + "bn");
    });
    bridgeItem(list, totalLabel, amount(payload[totalKey]) + "bn", true);
    check.textContent = payload.passed
      ? "Reconciled: difference " + amount(payload.difference_vnd_bn) + "bn"
      : "Review required: difference " + amount(payload.difference_vnd_bn) + "bn";
  }

  function renderThreeStatementAnalysis() {
    const status = byId("three-statement-status");
    if (!analysis) {
      if (status) {
        status.dataset.state = "error";
        status.firstElementChild.textContent = "Three-statement payload was not loaded.";
      }
      return;
    }

    const statements = periods
      .map((period) => analysis.statements.find((item) => item.period === period))
      .filter(Boolean);
    const byPeriod = Object.fromEntries(statements.map((statement) => [statement.period, statement]));

    if (status) {
      const statementCoverage = analysis.coverage.filter((item) => item.period !== "H1 2026");
      status.dataset.state = "ready";
      status.firstElementChild.textContent =
        statementCoverage.length + " statement periods plus H1 operating update | " + analysis.metadata.data_version;
      status.lastElementChild.textContent =
        analysis.metadata.fact_count + " facts | " + analysis.check_summary.passed + "/" + analysis.check_summary.checks + " checks passed";
    }

    const financialsBody = byId("financials-body");
    if (financialsBody) {
      financialsBody.replaceChildren();
      rows.forEach(([key, label, group], index) => {
        const tr = document.createElement("tr");
        const heading = cell(tr, "th", "");
        heading.scope = "row";
        if (index === 0 || rows[index - 1][2] !== group) {
          const small = document.createElement("small");
          small.textContent = group;
          heading.appendChild(small);
        }
        heading.append(document.createTextNode(label));
        periods.forEach((period) => {
          cell(tr, "td", amount(byPeriod[period]?.values_vnd_bn?.[key]));
        });
        financialsBody.appendChild(tr);
      });
    }

    const q1 = "Q1 2026A";
    bridge(
      "npat-cfo-bridge",
      "npat-cfo-check",
      analysis.bridges.npat_to_cfo.find((item) => item.period === q1),
      "Reported CFO",
      "reported_cfo_vnd_bn"
    );
    bridge(
      "cash-bridge",
      "cash-check",
      analysis.bridges.cash.find((item) => item.period === q1),
      "Reported closing cash",
      "reported_ending_cash_vnd_bn"
    );
    bridge(
      "retained-earnings-bridge",
      "retained-earnings-check",
      analysis.bridges.retained_earnings.find((item) => item.period === q1),
      "Reported closing retained earnings",
      "reported_closing_retained_earnings_vnd_bn"
    );

    const checkSummary = byId("check-summary");
    if (checkSummary) {
      checkSummary.textContent =
        analysis.check_summary.passed + "/" + analysis.check_summary.checks + " accounting checks passed";
    }

    const wcBody = byId("working-capital-body");
    if (wcBody) {
      wcBody.replaceChildren();
      analysis.working_capital.forEach((period) => {
        const tr = document.createElement("tr");
        const heading = cell(tr, "th", period.period);
        heading.scope = "row";
        if (period.q1_seasonality_warning) {
          const small = document.createElement("small");
          small.textContent = "90-day basis";
          heading.appendChild(small);
        }
        cell(tr, "td", days(period.days_inventory_outstanding));
        cell(tr, "td", days(period.days_sales_outstanding));
        cell(tr, "td", days(period.days_payables_outstanding));
        cell(tr, "td", days(period.cash_conversion_cycle));
        cell(tr, "td", percent(period.cfo_to_npat));
        cell(tr, "td", percent(period.inventory_provision_to_gross));
        cell(tr, "td", percent(period.capex_to_revenue));
        wcBody.appendChild(tr);
      });
    }

    const qoeBody = byId("quality-of-earnings-body");
    if (qoeBody) {
      qoeBody.replaceChildren();
      analysis.quality_of_earnings.forEach((item) => {
        const tr = document.createElement("tr");
        cell(tr, "th", item.indicator).scope = "row";
        cell(tr, "td", item.observation);
        cell(tr, "td", item.interpretation);
        cell(tr, "td", item.risk);
        qoeBody.appendChild(tr);
      });
    }

    const normalizationBody = byId("normalization-body");
    if (normalizationBody) {
      normalizationBody.replaceChildren();
      analysis.normalization.forEach((item) => {
        const tr = document.createElement("tr");
        cell(tr, "th", item.metric).scope = "row";
        cell(tr, "td", amount(item.reported_value_vnd_bn) + "bn");
        cell(tr, "td", amount(item.adjustment_vnd_bn) + "bn");
        cell(tr, "td", amount(item.normalized_value_vnd_bn) + "bn");
        cell(tr, "td", item.treatment.replaceAll("_", " ") + " | " + item.reason);
        normalizationBody.appendChild(tr);
      });
    }

    const limitations = byId("limitations-list");
    if (limitations) {
      limitations.replaceChildren();
      analysis.senior_readthroughs.forEach((item) => {
        const li = document.createElement("li");
        li.textContent = item;
        limitations.appendChild(li);
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", renderThreeStatementAnalysis);
  } else {
    renderThreeStatementAnalysis();
  }
})();