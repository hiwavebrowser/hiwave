"""Fetch a page once with the app's UA; served.html as sent, static.html with
script bodies emptied (the elements stay, nothing runs in either engine)."""
import gzip, pathlib, re, sys, urllib.request

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 '
      '(KHTML, like Gecko) Version/17.4 Safari/605.1.15 HiWave/1.0')
S = pathlib.Path(__file__).parent
req = urllib.request.Request(sys.argv[1], headers={
    'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9', 'Accept-Encoding': 'gzip'})
r = urllib.request.urlopen(req, timeout=30)
b = r.read()
if r.headers.get('Content-Encoding') == 'gzip':
    b = gzip.decompress(b)
t = b.decode('utf-8', 'replace')
(S / 'served.html').write_text(t)
static = re.sub(r'(<script\b)([^>]*)(>)(.*?)(</script\s*>)',
                lambda m: m[1] + ' type="x-off"' + re.sub(r'\b(src|type|async|defer|nonce)\s*=\s*("[^"]*"|\'[^\']*\'|[^\s>]+)', '', m[2]) + m[3] + m[5],
                t, flags=re.S | re.I)
(S / 'static.html').write_text(static)
print(r.status, len(t), len(static), 'scripts', len(re.findall(r'<script\b', t, re.I)),
      'noscript', len(re.findall(r'<noscript\b', t, re.I)), 'template', len(re.findall(r'<template\b', t, re.I)),
      'comments', len(re.findall(r'<!--', static)))
