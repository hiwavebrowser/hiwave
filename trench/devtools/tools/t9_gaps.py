#!/usr/bin/env python3
"""t9_gaps.py <run dir>...: what the T9 event logs hold beyond the report. Shapes and counts only."""
import collections
import json
import pathlib
import re
import sys


def brief(url):
    return re.sub(r"[?#].*", "", str(url or ""))[:100]


for d in map(pathlib.Path, sys.argv[1:]):
    print(f"== {d.name}")
    report = json.loads((d / "report.json").read_text())
    print("not_checked:", report["not_checked"], "scroll:", report["scroll"])
    rows = [json.loads(l) for l in (d / "events.jsonl").read_text().splitlines() if l.strip()]
    print("last event t:", rows[-1]["t_ms"])
    for r in rows:
        if r["type"] == "console" and r["level"] == "error":
            print(" console.error t", r["t_ms"], r["message"])
            for f in (r.get("stack") or "").splitlines()[:12]:
                print("   stack", brief(f.strip()))
            for f in (r.get("error_stack") or "").splitlines()[:12]:
                print("   error_stack", brief(f.strip()))
    relayouts = [r for r in rows if r["type"] == "relayout"]
    print(" relayouts:", len(relayouts), "last t", relayouts[-1]["t_ms"] if relayouts else None,
          "causes", dict(collections.Counter(str(r["cause"])[:30] for r in relayouts).most_common(6)))
    answered = {r["id"]: r for r in rows if r["type"] in ("response", "failure")}
    reqs = [r for r in rows if r["type"] == "request"]
    print(" requests", len(reqs), "open at end", sum(r["id"] not in answered for r in reqs))
    print(" types", dict(collections.Counter(r["resource_type"] for r in reqs)))
    print(" initiators", dict(collections.Counter(str(r["initiator"])[:24] for r in reqs).most_common(8)))
    statuses = collections.Counter(a.get("status") for a in answered.values() if a["type"] == "response")
    print(" statuses", dict(statuses))
    for r in reqs:
        if r["resource_type"] in ("fetch", "xhr"):
            a = answered.get(r["id"], {})
            print("  ", round(r["t_ms"]), r["resource_type"], brief(r["url"]), a.get("status"), a.get("encoded_size"))
    for r in rows:
        if r.get("outcome") not in (None, "ran"):
            print(" script", r["type"], r["outcome"], r.get("reason"), brief(r.get("script")), r.get("bytes"))
    errs = [r for r in rows if r.get("outcome") == "threw" or r["type"] == "script_error"]
    print(" threw", len(errs))
