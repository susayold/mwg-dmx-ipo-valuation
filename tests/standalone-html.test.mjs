import assert from "node:assert/strict";
import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const htmlPath = path.join(root, "index.html");
const threeStatementScriptPath = path.join(root, "public", "three-statement-data.js");
const standaloneScriptPath = path.join(root, "public", "standalone-site.js");

async function loadHtml() {
  return readFile(htmlPath, "utf8");
}

test("root index.html is a standalone recruiter-facing portfolio", async () => {
  const html = await loadHtml();

  assert.match(html, /^<!doctype html>/i);
  assert.match(html, /<title>[^<]*MWG[^<]*DMX[^<]*<\/title>/i);
  assert.match(html, /MWG after the DMX IPO/i);
  assert.match(html, /nearly 86%/i);
  assert.match(html, /~86% model approximation/i);
  assert.match(html, /DMX_RESULTS_2026H1/);
  assert.match(html, /issuer operating update; unaudited/i);
  assert.match(html, /management-adjusted like-for-like/i);
  assert.match(html, /type="range"/i);
  assert.match(html, /Bear/);
  assert.match(html, /Base/);
  assert.match(html, /Bull/);
  assert.match(html, /public\/three-statement-data\.js/);
  assert.match(html, /public\/standalone-site\.js/);
  assert.match(html, /Three-year financials/i);
  assert.match(html, /NPAT to CFO/i);
  assert.match(html, /CCC = DIO \+ DSO - DPO/);
  assert.match(html, /Quality of earnings/i);
  assert.match(html, /Normalization discipline/i);
  assert.match(html, /Illustrative MWG equity value/i);
  assert.match(html, /No per-share value, target price, rating, premium or upside is published/i);
  assert.match(html, /Not investment advice/i);
  assert.doesNotMatch(html, /85\.9%/);
  assert.doesNotMatch(html, /id="(?:shares|reference|per-share-output|premium-output)"/i);
  assert.doesNotMatch(html, /Your reference price/i);
  assert.doesNotMatch(html, /Illustrative MWG value \/ share/i);
  assert.doesNotMatch(html, /localhost/i);
  assert.doesNotMatch(html, /(?:href|src)="\/(?!\/)/i);

  for (const id of ["financials", "bridges", "working-capital", "quality", "valuation"]) {
    assert.match(html, new RegExp(`id="${id}"`));
  }

  const inlineScripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/gi)].map(
    (match) => match[1],
  );
  assert.ok(inlineScripts.length >= 1, "expected inline valuation JavaScript");
  for (const script of inlineScripts) {
    assert.doesNotThrow(() => new Function(script), "inline JavaScript must parse");
  }
});

test("generated three-statement payload covers the promised periods and controls", async () => {
  const script = await readFile(threeStatementScriptPath, "utf8");
  assert.match(script, /window\.DMX_THREE_STATEMENT_ANALYSIS\s*=/);

  const browserGlobal = {};
  const payload = new Function("window", `${script}\nreturn window.DMX_THREE_STATEMENT_ANALYSIS;`)(browserGlobal);

  assert.equal(payload.metadata.data_version, "three-statement-v1.0.0");
  assert.equal(payload.metadata.forecast_boundary.includes("no fully integrated three-statement forecast"), true);
  assert.deepEqual(
    ["FY2023A", "FY2024A", "FY2025A", "Q1 2026A"].map((period) =>
      payload.statements.some((statement) => statement.period === period),
    ),
    [true, true, true, true],
  );
  assert.equal(payload.check_summary.failed, 0);
  assert.ok(payload.check_summary.passed >= 30);
  assert.equal(payload.working_capital.some((period) => period.q1_seasonality_warning), true);
  assert.ok(payload.quality_of_earnings.length >= 6);
  assert.ok(payload.normalization.some((item) => item.treatment === "not_adjusted"));
});

test("standalone renderer script parses", async () => {
  const script = await readFile(standaloneScriptPath, "utf8");

  assert.match(script, /renderThreeStatementAnalysis/);
  assert.match(script, /working-capital-body/);
  assert.match(script, /quality-of-earnings-body/);
  assert.doesNotThrow(() => new Function(script), "standalone renderer JavaScript must parse");
});
test("all local links and assets in index.html exist in the repository", async () => {
  const html = await loadHtml();
  const references = [
    ...html.matchAll(/(?:href|src)="([^"]+)"/gi),
  ].map((match) => match[1]);

  const localReferences = references.filter(
    (reference) =>
      reference &&
      !reference.startsWith("#") &&
      !reference.startsWith("http://") &&
      !reference.startsWith("https://") &&
      !reference.startsWith("mailto:") &&
      !reference.startsWith("data:"),
  );

  assert.ok(localReferences.length >= 4, "expected downloadable portfolio assets");
  for (const reference of new Set(localReferences)) {
    const cleanPath = decodeURIComponent(reference.split(/[?#]/, 1)[0]);
    const target = path.resolve(root, cleanPath);
    assert.ok(target.startsWith(root), `reference escapes repository: ${reference}`);
    const targetStat = await stat(target);
    assert.ok(targetStat.isFile(), `reference is not a file: ${reference}`);
  }
});
