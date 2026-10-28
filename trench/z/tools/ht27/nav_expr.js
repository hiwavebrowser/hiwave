(() => {
  const root = document.querySelector('#globalnav') || document.querySelector('nav');
  const out = [];
  const walk = (el, d) => {
    if (d > 9 || out.length > 160) return;
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    out.push('  '.repeat(d) + el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') +
      (el.getAttribute('class') ? '.' + el.getAttribute('class').trim().split(/\s+/).join('.') : '') +
      ' ' + cs.display + ' ' + cs.position + ' [' + [r.x, r.y, r.width, r.height].map(Math.round) + ']' +
      ' bg=' + cs.backgroundColor + ' vis=' + cs.visibility + ' op=' + cs.opacity);
    for (const c of el.children) walk(c, d + 1);
  };
  if (root) { let p = root.parentElement, chain = []; while (p) { chain.push(p.tagName.toLowerCase() + (p.id ? '#' + p.id : '') + ' ' + getComputedStyle(p).display); p = p.parentElement; } out.push('chain: ' + chain.join(' < ')); walk(root, 0); }
  return out.join('\n');
})()
