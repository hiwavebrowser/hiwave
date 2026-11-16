#!/usr/bin/env python3
"""
commit_history_chart.py - development activity chart for the platform repos.

Reads metrics/commit_history.json (per-day counts) and writes
charts/commit-history.svg and charts/commit-history-dark.svg.

What is counted (see also the caption drawn on the chart):
  * Commits: non-merge commits (fewer than two parents) reachable from the
    `develop` branch of hiwave-macos, hiwave-windows and hiwave-linux,
    bucketed by author date (UTC). Merge commits are stored separately in
    the data file and are not drawn.
  * Merged pull requests: every merged PR in each repo, by merge date (UTC).
  * Weeks start on Monday (UTC). The umbrella repo is not counted, so its
    automated metrics commits never enter the figures.

Usage:
    python3 scripts/commit_history_chart.py            # render from the data file
    python3 scripts/commit_history_chart.py --fetch    # refresh the data file first
    python3 scripts/commit_history_chart.py --summary  # print headline figures

--fetch needs an authenticated GitHub CLI (`gh`); about 70 API requests.
Rendering needs only the Python standard library.
"""

import json
import subprocess
import sys
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DATA_FILE = REPO_ROOT / "metrics" / "commit_history.json"
CHARTS_DIR = REPO_ROOT / "charts"

ORG = "hiwavebrowser"
BRANCH = "develop"
REPOS = [("hiwave-macos", "macOS"), ("hiwave-windows", "Windows"), ("hiwave-linux", "Linux")]

THEMES = {
    "commit-history.svg": {
        "surface": "#fcfcfb", "ink": "#0b0b0b", "ink2": "#52514e", "muted": "#898781",
        "grid": "#e1e0d9", "axis": "#c3c2b7",
        "series": ["#2a78d6", "#eb6834", "#1baf7a"],
    },
    "commit-history-dark.svg": {
        "surface": "#1a1a19", "ink": "#f0efec", "ink2": "#c3c2b7", "muted": "#898781",
        "grid": "#2c2c2a", "axis": "#383835",
        "series": ["#3987e5", "#d95926", "#199e70"],
    },
}


# ---------------------------------------------------------------- fetch

def _gh(args):
    return subprocess.run(["gh"] + args, check=True, capture_output=True, text=True).stdout


def fetch():
    data = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "branch": BRANCH,
        "method": "non-merge commits reachable from the branch, by author date (UTC); "
                  "merge commits kept separately; merged PRs by merge date (UTC)",
        "repos": {},
    }
    for repo, _ in REPOS:
        out = _gh(["api", "--paginate", f"repos/{ORG}/{repo}/commits?sha={BRANCH}&per_page=100",
                   "--jq", '.[] | [.sha, .commit.author.date, (.parents | length)] | @tsv'])
        commits, merges, head = Counter(), Counter(), None
        for line in out.splitlines():
            sha, when, parents = line.split("\t")
            head = head or sha
            day = datetime.fromisoformat(when.replace("Z", "+00:00")).astimezone(timezone.utc).date().isoformat()
            (merges if int(parents) > 1 else commits)[day] += 1
        prs = json.loads(_gh(["pr", "list", "-R", f"{ORG}/{repo}", "--state", "merged",
                              "--limit", "5000", "--json", "mergedAt"]))
        merged = Counter(p["mergedAt"][:10] for p in prs)
        data["repos"][repo] = {
            "head": head,
            "commits_by_day": dict(sorted(commits.items())),
            "merge_commits_by_day": dict(sorted(merges.items())),
            "merged_prs_by_day": dict(sorted(merged.items())),
        }
        print(f"  {repo}: {sum(commits.values())} commits, {sum(merges.values())} merge commits, "
              f"{sum(merged.values())} merged PRs")
    DATA_FILE.write_text(json.dumps(data, indent=1) + "\n")
    return data


# ---------------------------------------------------------------- bucketing

def monday(d):
    return d - timedelta(days=d.weekday())


def weekly(data):
    """Return (weeks, commits[repo][i], prs[repo][i]) with Monday-start weeks."""
    data_day = date.fromisoformat(data["generated_at"][:10])
    days = [date.fromisoformat(k) for r in data["repos"].values()
            for key in ("commits_by_day", "merged_prs_by_day") for k in r[key]]
    first, last = monday(min(days)), monday(data_day)
    weeks = [first + timedelta(weeks=i) for i in range((last - first).days // 7 + 1)]
    index = {w: i for i, w in enumerate(weeks)}

    def bucket(by_day):
        out = [0] * len(weeks)
        for k, n in by_day.items():
            out[index[monday(date.fromisoformat(k))]] += n
        return out

    commits = {r: bucket(v["commits_by_day"]) for r, v in data["repos"].items()}
    prs = {r: bucket(v["merged_prs_by_day"]) for r, v in data["repos"].items()}
    return weeks, commits, prs, data_day


# ---------------------------------------------------------------- drawing

def nice_step(top, target=4):
    for step in (1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 2500, 5000):
        if top / step <= target:
            return step
    return 10000


def render(data, theme):
    weeks, commits, prs, data_day = weekly(data)
    n = len(weeks)
    W, left, right = 1200, 64, 96
    plot_w = W - left - right
    slot = plot_w / n
    bar_w = max(4.0, slot - 4)
    t = theme
    font = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
    partial = (data_day - weeks[-1]).days < 6  # last bucket is an unfinished week

    panels = [  # (title, series-or-None, top, height)
        ("Non-merge commits per week", commits, 100, 190),
        ("Merged pull requests per week", prs, 350, 150),
        ("Cumulative non-merge commits, all three repos", None, 560, 150),
    ]
    H = 800
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="{font}" role="img" aria-labelledby="t d">',
         '<title id="t">HiWave development activity per week</title>',
         f'<desc id="d">Weekly non-merge commits and merged pull requests on hiwave-macos, '
         f'hiwave-windows and hiwave-linux, and cumulative commits, from {weeks[0]} to {data_day}.</desc>',
         f'<rect width="{W}" height="{H}" fill="{t["surface"]}"/>',
         f'<text x="{left}" y="34" font-size="20" font-weight="600" fill="{t["ink"]}">'
         f'HiWave development activity</text>',
         f'<text x="{left}" y="56" font-size="13" fill="{t["ink2"]}">Weekly totals, '
         f'{weeks[0]} to {data_day} (weeks start Monday, UTC). Linear axes from zero.</text>']

    # legend (top right)
    lx = W - right - 280
    for i, (_, label) in enumerate(REPOS):
        x = lx + i * 100
        o.append(f'<rect x="{x}" y="24" width="12" height="12" rx="2" fill="{t["series"][i]}"/>')
        o.append(f'<text x="{x + 18}" y="35" font-size="13" fill="{t["ink2"]}">{label}</text>')

    def x_of(i):
        return left + i * slot + (slot - bar_w) / 2

    def y_axis(top, h, vmax):
        step = nice_step(vmax)
        axis_top = step * (int(vmax / step) + (1 if vmax % step else 0)) or step
        v = 0
        while v <= axis_top:
            y = top + h - h * v / axis_top
            o.append(f'<line x1="{left}" x2="{left + plot_w}" y1="{y:.1f}" y2="{y:.1f}" '
                     f'stroke="{t["axis"] if v == 0 else t["grid"]}" stroke-width="1"/>')
            o.append(f'<text x="{left - 8}" y="{y + 4:.1f}" font-size="11" text-anchor="end" '
                     f'fill="{t["muted"]}">{v:,}</text>')
            v += step
        return axis_top

    def x_axis(top, h):
        seen = set()
        for i, w in enumerate(weeks):
            # label the first week that starts in each month
            key = (w.year, w.month)
            if key in seen or (i == 0 and w.day > 7):
                seen.add(key) if i else None
                continue
            seen.add(key)
            x = left + i * slot
            o.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top + h}" y2="{top + h + 5}" stroke="{t["axis"]}"/>')
            o.append(f'<text x="{x:.1f}" y="{top + h + 18}" font-size="11" fill="{t["muted"]}">'
                     f'{w.strftime("%b")} {w.day}{", " + str(w.year) if w.month == 1 or i == 0 else ""}</text>')

    for title, series, top, h in panels:
        o.append(f'<text x="{left}" y="{top - 14}" font-size="14" font-weight="600" fill="{t["ink"]}">{title}</text>')
        if series is not None:
            totals = [sum(series[r][i] for r, _ in REPOS) for i in range(n)]
            axis_top = y_axis(top, h, max(totals))
            x_axis(top, h)
            for i in range(n):
                y = top + h
                for s, (repo, _) in enumerate(REPOS):
                    v = series[repo][i]
                    if not v:
                        continue
                    seg = h * v / axis_top
                    y -= seg
                    gap = 1.5 if seg > 3 else 0  # surface gap between stacked segments
                    opacity = ' fill-opacity="0.45"' if partial and i == n - 1 else ''
                    o.append(f'<rect x="{x_of(i):.1f}" y="{y:.2f}" width="{bar_w:.1f}" '
                             f'height="{max(seg - gap, 0.8):.2f}" fill="{t["series"][s]}"{opacity}/>')
            # direct labels: the tallest complete week and the latest complete week
            last_full = n - 2 if partial else n - 1
            peak = max(range(last_full + 1), key=lambda i: totals[i])
            for i in {peak, last_full}:
                y = top + h - h * totals[i] / axis_top
                o.append(f'<text x="{x_of(i) + bar_w / 2:.1f}" y="{y - 5:.1f}" font-size="11" '
                         f'text-anchor="middle" fill="{t["ink2"]}">{totals[i]:,}</text>')
            if partial:
                o.append(f'<text x="{left + plot_w + 6}" y="{top + h - 4}" font-size="10" '
                         f'fill="{t["muted"]}">week in</text>')
                o.append(f'<text x="{left + plot_w + 6}" y="{top + h + 8}" font-size="10" '
                         f'fill="{t["muted"]}">progress</text>')
        else:
            totals = [sum(commits[r][i] for r, _ in REPOS) for i in range(n)]
            cum, run = [], 0
            for v in totals:
                run += v
                cum.append(run)
            axis_top = y_axis(top, h, cum[-1])
            x_axis(top, h)
            pts = [(left + i * slot + slot / 2, top + h - h * c / axis_top) for i, c in enumerate(cum)]
            path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            o.append(f'<path d="{path}" fill="none" stroke="{t["ink2"]}" stroke-width="2" '
                     f'stroke-linejoin="round" stroke-linecap="round"/>')
            ex, ey = pts[-1]
            o.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="{t["ink2"]}" '
                     f'stroke="{t["surface"]}" stroke-width="2"/>')
            o.append(f'<text x="{ex + 9:.1f}" y="{ey + 4:.1f}" font-size="12" font-weight="600" '
                     f'fill="{t["ink"]}">{cum[-1]:,}</text>')

    cap_y = 752
    cap = [
        f"Counted: non-merge commits reachable from the {data['branch']} branch of hiwave-macos, hiwave-windows and "
        f"hiwave-linux, by author date; merge commits are excluded.",
        "Merged pull requests are counted by merge date. The umbrella repo and its automated metrics commits are not "
        f"counted. Data fetched {data['generated_at'][:10]} (UTC) with scripts/commit_history_chart.py.",
    ]
    for i, line in enumerate(cap):
        o.append(f'<text x="{left}" y="{cap_y + i * 16}" font-size="11" fill="{t["ink2"]}">{line}</text>')
    o.append('</svg>')
    return "\n".join(o) + "\n"


# ---------------------------------------------------------------- summary

def summary(data):
    weeks, commits, prs, data_day = weekly(data)
    n = len(weeks)

    def tot(series, i):
        return sum(series[r][i] for r, _ in REPOS)

    print(f"data date {data_day}; weeks {weeks[0]} .. {weeks[-1]} ({n} buckets, last may be partial)")
    for repo, _ in REPOS:
        r = data["repos"][repo]
        print(f"  {repo}: {sum(r['commits_by_day'].values())} non-merge commits, "
              f"{sum(r['merge_commits_by_day'].values())} merge commits, "
              f"{sum(r['merged_prs_by_day'].values())} merged PRs, head {r['head'][:8]}")
    print("  week        commits  merged PRs")
    for i in range(n):
        print(f"  {weeks[i]}  {tot(commits, i):7d}  {tot(prs, i):10d}")
    months = Counter()
    months_pr = Counter()
    for r in data["repos"].values():
        for k, v in r["commits_by_day"].items():
            months[k[:7]] += v
        for k, v in r["merged_prs_by_day"].items():
            months_pr[k[:7]] += v
    print("  month    commits  merged PRs")
    for m in sorted(set(months) | set(months_pr)):
        print(f"  {m}  {months[m]:7d}  {months_pr[m]:10d}")


def main():
    if "--fetch" in sys.argv:
        print("Fetching commit and pull request history...")
        data = fetch()
    else:
        data = json.loads(DATA_FILE.read_text())
    if "--summary" in sys.argv:
        summary(data)
        return
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    for name, theme in THEMES.items():
        (CHARTS_DIR / name).write_text(render(data, theme))
        print(f"  Generated: charts/{name}")


if __name__ == "__main__":
    main()
