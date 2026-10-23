"""netopen.py <event log jsonl>: origins of all requests, then each still-open request (origin+path, type, initiator, start ms)."""
import collections
import json
import sys
import urllib.parse

reqs, done = {}, set()
for line in open(sys.argv[1]):
    r = json.loads(line)
    if r["type"] == "request":
        reqs[r["id"]] = r
    elif r["type"] in ("response", "failure"):
        done.add(r["id"])

def split(url):
    u = urllib.parse.urlsplit(url)
    return u.scheme + "://" + u.netloc, u.path

print(dict(collections.Counter(split(q["url"])[0] for q in reqs.values())))
print("--- open")
for i, q in sorted(reqs.items()):
    if i not in done:
        o, p = split(q["url"])
        print(i, q["resource_type"], q["initiator"], o + (p if len(p) < 70 else p[:67] + "..."), "t=%d" % q["t_ms"])
