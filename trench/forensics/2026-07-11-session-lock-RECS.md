# Session-lock recommendations — both seats (2026-07-11)

**Author:** Prometheus · **When:** seats mid-session / lock — queue for next wake, do not thrash  
**Sources:** origin/master both repos, open PRs, Atlas broadcasts `5410cd4735a7` / `b9134e0b8636` / `3e5631786da7`

---

## Scoreboard snapshot (honest)

| Seat | Campaign | Holdout | Notes |
|------|----------|---------|--------|
| **macOS** | **21/26 @ t15** avg ~8.8 | **3/6** avg ~22.2 | T6 reset (sticky no longer free-pass). PRs #25–#33 this cycle. **0 open PRs.** |
| **Windows** | Builtins transformed post #13/#14 | **not mirrored** | Open **#16** flex-wrap, **#15** bg-clip:text. Local checkout on some machines may lag `origin/master` @ `f10e8c2`. |

Holdout first run already proved overfit: campaign greens ≠ generalization (flex-toolbar 52, gradient-text 32, grid-mosaic 27).

---

## What landed (do not re-dig)

### macOS (Atlas) — master @ `e1eeccc`
| PR | What | Residual |
|----|------|----------|
| #28–#29 | R0 instruments, R1 fixed CB = viewport | OK |
| #30 | bg-clip:text / GradientText | Holdout gradient-text still 31.8 → generalization incomplete |
| #31 | **IFC A+B** — parent-only align, symmetric text join | B2 mid-line split + C baseline still open in sketch |
| #32 | **T0+T1+T5** honest gate, holdout×6, instrument smokes | T2/T3 rect dual-gate, T4 WPT, T7 mutate still queued |
| #33 | **T6** t15 only, t8 CI cap builtins/micro, known_fail ledger | sticky-scroll 18.27 honestly fail |

### Windows (Athena) — master @ `f10e8c2` (+ open)
| PR | State | What |
|----|-------|------|
| #12→#13 | merged | Cascade + max-content re-land (merge-race class) |
| #14 | merged | var() + **sRGB gamma** + linear gradients (builtins jump) |
| **#16** | **OPEN MERGEABLE** | flex-wrap/flex-flow parse + pack wrapped lines (card-grid 41→57) |
| **#15** | **OPEN MERGEABLE** | background-clip:text (about 81→84; letter-spacing residual) |

macOS already has flex-wrap parse + `distribute_lines` free_space `.max(0.0)`. Windows #16 is still the right fix for **that fork’s** unclamped path — verify after merge that card-grid second row is on-screen; if macOS card-grid residual looks like row-gap phantom height, re-audit same site (stale-dimension map P1).

---

## Recommendations — Atlas (macOS) — next wake order

**Do not open a new epic mid-lock.** Queue:

### A-next-1 — Dig holdout first (anti-overfit)
1. **`holdout-flex-toolbar` (~52)** — nested chip toolbar; not campaign-shaped.  
2. **`holdout-grid-mosaic` (~27)** — 3-col tiles; ties card-grid class.  
3. **`holdout-gradient-text` (~32)** — after paint polish, prove PR #30 generalized.

**Rule:** campaign sticky/article residuals are secondary until holdout top-3 move. Digest must print holdout every run.

### A-next-2 — Advance-contract (text-stack brief) — chore lane
IFC A+B shipped → **one-night advance contract** is unblocked:
- Kill third TextShaper in renderer glyph path  
- Layout advances feed paint  
- Unit: sum(layout) == sum(paint) ±0.5px  
See `2026-07-11-text-stack-unification.md`. This also attacks letter-spacing under-apply (inheritance audit).

### A-next-3 — Scripts (when not dig night)
- **T2/T3:** rect dual-gate + `data-testid` on holdout/campaign key nodes  
- **T4:** WPT Tier-1 runner (orthogonal meter)  
- Expand holdout only with **new DOM**, never edit the sacred six without Pete

### A-next-4 — Cross-seat review when Athena rings
- Review Windows **#16** for portable stale free-space pattern (map entry).  
- Review **#15** against macOS #30 contract (clip on element → text run; no box fill).  
- Flag any case-id or about-page special casing.

### A-next-5 — IFC B2 design standby
Atlas asked Prometheus for B2 (center/right mid-line split with fragment ranges). **Do not implement B2 in the same PR as advance-contract.** Design first if Pete wants depth this week.

### Explicit don’ts (Atlas)
- Don’t raise thresholds / clear known_fail without Pete.  
- Don’t edit `websuite/holdout/**` in dig PRs.  
- Don’t merge Windows PRs from this seat unless Pete re-opens merge rights.

---

## Recommendations — Athena (Windows) — next wake order

### W-merge — Finish open stack cleanly
Both #15 and #16 are **independent of master** and MERGEABLE.

**Recommended merge order:**
1. **#16 flex-wrap first** (layout; card-grid class; stale free-space — high structural value)  
2. **#15 bg-clip:text second** (paint; about polish)

**Before merge each:**
- Confirm CI green on the PR tip  
- Re-measure the **named** case(s) on the merge commit (not branch tip from hours earlier) — #12/#13 race lesson  
- **Freeze branch** once “ready”: no fast-forward follow-ups onto a merge-in-flight branch

**After both land:** one scoreboard dump (campaign + any Windows micros) with honest t15 labels.

### W-next-1 — Mirror test fidelity (blocking for org truth)
Atlas already shipped the policy; Windows still has **NONE** of:
- `scope: holdout` + HTML (copy `websuite/holdout/*` **verbatim**, capture **Windows** Chrome baselines — not macOS PNGs)  
- `known_fail` + per-case gate / `GATE_SCOPE_CAPS`  
- `instrument_smoke.py` (Windows must pass gamma probe via **linear→Srgb** contract)

Priority: **W1 registry+holdout → W2 CI gate → W3 instrument smoke**. Without this, Windows “wins” can still be campaign-shaped.

### W-next-2 — Port IFC A+B contracts (after paint catch-up if needed)
macOS #31 portable rules:
1. Leaves **never** self-align — parent line pass only + subtree shifts  
2. Fitting text joins line from cursor 0 (no first-text-to-block asymmetric gate)  
3. Fixture: `parity-tests/repro/mixed-inline-center.html` (engine-agnostic)

Do **not** invent a Windows-only text-align path.

### W-next-3 — Don’t declare paint done
- about 83.8 residual is **letter-spacing / advance stack**, not more gradient code.  
- Holdout-gradient-text (when mirrored) is the generalization bar, not about alone.  
- Multi-stop / angled gradient strips remain open design (prior Prometheus gradient brief).

### W-next-4 — Shared-crate discipline
Any flex/layout change that is really a **stale-dimension** fix: post portable note to Atlas with site + fixture (map in `2026-07-11-stale-dimension-map.md`). Prefer dual-seat PRs when the bug is in shared algorithm shape.

### Explicit don’ts (Athena)
- Don’t open a third open PR until #15+#16 are merged or explicitly parked.  
- Don’t widen scope mid-PR (flex-wrap PR stays wrap+pack; clip PR stays clip).  
- Don’t raise pass thresholds to keep scoreboard pretty.

---

## Org-level (Pete / both) — while locked

| Priority | Action | Why now |
|----------|--------|---------|
| P0 | Let Athena land #16 then #15 with freeze discipline | Clean board before next digs |
| P0 | Windows holdout mirror before more Windows pixel chasing | Holdout already shows macOS overfit |
| P1 | Atlas dig holdout-flex-toolbar + advance-contract | Highest generalization ROI |
| P1 | Keep digest format: `campaign \| holdout \| tier1` | Numbers mean one thing post-T6 |
| P2 | Prometheus B2 IFC design when asked | Don’t block advance-contract |

**No irreversible work from Prometheus this pass** — recommendations only.

---

## Falsification

If next sessions:
- only campaign pp moves and holdout flat → still coding to the meter; enforce holdout-first dig rule  
- Windows merges without freeze and drops commits → re-apply #13 process hardening  
- advance-contract skipped for more gradient polish → letter-spacing class remains forever

— Prometheus
