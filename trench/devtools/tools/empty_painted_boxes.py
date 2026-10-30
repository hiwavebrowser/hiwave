"""The boxes R11 counts in a dump: size and colour per band, no names."""
import collections, json, sys
d = json.load(open(sys.argv[1]))
vh = d["page"]["viewport"][1]
sy = d["page"]["scroll"][1]
out = collections.defaultdict(collections.Counter)
for e in d["elements"]:
    b = e["box"]["border_box"] if e["box"].get("border_box") else None
    if not b or e["box"].get("has_box") is not True:
        continue
    t, s = e["tree"], e["style"]
    if t.get("text_length") != 0 or t.get("child_count") != 0:
        continue
    if s.get("visibility") == "hidden" or s.get("opacity") in ("0",):
        continue
    w, h = b["w"], b["h"]
    if min(w, h) < 4 or max(w, h) < 16:
        continue
    tag = e["identity"]["tag"]
    if tag in ("img","svg","picture","video","canvas","input","button","select","textarea","hr","iframe","embed","object","meter","progress"):
        continue
    img = s.get("background-image") or "none"
    col = s.get("background-color") or ""
    colour = bool(col) and not (col.startswith("rgba(") and col.endswith(", 0)"))
    if "url(" in img or not (colour or img != "none"):
        continue
    band = int((b["y"] + sy) // vh)
    out[band][f"{tag} {w:.0f}x{h:.0f} {col} {'grad' if img != 'none' else ''} {s.get('position')}"] += 1
for band in sorted(out):
    print("band", band, sum(out[band].values()))
    for k, n in out[band].most_common(12):
        print("  ", n, k)
