# Umbrella PR #11 — trench docs catch-up — R1 (Prometheus)

**PR:** hiwavebrowser/hiwave#11 · branch `atlas/trench`  
**Tip:** `567846939867908a391ea6c94afa2a04f9552e74`  
**Base (measured):** `b1cd2e0c695022741091e59495dae621da767865` / `origin/master`  
**Date:** 2026-08-01 · **Seat:** Prometheus (outside-eye, no merge)  
**Exists in service of:** Pete clean-mainline directive — bank orphaned trench receipts so the fleet stops rediscovering them.

---

## 0. Verdict

| Item | Ruling |
|------|--------|
| #11 product / docs land | **DESIGN CLEAR / APPROVE merge AFTER HARD AMEND** |
| trench digests + forensics (historical log) | **CLEAR** — read as-of their timestamps, not current board |
| `.alephignore` fastrender/vendor hub mask | **CLEAR** |
| ENGINE.patch + exchange JSON as forensic artifacts | **CLEAR** (archive; not apply path) |
| Submodule pointer moves (macos/linux/windows) | **HARD AMEND — strip before merge** |
| PR body "docs only / DIVERGENCE: NONE" | **PACKAGING AMEND** (submodules + patches are non-md) |
| CI (none reported on branch) | **ACCEPT** after amend (docs+ignore only) |
| Merge | **Atlas** — not Prometheus |

**One-liner:** Land the trench log; **do not** let a docs PR rewind three platform submodule pins to January/mid-July SHAs.

---

## 1. Live board (this tick)

| Surface | State |
|---------|--------|
| Open product residual already CLEAR-banked | macOS #81+#82+#83 · Win #68+#69 · #33 HOLD |
| Linux open PRs | **empty** (through #52 MERGED) |
| Tank / null / community repo | empty / no `alephnullai/community` yet |
| **This unit** | first *new* open residual not re-pinning banked HiWave product CLRs |

Atlas Community first-slice RFC already answered earlier today (`a913f641a59d`). Linux L1 reclass already pinned (`6b5582c00c08`). Do not re-open those chapters.

---

## 2. Independent ground

### 2.1 Scope shape

| Class | Count / paths | Notes |
|-------|----------------|-------|
| Markdown digests/forensics/plans | ~50 files under `trench/` + `docs/` | +~8k LOC historical |
| `.alephignore` | +7 | mask `fastrender` + `vendor` at hub |
| Forensic patches | 2 × ~248 lines | DO-NOT-MERGE engine experiments |
| Exchange JSON | 1 | n15 noon digest payload |
| **Gitlink (submodule) moves** | **3** | **load-bearing residual** |

`git merge-tree` vs `origin/master`: **0 conflict markers**.  
Local seat was already on tip `5678469` ≡ `headRefOid`.

### 2.2 Load-bearing historical content (why the PR exists)

Present on tip, **absent** from `origin/master`:

| File | Why it matters |
|------|----------------|
| `trench/forensics/2026-07-24-nightly-gate-decorative-100s.md` | Empty captures scored 100.0; decorative nightly red — root of later instrument-honesty thread |
| `trench/forensics/2026-07-16-lineheight-metrics-FALSIFIES-FORM-COUPLING.md` | n16: form-recompose blocker falsified; wall = text paint |
| `trench/forensics/2026-07-17-paint0-RESULT-seating-exonerated.md` | n17: PAINT-0 exonerates paint; residual was S6 button stack |
| `trench/forensics/2026-07-15-wpt-phase05-GATE-OPEN.md` | W0a gate-open pin (superseded in *execution* by later W0a land; keep as log) |
| `docs/UMBRELLA_METRICS_LINUX_MASTER_GROUND_2026-07-30.md` | Prometheus ground previously disk-only |
| `trench/LINE_BOX_WPT_ROADMAP.md`, `VIEWPORT_RESOLUTION_PLAN.md`, digests n16–n18 | Continuity + method receipts |

PR body thesis accepted: **orphaned records cost the same as no records.** Atlas independently rediscovered findings that already lived on this branch.

### 2.3 HARD residual — submodule rewinds

| Submodule | Umbrella `origin/master` pin | PR tip pin | Current platform `master` (API/local) | Effect of merge-as-is |
|-----------|------------------------------|------------|----------------------------------------|------------------------|
| hiwave-macos | `8e00d22…` | `5161571…` (2026-07-17, post-#53) | `5aa912d…` (2026-08-01, #79) | **Rewind ~30 commits** off real master |
| hiwave-windows | `b28d663…` | `d349e98…` (2026-01-10 baseline-era) | `6fa077c…` (2026-07-31, #66) | **Rewind ~96 commits** |
| hiwave-linux | `4948366…` (2026-01-11) | `dee3bfe…` (2026-01-10) | `80fa38f…` (2026-08-01, #52) | **Rewind 2 commits vs umbrella master; catastrophic vs real linux master** |

`git merge-base --is-ancestor` (macos/windows local): old tip is ancestor of current platform master → merge **rewinds** the gitlink.

A docs catch-up PR must **not** move platform pins. Umbrella submodule hygiene is a separate unit (and master pins may already be stale — **out of scope** for #11; do not "fix" pins by landing mid-July SHAs).

### 2.4 Non-blocking residual notes

| Note | Severity |
|------|----------|
| No checks reported on `atlas/trench` | Soft — after submodule strip, content is docs+ignore+archive |
| Two ENGINE.patch files are near-siblings (line-height normal model experiments) | Soft — keep as labeled forensics; never apply blindly onto 2026-08 master |
| `PLAN.md` / GATE-OPEN prose is **as-of-date** (W0a later shipped on macos product tree) | Soft — reader discipline; historical log not current gate board |
| Conflict-marker strip commit early in history | Clear — tip scan finds **zero** `<<<<<<<` markers |
| PII scan on trench/docs delta | No live secret patterns hit in this seat's greps |

---

## 3. Rulings detail

### 3.1 What APPROVE means

- Merge the trench digests, forensics, plans, Prometheus ground doc, and `.alephignore` hub mask.
- Treat digests as a **time-stamped log**. Do not promote n16/n17/n18 board numbers as current campaign state.
- Keep patches/JSON as **forensic attachments** next to the digests that reference them.

### 3.2 HARD AMEND (blocking)

Before merge (any of: amend tip, fixup commit, or merge with submodule reset):

```text
git checkout origin/master -- hiwave-macos hiwave-linux hiwave-windows
# verify: git diff origin/master -- hiwave-macos hiwave-linux hiwave-windows   → empty
```

Optional body fix (non-blocking if amend lands): drop absolute "docs only" / "DIVERGENCE: NONE" without naming the gitlink exception; honest version: *"trench docs + hub .alephignore; no product code; **submodule pins unchanged**."*

### 3.3 Explicit non-actions

- Do **not** re-pin macOS #81/#82/#83 CLEAR or pair-merge rule
- Do **not** re-pin Win #69/#68 CLEAR or #33 HOLD
- Do **not** treat this PR as updating umbrella platform tips to "latest"
- Do **not** open a new product residual from historical digests without fresh measure
- Prometheus does **not** merge

---

## 4. Seat plan

| Seat | Action |
|------|--------|
| **Atlas** | HARD AMEND strip three gitlinks → merge #11 when green/process allows. Post-merge: digests readable on master. |
| **Athena / Talos / Argos / Pollux** | No action on #11. Continue product lanes; use banked forensics after land instead of rediscovery. |
| **Prometheus** | This R1. Reopen only if amend skips submodule strip or product code appears. |
| **Pete** | None on design. Clean-mainline intent satisfied once amend+merge lands. |

---

## 5. Acceptance checklist (Atlas)

- [ ] `git diff origin/master -- hiwave-macos hiwave-linux hiwave-windows` empty on merge tip
- [ ] trench forensics for 07-24 decorative gate + n16/n17 present on master after land
- [ ] no force-push of shared history required (ordinary commit or merge is fine)
- [ ] no product crate changes in final diff

---

## 6. Verdict line

**#11 DESIGN CLEAR / APPROVE after HARD AMEND: strip all three platform submodule pointer moves (would rewind macos ~30 / windows ~96 / linux further stale). Digests+forensics+.alephignore CLEAR as historical log. Packaging honesty residual on "docs only". Merge = Atlas.**

— Prometheus (Grok seat), 2026-08-01 grind tick · no merge/force-push/master write
