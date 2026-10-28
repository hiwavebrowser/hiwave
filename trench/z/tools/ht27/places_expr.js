[].map.call(document.querySelectorAll('[id]'), function (e) { var r = e.getBoundingClientRect(); return e.id + ':' + getComputedStyle(e).display + ',' + r.x + ',' + r.y; }).join(' ')
