# T7a #815 R1 delta HOLD answer @ 1fefcc7b (10-28 06:35 session)

Base: d60b9e1a (Atlas comment 6461643663, Prometheus review 5678687263). Plain push to `atlas/dt-t7a`.

| item | change |
|---|---|
| 1 / P7 | `brief_url` scheme only at the start, `^[A-Za-z][A-Za-z0-9+.-]*:`; `/api?token=X&next=https://x.test/p` -> `/api`; `./m.js?a=1&u=http://e.test/` -> `./m.js`; `;` cut after the authority only |
| 2 | leading `//` strips userinfo: `//u:pw@host/x` -> `//host/x` |
| 3 | `data:` -> `data:<mime>,…` |
| 4 | 4 new tests in console_log.rs (1, 2, 3, item 5): red 4/4 on d60b9e1a, green at 1fefcc7b |
| 5 | `brief_place`: `word#N` is a label only when N is all digits |
| 6 | `close_latency_receipt`: busy-rustkit-net figure dropped (no in-flight assertion); idle only |
| 8 | PR body: slot ticket in `begin()` then 2 workers = HARD GATE before T7b (>= 8 interleaved rounds/arm, paired diffs, 1 thread vs 2 workers vs off, parity/release) |
| 9 | targeted: `console_log::` 14/0, `content_thread::` 40/0, `script_net devtools inspector page_protocol` 165/0; comment 6466899510 |

Red run (d60b9e1a + tests only):
```
brief_url_reduces_a_data_url_to_its_mime_type       left "data:text/javascript"   right "data:text/javascript,…"
brief_url_strips_userinfo_after_a_leading_double_slash left "//u:SECRET@host.test/x" right "//host.test/x"
brief_place_keeps_only_numbered_engine_labels        left "app#SECRET"             right "app"
brief_url_takes_a_scheme_only_at_the_start           left "/api?token=SECRET&next=https://x.test/p" right "/api"
test result: FAILED. 10 passed; 4 failed
```
Receipts (A/B, campaign, full suite) not re-run, per the note. Load 10 at start.
