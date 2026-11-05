// CH2.B7 reduced pages. Each reads #c (and #n if present): top+height.
const KIDS = '<div style="height:40px"></div><div style="height:44px"></div>';
const B = '<style>body{margin:0}</style>';
const v = (style, kids = KIDS) => `${B}<div id=c style="${style}">${kids}</div>`;
const COL0 = 'display:flex;flex-direction:column;height:0';
export const variants = [
  ['col_h0', v(COL0)],
  ['col_h10', v('display:flex;flex-direction:column;height:10px')],
  ['col_h0_ovh', v(COL0 + ';overflow:hidden')],
  ['row_h0', v('display:flex;height:0')],
  ['col_maxh0', v('display:flex;flex-direction:column;max-height:0')],
  ['col_maxh20', v('display:flex;flex-direction:column;max-height:20px')],
  ['col_maxh20_minh30', v('display:flex;flex-direction:column;max-height:20px;min-height:30px')],
  ['col_maxh20_bb_pad', v('display:flex;flex-direction:column;max-height:20px;padding:5px;box-sizing:border-box')],
  ['col_maxh20_ovauto', v('display:flex;flex-direction:column;max-height:20px;overflow:auto')],
  ['col_maxh20_textkids', v('display:flex;flex-direction:column;max-height:20px', '<div>a</div><div>b</div>')],
  ['block_h0', v('height:0')],
  ['block_maxh20_minh30', v('max-height:20px;min-height:30px')],
  ['block_h50_maxh20_minh30', v('height:50px;max-height:20px;min-height:30px')],
  ['col_h0_pad', v(COL0 + ';padding:5px')],
  ['col_h0_bb_pad', v(COL0 + ';padding:5px;box-sizing:border-box')],
  ['col_h0_text', v(COL0, 'hello<br>world')],
  ['col_h0_inflow', `${B}<div id=p><div id=c style="${COL0}">${KIDS}</div><div id=n style="height:5px"></div></div>`],
  ['col_h0_in_colflex_noshrink', `${B}<div id=p style="display:flex;flex-direction:column;height:300px"><div id=c style="${COL0};flex-shrink:0">${KIDS}</div><div id=n style="flex:1"></div></div>`],
  ['col_h0_in_colflex', `${B}<div id=p style="display:flex;flex-direction:column;height:300px"><div id=c style="${COL0}">${KIDS}</div><div id=n style="flex:1"></div></div>`],
  ['col_h0_in_rowflex', `${B}<div id=p style="display:flex;height:300px;align-items:flex-start"><div id=c style="${COL0}">${KIDS}</div></div>`],
  ['col_h0_pct', `${B}<div id=p style="height:0"><div id=c style="display:flex;flex-direction:column;height:100%">${KIDS}</div></div>`],
];
export const JS = `(function(){var c=document.getElementById('c');function r(e){var b=e.getBoundingClientRect();return Math.round(b.top)+'+'+Math.round(b.height)}
var n=document.getElementById('n');return 'c='+r(c)+' kids='+Array.prototype.map.call(c.children,r).join(',')+(n?' n='+r(n):'');})()`;
