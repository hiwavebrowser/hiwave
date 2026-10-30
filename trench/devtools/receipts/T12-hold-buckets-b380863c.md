Pete's 18:00 hand-test log had `other_ms` at 88% of a 36.8 s microsoft load hold and 97% of a 23.2 s ebay one, so the cost of a slow load was the one bucket with no name. This names it. Logging only: no engine behaviour changes.

**Acceptance is not finished.** The row asks for hand-test log lines (real window) for microsoft and ebay. This session has headless lines only: real-window runs are barred from 17:00 to 23:00, and the plan's rules forbid this seat loading ebay live. See "What is still owed".

## What the hold line says now

Between `present_ms` and `other_ms`, which stays last:

| field | what it counts |
|---|---|
| `script_ms`, `script_turns`, `script_longest_ms`, `script_stopped` | script turns: compile, run and microtasks, with count, longest, and turns the watchdog stopped |
| `parse_ms` | `Document::parse_html` |
| `style_ms` | parsing fetched stylesheets |
| `doc_fetch_ms` | the document's own fetch and body |
| `sheets_ms`, `fonts_ms`, `images_ms` | those phases of the subresource load (`images_ms` also holds images scripts added) |
| `script_fetch_ms` | the page's scripts still arriving after the subresources were done |
| `script_net_ms` | the script phase awaiting fetch/XHR, imports and inserted scripts |

**How the time is split:** one moment is charged once, to the innermost bucket. A script turn inside `script_net_ms` takes its time from it, and a relayout stage inside any bucket comes off that bucket, so a forced layout is `layout_ms`, not script as well. `other_ms` is now the hold less the five relayout stages and the buckets.

## Headless lines (parity build, b380863c, `--live-ms` 8000; load's fields, zero fields left out)

```
microsoft  entry=load ms=43378 build 2683 layout 233 snapshot 553 render 25 script 5178 (116 turns, longest 1682, 0 stopped) parse 11 style 13 doc_fetch 584 sheets 2351 fonts 728 images 4672 script_fetch 21240 script_net 4977  other_ms=128.2
cnn        entry=load ms=28891 build 7748 layout 7485 snapshot 1231 render 123 script 3898 (16 turns, longest 3537, 0 stopped) parse 127 doc_fetch 741 sheets 0.5 fonts 2062 images 3884 script_fetch 116 script_net 496  other_ms=960.3
yahoo      entry=load ms=12450 build 97 layout 29 render 61 script 375 (59 turns, longest 83, 0 stopped) parse 27 style 15 doc_fetch 1669 sheets 2936 fonts 5990 images 1077 script_fetch 54 script_net 0.1  other_ms=118.9
```

| site | load hold | other_ms | named share |
|---|---|---|---|
| microsoft | 43.4 s | 128 ms | 99.7% |
| cnn | 28.9 s | 960 ms | 96.7% |
| yahoo | 12.5 s | 119 ms | 99.0% |

Before, from the row (real window, develop 8f0488c6): `ms=36834 ... other_ms=32438.2` on microsoft and `ms=23169 ... other_ms=22551.6` on ebay. Real window against headless, so this is not a like-for-like before/after.

**What it already shows:** on microsoft the biggest cost this run was waiting for scripts to arrive (21.2 s). An earlier run at the same code had that at 2.4 s of 22.7 s, so it swings with the network, at load 7+. Script itself was 4.4 to 5.2 s, and cnn's cost is build + layout (15.2 s of 28.9 s). One run each, not a measurement of any site.

## What is still owed

- **Microsoft, real window:** the next slot at or after 23:00 (00:35), if the locks are free.
- **ebay, real window:** from Pete's next hand-test log. The line is in the app's log with no extra flag.
- Neither is proven until then. The real window polls a load in 8 ms slices, so time between polls lands in whichever bucket was open, or in `other_ms` if none was.

## Limits

- **`other_ms` on a tiny page in a debug build:** about 700 ms of an 876 ms test load stayed unnamed, and I did not find what it is. In a parity build `other_ms` was 119 to 960 ms across the three heavy pages above. Page setup (a new JS context per navigation) is my guess, not a finding. That engine test therefore pins the named buckets, not a bound on `other_ms`.
- **Live turns** get script turns and relayout stages, not network settling (it stays `other_ms`). The row is about load holds, and on these lines live-turn `other_ms` is small (10 to 634 ms).
- `sheets_ms`, `fonts_ms` and `images_ms` run in sequence alongside the script fetches, so `script_fetch_ms` is only the tail after them, not how long scripts took to fetch. A script's fetch time stays in the `script` event record.
- A wait is wall clock, whatever else the thread did between polls.
- `style_ms` is external sheets only; parsing an inline `<style>` is not in it.

## Red first

db247d10 holds the tests over no-op stubs: 6 failed, 10 passed in `wgate`. Then b380863c, with no new test. While making them green I replaced their upper time bounds, which failed on a sleep overrun at load 7, with "the buckets sum to no more than the wall clock"; a double charge fails that. One existing test's expected line gained the new fields. Those tests failed at db247d10 because no time was charged at all, so I also checked the guard by mutation: without the subtraction, `a_relayout_stage_inside_a_bucket_is_not_counted_twice` fails. `a_nested_bucket_...`'s sum check has not been seen failing on a double charge.

## Evidence

- `cargo test -p rustkit-engine --features headless --lib`: 1269 passed, 0 failed, 10 ignored, at b380863c.
- `cargo test -p rustkit-engine --features headless --lib wgate`: 16/0.
- `cargo check -p hiwave-app`: clean.
- Campaign 26/26, mean 1.1095%, the same mean as #835's and #838's receipts.
- No A/B, as the row says. Cost per hold: two more `Instant` reads per bucket switch and per script turn (microsoft: 116 turns). Not measured separately.

## Receipt

```json
{
 "base_sha": "8f0488c6",
 "binary_sha256": "744ee1c0ed78a3aa6d09e5dca4f3c0a2b54dd3c18044d451b0145efdb2c7b204",
 "branch": "atlas/dt-t12-hold-buckets",
 "campaign": {"cases": 26, "failed": 0, "mean_diff_pct": 1.1095, "passed": 26,
  "sha256": "e3c0acf345e4729e1dcd98c0a068f5c7218b5dab92d71ae4de0c962d9fa64a2e"},
 "candidate_sha": "b380863c623f6135b556f65e431358ed0d4d5afd",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "dirty_state": false,
 "profile": "parity",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)"
}
```

R1: Prometheus or Atlas.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
