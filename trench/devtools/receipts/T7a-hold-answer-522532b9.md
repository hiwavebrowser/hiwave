R1 HOLD answered @ 522532b9 (fixes in b4c9f720; 522532b9 adds only ignored receipt tests). Plain pushes, no force-push.

### Blockers
| item | answer |
|---|---|
| **C4** | Test 3 now asserts the closed view's `Weak<Inspector>` is dead within **1 s**. `close_latency_receipt` (ignored), n = 10 each: idle **p50 36 ms, max 45 ms**; with a second view keeping `rustkit-net` busy (24 × 4 MB bodies, read and base64-encoded on that thread) **p50 18 ms, max 54 ms**. |
| **D1, 20-site A/B** | One binary (parity, 522532b9), A = `HIWAVE_NET_RUNTIME=0`, B = on, `ab5.py` A,B,A,B per site, 30 s, 1280×800. 19 sites had all four frames (lyft lost one A capture). **Wall clock B/A = 1.014** (A 334.1 s, B 338.8 s). Per-site ratios go both ways, from 0.85 to 1.44; the biggest are short pages (youtube 11.0 vs 15.8 s, reddit 1.6 vs 0.8 s). Heavy pages are flat: microsoft 0.988, cnn 0.986, github 1.027. **Pixels: no runtime mover.** Every across-arm difference also shows up inside one arm, which means a served variant: linkedin 89.9% (within B), walmart 82.7% (within B), yahoo 31.2% (within A), google 1.68% (within A). Load was 10–13 the whole run. |
| **D1, two heavy tabs** | `two_heavy_tabs_receipt` (ignored, debug test build): cnn and yahoo in two views of one process, navigate → load complete, 4 interleaved rounds per arm. **cnn on 34.2 / 34.8 / 33.9 / 33.8 s, off 33.5 / 33.5 / 33.9 / 33.5 s (+1.7%)**. **yahoo on 18.9 / 19.2 / 18.6 / 18.9 s, off 18.9 / 18.4 / 18.8 / 18.5 s (+1.3%)**. Network records listed per view are the same in both arms (107 / 238–243). |
| **D1 ruling asked** | Both numbers are under the 5% wall-clock threshold, so I kept D1. The two-tab gap is small but in the same direction every round; I'm reporting it rather than calling it zero. If you read it as a regression, the fix is Prometheus's suggestion: take the slot ticket in `begin()` on the page thread, then use 2 workers. That is now the named follow-up in the body either way. The `DiagContext` and `net_runtime` docs no longer say multi-thread, and they list what runs serially on the thread. |
| **Lock hold, file sink on** | `lock_hold_receipt_with_the_file_sink_on` (ignored): 20 000 request + response record calls, each timed whole on one thread (an upper bound on the hold). With a `RollingFileSink` of 1 MB × 3 (rotations land in the sample): **p50 8.7 µs, p99 15.3 µs, max 4.2 ms**. Ring only: 3.5 µs, 10.5 µs, 1.5 ms. The max is one call in 40 000, with load at 11. The sink I/O stays under the lock. |
| **RSS and threads** | `parity-capture --url`, 30 s, interleaved, max RSS per run. **cnn**: off 777.7 / 774.6 / 808.0 / 775.1 / 776.6 MB, on 929.9 / 775.2 / 769.7 / 776.5 / 778.1 MB. The medians are equal (776.6 vs 776.5), and each arm has one high run. **yahoo**: off 254.7 / 257.3, on 260.0 / 260.0. **wikipedia**: off 153.1 / 153.6, on 152.2 / 152.8. **Threads: +1 by construction** (`rustkit-net`, started at the first live request). Sampling with `ps -M` every 100 ms reads 25–48 in both arms and can't resolve it. |
| **Campaign** | 26/26, mean 1.1078%, every case identical to T6d and cb7622c6. Receipt: binary sha256 `de075abd…`, campaign `2992fe90…`, base f3f281a3, dirty false, profile parity. |

### Nits done
- **Poke after store:** the task sends its outcome on a oneshot, then pokes. The page side awaits the oneshot. `AbortOnDrop` still holds the `JoinHandle`.
- **`DiagContext`:** a drop guard restores the nav id and test hooks, so they are restored on a panic too. The doc says the h2 driver runs outside it.
- **Test 7:** adds a failure reason that holds the full URL (`FAIL_NAMING_URL_PATH`, cfg(test)), written on `rustkit-net` and scrubbed at record time.
- **`brief_url`:** drops `;params` and `user:pass@`.
- **Mirror URLs:** console places, error frames, inserted-script lines and dynamic-import lines now go through `brief_url`; engine labels stay as they are. The header names what it covers. New test: `script_places_inserted_scripts_and_imports_drop_the_query_too`.

### Suite
`rustkit-engine --features headless --lib` at b4c9f720: **1139/0** (7 ignored), 1041 s, load 10–11.

### Left
- For T7b: test 8 and the ring clone per read.
- Still open from the nits: test 2 asserting the server sees the stream close, and a kill-switch env-parse test.
- develop has moved to e1093aad (#812); GitHub reports the PR MERGEABLE. I did not merge develop in.

**R1 asked: Prometheus and Atlas, delta cb7622c6 → 522532b9.**

🤖 Generated with [Claude Code](https://claude.com/claude-code)
