// CH2.E17 oracle: <style media> and StyleSheet.disabled in Chromium (pinned oracle).
import { chromium } from '../tools/parity_oracle/node_modules/playwright/index.mjs';
const b = await chromium.launch();
console.log('chromium', b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
const base = 'body{margin:0} #t{width:10px}';
const cases = [
  ['media_print', '<style>' + base + '</style><style media="print">#t{width:20px}</style><div id=t></div>', ''],
  ['media_screen', '<style>' + base + '</style><style media="screen">#t{width:20px}</style><div id=t></div>', ''],
  ['media_all', '<style>' + base + '</style><style media="all">#t{width:20px}</style><div id=t></div>', ''],
  ['media_empty', '<style>' + base + '</style><style media="">#t{width:20px}</style><div id=t></div>', ''],
  ['media_minw_match', '<style>' + base + '</style><style media="(min-width: 700px)">#t{width:20px}</style><div id=t></div>', ''],
  ['media_minw_nomatch', '<style>' + base + '</style><style media="(min-width: 900px)">#t{width:20px}</style><div id=t></div>', ''],
  ['media_list_print_screen', '<style>' + base + '</style><style media="print, screen">#t{width:20px}</style><div id=t></div>', ''],
  ['media_invalid', '<style>' + base + '</style><style media="foo bar">#t{width:20px}</style><div id=t></div>', ''],
  ['media_unknown_type', '<style>' + base + '</style><style media="tv">#t{width:20px}</style><div id=t></div>', ''],
  ['media_SCREEN_upper', '<style>' + base + '</style><style media="SCREEN">#t{width:20px}</style><div id=t></div>', ''],
  ['media_not_print', '<style>' + base + '</style><style media="not print">#t{width:20px}</style><div id=t></div>', ''],
  ['media_inner_rule', '<style>' + base + '</style><style media="print">@media screen { #t{width:20px} }</style><div id=t></div>', ''],
  ['media_set_by_script', '<style>' + base + '</style><style id=s>#t{width:20px}</style><div id=t></div>',
    'document.getElementById("s").setAttribute("media","print")'],
  ['media_removed_by_script', '<style>' + base + '</style><style id=s media=print>#t{width:20px}</style><div id=t></div>',
    'document.getElementById("s").removeAttribute("media")'],
  ['media_resize_flip', '<style>' + base + '</style><style media="(max-width: 500px)">#t{width:20px}</style><div id=t></div>', 'RESIZE'],
  ['disabled_true', '<style>' + base + '</style><style id=s>#t{width:20px}</style><div id=t></div>',
    'document.getElementById("s").sheet.disabled = true'],
  ['disabled_via_styleSheets', '<style>' + base + '</style><style id=s>#t{width:20px}</style><div id=t></div>',
    'document.styleSheets[1].disabled = true'],
  ['disabled_then_enabled', '<style>' + base + '</style><style id=s>#t{width:20px}</style><div id=t></div>',
    'var s=document.getElementById("s").sheet; s.disabled = true; document.body.offsetWidth; s.disabled = false'],
  ['disabled_then_text_change', '<style>' + base + '</style><style id=s>#t{width:20px}</style><div id=t></div>',
    'var e=document.getElementById("s"); e.sheet.disabled = true; e.textContent = "#t{width:30px}"'],
  ['disabled_then_append_text', '<style>' + base + '</style><style id=s>#t{width:20px}</style><div id=t></div>',
    'var e=document.getElementById("s"); e.sheet.disabled = true; e.appendChild(document.createTextNode("#t{height:5px}"))'],
  ['disabled_then_insertRule', '<style>' + base + '</style><style id=s>#t{width:20px}</style><div id=t></div>',
    'var e=document.getElementById("s"); e.sheet.disabled = true; e.sheet.insertRule("#t{height:5px}", 1)'],
  ['disabled_then_reinsert', '<style>' + base + '</style><style id=s>#t{width:20px}</style><div id=t></div>',
    'var e=document.getElementById("s"); e.sheet.disabled = true; e.remove(); document.head.appendChild(e)'],
  ['disabled_first_sheet', '<style id=s>' + base + ' #t{height:7px}</style><style>#t{width:20px}</style><div id=t></div>',
    'document.getElementById("s").sheet.disabled = true'],
  ['disabled_attr_on_style', '<style>' + base + '</style><style id=s disabled>#t{width:20px}</style><div id=t></div>', ''],
  ['media_print_sheet_rules_visible', '<style>' + base + '</style><style id=s media=print>#t{width:20px}</style><div id=t></div>', 'RULES'],
];
for (const [name, html, script] of cases) {
  await p.setViewportSize({ width: 800, height: 600 });
  await p.setContent(html);
  let extra = '';
  if (script === 'RESIZE') {
    const before = await p.evaluate(() => getComputedStyle(document.getElementById('t')).width);
    await p.setViewportSize({ width: 400, height: 600 });
    extra = ' before_resize=' + before;
  } else if (script === 'RULES') {
    extra = ' ' + await p.evaluate(() => {
      const s = document.getElementById('s').sheet;
      return 'cssRules=' + s.cssRules.length + ' mediaText=' + s.media.mediaText + ' disabled=' + s.disabled;
    });
  } else if (script) {
    await p.evaluate(script);
  }
  const out = await p.evaluate(() => {
    const t = document.getElementById('t');
    const s = document.getElementById('s');
    const cs = getComputedStyle(t);
    return 'width=' + cs.width + ' height=' + cs.height + (s && s.sheet ? ' disabled=' + s.sheet.disabled : '') +
      ' sheets=' + document.styleSheets.length;
  });
  console.log(name, out + extra);
}
await b.close();
