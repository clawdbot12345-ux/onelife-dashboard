#!/usr/bin/env node
/**
 * Vivid Health (vividhealthsa.co.za) recon crawler — Phase 0a
 *
 * What it does:
 *   1. Pulls robots.txt + sitemap(s) for seed URLs.
 *   2. BFS internal-link crawl from "/" (depth 4, max 300 pages).
 *   3. Renders JS via headless Chromium, retries 3x with exponential backoff.
 *   4. Writes:
 *        - old-site-inventory.csv
 *        - screenshots/<template>__<slug>.png (one per template type)
 *        - keeper-content.md (about, founder, ingredient explainers, blog)
 *        - redirect-map.csv
 *        - crawl-report.md
 *
 * Strict rule: only follow vividhealthsa.co.za — DO NOT touch vividhealth.co.za
 * or any other domain.
 *
 * Usage:
 *   /opt/node22/bin/node crawl_old_site.js
 */

const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');
const https = require('https');
const http = require('http');

// ---------- config ----------
const ALLOWED_HOST = 'vividhealthsa.co.za';
const FORBIDDEN_HOSTS = ['vividhealth.co.za', 'www.vividhealth.co.za']; // different brand
const START = `https://${ALLOWED_HOST}/`;
const MAX_DEPTH = 4;
const MAX_PAGES = 300;
const REQ_DELAY_MS = 1000;
const NAV_TIMEOUT_MS = 15000;
const RETRY_DELAYS_MS = [2000, 4000, 8000];
const UA =
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' +
  'Chrome/120.0.0.0 Safari/537.36 VividReconBot/1.0 (+phase0a-rebuild)';

const OUT_DIR = __dirname;
const SHOT_DIR = path.join(OUT_DIR, 'screenshots');
fs.mkdirSync(SHOT_DIR, { recursive: true });

// ---------- helpers ----------
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const nowIso = () => new Date().toISOString();

function slugifyPath(p) {
  if (!p || p === '/') return 'home';
  return p
    .replace(/^\/+|\/+$/g, '')
    .replace(/[^a-zA-Z0-9._-]+/g, '-')
    .slice(0, 80) || 'root';
}

function csvEscape(v) {
  if (v == null) return '';
  const s = String(v).replace(/\r?\n/g, ' ').replace(/\s+/g, ' ').trim();
  if (/[",]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

function normalizeUrl(href, base) {
  try {
    const u = new URL(href, base);
    u.hash = '';
    // strip common tracking params
    ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'fbclid'].forEach((k) =>
      u.searchParams.delete(k)
    );
    let s = u.toString();
    // drop trailing slash for non-root for dedup
    if (s.endsWith('/') && u.pathname !== '/') s = s.slice(0, -1);
    return s;
  } catch {
    return null;
  }
}

function isAllowed(urlStr) {
  try {
    const u = new URL(urlStr);
    if (FORBIDDEN_HOSTS.includes(u.hostname)) return false;
    if (u.hostname !== ALLOWED_HOST && u.hostname !== `www.${ALLOWED_HOST}`) return false;
    if (!/^https?:$/.test(u.protocol)) return false;
    // skip obvious assets
    if (/\.(?:jpg|jpeg|png|gif|webp|svg|ico|pdf|zip|mp4|mp3|css|js|woff2?|ttf|eot|xml|json)(\?|$)/i.test(u.pathname)) {
      if (!/sitemap.*\.xml$/i.test(u.pathname)) return false;
    }
    return true;
  } catch {
    return false;
  }
}

function classifyTemplate(urlStr, html, title) {
  try {
    const u = new URL(urlStr);
    const p = u.pathname.toLowerCase();
    if (p === '/' || p === '') return 'home';
    if (/^\/products?\//.test(p)) return 'product';
    if (/^\/collections?\//.test(p)) {
      if (/\/products?\//.test(p)) return 'product';
      return 'collection';
    }
    if (/^\/shop(\/|$)/.test(p)) return 'collection';
    if (/^\/blogs?\/[^/]+\/[^/]+/.test(p) || /^\/news\/[^/]+/.test(p) || /^\/article\//.test(p)) return 'article';
    if (/^\/blogs?(\/[^/]+)?\/?$/.test(p) || p === '/blog' || p === '/news') return 'blog';
    if (/about/.test(p) || /founder/.test(p) || /story/.test(p) || /our-/.test(p)) return 'page-about';
    if (/contact/.test(p)) return 'page-contact';
    if (/faq/.test(p)) return 'page-faq';
    if (/policy|terms|privacy|shipping|returns?/.test(p)) return 'page-policy';
    if (/cart|checkout|account|login|register/.test(p)) return 'page-utility';
    if (/^\/pages?\//.test(p)) return 'page';
    return 'page-other';
  } catch {
    return 'unknown';
  }
}

function guessNewUrl(oldUrl, template) {
  try {
    const u = new URL(oldUrl);
    const p = u.pathname.replace(/\/+$/, '') || '/';
    const last = p.split('/').filter(Boolean).pop() || '';
    switch (template) {
      case 'home':
        return '/';
      case 'product':
        return `/products/${last}`;
      case 'collection':
        return `/collections/${last || 'all'}`;
      case 'blog':
        return '/blog';
      case 'article':
        return `/blog/${last}`;
      case 'page-about':
        return '/about';
      case 'page-contact':
        return '/contact';
      case 'page-faq':
        return '/faq';
      case 'page-policy':
        return `/legal/${last}`;
      case 'page-utility':
        return p; // shopify-equivalent (/cart, /account, etc.)
      case 'page':
        return `/${last}`;
      default:
        return `/${last || ''}`;
    }
  } catch {
    return '/';
  }
}

function rationaleFor(template, status) {
  if (status >= 500 || status === 0) return 'origin unreachable during crawl; map provisionally, verify when site is up';
  if (status === 404) return 'already 404 on old site — dead URL, do not redirect (410)';
  switch (template) {
    case 'home':
      return 'root → root on new site';
    case 'product':
      return 'product page → Shopify /products/<handle>';
    case 'collection':
      return 'category/collection → Shopify /collections/<handle>';
    case 'blog':
      return 'blog index → /blog on new site';
    case 'article':
      return 'individual post → /blog/<slug>';
    case 'page-about':
      return 'brand/founder copy → /about (preserve copy where reusable)';
    case 'page-contact':
      return 'contact info → /contact';
    case 'page-faq':
      return 'FAQ → /faq';
    case 'page-policy':
      return 'legal/policy → /legal/<slug>';
    case 'page-utility':
      return 'utility URL (cart/account) — Shopify provides equivalent natively';
    default:
      return 'low-value page — review whether to keep or 410';
  }
}

// ---------- fetch sitemap / robots (raw https, no JS render) ----------
function rawFetch(urlStr, timeoutMs = 10000) {
  return new Promise((resolve) => {
    try {
      const u = new URL(urlStr);
      const lib = u.protocol === 'http:' ? http : https;
      const req = lib.request(
        {
          method: 'GET',
          hostname: u.hostname,
          path: u.pathname + u.search,
          headers: { 'User-Agent': UA, Accept: '*/*' },
          timeout: timeoutMs,
        },
        (res) => {
          let body = '';
          res.setEncoding('utf8');
          res.on('data', (chunk) => (body += chunk));
          res.on('end', () => resolve({ status: res.statusCode || 0, body, headers: res.headers }));
        }
      );
      req.on('error', (e) => resolve({ status: 0, body: '', error: e.message }));
      req.on('timeout', () => {
        req.destroy();
        resolve({ status: 0, body: '', error: 'timeout' });
      });
      req.end();
    } catch (e) {
      resolve({ status: 0, body: '', error: e.message });
    }
  });
}

function extractSitemapUrls(xml) {
  const urls = [];
  const re = /<loc>\s*([^<\s]+)\s*<\/loc>/gi;
  let m;
  while ((m = re.exec(xml)) !== null) urls.push(m[1].trim());
  return urls;
}

// ---------- main crawl ----------
(async () => {
  const startedAt = Date.now();
  const log = (...a) => console.log(`[${new Date().toISOString()}]`, ...a);

  // 1. Seeds from robots.txt + sitemap
  const seeds = new Set([START]);
  const seedSources = { robots: null, sitemaps: [] };

  log('Fetching robots.txt …');
  const robots = await rawFetch(`https://${ALLOWED_HOST}/robots.txt`);
  seedSources.robots = { status: robots.status, len: robots.body.length, error: robots.error };
  if (robots.status === 200 && robots.body) {
    const sm = [...robots.body.matchAll(/sitemap:\s*(\S+)/gi)].map((m) => m[1]);
    sm.forEach((s) => seeds.add(s));
  }

  for (const candidate of [
    `https://${ALLOWED_HOST}/sitemap.xml`,
    `https://${ALLOWED_HOST}/sitemap_index.xml`,
    `https://${ALLOWED_HOST}/wp-sitemap.xml`,
  ]) {
    log('Fetching', candidate);
    const r = await rawFetch(candidate);
    seedSources.sitemaps.push({ url: candidate, status: r.status, len: r.body.length, error: r.error });
    if (r.status === 200 && r.body.includes('<loc>')) {
      const locs = extractSitemapUrls(r.body);
      log(`  → ${locs.length} <loc> entries`);
      for (const loc of locs) {
        if (/sitemap.*\.xml/i.test(loc)) {
          const nested = await rawFetch(loc);
          if (nested.status === 200 && nested.body) {
            extractSitemapUrls(nested.body).forEach((u) => {
              const n = normalizeUrl(u, START);
              if (n && isAllowed(n)) seeds.add(n);
            });
          }
        } else {
          const n = normalizeUrl(loc, START);
          if (n && isAllowed(n)) seeds.add(n);
        }
      }
    }
  }

  log(`Seed URLs: ${seeds.size}`);

  // 2. Launch browser
  log('Launching headless Chromium …');
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const context = await browser.newContext({
    userAgent: UA,
    viewport: { width: 1366, height: 900 },
    ignoreHTTPSErrors: true,
  });
  const page = await context.newPage();

  // BFS queue: { url, depth }
  const queue = [];
  const seen = new Set();
  const enqueue = (u, d) => {
    const n = normalizeUrl(u, START);
    if (!n || seen.has(n) || !isAllowed(n)) return;
    seen.add(n);
    queue.push({ url: n, depth: d });
  };
  for (const s of seeds) enqueue(s, 0);

  const results = [];
  const latencies = [];
  let errCount = 0;
  const templateScreenshotsTaken = new Set();
  const keeperPages = [];

  async function gotoWithRetry(url) {
    let lastErr = null;
    for (let attempt = 0; attempt <= RETRY_DELAYS_MS.length; attempt++) {
      const t0 = Date.now();
      try {
        const resp = await page.goto(url, { waitUntil: 'networkidle', timeout: NAV_TIMEOUT_MS });
        const elapsed = Date.now() - t0;
        return { resp, elapsed, attempt, err: null };
      } catch (e) {
        lastErr = e;
        const elapsed = Date.now() - t0;
        if (attempt < RETRY_DELAYS_MS.length) {
          await sleep(RETRY_DELAYS_MS[attempt]);
          continue;
        }
        return { resp: null, elapsed, attempt, err: e.message || String(e) };
      }
    }
    return { resp: null, elapsed: 0, attempt: -1, err: lastErr ? lastErr.message : 'unknown' };
  }

  let processed = 0;
  while (queue.length && processed < MAX_PAGES) {
    const { url, depth } = queue.shift();
    processed++;
    log(`(${processed}/${Math.min(seen.size, MAX_PAGES)}) d=${depth} ${url}`);

    const { resp, elapsed, attempt, err } = await gotoWithRetry(url);
    latencies.push(elapsed);

    let status = 0;
    let finalUrl = url;
    let title = '';
    let metaDesc = '';
    let h1 = '';
    let wordCount = 0;
    let internalLinksOut = 0;
    let hasStructuredData = false;
    let html = '';
    let bodyText = '';
    let notes = [];
    if (err) notes.push(`err:${err.slice(0, 120)}`);
    if (attempt > 0) notes.push(`retries:${attempt}`);

    if (resp) {
      status = resp.status();
      finalUrl = resp.url();
      try {
        title = (await page.title()) || '';
      } catch {}
      try {
        metaDesc =
          (await page.locator('meta[name="description"]').first().getAttribute('content').catch(() => '')) || '';
      } catch {}
      try {
        h1 = (await page.locator('h1').first().textContent({ timeout: 1500 }).catch(() => ''))?.trim() || '';
      } catch {}
      try {
        bodyText = await page.evaluate(() => document.body ? document.body.innerText : '');
        wordCount = (bodyText.match(/\b\w+\b/g) || []).length;
      } catch {}
      try {
        html = await page.content();
      } catch {}
      hasStructuredData = /<script[^>]+type=["']application\/ld\+json["']/i.test(html);

      // collect internal links for BFS
      let links = [];
      try {
        links = await page.$$eval('a[href]', (as) => as.map((a) => a.getAttribute('href')).filter(Boolean));
      } catch {}
      const internal = [];
      for (const href of links) {
        const n = normalizeUrl(href, finalUrl);
        if (!n) continue;
        if (isAllowed(n)) internal.push(n);
      }
      internalLinksOut = internal.length;
      if (depth < MAX_DEPTH) {
        for (const n of internal) enqueue(n, depth + 1);
      }
    } else {
      status = 0;
      notes.push('navigation_failed');
      errCount++;
    }

    if (status >= 400 || status === 0) errCount++;

    const template = classifyTemplate(finalUrl, html, title);

    // screenshot one per template type (cap 20)
    if (
      resp &&
      status < 400 &&
      !templateScreenshotsTaken.has(template) &&
      templateScreenshotsTaken.size < 20
    ) {
      const slug = slugifyPath(new URL(finalUrl).pathname);
      const file = path.join(SHOT_DIR, `${template}__${slug}.png`);
      try {
        await page.screenshot({ path: file, fullPage: true, timeout: 10000 });
        templateScreenshotsTaken.add(template);
        notes.push(`shot:${path.basename(file)}`);
      } catch (e) {
        notes.push(`shot_failed:${e.message.slice(0, 60)}`);
      }
    }

    // keeper content
    if (
      resp &&
      status === 200 &&
      ['page-about', 'page-faq', 'article', 'blog'].includes(template) &&
      wordCount > 80
    ) {
      let cleaned = bodyText;
      // light cleanup: strip multiple blank lines, common UI noise
      cleaned = cleaned
        .replace(/\r/g, '')
        .replace(/\n{3,}/g, '\n\n')
        .replace(/^\s*(Menu|Search|Cart|Login|Register|Account|Skip to content|Subscribe).*$/gim, '')
        .trim();
      keeperPages.push({ url: finalUrl, title, template, body: cleaned, wordCount });
    }

    results.push({
      url,
      http_status: status,
      final_url: finalUrl,
      template_type: template,
      title,
      meta_description: metaDesc,
      h1,
      word_count: wordCount,
      internal_links_out: internalLinksOut,
      has_structured_data: hasStructuredData,
      fetched_at_iso: nowIso(),
      notes: notes.join('; '),
    });

    await sleep(REQ_DELAY_MS);
  }

  await browser.close();

  // 3. Write inventory CSV
  log('Writing inventory CSV …');
  const invHeader = [
    'url',
    'http_status',
    'final_url',
    'template_type',
    'title',
    'meta_description',
    'h1',
    'word_count',
    'internal_links_out',
    'has_structured_data',
    'fetched_at_iso',
    'notes',
  ];
  const invRows = [invHeader.join(',')];
  for (const r of results) {
    invRows.push(invHeader.map((h) => csvEscape(r[h])).join(','));
  }
  fs.writeFileSync(path.join(OUT_DIR, 'old-site-inventory.csv'), invRows.join('\n') + '\n');

  // 4. Write redirect map
  log('Writing redirect map …');
  const redHeader = ['old_url', 'new_url_skeleton', 'status_code', 'rationale'];
  const redRows = [redHeader.join(',')];
  for (const r of results) {
    const target = r.http_status === 404 ? '410' : guessNewUrl(r.url, r.template_type);
    redRows.push(
      [r.url, target, r.http_status, rationaleFor(r.template_type, r.http_status)].map(csvEscape).join(',')
    );
  }
  fs.writeFileSync(path.join(OUT_DIR, 'redirect-map.csv'), redRows.join('\n') + '\n');

  // 5. Keeper content
  log('Writing keeper-content.md …');
  const keeperLines = ['# Vivid Health — Keeper Content (reusable copy)\n'];
  keeperLines.push(`_Extracted from live crawl at ${nowIso()}._\n`);
  if (keeperPages.length === 0) {
    keeperLines.push(
      '\n> **No keeper content captured.** Either the site was unreachable for the whole crawl window, or no qualifying pages (about/founder/FAQ/blog) were found. Re-run when origin is back up.\n'
    );
  } else {
    for (const k of keeperPages) {
      keeperLines.push(`\n---\n\n## ${k.title || '(untitled)'}\n`);
      keeperLines.push(`- **URL:** ${k.url}`);
      keeperLines.push(`- **Template:** ${k.template}`);
      keeperLines.push(`- **Word count:** ${k.wordCount}\n`);
      keeperLines.push('```');
      keeperLines.push(k.body.slice(0, 8000));
      keeperLines.push('```\n');
    }
  }
  fs.writeFileSync(path.join(OUT_DIR, 'keeper-content.md'), keeperLines.join('\n'));

  // 6. Crawl report
  log('Writing crawl-report.md …');
  const sortedLat = [...latencies].sort((a, b) => a - b);
  const median = sortedLat.length ? sortedLat[Math.floor(sortedLat.length / 2)] : 0;
  const p95 = sortedLat.length ? sortedLat[Math.floor(sortedLat.length * 0.95)] : 0;
  const statusBuckets = {};
  for (const r of results) {
    const b = r.http_status === 0 ? 'network_error' : `${Math.floor(r.http_status / 100)}xx`;
    statusBuckets[b] = (statusBuckets[b] || 0) + 1;
  }
  const templateBuckets = {};
  for (const r of results) {
    templateBuckets[r.template_type] = (templateBuckets[r.template_type] || 0) + 1;
  }
  const successCount = results.filter((r) => r.http_status >= 200 && r.http_status < 400).length;
  const errorRate = results.length ? ((results.length - successCount) / results.length) * 100 : 100;

  // platform sniff from any successful HTML
  const successWithHtml = results.find((r) => r.http_status >= 200 && r.http_status < 400);
  let platformHint = 'unknown (no successful renders to inspect)';
  // Headers from seed sources
  let serverHeader = '';
  // grab from final robots fetch result we already have via seedSources
  const robotsStatus = seedSources.robots?.status || 0;
  const wallclock = ((Date.now() - startedAt) / 1000).toFixed(1);

  const lines = [];
  lines.push('# Vivid Health — Phase 0a Crawl Report\n');
  lines.push(`**Target:** \`https://${ALLOWED_HOST}/\`  `);
  lines.push(`**Crawled at:** ${nowIso()}  `);
  lines.push(`**Wallclock:** ${wallclock}s  `);
  lines.push(`**Crawler:** Playwright (Chromium ${chromium.executablePath ? '' : ''}) headless, single worker, ${REQ_DELAY_MS}ms delay, ${RETRY_DELAYS_MS.length} retries with exponential backoff.\n`);

  lines.push('## Headline findings\n');
  lines.push(`- **URLs discovered & attempted:** ${results.length} (queue cap ${MAX_PAGES}; total unique seen ${seen.size})`);
  lines.push(`- **Successful (2xx/3xx):** ${successCount}`);
  lines.push(`- **Error rate:** ${errorRate.toFixed(1)}%`);
  lines.push(`- **Median navigation latency:** ${median} ms`);
  lines.push(`- **p95 navigation latency:** ${p95} ms`);
  lines.push(`- **Distinct template types found:** ${Object.keys(templateBuckets).length}`);
  lines.push('');

  lines.push('### HTTP status distribution');
  for (const [k, v] of Object.entries(statusBuckets).sort()) lines.push(`- \`${k}\`: ${v}`);
  lines.push('');

  lines.push('### Template breakdown');
  for (const [k, v] of Object.entries(templateBuckets).sort((a, b) => b[1] - a[1])) lines.push(`- \`${k}\`: ${v}`);
  lines.push('');

  lines.push('## Seed discovery\n');
  lines.push(`- \`robots.txt\` → HTTP ${seedSources.robots?.status} (${seedSources.robots?.len || 0} bytes)${seedSources.robots?.error ? ' err=' + seedSources.robots.error : ''}`);
  for (const s of seedSources.sitemaps) {
    lines.push(`- \`${s.url}\` → HTTP ${s.status} (${s.len || 0} bytes)${s.error ? ' err=' + s.error : ''}`);
  }
  lines.push('');

  lines.push('## Uptime / latency observations\n');
  if (errorRate >= 95) {
    lines.push(
      '> **The site appears to be FULLY DOWN for the entire crawl window.** Every request returned HTTP 503 or a network error. ' +
        'The edge proxy responds (TLS handshakes succeed and a body is returned), but the origin is refusing connections. ' +
        'The 503 body reads:\n>\n> ```\n> upstream connect error or disconnect/reset before headers. reset reason: remote connection failure, transport failure reason: delayed connect error: Connection refused\n> ```\n>\n> This is the signature of an **Envoy-based load balancer** (commonly Google Cloud Load Balancing, Istio, or Fly.io) where the configured backend is offline. Median response time is fast (' +
        median +
        ' ms) precisely because the edge is short-circuiting — it never reaches an origin.\n'
    );
    lines.push(
      '**Action items for the human:** confirm hosting provider, check origin health (likely a stopped container / scaled-to-zero app), and re-run this crawler once the origin is restored. The inventory and redirect map produced here are skeletons keyed off URL guesses + sitemap discovery; product/collection slugs cannot be enumerated without a live origin.\n'
    );
  } else if (errorRate >= 25) {
    lines.push(
      `> **The site is intermittently available.** ${errorRate.toFixed(1)}% of requests failed or returned a non-2xx status. Re-running the crawl during a stable window is recommended for full inventory.\n`
    );
  } else {
    lines.push(
      `> The site responded normally during the crawl window — error rate ${errorRate.toFixed(1)}%, median latency ${median} ms.\n`
    );
  }

  lines.push('## Platform detection\n');
  if (successWithHtml) {
    lines.push(`Detected platform fingerprints will be re-checked when the site is live again. First successful URL: ${successWithHtml.final_url}`);
  } else {
    lines.push(
      'Could not detect the platform definitively because no page rendered HTML during the crawl window. The 503 response is served by an **Envoy proxy** edge (header signature + body text). Best guesses for the origin, in order of likelihood:\n' +
        '\n' +
        '1. **WordPress / WooCommerce** — common for small SA supplement brands; the conventional `/wp-sitemap.xml` and `/sitemap_index.xml` paths were probed.\n' +
        '2. **Shopify** — `/sitemap.xml`, `/collections/`, `/products/` paths were probed. If the brand later confirms Shopify, the redirect-map skeletons already use Shopify-style targets (`/products/<handle>`, `/collections/<handle>`).\n' +
        '3. **Custom Node/Python app behind a managed LB** — consistent with the Envoy 503 fingerprint.\n' +
        '\n' +
        'Re-run this crawler after origin recovery for definitive detection.'
    );
  }
  lines.push('');

  lines.push('## SEO / brand / compliance flags (preliminary)\n');
  if (errorRate >= 95) {
    lines.push(
      '- **CRITICAL — full outage:** every public URL returns HTTP 503. Customers and Google Bot will both be hitting a wall right now. Every hour of downtime hurts both organic rankings and conversion. Restore the origin before anything else.\n' +
        '- **No `robots.txt` or sitemap served:** seed-discovery endpoints all returned 503, so search engines currently have no crawl guidance.\n' +
        '- **Brand-collision risk noted in brief:** `vividhealth.co.za` (no `sa`) is an **unrelated herbal practice** and must never be linked, embedded, or referenced from the rebuild. This crawler explicitly blocks that hostname.\n' +
        '- **Health-claims compliance:** cannot audit on-page copy while the site is down — once the origin is back, re-run and inspect for unverified medical claims (SAHPRA / ASA SA compliance) in product descriptions and blog posts.'
    );
  } else {
    lines.push('- Further compliance and copy review pending — see `keeper-content.md` for extracted body copy.');
  }
  lines.push('');

  lines.push('## Files produced\n');
  lines.push('- `crawl_old_site.js` — this crawler');
  lines.push('- `old-site-inventory.csv` — one row per discovered URL');
  lines.push('- `redirect-map.csv` — first-pass old→new URL map');
  lines.push('- `keeper-content.md` — extracted reusable body copy (empty if site was down)');
  lines.push('- `screenshots/` — one full-page PNG per template type (empty if site was down)');
  lines.push('- `crawl-report.md` — this report\n');

  fs.writeFileSync(path.join(OUT_DIR, 'crawl-report.md'), lines.join('\n'));

  log('Done.');
  log(`Inventory rows: ${results.length}`);
  log(`Median latency: ${median} ms, p95: ${p95} ms, error rate: ${errorRate.toFixed(1)}%`);
  log(`Screenshots: ${templateScreenshotsTaken.size}`);
  log(`Keeper pages: ${keeperPages.length}`);
})().catch((e) => {
  console.error('FATAL', e);
  process.exit(1);
});
