## CH3.A6b: resource and page URLs on info/warn lines are scheme, host and path

Follow-up to #932 (CH3.A6), from its review. Signed CDN URLs carry tokens in the query; these lines logged them at info/warn, which is the default log.

**Red first** (`37544656`): `resource_url_log_tests` loads a local page whose stylesheet, image, SVG, web-font and page URLs carry a marker in the query and fragment. It also loads a 204 page and a 404 error page. On develop, 9 info/warn lines carry the marker (and 11 with the 204/404 loads). Both tests also check that each guarded line was logged, so a silent pass can't hide a missed line.

**Fix** (`dd88c665`):
- `url_for_log` moves from rustkit-engine (private) to rustkit-net as `pub` (same body, same unit test). It gains `str_url_for_log` for text that may not parse as a URL, such as an `@font-face` `src` list or a renderer image key: each `?…`/`#…` run is cut at the next `)`, quote, comma or space.
- Lines routed:
  - engine: Loading/Failed external stylesheet (6), Loading SVG image + its failures (6), Loading image, image budget, image-as-SVG, Failed to load image, `@font-face: source not loadable` (src list), Loading web font, Web font not loaded, `Navigation answered with no content`, `Showing the body of an error response`
  - presenter: three image warnings
  - rustkit-net: `Request blocked by interceptor` (2; shield-blocked tracker URLs carry queries), `Starting download` (whole URL now on a debug line beside it)
  - hiwave-app: the two `Popup blocked` lines go through `page_url_for_log`, so the whole URL still shows under `HIWAVE_DEBUG=1`/`HIWAVE_TEST_HOOKS=1`, as in #932
- Debug lines keep the whole URL (unchanged).

**Not in this PR (disclosed):** `NetError`/`HttpError` Display strings (`Invalid URL: {0}`, `Request failed: {0}`) are printed via `?e` and may embed a URL in some error paths. I didn't audit them. `hiwave-shield` `Failed to create request for {url}` (warn, rare) is not routed: the shield crate has no helper and doesn't depend on rustkit-net. The relayout summary line already used `summary_url` (origin + path).

**Narrow runs** (full gates in batch):
- `rustkit-engine --features headless --lib resource_url_log_tests url_for_log`: 3/3 (red 0/2 at `37544656`)
- `rustkit-net --lib`: 107/0
- `cargo check -p hiwave-app --tests`: ok
- The real-window driver's only reader of these lines (`driver.py:695`) matches the message text, not the URL.
- This is a log-only change with no pixel, fetch or script behaviour change, so I ran no campaign or A/B.

Base `33f4aa93` (develop). Candidate `dd88c665`. Toolchain: rustup 1.91.0 / stable, aarch64-apple-darwin. Builds through z-cargo (lease + sccache), debug profile. Host: macOS seat, load ~10-15.
