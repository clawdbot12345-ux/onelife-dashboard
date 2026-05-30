#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const workspace = path.resolve(__dirname, "..");
const defaultStore = "hgywg0-w7.myshopify.com";
const outputPath = path.join(workspace, "output/vivid-online-store-publication-latest.json");

function argValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] || fallback : fallback;
}

function hasFlag(name) {
  return process.argv.includes(name);
}

function extractJson(text) {
  const trimmed = String(text || "").trim();
  if (!trimmed) return {};
  try {
    return JSON.parse(trimmed);
  } catch {
    const start = trimmed.search(/[{[]/);
    if (start >= 0) return JSON.parse(trimmed.slice(start));
    throw new Error(`No JSON in Shopify CLI output: ${trimmed.slice(0, 500)}`);
  }
}

function runShopifyGraphql({ store, query, variables, allowMutations = false }) {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "vivid-publish-"));
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
    "--json",
  ];
  if (allowMutations) args.push("--allow-mutations");

  const result = spawnSync("shopify", args, {
    cwd: workspace,
    encoding: "utf8",
    maxBuffer: 1024 * 1024 * 20,
  });
  fs.rmSync(tempDir, { recursive: true, force: true });
  if (result.status !== 0) {
    const output = `${result.stdout || ""}\n${result.stderr || ""}`.trim();
    throw new Error(output || `shopify exited ${result.status}`);
  }
  return extractJson(result.stdout || result.stderr);
}

function userErrors(payload, key) {
  const errors = payload?.data?.[key]?.userErrors || payload?.[key]?.userErrors || payload?.errors || [];
  return errors.filter(Boolean);
}

const STATE_QUERY = `query VividOnlineStorePublicationState {
  publications(first: 20) {
    nodes { id name }
  }
  products(first: 250, query: "vendor:'Vivid Health'") {
    nodes { id handle title status onlineStoreUrl }
  }
  collections(first: 250) {
    nodes { id handle title }
  }
}`;

const PRODUCT_ACTIVATE = `mutation VividProductActivate($product: ProductUpdateInput!) {
  productUpdate(product: $product) {
    product { id handle title status }
    userErrors { field message }
  }
}`;

const PUBLISHABLE_PUBLISH = `mutation VividPublishablePublish($id: ID!, $input: [PublicationInput!]!) {
  publishablePublish(id: $id, input: $input) {
    publishable {
      ... on Product { id handle }
      ... on Collection { id handle }
    }
    userErrors { field message }
  }
}`;

function main() {
  const store = argValue("--store", defaultStore);
  const apply = hasFlag("--apply");

  const stateResponse = runShopifyGraphql({ store, query: STATE_QUERY, variables: {} });
  const state = stateResponse.data || stateResponse;
  const onlineStore = (state.publications?.nodes || []).find((publication) => publication.name === "Online Store");
  if (!onlineStore?.id) throw new Error("Online Store publication was not found.");

  const products = state.products?.nodes || [];
  const collections = (state.collections?.nodes || []).filter((collection) => collection.handle !== "frontpage");
  const planned = {
    productsToActivate: products.filter((product) => product.status !== "ACTIVE").map(({ handle, status }) => ({ handle, status })),
    productsToPublish: products.filter((product) => !product.onlineStoreUrl).map(({ handle }) => handle),
    collectionsToPublish: collections.map(({ handle }) => handle),
  };

  const applied = {
    productsActivated: [],
    productsPublished: [],
    collectionsPublished: [],
    skippedUserErrors: [],
  };

  if (apply) {
    for (const product of products) {
      if (product.status !== "ACTIVE") {
        const response = runShopifyGraphql({
          store,
          query: PRODUCT_ACTIVATE,
          variables: { product: { id: product.id, status: "ACTIVE" } },
          allowMutations: true,
        });
        const errors = userErrors(response, "productUpdate");
        if (errors.length) throw new Error(`productUpdate ${product.handle}: ${JSON.stringify(errors)}`);
        applied.productsActivated.push(product.handle);
      }
      const publishResponse = runShopifyGraphql({
        store,
        query: PUBLISHABLE_PUBLISH,
        variables: { id: product.id, input: [{ publicationId: onlineStore.id }] },
        allowMutations: true,
      });
      const publishErrors = userErrors(publishResponse, "publishablePublish");
      if (publishErrors.length) {
        applied.skippedUserErrors.push({ handle: product.handle, type: "product", errors: publishErrors });
      } else {
        applied.productsPublished.push(product.handle);
      }
    }

    for (const collection of collections) {
      const response = runShopifyGraphql({
        store,
        query: PUBLISHABLE_PUBLISH,
        variables: { id: collection.id, input: [{ publicationId: onlineStore.id }] },
        allowMutations: true,
      });
      const errors = userErrors(response, "publishablePublish");
      if (errors.length) {
        applied.skippedUserErrors.push({ handle: collection.handle, type: "collection", errors });
      } else {
        applied.collectionsPublished.push(collection.handle);
      }
    }
  }

  const report = {
    ok: true,
    mode: apply ? "apply" : "dry-run",
    store,
    onlineStorePublicationId: onlineStore.id,
    planned,
    applied,
  };
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, `${JSON.stringify(report, null, 2)}\n`);
  console.log(JSON.stringify(report, null, 2));
}

try {
  main();
} catch (error) {
  console.error(error?.stack || error?.message || error);
  process.exit(1);
}
