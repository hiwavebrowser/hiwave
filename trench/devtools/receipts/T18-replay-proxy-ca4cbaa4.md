## T18: `hiwave --replay-proxy <url>` replays a HAR in the real window

Branch `atlas/dt-t18-replay-proxy`, base develop 5e87a184. Red **fe0b2011**, fix **ca4cbaa4**. hiwave-app only. No engine or parity-capture change.

### What changes
- **The flag.** `hiwave --replay-proxy http://127.0.0.1:8989` (or `--replay-proxy=URL`) is the same flag parity-capture has. It is read in `main()` before any view is built (new `crates/hiwave-app/src/replay.rs`). `content_engine_builder()` passes it to `EngineBuilder::replay_proxy`, so every RustKit view gets it. That covers content, chrome and panels.
- **What the engine already did** (`rustkit-net`, unchanged): each request is rewritten to the proxy. The real URL goes in `X-Original-URL` and the real host in `Host`. The HTTP client can connect only to a loopback address on the proxy's port. A request that escaped the rewrite would be refused, not sent live.
- **The launch is refused**, with exit code 2 and a stderr line, when the value is:
  - missing, or followed directly by another `--` flag;
  - not a URL;
  - not `http:`;
  - not a loopback host (127.0.0.0/8, ::1 or `localhost`);
  - given twice.
  The flag is also refused on a build without RustKit content. There, the WKWebView would ignore it and go live. A typo never falls back to a live launch.
- **The no-live guard for ebay/shopify is untouched.** It is not in this repo's app code, and this change does not reach it.

### Tests
- **Red at fe0b2011**, with the parser and the builder hook stubbed. 3 of 5 failed:
  - `a_replay_launch_loads_a_har_page_with_no_request_off_this_machine` (`document.title = ""`). This test uses a loopback stand-in for `har_server.py` that answers by `X-Original-URL`. The page is `http://shop.replay.test/item?sku=7`. Its sheet comes from `cdn.replay.test` and its script from `js.replay.test`. The test checks that:
    - the title is set by the replayed script, and `margin-left: 37px` comes from the replayed sheet;
    - `location.href` keeps the HAR'd origin;
    - the server saw exactly those 3 URLs, each with its own `Host`.

    `.test` hosts do not resolve, so any request that went to the network would have failed.
  - `the_flag_takes_a_loopback_http_url_in_either_form`
  - `a_bad_value_refuses_the_launch_instead_of_going_live`
- **Pins that were green at red:** `no_flag_is_a_normal_launch` and `a_normal_launch_has_no_replay_proxy` (the default builder has no proxy).
- **Green at ca4cbaa4:** 5/5. Full `cargo test -p hiwave-app`: **102/0, 27/0, 1/0, 8/0** (develop had 97 in the bin suite). `check -p hiwave-app` is clean, and the warning count is unchanged at 33.

### Campaign
**26/26, mean 1.073%**, on the parity build. The release path was symlinked to `target/parity/parity-capture`, which was built this session at 06:47 ET, with the no-op cargo shim. The campaign cannot move, because parity-capture and the engine are untouched. The drop from 1.0896% (lane figure at b813ba0c) comes from develop. I did not run a develop arm.

### Known limits (follow-ups, not in this PR)
1. **The shield blocks nothing while replaying.** The interceptor runs after the rewrite, so it sees `127.0.0.1` URLs. The HAR decides what the page gets, and the launch log says so. To fix this, intercept on the original URL before the rewrite. That is an engine change in `fetch_with_inner`, and it would affect parity-capture replays too.
2. **The app has no start-URL argument.** A replay launch restores the last session, and those tabs load through the proxy (404 if they are not in the HAR). The HAR'd page is reached by typing its URL.
3. **The filter-list download is not routed.** It goes through `reqwest` in hiwave-shield, is app traffic rather than page traffic, and runs only when the cached list is stale.

### Not done
- **No real-window launch witness.** This seat needs approval to run a built binary, and even the refusal path (`hiwave --replay-proxy http://www.ebay.com/`) was refused. The row's red ("an app launch with the flag loads a HAR'd page with zero non-loopback requests") is proved in-process with the app's own builder and view, not by launching the app. For Atlas or Pete, in a real window, the steps are:
  1. Start `python3 tools/parity_oracle/har_server.py <har>`.
  2. Launch `hiwave --replay-proxy http://127.0.0.1:<port>`.
  3. Type the HAR's URL.
  4. Check that the server log lists every request, and that `nettop` or the shield count shows no other host.

### Receipt (`scripts/receipt.py`)

```json
{
 "base_sha": "5e87a184",
 "binary": "target/parity/parity-capture",
 "binary_mtime_utc": "2026-11-06T11:47:27.788600Z",
 "binary_sha256": "593409476e5f5447ca52bc8c49299797cb8d4efa069be0bfbf4f2c039e8aa7bc",
 "branch": "atlas/dt-t18-replay-proxy",
 "campaign": {
  "cases": 26,
  "failed": 0,
  "file": "parity-baseline/parity_test_results.json",
  "mean_diff_pct": 1.073,
  "passed": 26,
  "sha256": "1e79f8318cf2a286000f8e761695561bf9c1271371b7b4a196904faf04494d53",
  "timestamp": "2026-11-06T06:48:07.923011"
 },
 "candidate_sha": "ca4cbaa435aedc252b402e8d7bf5932e6e5a500d",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "cargo_lock_sha256": "36360f8f04d56d938a5d58455c21b1feb791b309cc1dc7eddd356856f9a28e0d",
 "chrome_version": null,
 "cpu": "arm",
 "dirty_state": false,
 "effective_engine_flags": {},
 "features": null,
 "host": null,
 "note": "T18: hiwave --replay-proxy; app-only change (hiwave-app), parity-capture and engine untouched, so the campaign measures develop's render path",
 "os": "macOS-26.5.2-arm64-arm-64bit",
 "profile": "parity",
 "raw_runs": [],
 "repo": "https://github.com/hiwavebrowser/hiwave-macos.git",
 "rustflags": null,
 "sccache": true,
 "target": "aarch64-apple-darwin",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "utc": "2026-11-06T11:48:16.143645Z",
 "work_package": "hiwave-app"
}
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)
