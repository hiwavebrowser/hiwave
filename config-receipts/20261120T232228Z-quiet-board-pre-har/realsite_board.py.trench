#!/usr/bin/env python3
"""Real-site board: live top sites, RustKit vs pinned Chrome.

Scores each site in websuite/realsite-top20.json on three checks (see
trench/BASELINE-realsite.md; the definitions live there, this file only
implements them):

  LOADS        parity-capture --url exits ok within 30s with a frame that is
               not blank (>= 2% of pixels differ from the frame's dominant
               colour).
  READABLE     >= 80% of the distinct words Chrome shows in the first
               viewport appear in RustKit's first-viewport text runs.
  LOOKS RIGHT  first-viewport pixel diff vs Chrome <= 15%. If Chrome vs
               Chrome for the site already exceeds 15% in the same run, the
               check is scored "unstable" (0 points, reported separately).

Writes trench/realsite/runs/<ts>/<site>.json and summary.json, prints a
one-screen table. Exits 0 even when sites fail; non-zero only when the
instrument itself is broken (no Chrome, no parity-capture, no node).

  python3 scripts/realsite_board.py                 # all sites
  python3 scripts/realsite_board.py --site google   # one site (repeatable)
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SITES_FILE = REPO / "websuite" / "realsite-top20.json"
# --board wide: the 80-site list, scored as its OWN number (out of 240) with its
# own trend file. It never feeds the 60-point board the trench is measured on.
BOARDS = {
    "top20": (SITES_FILE, "trend.csv"),
    "wide": (REPO / "websuite" / "realsite-top80.json", "trend-wide.csv"),
    # --board top25 (Pete, 2026-10-06): the top 20 plus five more, out of 75,
    # own trend file. A full run also writes the top-20 subset to trend.csv as
    # the /60 board, so one run keeps both numbers.
    "top25": (REPO / "websuite" / "realsite-top25.json", "trend-top25.csv"),
    # --board categories (Plan Z week 2, B0): 30 sites, six categories of five,
    # its own number (/90) and its own trend file. The manifest's "blocked" row
    # is not loaded here; it is reported beside the board, never scored into it.
    "categories": (REPO / "websuite" / "realsite-categories.json", "trend-categories.csv"),
}
ORACLE = REPO / "tools" / "parity_oracle" / "realsite.mjs"
DEFAULT_CHROME = (
    Path.home()
    / "Repos/hiwave/hiwave-macos/.browsers/chrome/mac_arm-148.0.7778.216"
    / "chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
)
PINNED_CHROME_VERSION = "148.0.7778.216"

LOAD_TIMEOUT_MS = 30000
BLANK_MIN_FRACTION = 0.02
READABLE_MIN = 0.80
LOOKS_RIGHT_MAX = 15.0
CHROME_SETTLE_MS = 5000

WORD_RE = re.compile(r"\w+", re.UNICODE)


def words(text):
    return {w.casefold() for w in WORD_RE.findall(text or "")}


def run_json(cmd, timeout, env=None, stderr_path=None):
    """Run a command that prints one JSON object on its last stdout line.
    With stderr_path, its stderr (the engine's log) is kept there."""
    try:
        p = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, env=env, cwd=REPO
        )
    except subprocess.TimeoutExpired as e:
        if stderr_path and e.stderr:
            Path(stderr_path).write_bytes(e.stderr if isinstance(e.stderr, bytes)
                                          else e.stderr.encode())
        return None, "killed after %ds" % timeout, None
    if stderr_path:
        Path(stderr_path).write_text(p.stderr or "")
    lines = [l for l in p.stdout.splitlines() if l.strip().startswith("{")]
    if not lines:
        tail = (p.stderr or p.stdout).strip().splitlines()[-3:]
        return None, "exit %d, no JSON: %s" % (p.returncode, " | ".join(tail)), p.returncode
    try:
        return json.loads(lines[-1]), None, p.returncode
    except json.JSONDecodeError as e:
        return None, "bad JSON: %s" % e, p.returncode


def load_ppm(path):
    """P6 PPM -> (width, height, bytes RGB)."""
    data = Path(path).read_bytes()
    fields, idx = [], 0
    while len(fields) < 4:
        while data[idx : idx + 1].isspace():
            idx += 1
        if data[idx : idx + 1] == b"#":
            while data[idx : idx + 1] not in (b"\n", b""):
                idx += 1
            continue
        start = idx
        while not data[idx : idx + 1].isspace():
            idx += 1
        fields.append(data[start:idx])
    idx += 1
    if fields[0] != b"P6":
        raise ValueError("not a P6 PPM")
    w, h = int(fields[1]), int(fields[2])
    return w, h, data[idx : idx + w * h * 3]


def non_background_fraction(ppm_path):
    """Fraction of pixels that differ (any channel > 8) from the dominant colour."""
    import numpy as np

    w, h, rgb = load_ppm(ppm_path)
    px = np.frombuffer(rgb, dtype=np.uint8).reshape(h * w, 3)
    packed = (px[:, 0].astype(np.uint32) << 16) | (px[:, 1].astype(np.uint32) << 8) | px[:, 2]
    vals, counts = np.unique(packed, return_counts=True)
    dom = int(vals[counts.argmax()])
    bg = np.array([(dom >> 16) & 255, (dom >> 8) & 255, dom & 255], dtype=np.int16)
    diff = np.abs(px.astype(np.int16) - bg).max(axis=1)
    return float((diff > 8).mean())


def rustkit_viewport_text(display_list_path, width, height):
    """Concatenate display-list text runs that fall inside the first viewport."""
    dl = json.loads(Path(display_list_path).read_text())
    cmds = dl.get("commands") if isinstance(dl, dict) else dl
    runs = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("op") == "text" and isinstance(node.get("text"), str):
                x = float(node.get("x") or 0)
                y = float(node.get("y") or 0)
                size = float(node.get("font_size") or 16)
                adv = node.get("advances")
                run_w = float(sum(adv)) if isinstance(adv, list) else size * len(node["text"])
                if x < width and x + run_w > 0 and y - size < height and y + size > 0:
                    runs.append(node["text"])
            for v in node.values():
                if isinstance(v, (dict, list)):
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(cmds if cmds is not None else dl)
    return " ".join(runs)


PRODUCT_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
              "(KHTML, like Gecko) Version/17.4 Safari/605.1.15 HiWave/1.0")


def probe_access(url):
    """Top-level document status + bot-manager vendor, as the product UA sees it.

    A separate plain GET (not RustKit's own request), recorded so a block is
    reported as blocked:<vendor> rather than a bare failure
    (PLAN-realsite.md, "Access blocks").
    """
    import urllib.error
    import urllib.request

    req = urllib.request.Request(url, headers={"User-Agent": PRODUCT_UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            status, headers = r.status, r.headers
    except urllib.error.HTTPError as e:
        status, headers = e.code, e.headers
    except Exception as e:  # network trouble is not a block
        return {"status": None, "error": str(e)[:120], "vendor": None, "blocked": False}

    h = {k.lower(): v for k, v in headers.items()}
    cookies = " ".join(v for k, v in headers.items() if k.lower() == "set-cookie")
    vendor = None
    if "x-datadome" in h or "datadome=" in cookies:
        vendor = "datadome"
    elif "x-amzn-waf-action" in h:
        vendor = "aws-waf"
    elif "cf-mitigated" in h or ("cf-ray" in h and status in (403, 429, 503)):
        vendor = "cloudflare"
    elif "bm_s=" in cookies or "_abck=" in cookies or "akamai" in h.get("server", "").lower():
        vendor = "akamai"
    blocked = status in (202, 403, 429, 503) and vendor is not None
    return {"status": status, "vendor": vendor, "blocked": blocked}


def chrome_capture(url, png, text_json, width, height, env):
    res, err, _ = run_json(
        ["node", str(ORACLE), "chrome", url, str(png), str(text_json),
         str(width), str(height), str(CHROME_SETTLE_MS)],
        timeout=120,
        env=env,
    )
    if res is None:
        return {"status": "error", "error": err}
    return res


def oracle_blocked(c):
    """Why a Chrome capture shows an error page instead of the site, or None.

    A capture that "succeeded" on Chrome's own error page (x, 2026-09-26:
    "Access to x.com was denied", HTTP 403) is not an oracle for the site;
    scoring against it credits RustKit for matching an error page.
    """
    if c.get("status") != "ok":
        return None
    if str(c.get("final_url") or "").startswith("chrome-error://"):
        return "chrome error page (%s)" % (c.get("nav_error") or "no nav error")
    st = c.get("http_status")
    if isinstance(st, int) and st >= 400:
        return "top-level document HTTP %d" % st
    return None


def pixel_diff(a, b, diff_png, env):
    res, err, _ = run_json(
        ["node", str(ORACLE), "diff", str(a), str(b)] + ([str(diff_png)] if diff_png else []),
        timeout=120,
        env=env,
    )
    if res is None:
        return {"error": err}
    return res


def score_site(site, capture_bin, outdir, width, height, env):
    sid, url = site["id"], site["url"]
    d = outdir / sid
    d.mkdir(parents=True, exist_ok=True)
    rec = {"id": sid, "url": url}

    # Chrome twice (self-noise), then RustKit once.
    chrome = []
    for tag in ("a", "b"):
        c = chrome_capture(url, d / f"chrome-{tag}.png", d / f"chrome-{tag}-text.json",
                           width, height, env)
        chrome.append(c)
    rec["chrome"] = chrome
    # The oracle is whichever Chrome capture succeeded (screenshots of heavy
    # pages occasionally time out under swiftshader); self-noise needs both.
    for c in chrome:
        why = oracle_blocked(c)
        if why:
            c["oracle_blocked"] = why
    ok_tags = [t for t, c in zip("ab", chrome)
               if c.get("status") == "ok" and not c.get("oracle_blocked")
               and (d / f"chrome-{t}.png").exists()]
    chrome_ok = bool(ok_tags)
    oracle = ok_tags[0] if ok_tags else "a"
    rec["oracle_capture"] = oracle if chrome_ok else None

    rk_frame, rk_dl = d / "rustkit.ppm", d / "rustkit-display-list.json"
    started = time.time()
    rk, rk_err, rk_code = run_json(
        [str(capture_bin), "--url", url, "--width", str(width), "--height", str(height),
         "--timeout-ms", str(LOAD_TIMEOUT_MS), "--dump-frame", str(rk_frame),
         "--dump-display-list", str(rk_dl), "--verbose"],
        timeout=LOAD_TIMEOUT_MS // 1000 + 15,
        # The engine's info log, timestamped: where a slow load spent its 30s.
        stderr_path=d / "rustkit-stderr.log",
    )
    rec["rustkit"] = rk if rk is not None else {"status": "crash", "error": rk_err,
                                                "exit_code": rk_code}
    rec["rustkit"]["wall_ms"] = int((time.time() - started) * 1000)

    # LOADS
    loads, loads_why = False, None
    if rk is None or rk.get("status") != "ok":
        loads_why = (rk or {}).get("error") or rk_err
    elif not rk_frame.exists():
        loads_why = "no frame written"
    else:
        frac = non_background_fraction(rk_frame)
        rec["rustkit"]["non_background_fraction"] = round(frac, 4)
        if frac < BLANK_MIN_FRACTION:
            loads_why = "blank frame (%.2f%% non-background)" % (frac * 100)
        else:
            loads = True
    access = probe_access(url)
    rec["access"] = access
    # A blocked site scores LOADS=0 (PLAN-realsite.md, "Access blocks") even
    # when RustKit paints something: that something is the vendor's challenge
    # page, which Chrome gets too, so it would also "look right" (chatgpt,
    # 20260925T1925Z-subdl: 2 points for matching Cloudflare's interstitial).
    if access["blocked"]:
        if loads:
            loads, loads_why = False, "painted the challenge page"
        loads_why = "blocked:%s (HTTP %s) — %s" % (access["vendor"], access["status"], loads_why)
    rec["loads"] = {"pass": loads, "why": loads_why}

    # READABLE
    readable = {"pass": False}
    if not chrome_ok:
        readable["why"] = "chrome capture failed: %s" % (
            chrome[0].get("oracle_blocked") or chrome[0].get("error"))
        readable["oracle_failed"] = True
    else:
        cw = words(json.loads((d / f"chrome-{oracle}-text.json").read_text())["text"])
        rw = set()
        if loads and rk_dl.exists():
            rw = words(rustkit_viewport_text(rk_dl, width, height))
        readable["chrome_words"] = len(cw)
        readable["rustkit_words"] = len(rw)
        if not cw:
            readable["why"] = "chrome shows no text in first viewport (unscored, 0 points)"
            readable["unscored"] = True
        else:
            hit = len(cw & rw) / len(cw)
            readable["ratio"] = round(hit, 4)
            readable["pass"] = hit >= READABLE_MIN
            readable["missing_sample"] = sorted(cw - rw)[:25]
    rec["readable"] = readable

    # LOOKS RIGHT
    looks = {"pass": False}
    if not chrome_ok:
        looks["why"] = "chrome capture failed"
        looks["oracle_failed"] = True
    else:
        if len(ok_tags) == 2:
            noise = pixel_diff(d / "chrome-a.png", d / "chrome-b.png", None, env)
            looks["chrome_self_diff"] = noise.get("diffPercent")
        if loads:
            diff = pixel_diff(d / f"chrome-{oracle}.png", rk_frame, d / "diff.png", env)
            looks["diff"] = diff.get("diffPercent")
            if diff.get("instrumentFailure") or diff.get("error"):
                looks["why"] = diff.get("instrumentFailure") or diff.get("error")
        else:
            looks["why"] = "rustkit did not load"
        noise_pct = looks.get("chrome_self_diff")
        if noise_pct is not None and noise_pct > LOOKS_RIGHT_MAX:
            looks["unstable"] = True
            looks["why"] = "chrome-vs-chrome %.1f%% > %.0f%% (unstable, 0 points)" % (
                noise_pct, LOOKS_RIGHT_MAX)
        elif looks.get("diff") is not None and not looks.get("why"):
            looks["pass"] = looks["diff"] <= LOOKS_RIGHT_MAX
    rec["looks_right"] = looks

    rec["points"] = int(loads) + int(readable["pass"]) + int(looks["pass"])
    (outdir / f"{sid}.json").write_text(json.dumps(rec, indent=2))
    return rec


def fmt_row(r):
    def mark(c):
        if c.get("unstable"):
            return "unst"
        if c.get("unscored"):
            return "n/a"
        return "PASS" if c["pass"] else "fail"

    rd = r["readable"]
    lk = r["looks_right"]
    ratio = "%5.1f%%" % (rd["ratio"] * 100) if "ratio" in rd else "   -  "
    diff = "%5.1f%%" % lk["diff"] if lk.get("diff") is not None else "   -  "
    noise = "%5.1f%%" % lk["chrome_self_diff"] if lk.get("chrome_self_diff") is not None else "   -  "
    why = r["loads"]["why"] or ""
    return "%-10s %-4s %-4s %s %-4s %s (cc %s)  %d/3  %s" % (
        r["id"], mark(r["loads"]), mark(rd), ratio, mark(lk), diff, noise, r["points"], why[:60])


def summarize(rows, ts, width, height, all_ids):
    summary = {
        "ts": ts,
        "chrome": PINNED_CHROME_VERSION,
        "viewport": [width, height],
        "sites": len(rows),
        "points": sum(r["points"] for r in rows),
        "max_points": 3 * len(rows),
        "loads": sum(bool(r["loads"]["pass"]) for r in rows),
        "readable": sum(bool(r["readable"]["pass"]) for r in rows),
        "looks_right": sum(bool(r["looks_right"]["pass"]) for r in rows),
        "looks_right_unstable": [r["id"] for r in rows if r["looks_right"].get("unstable")],
        "readable_unscored": [r["id"] for r in rows if r["readable"].get("unscored")],
        "oracle_failed": [r["id"] for r in rows if r["oracle_capture"] is None],
        # Both Chrome captures landed on an error page (a subset of oracle_failed).
        "oracle_blocked": {r["id"]: r["chrome"][0]["oracle_blocked"] for r in rows
                           if r["oracle_capture"] is None
                           and all(c.get("oracle_blocked") for c in r["chrome"])},
        "blocked": {r["id"]: "%s/%s" % (r["access"]["vendor"], r["access"]["status"])
                    for r in rows if r["access"]["blocked"]},
        "per_site": {r["id"]: r["points"] for r in rows},
    }
    # n/scorable (PLAN A2): points on the sites the board can score at all,
    # i.e. neither RustKit's access probe nor Chrome's oracle was blocked.
    # Reported alongside /60, never instead of it.
    scorable = [r for r in rows if not r["access"]["blocked"]
                and r["id"] not in summary["oracle_blocked"]]
    summary["scorable_sites"] = len(scorable)
    summary["scorable_points"] = sum(r["points"] for r in scorable)
    summary["scorable_max"] = 3 * len(scorable)
    summary["full_run"] = {r["id"] for r in rows} == set(all_ids)
    return summary


def append_trend(summary, run_name, trend_name="trend.csv"):
    """PLAN A6: one row in trench/realsite/<trend_name> per full run."""
    trend = REPO / "trench" / "realsite" / trend_name
    new = not trend.exists()
    with trend.open("a") as f:
        if new:
            f.write("ts,run,points,max,loads,readable,looks_right,"
                    "scorable_points,scorable_max,blocked,oracle_blocked\n")
        f.write("%s,%s,%d,%d,%d,%d,%d,%d,%d,%s,%s\n" % (
            summary["ts"], run_name, summary["points"], summary["max_points"],
            summary["loads"], summary["readable"], summary["looks_right"],
            summary["scorable_points"], summary["scorable_max"],
            "|".join(sorted(summary["blocked"])), "|".join(sorted(summary["oracle_blocked"]))))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--site", action="append", help="only these site ids")
    ap.add_argument("--board", choices=sorted(BOARDS), default="top20",
                    help="top20 (the trench metric, /60), top25 (top20 + five, /75, also writes "
                         "the /60 row) or wide (80 sites, /240, separate trend)")
    ap.add_argument("--capture-bin", default=str(REPO / "target/release/parity-capture"))
    ap.add_argument("--out", help="run directory (default trench/realsite/runs/<ts>)")
    ap.add_argument("--summarize", action="store_true",
                    help="capture nothing; rebuild summary.json from the per-site JSONs "
                         "already in --out (a run done in --site chunks)")
    ap.add_argument("--oracle-headless", action="store_true",
                    help="run the Chrome oracle headless (the pre-A1 identity) for a before/after "
                         "reading; the default is headed, off-screen")
    ap.add_argument("--viewport", metavar="WxH",
                    help="score at another size (PLAN 2026-09-27 16:20, elasticity): Chrome and "
                         "RustKit both at WxH. A separate score with its own trend file "
                         "(trend-WxH.csv), never part of the pinned-size /60")
    args = ap.parse_args()
    if args.oracle_headless:
        os.environ["REALSITE_ORACLE_HEADLESS"] = "1"

    sites_file, trend_name = BOARDS[args.board]
    cfg = json.loads(sites_file.read_text())
    width, height = cfg["viewport"]["width"], cfg["viewport"]["height"]
    size_suffix = ""
    if args.viewport:
        w, _, h = args.viewport.partition("x")
        if (int(w), int(h)) != (width, height):
            width, height = int(w), int(h)
            size_suffix = "-%dx%d" % (width, height)
            trend_name = trend_name.replace(".csv", size_suffix + ".csv")
    sites = cfg["sites"]
    all_ids = [s["id"] for s in sites]
    if args.summarize:
        if not args.out:
            sys.exit("--summarize needs --out")
        outdir = Path(args.out)
        rows = [json.loads((outdir / f"{i}.json").read_text()) for i in all_ids
                if (outdir / f"{i}.json").exists()]
        ts = outdir.name
    else:
        if args.site:
            sites = [s for s in sites if s["id"] in set(args.site)]
            if not sites:
                sys.exit("no such site ids: %s" % args.site)

        env = dict(os.environ)
        chrome_path = env.get("PARITY_CHROME_PATH") or str(DEFAULT_CHROME)
        problems = []
        if not Path(chrome_path).exists():
            problems.append("pinned Chrome not found: %s" % chrome_path)
        if not Path(args.capture_bin).exists():
            problems.append("parity-capture not built: %s" % args.capture_bin)
        if not shutil.which("node"):
            problems.append("node not on PATH")
        if problems:
            sys.exit("INSTRUMENT BROKEN: " + "; ".join(problems))
        env["PARITY_CHROME_PATH"] = chrome_path

        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        outdir = Path(args.out) if args.out else REPO / "trench" / "realsite" / "runs" / (ts + ("-wide" if args.board == "wide" else "") + size_suffix)
        outdir.mkdir(parents=True, exist_ok=True)

        rows = []
        for s in sites:
            r = score_site(s, Path(args.capture_bin), outdir, width, height, env)
            print(fmt_row(r), flush=True)
            rows.append(r)

    versions = {c.get("browser_version") for r in rows for c in r["chrome"] if c.get("browser_version")}
    if versions and versions != {PINNED_CHROME_VERSION}:
        sys.exit("INSTRUMENT BROKEN: oracle ran Chrome %s, pinned is %s" % (
            sorted(versions), PINNED_CHROME_VERSION))

    summary = summarize(rows, ts, width, height, all_ids)
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2))
    top20 = None
    if args.board == "top25":
        top20_ids = [x["id"] for x in json.loads(SITES_FILE.read_text())["sites"]]
        top20 = summarize([r for r in rows if r["id"] in set(top20_ids)],
                          ts, width, height, top20_ids)
        summary["top20"] = {k: top20[k] for k in (
            "points", "max_points", "loads", "readable", "looks_right",
            "scorable_points", "scorable_max", "full_run")}
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2))
    if summary["full_run"]:
        append_trend(summary, outdir.name, trend_name)
        if top20 and not size_suffix:
            append_trend(top20, outdir.name, "trend.csv")
    if args.summarize:
        for r in rows:
            print(fmt_row(r))
    print("-" * 78)
    print("POINTS %d/%d   loads %d  readable %d  looks-right %d   unstable: %s   oracle failed: %s" % (
        summary["points"], summary["max_points"], summary["loads"], summary["readable"],
        summary["looks_right"], ", ".join(summary["looks_right_unstable"]) or "none",
        ", ".join(summary["oracle_failed"]) or "none"))
    print("BLOCKED %s" % (", ".join("%s (%s)" % kv for kv in summary["blocked"].items()) or "none"))
    print("ORACLE BLOCKED %s" % (
        ", ".join("%s (%s)" % kv for kv in summary["oracle_blocked"].items()) or "none"))
    if top20:
        print("TOP20 %d/%d   loads %d  readable %d  looks-right %d   (scorable %d/%d)" % (
            top20["points"], top20["max_points"], top20["loads"], top20["readable"],
            top20["looks_right"], top20["scorable_points"], top20["scorable_max"]))
    print("SCORABLE %d/%d on %d sites" % (
        summary["scorable_points"], summary["scorable_max"], summary["scorable_sites"]))
    print("run: %s" % outdir.relative_to(REPO) if outdir.is_relative_to(REPO) else outdir)


if __name__ == "__main__":
    main()
