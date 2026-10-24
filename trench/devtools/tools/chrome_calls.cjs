// Count a page's fetch/XHR by host in Chromium over N ms (no bodies, paths only).
// usage: node chrome_calls.cjs <url> <ms>
const { chromium } = require(process.env.ORACLE + '/node_modules/playwright');
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15 HiWave/1.0';
(async () => {
  const [url, waitMs] = [process.argv[2], Number(process.argv[3] || 25000)];
  const browser = await chromium.launch();
  const page = await browser.newPage({ userAgent: UA, viewport: { width: 1280, height: 800 } });
  const t0 = Date.now();
  const calls = [];
  page.on('request', (r) => {
    const kind = r.resourceType();
    if (kind === 'fetch' || kind === 'xhr') {
      const u = new URL(r.url());
      calls.push([Date.now() - t0, kind, u.host, u.pathname.slice(0, 60)]);
    }
  });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e.name || 'Error')));
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(waitMs);
  const height = await page.evaluate(() => document.documentElement.scrollHeight);
  const byHost = {};
  for (const c of calls) byHost[c[2]] = (byHost[c[2]] || 0) + 1;
  console.log('document height', height, 'page errors', errors.length, JSON.stringify(errors.slice(0, 5)));
  console.log('fetch/xhr by host', JSON.stringify(byHost, null, 1));
  const host = new URL(url).host;
  for (const c of calls.filter((c) => c[2] === host)) console.log(c.join('  '));
  await browser.close();
})();
