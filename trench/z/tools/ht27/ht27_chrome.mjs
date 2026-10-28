// ht27_chrome.mjs <url> <out.png> <rects.json> (scratch, not committed)
// Pinned Chrome frame of a live URL at 1280x800 plus the border boxes of the
// first-screen elements (tag, id, class, rect) for a region-by-region compare.
import { chromium } from 'playwright';
import { writeFileSync } from 'fs';
import { createDeterministicContext, getDeterministicLaunchOptions } from './deterministic.mjs';

const [url, out, rectsOut] = process.argv.slice(2);
const browser = await chromium.launch(getDeterministicLaunchOptions());
try {
  const context = await createDeterministicContext(browser, 1280, 800);
  const page = await context.newPage();
  try {
    await page.goto(url, { waitUntil: 'load', timeout: 60000 });
  } catch (e) {
    console.log('goto:', String(e.message).slice(0, 200));
  }
  await page.waitForTimeout(6000);
  await page.screenshot({ path: out, type: 'png', fullPage: false });
  const rects = await page.evaluate(() => {
    const res = [];
    for (const el of document.querySelectorAll('body *')) {
      const r = el.getBoundingClientRect();
      if (r.width < 1 || r.height < 1 || r.top > 1600) continue;
      const cs = getComputedStyle(el);
      res.push({
        tag: el.tagName.toLowerCase(), id: el.id || '', cls: (el.getAttribute('class') || '').slice(0, 80),
        x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height),
        display: cs.display, pos: cs.position,
      });
    }
    return { version: navigator.userAgent, docH: document.documentElement.scrollHeight, rects: res };
  });
  rects.browser = browser.version();
  writeFileSync(rectsOut, JSON.stringify(rects));
  console.log('chrome', browser.version(), 'docH', rects.docH, 'n', rects.rects.length);
} finally {
  await browser.close();
}
