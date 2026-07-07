# HiWave Trench Campaign — Plan of Record
Started 2026-07-07. Owners: Atlas (macOS seat), Athena (Windows seat). Authorized by Pete.

## Why this exists
HiWave stalled at the berserker→trench transition (mirror session, 2026-07-07). This campaign makes trench motion visible without Pete driving it: agents grind nightly, Pete reads a noon digest, Fridays converge.

## Metrics
- **Campaign metric (per seat, pinned in BASELINE-<os>.md):** pixel-parity vs **Chrome 148.0.7778.216 (pinned, frozen for the campaign)**. Re-pin only at campaign boundaries, deliberately, both seats in lockstep.
- **North star (Friday trendline):** WPT (Web Platform Tests) pass-rate — absolute conformance, not defined in terms of Chrome. Stand up in Phase 0.5.
- **Quirks ledger (`trench/QUIRKS.md`):** diffs traced to Chrome deviating from spec get recorded and dropped, not chased. Match the spec, not the bug.

## Phases
- **Phase 0 — Revive the instruments (night 1).** No renderer code until the harness is green.
  - macOS: parity_oracle npm deps; fresh pinned-Chrome baseline; classify run; rebuild .aleph with vendor masking (42% of fastrender syms are vendor — mask before agents navigate).
  - Windows: build parity-capture; same pinned baseline; build .aleph index + same mask.
  - Exit: `BASELINE-<os>.md` with current overall parity % and per-bucket shares. Jan's "59% text" is re-verified, not inherited.
- **Phase 0.5 — WPT runner** (either seat, whoever exits Phase 0 first): minimal WPT run against HiWave; record pass-rate; add to Friday trendline.
- **Phase 1 — Decompose (day 2).** Identical bucket formulas + thresholds on both OSes (text metrics / gradients / layout / compositing). Ranked defect ledger on the exchange. Each seat pins ONE metric from its own data.
- **Phase 2 — Nightly trench (day 3+).** One capped ~2h agent session per seat per night. Branches `atlas/trench-<metric>`, `athena/trench-<metric>`. Test-passing commits, never force-pushed. Digest appended to `trench/digest-<os>.md`, posted to the exchange, doorbelled at noon. Silence between digests.
- **Phase 3 — Friday convergence.** Trendline review, portable-fix merges, metric health. 7 days without movement → new angle or a written funeral note. No zombie loops.

## Write policy (Pete-locked, 2026-07-07)
- Platform-specific code: free-fire on your own OS.
- Shared crates (fastrender core, rustkit-*): PR + **other-seat review** before merge. Atlas reviews Athena's, Athena reviews Atlas's.
- Every digest flags portable fixes. Each night begins by porting the other seat's proven wins before hunting new bugs. The same glyph bug is never solved twice.

## Effort + tooling rules
- Nightly cap: one ~2h agent session per seat. Sustainable beats heroic; this is the trench.
- Aleph: vendor masking is the only sanctioned tooling addition. No new infrastructure layers — the campaign metric is parity, not shovel quality.
