// ht27_eval.mjs <url> <js expression> (scratch, not committed): evaluate one expression in pinned Chrome after load.
import { chromium } from 'playwright';
import * as fsmod from 'fs';
const require_fs = () => fsmod;
import { createDeterministicContext, getDeterministicLaunchOptions } from './deterministic.mjs';

const [url, expr] = process.argv.slice(2);
const browser = await chromium.launch(getDeterministicLaunchOptions());
try {
  const context = await createDeterministicContext(browser, 1280, 800);
  if (process.env.HT27_UA) await context.setExtraHTTPHeaders({'user-agent': process.env.HT27_UA});
  if (process.env.HT27_INIT) await context.addInitScript({ content: require_fs().readFileSync(process.env.HT27_INIT, 'utf8') });
  const page = await context.newPage();
  if (process.env.HT27_SAVE) page.on('response', async (r) => { if (r.request().resourceType() === 'document') { try { (await import('fs')).writeFileSync(process.env.HT27_SAVE + '-' + Date.now() + '.html', await r.body()); } catch (e) {} } });
  try { await page.goto(url, { waitUntil: 'load', timeout: 60000 }); } catch (e) { console.log('goto', e.message.slice(0, 120)); }
  await page.waitForTimeout(5000);
  console.log(JSON.stringify(await page.evaluate(expr), null, 1));
} finally {
  await browser.close();
}
