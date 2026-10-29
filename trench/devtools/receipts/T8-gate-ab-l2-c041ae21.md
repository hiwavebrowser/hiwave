## T8 (#827) gate rerun, 20-site A/B and L2 pin (devtools lane, 10-29 18:35)

Heads: receipts measured on **df6a05af** (parity build, `parity-capture` sha256 02893ac4...); branch now **c041ae21** = df6a05af + one test-only commit (L2), no runtime change, so the receipts stand for the head.

### 1. Two heavy tabs, three arms (`trench/devtools/tools/three_arms.py <wt> 8 parity`), INDICATIVE
Load at round start 22.15, 17.26, 14.54, 12.28, 10.79, 9.5, 9.23, 8.27: never under 8 at a round start, so this is indicative, not the quiet gate (Atlas 13:50: run anyway, label it). Load came from outside the lane (it was 9.5 before anything started; peaked 24 during the build).

| tab | off | w1 | w2 | w2-w1 paired median (spread) | w2-off paired median (spread) |
|---|---|---|---|---|---|
| cnn | 17.30 s | 17.25 s | 17.40 s | -0.10 s, -0.6% (-0.90..+1.60) | -0.00 s, -0.0% (-0.90..+1.20) |
| yahoo | 9.75 s | 9.55 s | 9.60 s | +0.10 s, +1.0% (-0.50..+1.50) | -0.10 s, -1.0% (-0.70..+1.60) |

n=8 per arm, interleaved off,w1,w2 per round. Spreads are tighter than the 13:10 run (cnn w2 range 16.7-18.5 vs 14.4-19.2). Network records listed: cnn 110 in all 24 runs; yahoo 254-258 in every arm (same band). 24/24 runs ok, no panics. Log: `T8-three-arms-1835-df6a05af.log`.

### 2. 20-site A/B, A = `HIWAVE_NET_RUNTIME=0`, B = `HIWAVE_NET_WORKERS=2` (default)
`trench/z/tools/ab5.py` with env wrappers, 1280x800, 30 s, A,B,A,B per site; load 3.4-9.8.
- **Wall clock, 17 clean sites: A 333.1 s, B 322.7 s, B/A 0.969.** (T7a w1 vs off was 1.014.)
- **Pixel movers: none.** No site has every across-arm pair above both within-arm differences.
- Dropped (one failed capture each): lyft (A run 2, 0.3 s; the same A-arm failure as in the T7a A/B), linkedin (A run 1 timed out at 30 s; B's 89.9% is the served variant seen in T7a too), cnn (B run 1 at 30.2 s; the other three 28.1-28.7 s).
- Table: `T8-ab-w2-df6a05af.txt`.

### 3. L2 pin (Prometheus R1 L2) @ c041ae21
`policy::tests::two_origins_competing_for_the_page_slot_keep_per_origin_order`: two origins share one page slot (`max_in_flight_per_page: 1`, `max_in_flight_per_origin: 1`); 8 reservations interleaved origin1/origin2 for /a../d; tasks spawned in reverse on a 2-worker runtime. Asserts each origin is served /a,/b,/c,/d, nothing starves (10 s bound), peak 1 per origin. The cross-origin order (page-slot grant order) is deliberately not asserted: that is the documented contract on `reserve`, and Prometheus's L2 asks to pin exactly the per-origin-only contract.
- Red by mutation (`reserve` skips its first poll): `first origin left its reserve order, left ["/d","/c","/b","/a"]`. Restored: green.
- rustkit-net lib 105/0, five consecutive runs.
- Note on Atlas's 15:30 wording ("fetches the page slot in reservation order when two origins compete"): the code does not reserve the page slot, by design (a request queued on a busy origin must not hold one). Pinning a cross-origin page-slot order would need a code change that re-opens the starvation question; the pin follows Prometheus's L2 text instead.

Not run this session: G1 50x loop (still open from 12:35).
