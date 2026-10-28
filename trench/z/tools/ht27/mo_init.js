// Records every attribute / childList mutation from document start, in order:
// [tag, attr or 'childList', connected]. Read back as window.__mo.
(function () {
  window.__mo = [];
  var mo = new MutationObserver(function (list) {
    for (var i = 0; i < list.length; i++) {
      var r = list[i];
      var t = r.target;
      window.__mo.push([(t.tagName || '#').toLowerCase(), r.type === 'attributes' ? r.attributeName : r.type, r.type === 'attributes' && (r.attributeName === 'class' || r.attributeName === 'style') ? String(t.getAttribute(r.attributeName) || '').length : 0]);
    }
  });
  mo.observe(document, { subtree: true, attributes: true, childList: true });
})();
