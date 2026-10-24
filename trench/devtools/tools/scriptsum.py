"""scriptsum.py <event-log.jsonl>: the T3 script lifecycle, one line per record.

Prints every `script` and `lifecycle` record in order with its stage times,
then the scripts that held window load. Query strings are already gone from
the log (Privacy), so the output can be pasted into a PR.
"""
import json
import sys


def ms(v):
    return "-" if v is None else f"{v:.0f}"


records = [json.loads(line) for line in open(sys.argv[1]) if line.strip()]
held_load = []
for r in records:
    if r["type"] == "script":
        reason = f" ({r['reason']})" if r.get("reason") else ""
        print(
            f"{r['t_ms']:>9.0f}  script {r['kind']:<8} {r['outcome']}{reason}"
            f"  q={ms(r.get('queued_ms'))} f={ms(r.get('fetch_ms'))} w={ms(r.get('waited_ms'))}"
            f" run={ms(r.get('ran_ms'))}  held={r.get('held') or '-'} ev={r.get('event') or '-'}  {r['script']}"
        )
        if r.get("held") == "load":
            held_load.append(r)
    elif r["type"] == "lifecycle":
        print(f"{r['t_ms']:>9.0f}  lifecycle {r['event']} held_by_count={r['held_by_count']}")
    elif r["type"] in ("load_finished", "navigation_commit"):
        print(f"{r['t_ms']:>9.0f}  {r['type']}")
print()
print(f"held window load: {len(held_load)}")
for r in sorted(held_load, key=lambda r: -(r.get("queued_ms") or 0) - (r.get("fetch_ms") or 0) - (r.get("waited_ms") or 0)):
    total = sum(r.get(k) or 0 for k in ("queued_ms", "fetch_ms", "waited_ms", "ran_ms"))
    print(f"  {total:>7.0f} ms  {r['kind']} {r['outcome']}  {r['script']}")
