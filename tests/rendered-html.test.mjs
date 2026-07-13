import assert from "node:assert/strict";
import test from "node:test";

async function render(path = "/") {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", String(Date.now()));
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("http://localhost" + path, {
      headers: { accept: "text/html" },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  );
}

test("server-renders the complete MWG-DMX case", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /MWG after the/);
  assert.match(html, /DMX IPO/);
  assert.match(html, /Rebuild the SOTP/);
  assert.match(html, /Primary documents/);
  assert.match(html, /Not investment advice/);
  assert.match(html, /nearly 86%/i);
  assert.match(html, /issuer operating update; unaudited/i);
  assert.match(html, /stated like-for-like basis/i);
  assert.match(html, /DMX_RESULTS_2026H1/);
  assert.doesNotMatch(html, /85\.9%/);
  assert.doesNotMatch(html, /codex-preview/);
  assert.doesNotMatch(html, /Your site is taking shape/);
});

test("includes accessible primary sections and artifact links", async () => {
  const response = await render();
  const html = await response.text();

  for (const id of ["case", "forecast", "valuation", "methodology", "sources"]) {
    assert.match(html, new RegExp('id="' + id + '"'));
  }

  assert.match(html, /aria-label="Primary navigation"/);
  assert.match(html, /MWG_DMX_IPO_SOTP_Model\.xlsx/);
  assert.match(html, /Investment_Memo_EN\.pdf/);
  assert.match(html, /validation_report\.html/);
});
