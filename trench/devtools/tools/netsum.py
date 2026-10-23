"""netsum.py <event log jsonl>: requests by outcome; every failure as origin+path with stage, reason, blocked_by."""
import collections
import json
import sys
import urllib.parse

reqs, outcome = {}, {}
for line in open(sys.argv[1]):
    r = json.loads(line)
    kind = r.get("kind") or r.get("type")
    if kind == "request":
        reqs[r["id"]] = r
    elif kind in ("response", "failure"):
        outcome[r["id"]] = r

def short(url):
    u = urllib.parse.urlsplit(url)
    return u.scheme + "://" + u.netloc + u.path

counts = collections.Counter()
for i, q in reqs.items():
    o = outcome.get(i)
    if o is None:
        counts["open"] += 1
    elif "status" in o and o.get("kind", o.get("type")) == "response":
        counts["response %s" % (o["status"] // 100 * 100)] += 1
    else:
        counts["failure " + str(o.get("stage"))] += 1
print("requests", len(reqs), dict(counts))
by_init = collections.Counter((q.get("resource_type"), q.get("initiator")) for q in reqs.values())
print("by type/initiator", dict(by_init))
print("---")
for i, q in sorted(reqs.items()):
    o = outcome.get(i)
    if o is None or o.get("kind", o.get("type")) != "failure":
        continue
    print(i, q.get("resource_type"), q.get("initiator"), short(q["url"]), "|", o.get("stage"), o.get("reason"), "|", json.dumps(o.get("blocked_by")))
