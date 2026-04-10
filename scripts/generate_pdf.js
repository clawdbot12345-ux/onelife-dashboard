#!/usr/bin/env node
/**
 * Render index.html to onelife-dashboard.pdf using headless Chrome.
 * Used by the daily refresh GitHub Actions workflow.
 */
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const https = require('https');

const ROOT = path.resolve(__dirname, '..');
const INDEX_HTML = path.join(ROOT, 'index.html');
const PDF_OUT = path.join(ROOT, 'onelife-dashboard.pdf');
const CHART_LOCAL = path.join(ROOT, 'chart.min.js');
const INDEX_PDF = path.join(ROOT, 'index-pdf.html');
const CHART_CDN = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js';

async function download(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    https.get(url, (res) => {
      res.pipe(file);
      file.on('finish', () => file.close(resolve));
    }).on('error', (err) => {
      fs.unlink(dest, () => reject(err));
    });
  });
}

(async () => {
  // 1. Download Chart.js locally for offline rendering
  console.log('Downloading Chart.js...');
  await download(CHART_CDN, CHART_LOCAL);

  // 2. Create a copy of index.html that uses the local Chart.js
  const html = fs.readFileSync(INDEX_HTML, 'utf8');
  const localHtml = html.replace(CHART_CDN, 'chart.min.js');
  fs.writeFileSync(INDEX_PDF, localHtml);

  // 3. Launch headless Chrome and render
  console.log('Launching headless browser...');
  const browser = await puppeteer.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-gpu',
      '--disable-dev-shm-usage',
    ],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  console.log('Loading dashboard...');
  await page.goto(`file://${INDEX_PDF}`, { waitUntil: 'load', timeout: 300000 });

  // Wait for Chart.js to finish rendering
  await new Promise((r) => setTimeout(r, 6000));

  // Make all tab panels visible so every section gets captured
  await page.evaluate(() => {
    document.querySelectorAll('.tab-panel').forEach((p) => {
      p.style.display = 'block';
      p.classList.add('active');
    });
  });
  await new Promise((r) => setTimeout(r, 3000));

  console.log('Generating PDF...');
  await page.pdf({
    path: PDF_OUT,
    format: 'A3',
    landscape: true,
    printBackground: true,
    margin: { top: '8mm', bottom: '8mm', left: '8mm', right: '8mm' },
  });

  await browser.close();

  // 4. Clean up temp files
  fs.unlinkSync(CHART_LOCAL);
  fs.unlinkSync(INDEX_PDF);

  const sizeMB = (fs.statSync(PDF_OUT).size / 1024 / 1024).toFixed(2);
  console.log(`PDF saved: ${PDF_OUT} (${sizeMB} MB)`);
})().catch((err) => {
  console.error('PDF generation failed:', err);
  process.exit(1);
});
