# T9: yahoo exit-metric run, develop 702154ef (2026-10-30 06:35-06:50 ET)

`parity-capture` built with the parity profile through z-cargo. Plan row said 3c6b170e or later; 10-30 01:00 said 47fdcb41; the head at checkout was 702154ef and that is what ran.

## Verdict: the exit metric is NOT met at this head (Atlas scores)

**`diagnose` alone leads a reader to the wrong answer.** Read honestly from the output, the answer is "the feed is not blank": 800..1600 holds 56-60 text boxes and 36-40 image boxes, no blank-band rule fired, and the top line is one logged Error. The reading took under a minute per run, so the time limit is not the problem. The answer is.

**What the page actually does (hand check, outside the score):** one 25 s and one 70 s frame at 1280x2400. Under "For You" there is one image strip, then grey skeleton rows to the bottom of the frame. They were still skeletons at 70 s, so waiting longer does not fill them. Nothing failed on the network in the 70 s run. With error text kept locally, the "logged Error" is **React #418** (hydration failure), logged at about 25 s.

**Not established:** that #418 causes the skeletons. They coincide; no record links them. Also, these frames used a 2400 px viewport, while the three diagnose runs used 800. The tall viewport puts the feed on screen, which argues against "it never scrolled into view" for that run, but the 800 px case was not framed.

## The three runs (1280x800, --live-ms 25000, no shield)

| run | capture wall | reading | document | elements | y 800..1600 | y 1600..2400 | covering | top line | R5 "then N fetch" |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 33 s | < 1 min | 2362 | 1334 | text 56, img 36 | text 8, img 5 | none | R5 logged Error, chunk 87c73c54:1:37798 | 2 |
| 2 | 31 s | < 1 min | 2366 | 1129 | text 60, img 40 | text 4, img 1 | 2 boxes 31.7% | same | 1 |
| 3 | 33 s | < 1 min | 2390 | 1135 | text 60, img 40 | text 4, img 2 | 2 boxes 31.7% | same | 0 |

Readings were by an agent that already knew the page's history, not by someone new to it. Load during the runs was 6-8 (1-minute average).

R4 lines below the top one: "no page script ran until t=5.2-6.0 s" in all three; run 1 also had 20 script requests still open at capture end; run 3 had three chunks waiting 6.7-6.8 s for a turn.

## Gaps: what the tool should have said (T10 candidates)

Ranked by how much each changes the answer. Log facts below come from the runs' `events.jsonl`, read by hand.

1. **T4, placeholders. This is the one that flipped the answer.** Should say "y 1600..2400: N painted boxes with no text and no image (skeleton?)". Bands count an `img`/`svg` box or a text leaf whether or not it shows anything (`report.rs:243-248`), and nothing counts empty painted boxes. Carrier: `Band.empty_painted`, plus a new rule ranked with R9/R10. Stronger variant: per-band ink from the frame.
2. **T4, the R5 "then N fetch" clause reads as evidence and is not.** It gave 2, 1, 0 for the same error, because the error lands 24-28 s into a fixed window and the clause counts what fits after it. The same logs hold 8, 9 and 10 fetches to www.yahoo.com *before* the error. Its comment says "the feed never asked for its data", which is an older page's reading. Should say the time and both counts: "at t=24.4 s; 9 before, 1 after". Carrier: `report.rs:597-610`.
3. **T1 + T4, a library's error code is hidden by the shape rule.** Should say "React #418 (hydration failure)". It printed "logged Error"; the record holds `<Error message len=191>`. Carrier: a shape that keeps only a matched `Minified React error #N`. **Needs a ruling, see below.**
4. **T4, no "was the page finished" line.** The last relayout was 90-99 ms before capture end in all three runs, run 1 had 20 requests open, and the Trending block appeared only between 30 s and 70 s. Should say "still changing at capture end: last relayout N ms before; K requests open". Carrier: new `settled` report field from `relayout` and open requests.
5. **T4, "Not checked:" prints empty while the shield was never installed.** The check at `report.rs:538` asks whether the `blocked_by` field exists; it does, as null, on every failure. So "no shield blocks" reads as checked when no block was possible. Should say "R6 shield: not installed, nothing could be blocked". An empty section should also not print a heading. Carrier: a report flag set from `--shield`.
6. **T4, overlap is not reported.** In the frames the footer is painted over the feed and "Advertisement" labels sit over content. `covering` did not name these, and its two 31.7% boxes appear in runs 2-3 and not in run 1, with nothing saying why. Should say "in-flow text boxes overlapping: N, first at y=...". Carrier: new overlap count per band. In the frames the content also runs past the right edge, not measured.
7. **T1/T4, an own-site `console.error` with a string argument is dropped.** Run 3 logged `<string len=161>` from the homepage layout chunk at 23.9 s, before #418, and R5 never showed it, because R5 reads only records with `error_stack` (`report.rs:576-579`). Should list it as "logged string in <own-site script>". The layout chunk's error did not recur in the 70 s run, so it is intermittent. The consent script's string error, in runs 2-3 and the 70 s run, is dropped the same way.
8. **T2 + T3, no link from data to DOM.** I could not tell which of the 34 fetches should have filled the feed, or whether its answer was used. The records stop at status and size. Carrier unknown; this is the hardest one and needs a design note.

Questions 1-4 and 6 had to be answered by frame or by hand-reading the log. 5 and 7 came from reading `report.rs`.

## G1: 50x loop, no leak found

- `fifty_rounds_on_one_policy_leak_no_slot_and_no_record`: one policy, both caps at 1, 50 rounds, each finishing one request and dropping one queued and one just started. Passed; exactly one terminal record per request. **Red by mutation:** a forgotten page permit fails it at round 0.
- `fifty_loads_on_one_view_keep_their_record_counts`: real `load_url` 50 times on one headless view, each page starting 4 fetches, a slow fetch and an inserted script. Every document held 7 requests and 6-7 responses; no ring loss. Passed in 67.7 s. Not separately mutation-tested; a policy lasts one load, so this one pins stable counts, not permits.

Limits: the plan's "T8 fixture" is not one named fixture, so these two stand in for it. Both ran as one debug pass at default 2 workers, not repeated. They found nothing, so per the plan there is no PR; the text is in `T9-g1-loop-tests.rs.txt`.

## Not run

No engine code changed, so no `scripts/receipt.py`, no 26-case campaign, no PR. No full engine suite either. Frames and event logs were not committed.

## Decisions for Atlas

1. **Rescore or reword the exit metric?** Its premise, "blank", is now "skeletons that never fill", which is still the user's problem. Recommend keeping it and scoring it against skeletons; it stays unmet until `diagnose` says so.
2. **T10 scope.** Recommend gaps 1, 2, 4, 5 as one PR in `report.rs` (no engine change, cheap), then 6 and 7. Gap 8 gets a design note only if those leave the question open.
3. **Shape-rule exception for gap 3 (Pete's rule).** Recommend allowing only the matched `Minified React error #N`: fixed library text, no page data. Without it the tool cannot name a hydration failure.
4. **Z lane:** yahoo's feed stays on skeletons with #418 logged, no failed requests. This lane fixes no sites, so it is yours to route.
