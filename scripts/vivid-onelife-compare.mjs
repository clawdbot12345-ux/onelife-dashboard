#!/usr/bin/env node
/**
 * Vivid Health vs Onelife Health — backend parity audit.
 * Queries both Shopify Admin APIs and produces a structured diff.
 *
 * Env (all required):
 *   ONELIFE_STORE                e.g. onelifehealth.myshopify.com
 *   ONELIFE_CLIENT_ID            (same as scripts/publish_blog.py uses)
 *   ONELIFE_CLIENT_SECRET
 *   VIVID_STORE                  e.g. hgywg0-w7.myshopify.com
 *   VIVID_CLIENT_ID
 *   VIVID_CLIENT_SECRET
 *   SHOPIFY_API_VERSION          e.g. 2026-04
 *
 * Output: writes output/vivid-onelife-compare/report.md (uploaded by workflow)
 */

import { mkdir, writeFile } from "node:fs/promises";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const REPO_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const OUT_DIR = resolve(REPO_ROOT, "output/vivid-onelife-compare");
const API = required("SHOPIFY_API_VERSION");

function required(k) {
  if (!process.env[k]) { console.error("Missing env:", k); process.exit(1); }
  return process.env[k];
}

async function exchangeToken(store, id, secret) {
  const r = await fetch(`https://${store}/admin/oauth/access_token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ client_id: id, client_secret: secret, grant_type: "client_credentials" }),
  });
  const j = await r.json();
  if (!j.access_token) throw new Error(`Token exchange ${store}: ${JSON.stringify(j).slice(0, 200)}`);
  return j.access_token;
}

function gqlFor(store, token) {
  return async (query, variables = {}) => {
    const r = await fetch(`https://${store}/admin/api/${API}/graphql.json`, {
      method: "POST",
      headers: { "X-Shopify-Access-Token": token, "Content-Type": "application/json" },
      body: JSON.stringify({ query, variables }),
    });
    const j = await r.json();
    if (j.errors) console.error(`[${store}] GQL`, JSON.stringify(j.errors).slice(0, 200));
    return j.data;
  };
}

async function snapshot(label, gql) {
  console.log(`Snapshotting ${label} …`);
  const out = { label };

  out.shop = (await gql(`{ shop { name myshopifyDomain plan { displayName } currencyCode } }`)).shop;

  const products = await gql(`{ productsCount { count } }`);
  out.productCount = products?.productsCount?.count;

  const colls = await gql(`{ collections(first: 100) { edges { node { handle title productsCount { count } } } } }`);
  out.collections = colls.collections.edges.map((e) => ({ handle: e.node.handle, title: e.node.title, count: e.node.productsCount?.count }));

  // Pages: paginate to get all
  const pages = [];
  let cursor = null;
  for (;;) {
    const r = await gql(`query($a:String){ pages(first: 100, after: $a) { edges { node { handle title isPublished } } pageInfo { hasNextPage endCursor } } }`, { a: cursor });
    for (const e of r.pages.edges) pages.push({ handle: e.node.handle, title: e.node.title, published: e.node.isPublished });
    if (!r.pages.pageInfo.hasNextPage) break;
    cursor = r.pages.pageInfo.endCursor;
  }
  out.pages = pages;

  const blogs = await gql(`{ blogs(first: 20) { edges { node { handle title articlesCount { count } } } } }`);
  out.blogs = blogs.blogs.edges.map((e) => ({ handle: e.node.handle, title: e.node.title, articles: e.node.articlesCount?.count }));

  const menus = await gql(`{ menus(first: 30) { edges { node { handle title items { title url type } } } } }`);
  out.menus = menus.menus.edges.map((e) => ({ handle: e.node.handle, title: e.node.title, items: e.node.items.map((i) => ({ title: i.title, url: i.url, type: i.type })) }));

  // Sample of articles per blog (max 50 each, just for naming + tags)
  out.articleSamples = [];
  for (const b of out.blogs) {
    const r = await gql(`query($h:String!){ blogs(first:5,query:$h){edges{node{ id handle articles(first:50){edges{node{ handle title tags isPublished }}} }}} }`, { h: `handle:${b.handle}` });
    const node = r.blogs.edges.find((e) => e.node.handle === b.handle)?.node;
    if (node) out.articleSamples.push({ blog: b.handle, articles: node.articles.edges.map((e) => ({ handle: e.node.handle, title: e.node.title, tags: e.node.tags, published: e.node.isPublished })) });
  }

  const themes = await gql(`{ themes(first: 20) { edges { node { id name role } } } }`);
  out.themes = themes.themes.edges.map((e) => ({ id: e.node.id.split("/").pop(), name: e.node.name, role: e.node.role }));

  // Try policies, suppress errors if not granted
  try {
    const pol = await gql(`{ shop { shopPolicies { type body } } }`);
    if (pol?.shop?.shopPolicies) {
      out.policies = pol.shop.shopPolicies.map((p) => ({ type: p.type, words: (p.body || "").replace(/<[^>]+>/g, " ").split(/\s+/).filter(Boolean).length }));
    }
  } catch (_) { out.policies = []; }

  console.log(`  ${out.shop.name}  ·  ${out.productCount} products · ${out.collections.length} collections · ${out.pages.length} pages · ${out.blogs.length} blogs`);
  return out;
}

function diff(onelife, vivid) {
  const oPages = new Set(onelife.pages.map((p) => p.handle));
  const vPages = new Set(vivid.pages.map((p) => p.handle));
  const oColls = new Set(onelife.collections.map((c) => c.handle));
  const vColls = new Set(vivid.collections.map((c) => c.handle));
  const oBlogs = new Set(onelife.blogs.map((b) => b.handle));
  const vBlogs = new Set(vivid.blogs.map((b) => b.handle));

  const onelifeOnlyPages = [...oPages].filter((h) => !vPages.has(h)).sort();
  const vividOnlyPages = [...vPages].filter((h) => !oPages.has(h)).sort();
  const onelifeOnlyColls = [...oColls].filter((h) => !vColls.has(h)).sort();
  const vividOnlyColls = [...vColls].filter((h) => !oColls.has(h)).sort();
  const onelifeOnlyBlogs = [...oBlogs].filter((h) => !vBlogs.has(h)).sort();
  const vividOnlyBlogs = [...vBlogs].filter((h) => !oBlogs.has(h)).sort();

  // Categorize Onelife-only pages by likely template (guides, policies, store, etc.)
  const groupPage = (handle) => {
    if (handle.startsWith("guide-") || handle === "supplement-guides") return "Ingredient guide pages (SEO)";
    if (handle.includes("loyalty") || handle.includes("reward")) return "Loyalty / rewards";
    if (handle.includes("consultation")) return "Consultation booking";
    if (handle === "store-locator" || handle === "centurion" || handle === "edenvale" || handle === "glen-village") return "Store-specific";
    if (handle.includes("pcos") || handle.includes("glp-1")) return "Condition-specific landings";
    if (handle === "llms-txt") return "AI / LLM discovery";
    if (handle === "brands") return "Brand directory";
    if (handle === "shop") return "Custom shop page";
    return "Other";
  };

  const onelifePagesGrouped = onelifeOnlyPages.reduce((m, h) => {
    const k = groupPage(h); (m[k] = m[k] || []).push(h); return m;
  }, {});

  return { onelifeOnlyPages, vividOnlyPages, onelifeOnlyColls, vividOnlyColls, onelifeOnlyBlogs, vividOnlyBlogs, onelifePagesGrouped };
}

function md(onelife, vivid, diffs) {
  const lines = [];
  const push = (s = "") => lines.push(s);
  push(`# Vivid Health vs Onelife Health — backend parity audit`);
  push(`\n_Generated ${new Date().toISOString()} by \`scripts/vivid-onelife-compare.mjs\`._\n`);

  push(`## Shape comparison\n`);
  push(`| Metric | Onelife | Vivid | Gap |`);
  push(`|---|---:|---:|---|`);
  const row = (m, o, v) => push(`| ${m} | ${o} | ${v} | ${o > v ? `+${o - v} ${m.toLowerCase()}` : o === v ? "—" : `Vivid +${v - o}`} |`);
  row("Products", onelife.productCount, vivid.productCount);
  row("Collections", onelife.collections.length, vivid.collections.length);
  row("Pages", onelife.pages.length, vivid.pages.length);
  row("Blogs", onelife.blogs.length, vivid.blogs.length);
  row("Total articles", onelife.articleSamples.reduce((s, b) => s + b.articles.length, 0), vivid.articleSamples.reduce((s, b) => s + b.articles.length, 0));
  row("Menus", onelife.menus.length, vivid.menus.length);
  row("Themes", onelife.themes.length, vivid.themes.length);
  push();

  push(`## Pages — Onelife has, Vivid doesn't (grouped)\n`);
  for (const [grp, handles] of Object.entries(diffs.onelifePagesGrouped)) {
    push(`### ${grp} (${handles.length})`);
    for (const h of handles) push(`- \`/pages/${h}\``);
    push();
  }

  push(`## Pages — Vivid has, Onelife doesn't\n`);
  for (const h of diffs.vividOnlyPages) push(`- \`/pages/${h}\``);
  push();

  push(`## Collections — Onelife only (sample of ${Math.min(40, diffs.onelifeOnlyColls.length)} of ${diffs.onelifeOnlyColls.length})\n`);
  for (const h of diffs.onelifeOnlyColls.slice(0, 40)) push(`- \`/collections/${h}\``);
  if (diffs.onelifeOnlyColls.length > 40) push(`- _…and ${diffs.onelifeOnlyColls.length - 40} more_`);
  push();

  push(`## Collections — Vivid only\n`);
  for (const h of diffs.vividOnlyColls) push(`- \`/collections/${h}\``);
  push();

  push(`## Blogs comparison\n`);
  push(`### Onelife blogs`);
  for (const b of onelife.blogs) push(`- \`${b.handle}\` "${b.title}" — ${b.articles} articles`);
  push(`\n### Vivid blogs`);
  for (const b of vivid.blogs) push(`- \`${b.handle}\` "${b.title}" — ${b.articles} articles`);
  push();

  push(`## Menus\n`);
  for (const [label, store] of [["Onelife", onelife], ["Vivid", vivid]]) {
    push(`### ${label}`);
    for (const m of store.menus) push(`- \`${m.handle}\` "${m.title}" — ${m.items.length} items`);
    push();
  }

  push(`## Policies\n`);
  push(`| Policy | Onelife (words) | Vivid (words) |`);
  push(`|---|---:|---:|`);
  const polTypes = new Set([...(onelife.policies || []), ...(vivid.policies || [])].map((p) => p.type));
  for (const t of polTypes) {
    const o = onelife.policies?.find((p) => p.type === t)?.words ?? "—";
    const v = vivid.policies?.find((p) => p.type === t)?.words ?? "—";
    push(`| ${t} | ${o} | ${v} |`);
  }
  push();

  return lines.join("\n");
}

async function main() {
  await mkdir(OUT_DIR, { recursive: true });

  console.log("Authenticating both stores…");
  const oToken = await exchangeToken(required("ONELIFE_STORE"), required("ONELIFE_CLIENT_ID"), required("ONELIFE_CLIENT_SECRET"));
  const vToken = await exchangeToken(required("VIVID_STORE"), required("VIVID_CLIENT_ID"), required("VIVID_CLIENT_SECRET"));

  const onelife = await snapshot("Onelife", gqlFor(process.env.ONELIFE_STORE, oToken));
  const vivid = await snapshot("Vivid", gqlFor(process.env.VIVID_STORE, vToken));

  const diffs = diff(onelife, vivid);
  const report = md(onelife, vivid, diffs);

  await writeFile(resolve(OUT_DIR, "report.md"), report, "utf8");
  await writeFile(resolve(OUT_DIR, "onelife.json"), JSON.stringify(onelife, null, 2), "utf8");
  await writeFile(resolve(OUT_DIR, "vivid.json"), JSON.stringify(vivid, null, 2), "utf8");

  console.log(`\nWrote: ${OUT_DIR}/report.md`);
  console.log(`\n══ headline numbers ══`);
  console.log(`  Pages Onelife-only: ${diffs.onelifeOnlyPages.length}`);
  console.log(`  Pages Vivid-only:   ${diffs.vividOnlyPages.length}`);
  console.log(`  Collections Onelife-only: ${diffs.onelifeOnlyColls.length}`);
  console.log(`  Articles Onelife: ${onelife.articleSamples.reduce((s, b) => s + b.articles.length, 0)}`);
  console.log(`  Articles Vivid:   ${vivid.articleSamples.reduce((s, b) => s + b.articles.length, 0)}`);
}

main().catch((e) => { console.error(e); process.exit(2); });
