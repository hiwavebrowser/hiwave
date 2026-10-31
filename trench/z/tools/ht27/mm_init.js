// Logs every matchMedia query (and its answer) and every data-issplitform
// write with a short stack, from document start. Read back as window.__mm.
(function () {
  window.__mm = [];
  var mm = window.matchMedia;
  window.matchMedia = function (q) {
    var r = mm.call(window, q);
    window.__mm.push('mm ' + q + ' = ' + r.matches);
    return r;
  };
  var sa = Element.prototype.setAttribute;
  Element.prototype.setAttribute = function (n, v) {
    if (String(n).toLowerCase() === 'data-issplitform') {
      window.__mm.push('set ' + n + '=' + v + ' @ ' + String(new Error().stack).split('\n').slice(2, 5).map(function (s) { return s.trim().slice(0, 90); }).join(' | '));
    }
    return sa.call(this, n, v);
  };
  new MutationObserver(function (list) {
    list.forEach(function (r) {
      if (r.attributeName === 'data-issplitform') window.__mm.push('mut ' + r.target.tagName + ' ' + r.oldValue + ' -> ' + r.target.getAttribute('data-issplitform'));
    });
  }).observe(document, { subtree: true, attributes: true, attributeOldValue: true, attributeFilter: ['data-issplitform'] });
})();
