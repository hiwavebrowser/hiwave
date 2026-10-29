"""rd1_probe.py <binary>: hand-made SVG fixtures for RD1 (reddit interstitial logo
paints black). Each page is one 200x200 inline SVG inside `.logo svg{fill:currentColor}`,
with a shape whose fill comes from a class rule in a <style> in <head>. Prints the
colour at the shape's centre. Expected (Chrome): the class rule's colour."""
import pathlib, subprocess, sys

binary = sys.argv[1]
d = pathlib.Path(__file__).with_name('rd1_fx')
d.mkdir(exist_ok=True)

HEAD = """<!doctype html><html><head><style>
body{margin:0} .logo svg{fill:currentColor;width:200px;height:200px;display:block}
%s
</style></head><body><div class="logo"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
<defs><radialGradient id="g" cx="100" cy="100" r="80" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="#00ff00"></stop><stop offset="1" stop-color="#00ff00"></stop></radialGradient>
<radialGradient id="g2" xlink:href="#g" xmlns:xlink="http://www.w3.org/1999/xlink" cx="100"></radialGradient></defs>
%s
</svg></div></body></html>"""

CASES = {
    'plain_class': ('.a{fill:#ff4500}', '<rect class="a" x="0" y="0" width="200" height="200"></rect>', (255, 69, 0)),
    'plain_attr': ('', '<rect fill="#ff4500" x="0" y="0" width="200" height="200"></rect>', (255, 69, 0)),
    'path_class': ('.a{fill:#ff4500}', '<path class="a" d="m0,0h200v200h-200Z"></path>', (255, 69, 0)),
    'class_stroke_width_list': ('.a{fill:#ff4500}.a,.b{stroke-width:0}', '<rect class="a" x="0" y="0" width="200" height="200"></rect>', (255, 69, 0)),
    'url_fallback_class': ('.a{fill:url(#g) white}', '<rect class="a" x="0" y="0" width="200" height="200"></rect>', (0, 255, 0)),
    'url_class': ('.a{fill:url(#g)}', '<rect class="a" x="0" y="0" width="200" height="200"></rect>', (0, 255, 0)),
    'url_href_stops': ('.a{fill:url(#g2) white}', '<rect class="a" x="0" y="0" width="200" height="200"></rect>', (0, 255, 0)),
    'url_missing_fallback': ('.a{fill:url(#nope) #ff4500}', '<rect class="a" x="0" y="0" width="200" height="200"></rect>', (255, 69, 0)),
}

for name, (css, body, want) in CASES.items():
    page = d / (name + '.html')
    page.write_text(HEAD % (css, body))
    ppm = d / (name + '.ppm')
    r = subprocess.run([binary, '--html-file', str(page), '--width', '400', '--height', '300', '--dump-frame', str(ppm)],
                       capture_output=True, text=True)
    if r.returncode or not ppm.exists():
        print(name, 'capture failed', r.returncode, r.stderr[-300:])
        continue
    data = ppm.read_bytes()
    magic, w, h, rest = data.split(maxsplit=3)
    w = int(w)
    px = rest[len(rest.split(maxsplit=1)[0]) + 1:]
    i = (100 * w + 100) * 3
    got = tuple(px[i:i + 3])
    ok = all(abs(a - b) <= 8 for a, b in zip(got, want))
    print('%-26s want %-14s got %-14s %s' % (name, want, got, 'ok' if ok else 'WRONG'))
