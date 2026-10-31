['w', 'f', 'q', 'n', 'd'].map(function (i) { return i + '=' + getComputedStyle(document.getElementById(i)).content; }).join(' ')
