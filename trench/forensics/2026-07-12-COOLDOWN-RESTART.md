# Cold start after cooldown (2026-07-12)

**Author:** Prometheus · **Pete:** loops killed → full context wipe; workers back in ~1h  
**Supersedes for this wake:** same north stars as reboot plans, **board updated**

Prior full plans (still valid method):  
- `2026-07-11-REBOOT-EXEC-PLAN-ATLAS.md`  
- `2026-07-11-REBOOT-EXEC-PLAN-ATHENA.md`

---

## Board truth (re-measure on wake)

| | macOS (Atlas) | Windows (Athena) |
|--|---------------|------------------|
| Last known campaign | **24/26 @ t15** avg ~7.3 | re-measure after #20 |
| Holdout | **6/6** avg ~5.8 | HTML mirrored; RESET may be incomplete |
| Master wins this cycle | #45 settings (radial position axis), #46 sticky (nowrap) | #12–#19 paint/fidelity/canvas/UA font |
| Open PRs | **none** | **#20 PAGE-MIRROR** (HTML byte-identical; harness+baselines may still be landing) |
| Remaining macOS KF fails | **about** ~16.7, **image-gallery** ~21.4 | — |
| Portability model | **P-shared / P-contract / P-macos-only / W-local** — do not assert 1:1 patch ports | Windows layout/engine ~37–40% of macOS surface; cherry-picks of #45/#46 are **N/A** |

**First commands both seats:**

```text
null exchange sync
# read stream petes-macbook-pro-local-2a604c.prometheus — last 15 entries
git fetch && git checkout master && git pull --ff-only
gh pr list --state open
# full parity measure → post board line
```

---

## Atlas — north star this wake

**Product KF residual:** clear **`about`** under t15 (letter-spacing / advance residual), then **`image-gallery`** only after confirming asset/network vs layout.

Optional hygiene (not dig thrash): registry-only PR to clear **stale-green** KF flags with measured numbers in body:  
`gradient-no-radius`, `gradient-radius-only`, `images-intrinsic`.

**Do not:** re-open IFC A–C, advance contract, canvas, DIG-1/2, #45/#46 stories.  
**Portable notes:** ship as **P-contract** (fixture + behavior + site description), not patch recipes.

---

## Athena — north star this wake

1. **Finish #20** — harness **(b)** (enumerate holdout + new micros from HTML/registry, not only baseline dirs) → CfT **148.0.7778.216** baselines → **RESET** board labeled page-mirror discontinuity.  
2. **SHIP** Windows-local `wrap_text` respects `white-space:nowrap|pre` (standalone PR; not a port of #46).  
3. Then reboot **Phase B** contract catch-up: IFC align → advance → valign (feature epics, not cherry-picks).

**You are not blocked on Prometheus** for page-mirror scope — already confirmed (UNBLOCK / harness b / CfT pin on exchange).

---

## Comms (read this if “Prometheus silent”)

- Messages live on **GitHub exchange streams**, not UDP content.  
- After any `reply_expected: true` you post: **sync and read prometheus stream** before declaring blocked.  
- Shared `~/.null/exchange` can non-FF; `git fetch` + compare origin stream line counts if sync looks empty.

---

## Success this wake

| Seat | Done means |
|------|------------|
| Atlas | about ≤15 or written probe blocker; holdout still 6/6 |
| Athena | #20 merged or WAITING_MERGE with RESET numbers posted; wrap_text PR open/merged |

— Prometheus
