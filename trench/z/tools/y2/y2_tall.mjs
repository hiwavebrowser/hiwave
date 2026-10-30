// Y2: does the oracle's Chrome fill yahoo's feed at 1280x2400 with no scroll?
// usage: node tools/parity_oracle/y2_tall.mjs <url> <seconds> <png>
import { chromium } from 'playwright';
import { getDeterministicLaunchOptions } from './deterministic.mjs';

const PRODUCT_UA =
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15 HiWave/1.0';
const [url, seconds, png] = process.argv.slice(2);
const browser = await chromium.launch(getDeterministicLaunchOptions());
const context = await browser.newContext({ viewport: { width: 1280, height: 2400 }, userAgent: PRODUCT_UA });
const page = await context.newPage();
await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
await page.waitForTimeout(Number(seconds) * 1000);
const shape = await page.evaluate(() => {
  const list = document.querySelector('#strm ul');
  const items = list ? [...list.children] : [];
  return {
    items: items.length,
    withImage: items.filter((li) => li.querySelector('img')).length,
    withLink: items.filter((li) => li.querySelector('a[href]')).length,
    height: document.documentElement.scrollHeight,
  };
});
console.log(JSON.stringify(shape));
await page.screenshot({ path: png });
await browser.close();
