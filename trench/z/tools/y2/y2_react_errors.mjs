// Y2: does the oracle's Chrome log a React minified error on a page, under the
// app's user agent? Shape only: the error number, never page text.
// usage: node tools/parity_oracle/y2_react_errors.mjs <url> <seconds> [product|default]
import { chromium } from 'playwright';
import { getDeterministicLaunchOptions } from './deterministic.mjs';

const PRODUCT_UA =
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15 HiWave/1.0';
const [url, seconds, ua] = process.argv.slice(2);
const browser = await chromium.launch(getDeterministicLaunchOptions());
const options = { viewport: { width: 1280, height: 800 } };
if (ua !== 'default') options.userAgent = PRODUCT_UA;
const context = await browser.newContext(options);
const page = await context.newPage();
const t0 = Date.now();
const seen = [];
const note = (kind, text) => {
  const m = /Minified React error #(\d+)/.exec(text);
  seen.push([((Date.now() - t0) / 1000).toFixed(1), kind, m ? 'React #' + m[1] : 'len=' + text.length]);
};
page.on('console', (m) => { if (m.type() === 'error') note('console', m.text()); });
page.on('pageerror', (e) => note('pageerror', String(e)));
const r = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 }).catch((e) => ({ status: () => 'goto ' + e.name }));
console.log('chrome ' + browser.version() + ' ua=' + (ua || 'product') + ' status ' + r.status());
await page.waitForTimeout(Number(seconds) * 1000);
const shape = await page.evaluate(() => ({
  elements: document.getElementsByTagName('*').length,
  height: document.documentElement.scrollHeight,
  images: document.images.length,
  articles: document.querySelectorAll('article, [data-test-locator="stream"] li, li.stream-item').length,
}));
console.log(JSON.stringify(shape));
for (const row of seen) if (row[2].startsWith('React') || row[1] === 'pageerror') console.log(row.join(' '));
console.log('console errors total', seen.length);
await browser.close();
