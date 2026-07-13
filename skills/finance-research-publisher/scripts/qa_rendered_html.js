#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
const { chromium } = require('playwright');

function arg(name, required = false) {
  const index = process.argv.indexOf(name);
  const value = index >= 0 ? process.argv[index + 1] : null;
  if (required && !value) throw new Error(`${name} is required`);
  return value;
}

(async () => {
  const htmlPath = path.resolve(arg('--html', true));
  const output = arg('--output');
  const screenshotDir = arg('--screenshot-dir');
  if (!fs.existsSync(htmlPath) || fs.statSync(htmlPath).size === 0) throw new Error('HTML is missing or empty');
  if (screenshotDir) fs.mkdirSync(screenshotDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const results = [];
  for (const viewport of [{ name: 'desktop', width: 1440, height: 1100 }, { name: 'mobile', width: 390, height: 844 }]) {
    const page = await browser.newPage({ viewport });
    const consoleErrors = [];
    page.on('console', message => {
      if (message.type() === 'error' || message.type() === 'warning') consoleErrors.push(message.text());
    });
    page.on('pageerror', error => consoleErrors.push(String(error)));
    await page.goto(pathToFileURL(htmlPath).href, { waitUntil: 'load' });
    const metrics = await page.evaluate(() => {
      const required = ['summary', 'market', 'drivers', 'news', 'tech', 'commodities', 'global', 'deep', 'tomorrow'];
      const missing = required.filter(id => !document.getElementById(id));
      const bodyOverflow = document.documentElement.scrollWidth > window.innerWidth + 1;
      const emptyText = (document.body.innerText || '').trim().length < 500;
      const badTables = [...document.querySelectorAll('table')].filter(table => {
        const parent = table.parentElement;
        return table.scrollWidth > table.clientWidth + 1 && (!parent || getComputedStyle(parent).overflowX === 'visible');
      }).length;
      return { missing, bodyOverflow, emptyText, badTables, textLength: document.body.innerText.length };
    });
    if (screenshotDir) await page.screenshot({ path: path.join(screenshotDir, `${viewport.name}.png`), fullPage: true });
    results.push({ viewport, ...metrics, consoleErrors });
    await page.close();
  }
  await browser.close();
  const valid = results.every(row => !row.bodyOverflow && !row.emptyText && row.badTables === 0 && row.missing.length === 0 && row.consoleErrors.length === 0);
  const payload = { valid, html: htmlPath, results };
  if (output) {
    fs.mkdirSync(path.dirname(path.resolve(output)), { recursive: true });
    fs.writeFileSync(output, JSON.stringify(payload, null, 2) + '\n');
  }
  console.log(JSON.stringify(payload, null, 2));
  process.exit(valid ? 0 : 1);
})().catch(error => {
  console.error(error.stack || String(error));
  process.exit(1);
});
