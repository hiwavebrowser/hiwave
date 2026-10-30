"""nf_form.py <binary> <out prefix> : netflix.com real load (live-ms 8000, as HT27), print the hero form's
input and button boxes from --dump-layout. Out prefix must be private (renders-private)."""
import json, pathlib, subprocess, sys

b, prefix = sys.argv[1], sys.argv[2]
lay = pathlib.Path(prefix + '-layout.json')
r = subprocess.run([b, '--url', 'https://www.netflix.com/', '--width', '1280', '--height', '800', '--live-ms', '8000',
                    '--timeout-ms', '90000', '--dump-layout', str(lay), '--dump-frame', prefix + '.ppm'],
                   capture_output=True, text=True)
print('exit', r.returncode)
d = json.load(open(lay))


def walk(n, path):
    tag = (n.get('tag') or n.get('element') or n.get('node_name') or '').lower()
    r = n.get('rect') or n.get('border_box') or n.get('content_rect') or {}
    if tag in ('form', 'input', 'button') and isinstance(r, dict) and r.get('y', 9999) < 900:
        print('%-6s %s' % (tag, {k: round(v, 2) for k, v in r.items()}), '|', path[-3:])
    for c in n.get('children', []):
        walk(c, path + [tag])


walk(d['root'], [])
