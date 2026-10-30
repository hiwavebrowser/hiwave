// GCS1: getComputedStyle(el, pseudo) in Chromium. Hand-made page, no site.
// usage: node gcs1_probe.mjs <worktree>/tools/parity_oracle/node_modules
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const html = `<!DOCTYPE html><style>
#hidden::before{content:"md";display:none}
#shown::before{content:"bf";color:rgb(1,2,3);position:absolute;width:10px}
#shown::after{content:"af" "x"}
#shown{color:rgb(9,9,9)}
#own{content:"z";color:rgb(4,5,6)}
#none::before{content:none;color:rgb(7,8,9)}
#nocontent::before{color:rgb(7,8,9)}
#reset.a::before{content:"lower"}
#reset.a.b::before{content:attr(data-x)}
#reseturl::before{content:"lower"}
#reseturl.b::before{content:url(data:image/gif;base64,R0lGODlhAQABAAAAACw=)}
#counter::before{content:"lower"}
#counter.b::before{content:counter(c)}
#mix::before{content:"a" attr(data-x) "b"}
</style><body>
<div id=hidden></div><div id=shown></div><div id=own></div><div id=none></div><div id=nocontent></div><div id=plain></div>
<div id=reset class="a b" data-x=val></div><div id=reseturl class=b></div><div id=counter class=b></div><div id=mix data-x=val></div>
</body>`;
const expr = `(() => {
  const q = (id, p) => { const c = getComputedStyle(document.getElementById(id), p);
    return [id, String(p), 'content=' + c.content, 'display=' + c.display, 'color=' + c.color, 'pos=' + c.position, 'w=' + c.width, 'len=' + (c.length > 0)].join(' '); };
  const out = [];
  for (const [id, p] of [['hidden','::before'],['hidden',':before'],['hidden','::after'],['shown','::before'],['shown','::after'],['shown',':after'],
    ['shown','::BEFORE'],['shown','before'],['shown','::foo'],['shown','::first-line'],['shown',''],['shown',null],['shown',undefined],['own',undefined],['own','::before'],
    ['none','::before'],['nocontent','::before'],['plain','::before'],['plain',undefined],['reset','::before'],['reseturl','::before'],['counter','::before'],['mix','::before']]) out.push(q(id, p));
  return out;
})()`;
const b = await chromium.launch();
const p = await b.newPage();
await p.setContent(html);
console.log(b.version());
console.log((await p.evaluate(expr)).join('\n'));
await b.close();
