// ht27_rules.mjs <url> <out.json> <css selector>... (scratch, not committed)
// For each selector's first element in pinned Chrome: every style rule that
// matches it, with the chain of enclosing at-rule conditions and whether that
// chain currently applies, plus its computed values for the declared props.
import { chromium } from 'playwright';
import { writeFileSync } from 'fs';
import { createDeterministicContext, getDeterministicLaunchOptions } from './deterministic.mjs';

const [url, out, ...sels] = process.argv.slice(2);
const browser = await chromium.launch(getDeterministicLaunchOptions());
try {
  const context = await createDeterministicContext(browser, 1280, 800);
  const page = await context.newPage();
  try { await page.goto(url, { waitUntil: 'load', timeout: 60000 }); } catch (e) { console.log('goto', e.message.slice(0, 120)); }
  await page.waitForTimeout(5000);
  const res = await page.evaluate((sels) => {
    const outp = {};
    for (const sel of sels) {
      const el = document.querySelector(sel);
      if (!el) { outp[sel] = 'none'; continue; }
      const rules = [];
      const visit = (list, chain) => {
        for (const r of list) {
          if (r.cssRules && !(r instanceof CSSStyleRule)) {
            const cond = r.conditionText || r.media?.mediaText || r.name || r.constructor.name;
            let applies = null;
            if (r instanceof CSSMediaRule) applies = matchMedia(r.media.mediaText).matches;
            visit(r.cssRules, chain.concat([{ kind: r.constructor.name, cond, applies }]));
          } else if (r instanceof CSSStyleRule) {
            let m = false;
            try { m = el.matches(r.selectorText); } catch (e) {}
            if (m) rules.push({ sel: r.selectorText.slice(0, 120), chain, decl: r.style.cssText.slice(0, 4000) });
            if (r.cssRules && r.cssRules.length) visit(r.cssRules, chain.concat([{ kind: 'nest', cond: r.selectorText }]));
          }
        }
      };
      for (const s of document.styleSheets) { try { visit(s.cssRules, []); } catch (e) {} }
      const cs = getComputedStyle(el); const custom = {}; for (const r of rules) for (const m of r.decl.matchAll(/(--[\w-]+)\s*:/g)) custom[m[1]] = cs.getPropertyValue(m[1]);
      outp[sel] = { rules, computed: { display: cs.display, flexDirection: cs.flexDirection, padding: cs.padding, height: cs.height, width: cs.width, minHeight: cs.minHeight, backgroundImage: cs.backgroundImage.slice(0, 200), containerType: cs.containerType, custom } };
    }
    return outp;
  }, sels);
  writeFileSync(out, JSON.stringify(res, null, 1));
} finally {
  await browser.close();
}
