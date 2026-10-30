// Y2: the oracle's Chrome's fetch/XHR requests on a page, paths without queries.
// usage: node tools/parity_oracle/y2_requests.mjs <url> <seconds> [height]
import { chromium } from 'playwright';
import { getDeterministicLaunchOptions } from './deterministic.mjs';

const PRODUCT_UA =
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15 HiWave/1.0';
const [url, seconds, height] = process.argv.slice(2);
const browser = await chromium.launch(getDeterministicLaunchOptions());
const context = await browser.newContext({ viewport: { width: 1280, height: Number(height || 2400) }, userAgent: PRODUCT_UA });
const page = await context.newPage();
const t0 = Date.now();
page.on('response', (r) => {
  const q = r.request();
  if (!['fetch', 'xhr'].includes(q.resourceType())) return;
  const u = new URL(r.url());
  console.log(((Date.now() - t0) / 1000).toFixed(1), q.method(), r.status(), u.host + u.pathname.slice(0, 70));
});
await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
await page.waitForTimeout(Number(seconds) * 1000);
await browser.close();
