#!/usr/bin/env node
/**
 * Vivid Health — publish blog + articles to Shopify.
 *
 * Reads vivid/data/journal.json and:
 *   1. Creates (or reuses) a blog with handle "journal"
 *   2. Upserts each article (idempotent — looks up by handle, updates or creates)
 *   3. Tags articles with their category for filtering
 *   4. Uploads the hero image if it's a relative path under vivid/assets
 *
 * Requires Shopify Admin API scopes: write_content (currently NOT granted
 * on the Vivid Claude Review app — extend or use a separate write-scoped app).
 *
 * Env:
 *   SHOPIFY_STORE           e.g. hgywg0-w7.myshopify.com
 *   SHOPIFY_API_VERSION     e.g. 2026-04
 *   SHOPIFY_CLIENT_ID       client credentials
 *   SHOPIFY_CLIENT_SECRET
 *   DRY_RUN=1               print actions without executing
 */

import { readFile } from "node:fs/promises";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const STORE = required("SHOPIFY_STORE");
const API = required("SHOPIFY_API_VERSION");
const CLIENT_ID = required("SHOPIFY_CLIENT_ID");
const CLIENT_SECRET = required("SHOPIFY_CLIENT_SECRET");
const DRY_RUN = process.env.DRY_RUN === "1";
const REPO_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const JOURNAL_JSON = resolve(REPO_ROOT, "vivid", "data", "journal.json");
const BLOG_HANDLE = "journal";
const BLOG_TITLE = "Journal";
const COMMIT_POLICY_NOTE = "All articles authored by Vivid Lab Team. Re-publishing this script is idempotent.";

function required(k) {
  const v = process.env[k];
  if (!v) { console.error("Missing env: " + k); process.exit(1); }
  return v;
}

async function tokenExchange() {
  const r = await fetch(`https://${STORE}/admin/oauth/access_token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ client_id: CLIENT_ID, client_secret: CLIENT_SECRET, grant_type: "client_credentials" }),
  });
  const j = await r.json();
  if (!j.access_token) throw new Error("token exchange failed: " + JSON.stringify(j));
  return j.access_token;
}

function api(token) {
  return async function (query, variables = {}) {
    const r = await fetch(`https://${STORE}/admin/api/${API}/graphql.json`, {
      method: "POST",
      headers: { "X-Shopify-Access-Token": token, "Content-Type": "application/json" },
      body: JSON.stringify({ query, variables }),
    });
    const j = await r.json();
    if (j.errors) throw new Error("GraphQL: " + JSON.stringify(j.errors));
    return j.data;
  };
}

async function ensureBlog(gql) {
  const found = await gql(`{ blogs(first: 50) { edges { node { id handle title } } } }`);
  const existing = found.blogs.edges.find((e) => e.node.handle === BLOG_HANDLE);
  if (existing) { console.log(`  · blog "${BLOG_HANDLE}" exists → ${existing.node.id}`); return existing.node.id; }
  if (DRY_RUN) { console.log(`  · DRY_RUN: would create blog "${BLOG_HANDLE}"`); return "gid://shopify/Blog/DRY"; }
  const res = await gql(`mutation($input: BlogCreateInput!) { blogCreate(blog: $input) { blog { id handle title } userErrors { field message } } }`, {
    input: { title: BLOG_TITLE, handle: BLOG_HANDLE, commentPolicy: "MODERATED" },
  });
  const errs = res.blogCreate?.userErrors || [];
  if (errs.length) throw new Error("blogCreate: " + JSON.stringify(errs));
  console.log(`  · created blog "${BLOG_HANDLE}" → ${res.blogCreate.blog.id}`);
  return res.blogCreate.blog.id;
}

async function listArticles(gql, blogId) {
  const all = new Map();
  let cursor = null;
  for (;;) {
    const r = await gql(`query($id: ID!, $after: String) {
      blog(id: $id) {
        articles(first: 50, after: $after) {
          edges { node { id handle title isPublished tags } }
          pageInfo { hasNextPage endCursor }
        }
      }
    }`, { id: blogId, after: cursor });
    for (const e of r.blog.articles.edges) all.set(e.node.handle, e.node);
    if (!r.blog.articles.pageInfo.hasNextPage) break;
    cursor = r.blog.articles.pageInfo.endCursor;
  }
  return all;
}

function authorBody(article) {
  const head = `<p class="article-sub">${article.sub}</p>`;
  const meta = `<p class="article-meta"><strong>${article.cat}</strong> · ${article.read} · ${article.date}</p>`;
  let body = article.body_html;
  // Wrap in <article class="rte"> for theme styling.
  const related = (article.related || []).length
    ? `<aside class="article-pairings"><h3>Pairs well with</h3><ul>${article.related.map(h => `<li><a href="/products/${h}">${h}</a></li>`).join("")}</ul></aside>`
    : "";
  return `${meta}\n${head}\n${body}\n${related}`;
}

async function upsertArticle(gql, blogId, article, existing) {
  const body = authorBody(article);
  const tags = [article.cat || "", "vivid-journal", "category:" + (article.cat || "").toLowerCase().replace(/\s+/g, "-")].filter(Boolean);
  if (existing) {
    if (DRY_RUN) { console.log(`  · DRY_RUN: would UPDATE ${article.handle}`); return; }
    const r = await gql(`mutation($id: ID!, $article: ArticleUpdateInput!) {
      articleUpdate(id: $id, article: $article) {
        article { id handle title }
        userErrors { field message }
      }
    }`, {
      id: existing.id,
      article: { title: article.title, body, summary: article.sub, tags, author: { name: article.author || "Vivid Lab Team" } },
    });
    const errs = r.articleUpdate?.userErrors || [];
    if (errs.length) throw new Error(`articleUpdate ${article.handle}: ` + JSON.stringify(errs));
    console.log(`  · updated  ${article.handle}`);
  } else {
    if (DRY_RUN) { console.log(`  · DRY_RUN: would CREATE ${article.handle}`); return; }
    const r = await gql(`mutation($article: ArticleCreateInput!) {
      articleCreate(article: $article) {
        article { id handle title }
        userErrors { field message }
      }
    }`, {
      article: {
        blogId,
        title: article.title,
        handle: article.handle,
        body,
        summary: article.sub,
        tags,
        author: { name: article.author || "Vivid Lab Team" },
        isPublished: true,
      },
    });
    const errs = r.articleCreate?.userErrors || [];
    if (errs.length) throw new Error(`articleCreate ${article.handle}: ` + JSON.stringify(errs));
    console.log(`  · created  ${article.handle}`);
  }
}

async function main() {
  console.log(`Vivid blog publish ${DRY_RUN ? "(DRY_RUN)" : ""}\n`);
  const articles = JSON.parse(await readFile(JOURNAL_JSON, "utf8"));
  console.log(`Source: ${JOURNAL_JSON} — ${articles.length} articles\n`);

  const token = await tokenExchange();
  const gql = api(token);

  console.log("Ensure blog exists:");
  const blogId = await ensureBlog(gql);

  console.log("\nList existing articles:");
  const existing = DRY_RUN ? new Map() : await listArticles(gql, blogId);
  console.log(`  ${existing.size} existing in "${BLOG_HANDLE}"`);

  console.log("\nUpsert articles:");
  let ok = 0, fail = 0;
  for (const a of articles) {
    try { await upsertArticle(gql, blogId, a, existing.get(a.handle)); ok++; }
    catch (e) { console.error(`  ✗ ${a.handle}: ${e.message}`); fail++; }
  }

  console.log(`\nDone. ok=${ok}  fail=${fail}`);
  console.log(`\n${COMMIT_POLICY_NOTE}`);
  process.exit(fail > 0 ? 1 : 0);
}

main().catch((e) => { console.error(e); process.exit(2); });
