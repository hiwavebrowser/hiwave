"""bbox.py a.ppm b.ppm: bounding box and count of differing pixels."""
import sys


def ppm(path):
    data = open(path, "rb").read()
    fields, i = [], 0
    while len(fields) < 4:
        while data[i] in b" \t\r\n":
            i += 1
        j = i
        while data[j] not in b" \t\r\n":
            j += 1
        fields.append(data[i:j])
        i = j
    i += 1
    w, h = int(fields[1]), int(fields[2])
    return w, h, data[i:]


wa, ha, a = ppm(sys.argv[1])
wb, hb, b = ppm(sys.argv[2])
print("sizes", wa, ha, wb, hb)
xs, ys, n = [], [], 0
for y in range(min(ha, hb)):
    ra, rb = a[y * wa * 3:(y + 1) * wa * 3], b[y * wb * 3:(y + 1) * wb * 3]
    if ra == rb:
        continue
    for x in range(min(wa, wb)):
        if ra[x * 3:x * 3 + 3] != rb[x * 3:x * 3 + 3]:
            n += 1
            xs.append(x)
            ys.append(y)
if n:
    print("diff", n, "bbox", min(xs), min(ys), max(xs), max(ys))
else:
    print("identical")
