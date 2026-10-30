// SV1: what Chromium's parser does with SVG name case. Hand-made page, no site.
// Run from <worktree>/tools/parity_oracle via `node <this file> <node_modules>`.
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const page_html = `<!DOCTYPE html><body>
<svg id=s viewbox="0 0 1 1" PRESERVEASPECTRATIO=none data-k=v><lineargradient id=g gradientunits=userSpaceOnUse></lineargradient>
<clippath id=c></clippath><g id=g2></g><foreignobject id=fo><div id=h viewbox=1></div><svg id=inner></svg></foreignobject>
<title id=t><b id=tb></b></title><desc id=de><i id=di></i></desc><a id=a1 xlink:href="#x"></a><font id=f1></font></svg>
<svg id=b1><div id=br></div></svg><svg id=b2><font id=f2 color=red></font></svg>
<math id=m definitionurl=x><mi id=mi></mi></math><div id=plain viewbox=1></div><template id=tp><svg id=ts viewbox="0 0 2 2"></svg></template>
<table id=tb1><svg id=fost viewbox="0 0 3 3"><path id=fp></path></svg></table>
</body>`;
const expr = `(() => {
  const d = (id) => { const e = document.getElementById(id); if (!e) return id + ':missing';
    return [id, e.tagName, e.localName, e.namespaceURI && e.namespaceURI.split('/').pop(), e.getAttributeNames().join(','), e.parentNode && e.parentNode.nodeName].join(' '); };
  const out = {};
  out.parsed = ['s','g','c','g2','fo','h','inner','t','tb','de','di','a1','f1','b1','br','b2','f2','m','mi','plain','fost','fp'].map(d);
  const s = document.getElementById('s');
  const ts = document.getElementById('tp').content.firstChild;
  out.template = [ts.tagName, ts.namespaceURI.split('/').pop(), ts.getAttributeNames().join()];
  out.ifaces = [s instanceof SVGSVGElement, s instanceof SVGElement, s instanceof HTMLElement, document.getElementById('g') instanceof SVGElement];
  out.apis = ['dataset','tabIndex','style','className','focus','blur','click','innerText','offsetWidth','onclick','hidden','title'].map(k => k + ':' + (typeof s[k]));
  out.dataset = s.dataset.k;
  out.get = [s.getAttribute('viewBox'), s.getAttribute('viewbox'), s.hasAttribute('VIEWBOX')];
  s.setAttribute('preserveAspectRatio', 'xMinYMin'); s.setAttribute('FooBar', '1');
  out.set = s.getAttributeNames().join();
  const div = document.createElement('div');
  div.innerHTML = '<svg viewbox="0 0 1 1"><lineargradient gradientunits=x></lineargradient></svg>';
  out.divInner = div.innerHTML;
  out.divTag = div.firstChild.tagName + ' ' + div.firstChild.firstChild.tagName;
  const g2 = document.getElementById('g2');
  g2.innerHTML = '<clippath clippathunits=x><path></path></clippath><div></div>';
  out.svgInner = g2.innerHTML; out.svgInnerTag = g2.firstChild.tagName + ' ' + g2.firstChild.namespaceURI.split('/').pop();
  const fo = document.getElementById('fo'); const nf = document.createElement('div'); fo.appendChild(nf);
  const fo2 = fo; fo2.innerHTML = '<p viewbox=1></p><lineargradient></lineargradient>';
  out.foInner = fo2.innerHTML + ' ' + fo2.firstChild.namespaceURI.split('/').pop() + ' ' + fo2.lastChild.namespaceURI.split('/').pop();
  out.qs = ['lineargradient','linearGradient','svg lineargradient','[viewbox]','[viewBox]','svg[viewBox]'].map(q => q + ':' + !!document.querySelector(q));
  out.byTag = [document.getElementsByTagName('lineargradient').length, document.getElementsByTagName('linearGradient').length];
  return out;
})()`;
const b = await chromium.launch();
const p = await b.newPage();
await p.setContent(page_html);
console.log(b.version());
console.log(JSON.stringify(await p.evaluate(expr), null, 1));
await b.close();
