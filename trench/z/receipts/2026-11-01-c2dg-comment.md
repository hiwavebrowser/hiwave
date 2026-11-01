## Author, at `68f4cf7b`: the 12:35 order done; the shopify hold is cleared in a capture

**Atlas: this replaces my hold above. Flip and send to R1 when you choose. It has had no review since these commits, and no real-window run.** Your dropdown page from #855 should now paint its panel; that needs your seat.

**Merged:** develop `525f6ec0` (#855).

**Shopify:** in a capture from this build, the sticky header paints and the two black columns over the hero are gone. Still wrong: the logo is black on dark (it only shows now that the header paints), and the paragraph overlaps "AI all-star" (on base too). Frames are private, at the seat.

**#854 R1 finding 1, red `b3baf512` (3 of 75 failing), fix `bbf114fe`:** `held` keys on a containing block for fixed boxes.
- `will-change` holds when it names `transform`, `-webkit-transform`, `translate`, `scale`, `rotate`, `perspective`, `filter`, `backdrop-filter`, `contain` or `transform-style`.
- `contain` holds for `paint`, `layout`, `strict`, `content`. An invalid value leaves the earlier declaration in place.
- All from Chromium 143.0.7499.4, `held2_probe.mjs`.

**Beyond the order:** such a box inside a scroller now carries its fixed and absolute children with the scroller (Chromium: both move by -40 at `scrollTop` 40). It was keyed on a transform only.

**#854 R1 finding 2:** the test for a fixed box in an element scroller with no transform is `a_fixed_box_in_an_element_scroller_stays_put`.

**The two new fields do nothing else.** `will-change` and `contain` set a flag read only by this walk. Neither promotes, clips nor contains anything in layout or paint, so `contain: paint` still does not clip here.

| Gate | At `68f4cf7b`, against develop `525f6ec0` |
|---|---|
| Headless engine | 1436 passed, 0 failed, 14 ignored |
| Layout / bindings / engine lib | 881/0, 428/0, 618/0 |
| `hiwave-app` debug build | rc=0 |
| Campaign | 26/26, 0 moved |
| Declaration census guard | pass, run on the fix before the merge |

Binaries, parity profile: base `c52c13c2ec79...`, candidate `13ead325b229...` (sha256, full values in the hub receipts). Not filled in by `receipt.py` this time.

**20-site A/B, 4 captures per site, then repeats:**

| Row | Read |
|---|---|
| shopify | the mover: 0.81% to 2.83% across on every pair in both runs. 2.02% inside one arm in both runs as well, in the base arm each time and in the candidate arm in the first. Frame read: the header |
| linkedin | 89.90% inside the candidate arm with script records 18 against 6; repeat 0.00% on all pairs |
| bing | 25.40% inside base, then 25.40% inside the candidate on the repeat; varies by run |
| google | 1.53% inside each arm; not repeated |
| lyft | clean first; repeat with arms swapped refused one capture in the second slot, which was base |
| cnn | 30 s limit on all four; at 90 s, 0.03% at most |
| the other 14 | 0.00% on all pairs |

These captures sit at scroll 0, so they say little about what happens once a page scrolls.

**Still not read for `held`, though Chromium holds for them:** `perspective`, `backdrop-filter`, `transform-style`, `content-visibility`.

**Where layout places a fixed box** under its containing block is unchanged: row C10 (m).
