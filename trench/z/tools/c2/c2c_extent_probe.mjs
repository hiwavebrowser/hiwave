// C2(c): scroll extents of padded and nested scrollers, and of a padded box that is not one, in Chromium.
// usage: node c2c_extent_probe.mjs <dir holding node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const html = `<!doctype html><style>body{margin:0}
#out{overflow:auto;width:300px;height:200px}
#gap{height:400px}
#in{overflow:auto;width:200px;height:100px;border:5px solid #000;padding:7px}
#in-gap{height:300px;width:600px}#t{height:20px;width:30px;margin-left:400px}#after{height:300px}
#vis{width:100px;height:50px;padding:7px}#vis-c{height:100px;width:200px}
#hid{overflow:hidden;width:100px;height:50px;padding:7px}#hid-c{height:100px;width:200px}
#clip{overflow:clip;width:100px;height:50px;padding:7px}#clip-c{height:100px;width:200px}
#o2{overflow:auto;width:100px;height:50px}
#vis2{height:20px}#vis2-c{height:100px}
#o3{overflow:auto;width:100px;height:50px}
#hid3{overflow:hidden;height:20px}#hid3-c{height:100px}
#o4{overflow:auto;width:100px;height:50px}
#clip4{overflow:clip;height:20px}#clip4-c{height:100px}
#o5{overflow:auto;width:100px;height:50px;position:relative}
#st5{overflow:auto;height:20px}#ab5{position:absolute;top:200px;height:10px;width:10px}
#short{overflow:auto;width:100px;height:100px;padding:7px}#short-c{height:20px}
#mb{overflow:auto;width:100px;height:50px}#mb-c{height:100px;margin-bottom:9px}
</style><body>
<div id=out><div id=gap></div><div id=in><div id=in-gap></div><div id=t></div><div id=after></div></div></div>
<div id=vis><div id=vis-c></div></div>
<div id=hid><div id=hid-c></div></div>
<div id=clip><div id=clip-c></div></div>
<div id=o2><div id=vis2><div id=vis2-c></div></div></div>
<div id=o3><div id=hid3><div id=hid3-c></div></div></div>
<div id=o4><div id=clip4><div id=clip4-c></div></div></div>
<div id=o5><div id=st5><div id=ab5></div></div></div>
<div id=short><div id=short-c></div></div>
<div id=mb><div id=mb-c></div></div>
</body>`;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
await p.setContent(html);
console.log(b.version());
for (const i of ['out', 'in', 'vis', 'hid', 'clip', 'o2', 'o3', 'o4', 'o5', 'short', 'mb'])
  console.log(i, await p.evaluate(`(function(){var e=document.getElementById(${JSON.stringify(i)});return [e.scrollWidth,e.scrollHeight,e.clientWidth,e.clientHeight].join(' ')})()`));
await b.close();
