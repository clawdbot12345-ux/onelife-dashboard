#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const fsp = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const { randomUUID } = require("node:crypto");
const { spawnSync } = require("node:child_process");

const workspace = path.resolve(__dirname, "..");
const defaultStore = "hgywg0-w7.myshopify.com";
const defaultOut = path.join(workspace, "audit-output/vivid-inventory-sync");
const defaultApiVersion = "2026-04";

function argValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] || fallback : fallback;
}

function hasFlag(name) {
  return process.argv.includes(name);
}

function normalizeSku(value) {
  return String(value || "").replace(/\s+/g, "").toUpperCase();
}

function skuKeys(value) {
  const exact = normalizeSku(value);
  if (!exact) return [];
  const stripped = exact.replace(/^0+(?=\d)/, "");
  return [...new Set([exact, stripped].filter(Boolean))];
}

function parseNumber(value) {
  if (value == null) return null;
  const text = String(value).trim().replace(/,/g, "").replace(/N$/, "");
  if (!text) return null;
  const number = Number(text);
  return Number.isFinite(number) ? number : null;
}

function stockAvailable(value) {
  const available = parseNumber(value);
  return available == null ? null : Math.max(0, Math.round(available));
}

function parseOmniPoExport(filePath) {
  const rows = [];
  const lines = fs.readFileSync(filePath, "latin1").split(/\r?\n/);
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index].padEnd(276, " ");
    const sku = line.slice(10, 25).trim();
    if (!sku) continue;
    const available = parseNumber(line.slice(105, 120));
    rows.push({
      sourceLine: index + 1,
      sku,
      skuKey: normalizeSku(sku),
      description: line.slice(25, 60).trim(),
      level: parseNumber(line.slice(60, 75)),
      onOrder: parseNumber(line.slice(75, 90)),
      reserved: parseNumber(line.slice(90, 105)),
      available: stockAvailable(available),
      sourceFormat: "fixed_width_po",
    });
  }
  return rows;
}

function parseOmniJsonExport(filePath) {
  const body = JSON.parse(fs.readFileSync(filePath, "utf8"));
  const firstArray = Array.isArray(body)
    ? body
    : Object.values(body).find((value) => Array.isArray(value));
  if (!firstArray) throw new Error(`No array found in Omni JSON export: ${filePath}`);

  const rows = [];
  for (let index = 0; index < firstArray.length; index += 1) {
    const row = firstArray[index] || {};
    const available = stockAvailable(row.available ?? row.OAVAILABLE ?? row.Available);
    const description = String(row.stock_description || row.description || row.ODESCRIPTION || "").trim();
    const candidates = [
      ["stock_code", row.stock_code ?? row.OSTKCDE],
      ["bar_code", row.bar_code ?? row.barcode ?? row.OBARCODE],
      ["sku", row.sku ?? row.SKU],
    ];
    const emitted = new Set();
    for (const [field, value] of candidates) {
      for (const skuKey of skuKeys(value)) {
        if (!skuKey || emitted.has(skuKey)) continue;
        emitted.add(skuKey);
        rows.push({
          sourceLine: index + 1,
          sku: String(value || "").trim(),
          skuKey,
          description,
          level: parseNumber(row.level ?? row.OLEVEL),
          onOrder: parseNumber(row.on_order ?? row.ONORDER),
          reserved: parseNumber(row.reserved ?? row.ORESERVED),
          available,
          sourceFormat: "json_report",
          sourceField: field,
        });
      }
    }
  }
  return rows;
}

function parseOmniExport(filePath) {
  const prefix = fs.readFileSync(filePath, "utf8").trimStart().slice(0, 1);
  if (prefix === "{" || prefix === "[") return parseOmniJsonExport(filePath);
  return parseOmniPoExport(filePath);
}

function chooseLatestOmniExport() {
  const dir = path.join(workspace, "tmp/omni-smb-pull/Automation");
  if (!fs.existsSync(dir)) throw new Error(`Missing Omni export directory: ${dir}`);
  const candidates = fs
    .readdirSync(dir)
    .filter((name) => /^PO_.*\.csv$/i.test(name) && !/^PO_EDITS/i.test(name))
    .map((name) => path.join(dir, name));
  if (!candidates.length) throw new Error(`No PO_*.csv Omni export found under ${dir}`);
  return candidates.sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs)[0];
}

function extractJson(text) {
  const trimmed = String(text || "").trim();
  if (!trimmed) return {};
  try {
    return JSON.parse(trimmed);
  } catch {
    const start = trimmed.search(/[{[]/);
    if (start >= 0) return JSON.parse(trimmed.slice(start));
    throw new Error(`No JSON in output: ${trimmed.slice(0, 500)}`);
  }
}

async function adminGraphql({ store, token, query, variables }) {
  const response = await fetch(`https://${store}/admin/api/${process.env.SHOPIFY_API_VERSION || defaultApiVersion}/graphql.json`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      "X-Shopify-Access-Token": token,
      "User-Agent": "vivid-inventory-sync/1.0",
    },
    body: JSON.stringify({ query, variables: variables || {} }),
  });
  const text = await response.text();
  if (!response.ok) throw new Error(`Shopify Admin API ${response.status}: ${text.slice(0, 1200)}`);
  return extractJson(text);
}

async function clientCredentialsToken(store) {
  const clientId = process.env.VIVID_SHOPIFY_CLIENT_ID || "";
  const clientSecret = process.env.VIVID_SHOPIFY_CLIENT_SECRET || "";
  if (!clientId || !clientSecret) return "";

  const response = await fetch(`https://${store}/admin/oauth/access_token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      Accept: "application/json",
      "User-Agent": "vivid-inventory-sync/1.0",
    },
    body: new URLSearchParams({
      grant_type: "client_credentials",
      client_id: clientId,
      client_secret: clientSecret,
    }),
  });
  const text = await response.text();
  const body = extractJson(text);
  if (!response.ok || !body.access_token) {
    throw new Error(`Shopify client credentials token request failed ${response.status}: ${text.slice(0, 1200)}`);
  }
  return body.access_token;
}

function cliGraphql({ store, query, variables, allowMutations = false }) {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "vivid-inventory-"));
  const queryFile = path.join(tempDir, "query.graphql");
  const variableFile = path.join(tempDir, "variables.json");
  fs.writeFileSync(queryFile, query);
  fs.writeFileSync(variableFile, JSON.stringify(variables || {}));
  const args = [
    "store",
    "execute",
    "--store",
    store,
    "--query-file",
    queryFile,
    "--variable-file",
    variableFile,
    "--version",
    process.env.SHOPIFY_API_VERSION || defaultApiVersion,
    "--json",
  ];
  if (allowMutations) args.push("--allow-mutations");
  const result = spawnSync("shopify", args, { cwd: workspace, encoding: "utf8", maxBuffer: 1024 * 1024 * 20 });
  fs.rmSync(tempDir, { recursive: true, force: true });
  if (result.status !== 0) {
    const output = `${result.stdout || ""}\n${result.stderr || ""}`.trim();
    throw new Error(output || `shopify exited ${result.status}`);
  }
  return extractJson(result.stdout || result.stderr);
}

async function graphql({ store, token, query, variables, allowMutations = false }) {
  if (token) return adminGraphql({ store, token, query, variables });
  return cliGraphql({ store, query, variables, allowMutations });
}

const INVENTORY_QUERY = `query VividInventory($query: String!) {
  products(first: 100, query: $query) {
    nodes {
      id
      handle
      title
      productType
      tags
      variants(first: 10) {
        nodes {
          sku
          inventoryItem {
            id
            tracked
            inventoryLevels(first: 5) {
              nodes {
                location { id }
                quantities(names: ["available"]) { name quantity }
              }
            }
          }
        }
      }
    }
  }
}`;

const SET_INVENTORY = `mutation SetInventory($input: InventorySetQuantitiesInput!, $idempotencyKey: String!) {
  inventorySetQuantities(input: $input) @idempotent(key: $idempotencyKey) {
    inventoryAdjustmentGroup {
      reason
      referenceDocumentUri
      changes { name delta quantityAfterChange }
    }
    userErrors { code field message }
  }
}`;

function flattenVariants(products) {
  const rows = [];
  for (const product of products) {
    if (product.productType !== "Supplement") continue;
    for (const variant of product.variants?.nodes || []) {
      const level = variant.inventoryItem?.inventoryLevels?.nodes?.[0];
      rows.push({
        productId: product.id,
        handle: product.handle,
        title: product.title,
        tags: product.tags || [],
        sku: variant.sku || "",
        skuKey: normalizeSku(variant.sku),
        inventoryItemId: variant.inventoryItem?.id || null,
        tracked: Boolean(variant.inventoryItem?.tracked),
        locationId: level?.location?.id || null,
        currentAvailable: (level?.quantities || []).find((q) => q.name === "available")?.quantity ?? null,
      });
    }
  }
  return rows;
}

async function writeJson(filePath, data) {
  await fsp.mkdir(path.dirname(filePath), { recursive: true });
  await fsp.writeFile(filePath, `${JSON.stringify(data, null, 2)}\n`);
}

async function main() {
  const apply = hasFlag("--apply");
  const store = (argValue("--store", process.env.VIVID_SHOPIFY_STORE || defaultStore) || defaultStore)
    .replace(/^https?:\/\//, "")
    .replace(/\/$/, "");
  const token = process.env.VIVID_SHOPIFY_ADMIN_TOKEN || "";
  const exportPath = path.resolve(argValue("--omni-export", process.env.ONELIFE_OMNI_EXPORT_PATH || chooseLatestOmniExport()));
  const outDir = path.resolve(argValue("--out-dir", defaultOut));
  const maxAgeDays = Number(argValue("--max-age-days", "2"));
  const referenceDocumentUri =
    process.env.ONELIFE_OMNI_REFERENCE_URI ||
    `omni://onelife/${path.basename(exportPath).replace(/[^a-z0-9_.-]+/gi, "-")}`;

  const exportStat = fs.statSync(exportPath);
  const exportAgeDays = (Date.now() - exportStat.mtimeMs) / 86400000;
  const omniRows = parseOmniExport(exportPath);
  const omniBySku = new Map();
  const duplicateOmniSkus = new Set();
  for (const row of omniRows) {
    if (!row.skuKey) continue;
    if (omniBySku.has(row.skuKey)) duplicateOmniSkus.add(row.skuKey);
    else omniBySku.set(row.skuKey, row);
  }

  const accessToken = token || (await clientCredentialsToken(store));

  const productResponse = await graphql({
    store,
    token: accessToken,
    query: INVENTORY_QUERY,
    variables: { query: "vendor:'Vivid Health'" },
  });
  const products = productResponse.data?.products?.nodes || productResponse.products?.nodes || [];
  const variants = flattenVariants(products);
  const changes = [];
  const skipped = [];

  for (const variant of variants) {
    const omni = omniBySku.get(variant.skuKey);
    if (!variant.skuKey) {
      skipped.push({ ...variant, reason: "missing_shopify_sku" });
    } else if (duplicateOmniSkus.has(variant.skuKey)) {
      skipped.push({ ...variant, reason: "duplicate_omni_sku" });
    } else if (!omni) {
      skipped.push({ ...variant, reason: "missing_omni_sku" });
    } else if (omni.available == null) {
      skipped.push({ ...variant, reason: "invalid_omni_available", omni });
    } else if (!variant.inventoryItemId || !variant.locationId) {
      skipped.push({ ...variant, reason: "missing_inventory_item_or_location", omni });
    } else if (variant.currentAvailable !== omni.available) {
      changes.push({
        ...variant,
        omniAvailable: omni.available,
        delta: omni.available - Number(variant.currentAvailable || 0),
        omniDescription: omni.description,
      });
    }
  }

  const stale = exportAgeDays > maxAgeDays;
  const allowedSkipped = skipped.filter(
    (variant) =>
      variant.reason === "missing_omni_sku" &&
      Array.isArray(variant.tags) &&
      variant.tags.includes("launch-hold:inventory-mapping"),
  );
  const blockingSkipped = skipped.filter((variant) => !allowedSkipped.includes(variant));
  const report = {
    ok: !stale && blockingSkipped.length === 0,
    mode: apply ? "apply" : "dry-run",
    store,
    exportPath,
    exportMtime: exportStat.mtime.toISOString(),
    exportAgeDays: Number(exportAgeDays.toFixed(2)),
    maxAgeDays,
    summary: {
      omniRows: omniRows.length,
      vividSupplementVariants: variants.length,
      changes: changes.length,
      skipped: skipped.length,
      allowedSkipped: allowedSkipped.length,
      blockingSkipped: blockingSkipped.length,
      staleExport: stale,
    },
    changes,
    skipped,
    allowedSkipped,
    blockingSkipped,
    generatedAt: new Date().toISOString(),
  };

  await writeJson(path.join(outDir, "vivid-inventory-sync-latest.json"), report);

  if (stale && apply) {
    console.log(JSON.stringify({ ...report, ok: false, reason: "stale_omni_export_not_applied" }, null, 2));
    process.exit(2);
  }

  if (!apply || !changes.length) {
    console.log(JSON.stringify(report, null, 2));
    process.exit(stale ? 2 : 0);
  }

  const chunks = [];
  for (let index = 0; index < changes.length; index += 50) chunks.push(changes.slice(index, index + 50));
  const applyResults = [];
  for (const chunk of chunks) {
    const response = await graphql({
      store,
      token: accessToken,
      query: SET_INVENTORY,
      variables: {
        idempotencyKey: randomUUID(),
        input: {
          name: "available",
          reason: "correction",
          referenceDocumentUri,
          quantities: chunk.map((change) => ({
            inventoryItemId: change.inventoryItemId,
            locationId: change.locationId,
            quantity: change.omniAvailable,
            changeFromQuantity: null,
          })),
        },
      },
      allowMutations: true,
    });
    const payload = response.data?.inventorySetQuantities || response.inventorySetQuantities;
    const errors = payload?.userErrors || response.errors || [];
    if (errors.length) throw new Error(`inventorySetQuantities failed: ${JSON.stringify(errors)}`);
    applyResults.push(payload.inventoryAdjustmentGroup);
  }

  report.ok = !stale && blockingSkipped.length === 0;
  report.applyResults = applyResults;
  await writeJson(path.join(outDir, "vivid-inventory-sync-latest.json"), report);
  console.log(JSON.stringify(report, null, 2));
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exit(1);
});
