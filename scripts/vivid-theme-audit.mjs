#!/usr/bin/env node
/**
 * Vivid Health — draft theme audit.
 *
 * Read-only against the deployed Shopify theme. Uses the Vivid Claude Review
 * Dev Dashboard app's client credentials (read-only-ish scopes — only
 * write_theme_code is granted, and this script does not exercise it).
 *
 * Required env:
 *   SHOPIFY_STORE             e.g. hgywg0-w7.myshopify.com
 *   SHOPIFY_API_VERSION       e.g. 2025-04
 *   SHOPIFY_CLIENT_ID         Dev Dashboard app client id
 *   SHOPIFY_CLIENT_SECRET     Dev Dashboard app client secret
 *
 * Optional env:
 *   VIVID_THEME_ID            draft theme id (default 148718944342)
 *   VIVID_STOREFRONT_PASSWORD storefront password if you want storefront fetches
 *   AUDIT_OUT_DIR             output directory (default output/vivid-theme-audit)
 *
 * What it does:
 *   1. Exchange client credentials → 24-hour Admin API token.
 *   2. Fetch the full asset listing of the draft theme.
 *   3. Pull every Liquid/JSON/CSS/JS file's source.
 *   4. Run integrity checks:
 *      a. JSON parses (templates, schema islands, config)
 *      b. Section refs in templates resolve to deployed sections
 *      c. Block refs in templates resolve to schema-defined block types
 *      d. asset_url references resolve to uploaded assets
 *      e. Asset size budget (warn > 500KB, error > 2MB; total > 50MB warn)
 *      f. Drift vs the repo (sha256 per file, flag deployed != repo)
 *   5. Try storefront smoke fetches of home/collection/PDP/cart/quiz/contact.
 *      (Skipped gracefully if storefront is password-protected and no
 *       VIVID_STOREFRONT_PASSWORD is set.)
 *   6. Emit a markdown report + json summary to output/vivid-theme-audit/.
 */

import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile, readdir, stat } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

/* ─── config ─── */

const ENV = process.env;
const STORE = required("SHOPIFY_STORE");
const API_VERSION = required("SHOPIFY_API_VERSION");
const CLIENT_ID = required("SHOPIFY_CLIENT_ID");
const CLIENT_SECRET = required("SHOPIFY_CLIENT_SECRET");
const THEME_ID = ENV.VIVID_THEME_ID || "148718944342";
const STOREFRONT_PASSWORD = ENV.VIVID_STOREFRONT_PASSWORD || "";
const REPO_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const REPO_THEME = join(REPO_ROOT, "vivid", "theme");
const OUT_DIR = resolve(REPO_ROOT, ENV.AUDIT_OUT_DIR || "output/vivid-theme-audit");
const ASSET_BUDGET_WARN = 500 * 1024;        // 500 KB
const ASSET_BUDGET_ERROR = 2 * 1024 * 1024;  // 2 MB
const THEME_BUDGET_WARN = 50 * 1024 * 1024;  // 50 MB
const STOREFRONT_PATHS = [
  { name: "Home",               path: "/" },
  { name: "All formulations",   path: "/collections/all-formulations" },
  { name: "Bundles",            path: "/collections/bundles" },
  { name: "Gut collection",     path: "/collections/gut" },
  { name: "Stress collection",  path: "/collections/stress" },
  { name: "Cart",               path: "/cart" },
  { name: "Quiz page",          path: "/pages/quiz" },
  { name: "Contact page",       path: "/pages/contact" },
  { name: "About page",         path: "/pages/about" },
];

function required(name) {
  const v = ENV[name];
  if (!v) { console.error(`Missing required env: ${name}`); process.exit(1); }
  return v;
}

/* ─── audit state ─── */

const findings = { error: [], warn: [], info: [] };
const summary = { startedAt: new Date().toISOString(), checks: {} };

const report = (level, area, message, extra) => {
  findings[level].push({ area, message, ...(extra || {}) });
};

const sha = (buf) => createHash("sha256").update(buf).digest("hex");

/* ─── Shopify Admin API ─── */

async function tokenExchange() {
  const url = `https://${STORE}/admin/oauth/access_token`;
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET,
      grant_type: "client_credentials",
    }),
  });
  if (!r.ok) {
    const body = await r.text();
    throw new Error(`Token exchange failed: ${r.status} ${body.slice(0, 200)}`);
  }
  const j = await r.json();
  if (!j.access_token) throw new Error(`Token exchange returned no token`);
  return j.access_token;
}

function api(token) {
  return async function (path, opts = {}) {
    const url = path.startsWith("http")
      ? path
      : `https://${STORE}/admin/api/${API_VERSION}${path}`;
    const r = await fetch(url, {
      ...opts,
      headers: {
        "X-Shopify-Access-Token": token,
        Accept: "application/json",
        "Content-Type": "application/json",
        ...(opts.headers || {}),
      },
    });
    if (!r.ok) {
      const body = await r.text();
      throw new Error(`API ${path} → ${r.status}: ${body.slice(0, 200)}`);
    }
    return r.json();
  };
}

async function getAllAssets(call) {
  const r = await call(`/themes/${THEME_ID}/assets.json`);
  return r.assets || [];
}

async function getAssetValue(call, key) {
  const r = await call(`/themes/${THEME_ID}/assets.json?asset[key]=${encodeURIComponent(key)}`);
  return r.asset;
}

/* ─── checks ─── */

function jsonOf(s) {
  try { return JSON.parse(s); } catch (e) { return { __error: e.message }; }
}

function extractSchema(liquid) {
  const m = liquid.match(/\{%\s*schema\s*%\}([\s\S]*?)\{%\s*endschema\s*%\}/);
  return m ? m[1] : null;
}

/* All section "type" references in a template + all block "type" references.
   Returns { sectionTypes: Set, blockUsages: [{sectionKey, sectionType, blockKey, blockType}] }
*/
function extractTemplateRefs(tpl) {
  const sectionTypes = new Set();
  const blockUsages = [];
  if (!tpl?.sections) return { sectionTypes, blockUsages };
  for (const [sectionKey, sec] of Object.entries(tpl.sections)) {
    if (sec?.type) sectionTypes.add(sec.type);
    if (sec?.blocks) {
      for (const [blockKey, blk] of Object.entries(sec.blocks)) {
        blockUsages.push({
          sectionKey,
          sectionType: sec.type,
          blockKey,
          blockType: blk.type,
        });
      }
    }
  }
  return { sectionTypes, blockUsages };
}

function extractAssetUrls(src) {
  const re = /['"]([\w\-./]+\.(?:jpg|jpeg|png|webp|svg|gif|ico|woff2?|css|js))['"]\s*\|\s*asset_url/gi;
  const hits = new Set();
  let m;
  while ((m = re.exec(src))) hits.add(m[1]);
  return hits;
}

async function readRepoTheme() {
  const map = new Map();
  if (!existsSync(REPO_THEME)) {
    report("warn", "drift", "Repo theme directory not found — drift check skipped");
    return map;
  }
  async function walk(dir) {
    const entries = await readdir(dir, { withFileTypes: true });
    for (const ent of entries) {
      const full = join(dir, ent.name);
      if (ent.isDirectory()) await walk(full);
      else if (ent.isFile()) {
        const rel = relative(REPO_THEME, full).replaceAll("\\", "/");
        const buf = await readFile(full);
        map.set(rel, { sha: sha(buf), size: buf.length });
      }
    }
  }
  await walk(REPO_THEME);
  return map;
}

/* ─── storefront fetch ─── */

async function storefrontFetch(path) {
  const url = `https://${STORE}${path}?preview_theme_id=${THEME_ID}`;
  try {
    const headers = {};
    if (STOREFRONT_PASSWORD) {
      // Send password as a cookie / Authorization is fiddly — most reliable
      // is the /password endpoint flow. We attempt a header that some
      // password-protected stores accept; if not, the storefront block is
      // documented in the report and skipped.
      headers["x-shopify-password"] = STOREFRONT_PASSWORD;
    }
    const r = await fetch(url, { headers, redirect: "manual" });
    return { status: r.status, headers: Object.fromEntries(r.headers), bodyLen: (await r.text()).length };
  } catch (e) {
    return { status: 0, error: e.message };
  }
}

/* ─── pretty bytes ─── */

function pretty(n) {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(2)} MB`;
}

/* ─── main ─── */

async function main() {
  await mkdir(OUT_DIR, { recursive: true });

  console.log(`▶ exchanging client credentials for Admin API token …`);
  const token = await tokenExchange();
  const call = api(token);
  console.log(`✓ token acquired`);

  console.log(`▶ fetching theme listing for ${THEME_ID} …`);
  const assets = await getAllAssets(call);
  summary.checks.assetCount = assets.length;
  console.log(`✓ ${assets.length} asset keys returned`);

  // Categorise
  const sectionKeys = assets.filter((a) => a.key.startsWith("sections/") && a.key.endsWith(".liquid"));
  const templateKeys = assets.filter((a) => a.key.startsWith("templates/") && a.key.endsWith(".json"));
  const snippetKeys = assets.filter((a) => a.key.startsWith("snippets/") && a.key.endsWith(".liquid"));
  const assetKeys = assets.filter((a) => a.key.startsWith("assets/"));
  const configKeys = assets.filter((a) => a.key.startsWith("config/"));
  const layoutKeys = assets.filter((a) => a.key.startsWith("layout/"));

  summary.checks.bySection = {
    sections: sectionKeys.length,
    templates: templateKeys.length,
    snippets: snippetKeys.length,
    assets: assetKeys.length,
    config: configKeys.length,
    layout: layoutKeys.length,
  };

  // Asset weight pass — listing returns size for binaries
  let totalBytes = 0;
  const heavyAssets = [];
  for (const a of assetKeys) {
    const sz = a.size || 0;
    totalBytes += sz;
    if (sz > ASSET_BUDGET_ERROR) {
      report("error", "perf", `Asset > ${pretty(ASSET_BUDGET_ERROR)}: ${a.key} (${pretty(sz)})`);
    } else if (sz > ASSET_BUDGET_WARN) {
      report("warn", "perf", `Asset > ${pretty(ASSET_BUDGET_WARN)}: ${a.key} (${pretty(sz)})`);
    }
    heavyAssets.push({ key: a.key, size: sz });
  }
  heavyAssets.sort((a, b) => b.size - a.size);
  summary.checks.totalBytes = totalBytes;
  summary.checks.heaviestAssets = heavyAssets.slice(0, 12);
  if (totalBytes > THEME_BUDGET_WARN) {
    report("warn", "perf", `Total asset weight ${pretty(totalBytes)} exceeds ${pretty(THEME_BUDGET_WARN)} comfort budget`);
  }

  console.log(`▶ pulling text sources (sections/templates/snippets/layout/config) …`);
  // Fetch all text source files
  const sources = new Map(); // key -> { value, attachment? }
  const textKeys = [...sectionKeys, ...templateKeys, ...snippetKeys, ...layoutKeys, ...configKeys];
  for (const a of textKeys) {
    const got = await getAssetValue(call, a.key);
    if (got?.value != null) sources.set(a.key, got.value);
    else if (got?.attachment) report("warn", "fetch", `Source-only file returned as attachment: ${a.key}`);
  }
  // Also fetch base.css + theme.js (text-ish even if listed in assets/)
  for (const ak of ["assets/base.css", "assets/theme.js"]) {
    if (assets.find((a) => a.key === ak)) {
      const got = await getAssetValue(call, ak);
      if (got?.value != null) sources.set(ak, got.value);
    }
  }
  console.log(`✓ ${sources.size} text sources fetched`);

  // a) JSON parse
  for (const key of templateKeys.map((k) => k.key).concat(configKeys.map((k) => k.key))) {
    const src = sources.get(key);
    if (!src) continue;
    const j = jsonOf(src);
    if (j.__error) report("error", "json", `${key}: ${j.__error}`);
  }

  // b) Section schema parse
  const sectionSchemas = new Map();
  for (const k of sectionKeys.map((k) => k.key)) {
    const src = sources.get(k);
    if (!src) continue;
    const s = extractSchema(src);
    if (!s) {
      report("info", "schema", `${k} has no {% schema %} block`);
      continue;
    }
    const j = jsonOf(s);
    if (j.__error) {
      report("error", "schema", `${k} schema: ${j.__error}`);
    } else {
      sectionSchemas.set(k.replace(/^sections\//, "").replace(/\.liquid$/, ""), j);
    }
  }

  // c) Template ↔ section refs
  const sectionNames = new Set([...sectionSchemas.keys()]);
  for (const tk of templateKeys.map((k) => k.key)) {
    const src = sources.get(tk);
    if (!src) continue;
    const tpl = jsonOf(src);
    if (tpl.__error) continue;
    const { sectionTypes, blockUsages } = extractTemplateRefs(tpl);
    for (const t of sectionTypes) {
      if (!sectionNames.has(t)) {
        report("error", "template", `${tk} references missing section type "${t}"`);
      }
    }
    for (const u of blockUsages) {
      const schema = sectionSchemas.get(u.sectionType);
      if (!schema) continue;
      const validBlockTypes = new Set((schema.blocks || []).map((b) => b.type));
      if (validBlockTypes.size === 0) {
        report("warn", "template", `${tk}.${u.sectionKey} declares blocks but section "${u.sectionType}" defines no blocks`);
        continue;
      }
      if (!validBlockTypes.has(u.blockType)) {
        report("error", "template", `${tk}.${u.sectionKey}.blocks.${u.blockKey} type "${u.blockType}" not in section "${u.sectionType}" schema`);
      }
    }
  }

  // d) asset_url references
  const assetSet = new Set(assets.map((a) => a.key.replace(/^assets\//, "")));
  for (const [k, src] of sources) {
    if (!/\.(liquid|css)$/.test(k)) continue;
    const refs = extractAssetUrls(src);
    for (const r of refs) {
      if (!assetSet.has(r)) {
        report("error", "assetref", `${k} references missing asset_url '${r}'`);
      }
    }
  }

  // e) Drift vs repo
  const repoMap = await readRepoTheme();
  if (repoMap.size > 0) {
    const drift = [];
    // Compare text sources
    for (const [k, src] of sources) {
      const repoEntry = repoMap.get(k);
      if (!repoEntry) {
        drift.push({ file: k, kind: "deployed-only" });
        continue;
      }
      const deployedSha = sha(Buffer.from(src, "utf8"));
      if (deployedSha !== repoEntry.sha) drift.push({ file: k, kind: "different" });
    }
    // Files in repo not on deployed
    for (const k of repoMap.keys()) {
      if (!sources.has(k) && !assets.find((a) => a.key === k)) {
        drift.push({ file: k, kind: "repo-only" });
      }
    }
    summary.checks.drift = drift;
    for (const d of drift) {
      const level = d.kind === "different" ? "warn" : "info";
      report(level, "drift", `${d.kind}: ${d.file}`);
    }
  }

  // f) Storefront smoke
  console.log(`▶ smoke-fetching storefront preview pages …`);
  const storefront = [];
  for (const p of STOREFRONT_PATHS) {
    const r = await storefrontFetch(p.path);
    storefront.push({ ...p, ...r });
    const colored =
      r.status === 200 ? "✓" :
      r.status >= 300 && r.status < 400 ? "↪" :
      r.status === 401 ? "🔒" : "✗";
    console.log(`  ${colored} ${p.path} → ${r.status}`);
  }
  summary.checks.storefront = storefront;
  const blockedByPassword = storefront.filter((s) => s.status === 401).length;
  if (blockedByPassword > 0 && !STOREFRONT_PASSWORD) {
    report("info", "storefront", `${blockedByPassword} pages returned 401 (storefront password-protected — set VIVID_STOREFRONT_PASSWORD to render-check)`);
  }
  for (const s of storefront) {
    if (s.status >= 500) report("error", "storefront", `${s.path} → ${s.status}`);
    else if (s.status === 404) report("error", "storefront", `${s.path} → 404 (route missing)`);
  }

  // Write report
  const reportPath = join(OUT_DIR, "report.md");
  const summaryPath = join(OUT_DIR, "summary.json");
  const md = renderReport(findings, summary, sectionNames, repoMap);
  await writeFile(reportPath, md, "utf8");
  await writeFile(summaryPath, JSON.stringify({ findings, summary }, null, 2), "utf8");

  console.log(`\n══ summary ══`);
  console.log(`  errors: ${findings.error.length}`);
  console.log(`  warns:  ${findings.warn.length}`);
  console.log(`  infos:  ${findings.info.length}`);
  console.log(`\n  report: ${reportPath}`);

  // Exit non-zero if any errors so CI surfaces it without blocking
  process.exit(findings.error.length > 0 ? 1 : 0);
}

function renderReport(findings, summary, sectionNames, repoMap) {
  const lines = [];
  const push = (s = "") => lines.push(s);
  push(`# Vivid Health draft theme audit`);
  push();
  push(`**Theme:** \`${THEME_ID}\`  `);
  push(`**Store:** \`${STORE}\`  `);
  push(`**API version:** \`${API_VERSION}\`  `);
  push(`**Generated:** ${summary.startedAt}  `);
  push();
  push(`## Summary`);
  push();
  push(`| Severity | Count |`);
  push(`|---|---|`);
  push(`| Errors | ${findings.error.length} |`);
  push(`| Warnings | ${findings.warn.length} |`);
  push(`| Info | ${findings.info.length} |`);
  push();
  push(`## Inventory`);
  push();
  const bs = summary.checks.bySection || {};
  push(`- Sections: ${bs.sections}`);
  push(`- Templates: ${bs.templates}`);
  push(`- Snippets: ${bs.snippets}`);
  push(`- Layout files: ${bs.layout}`);
  push(`- Config files: ${bs.config}`);
  push(`- Asset files: ${bs.assets}`);
  push(`- Total asset bytes: ${pretty(summary.checks.totalBytes || 0)}`);
  push();
  if (summary.checks.heaviestAssets?.length) {
    push(`### Heaviest 12 assets`);
    push();
    push(`| Asset | Size |`);
    push(`|---|---|`);
    for (const a of summary.checks.heaviestAssets) push(`| \`${a.key}\` | ${pretty(a.size)} |`);
    push();
  }
  if (summary.checks.drift?.length) {
    push(`## Drift vs repo (vivid/theme/)`);
    push();
    push(`| File | Kind |`);
    push(`|---|---|`);
    for (const d of summary.checks.drift) push(`| \`${d.file}\` | ${d.kind} |`);
    push();
  }
  if (summary.checks.storefront?.length) {
    push(`## Storefront smoke`);
    push();
    push(`| Page | Path | Status | Body |`);
    push(`|---|---|---|---|`);
    for (const s of summary.checks.storefront) {
      push(`| ${s.name} | \`${s.path}\` | ${s.status} | ${s.bodyLen ? pretty(s.bodyLen) : "—"} |`);
    }
    push();
  }
  for (const [lvl, label] of [["error", "Errors"], ["warn", "Warnings"], ["info", "Info"]]) {
    if (!findings[lvl].length) continue;
    push(`## ${label} (${findings[lvl].length})`);
    push();
    for (const f of findings[lvl]) push(`- **[${f.area}]** ${f.message}`);
    push();
  }
  return lines.join("\n");
}

main().catch((e) => {
  console.error(`▼ audit failed:`, e);
  process.exit(2);
});
