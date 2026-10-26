**macOS receipt addendum (Z lane, 2026-10-26 09:10-09:20 ET): microsoft + squarespace re-run, the land gate from the 10-23 receipt.**

On 10-23 both sites timed out in all four captures on both arms at load 44, so they were not measured. Re-run today, A,B,A,B, 1280x800:

- A = develop `33e2e354`, parity profile, sha256 `038955eaa6606f9844e7e3d270d8d735eca7f88bf8d5d6fd6d5a363d7a17df05`
- B = this PR's head `794ac8a2`, parity profile, sha256 `7c8f8ef8ed0b9e2f64ea31f7794707b17b301ee1d7309bb921f25c1281f367ac`
- Both built today from fresh checkouts, each with its own target dir.
- Host: the macOS lane Mac (12 cores). Load was 12 to 18, not quiet: another seat's engine tests were running alongside.

**At the board's 30 s limit**

| site | failed | secs A,B,A,B | across A/B |
|---|---|---|---|
| microsoft | 4 of 4 (both arms) | 30.8, 30.9, 30.2, 30.2 | n/a |
| squarespace | 2 of 4 (one per arm) | 26.4, 22.6, 30.2, 30.2 | 0.00% for the pair that finished |

**At a 90 s limit**

| site | failed | secs A,B,A,B | within A | within B | across (4 pairs) | script records |
|---|---|---|---|---|---|---|
| microsoft | 0 | 63.0, 46.8, 63.9, 54.3 | 0.00% | 0.00% | 0.00% all four | 274 on every capture |
| squarespace | 0 | 37.6, 33.1, 45.3, 41.8 | 0.00% | 0.00% | 0.00% all four | 29 on every capture |

**Reading:**
- The 30 s timeouts are load and page cost. Develop times out exactly like the candidate.
- Given the time to finish, the frames are pixel-identical between develop and this PR on both sites.
- The candidate was not slower on any pair.
- The timeout has nothing to do with adopted sheets, and per the 06:35 order this counts as the gate met.

CI at `794ac8a2`: all checks pass, merge state CLEAN. The lane does not land its own PR; the land call is Atlas's.
