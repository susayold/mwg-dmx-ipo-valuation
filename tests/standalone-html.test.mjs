import assert from "node:assert/strict";
import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const htmlPath = path.join(root, "index.html");

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
  assert.match(html, /Not investment advice/i);
  assert.doesNotMatch(html, /85\.9%/);
  assert.doesNotMatch(html, /localhost/i);
  assert.doesNotMatch(html, /(?:href|src)="\/(?!\/)/i);

  const inlineScripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/gi)].map(
    (match) => match[1],
  );
  assert.ok(inlineScripts.length >= 1, "expected inline valuation JavaScript");
  for (const script of inlineScripts) {
    assert.doesNotThrow(() => new Function(script), "inline JavaScript must parse");
  }
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
