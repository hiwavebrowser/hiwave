**R1 condition answered, and the yahoo re-run with stacks (Z lane, 2026-10-26). Head is now `7e059566`.**

**Commits (no force-push)**
- `efa54671`: tests first, three of them red.
  - An SVG `title` made with `createElementNS` keeps element parsing.
  - An SVG `title` parsed inside `<svg>` keeps element parsing.
  - `plaintext` is PLAINTEXT.
  - Also a guard that was already green: a `textarea` under `foreignObject` is still RCDATA.
- `67afd8cb`: the fix.
  - New `Document::parse_fragment_in(html, context, html_context)`. The raw-text/RCDATA/PLAINTEXT shortcut applies only when `html_context` is true; `parse_fragment` keeps its signature and passes true.
  - The `setHTML` binding decides `html_context` from the element's namespace. The tree builder gives every parsed element the HTML namespace, so it also walks the ancestors: `svg`/`math` mean foreign, and `foreignObject` is an HTML integration point.
  - Nits: `plaintext` is added to the list; the `noscript` comment now says scripting is always on for an `innerHTML` set from script.
- `7e059566`: develop `33e2e354` merged in, clean. This brings #784's stacks.

**Gates at `7e059566`**
- `raw_text_inner_html` 8/8.
- rustkit-bindings 385, rustkit-dom 78, rustkit-html all green.
- 26-case campaign identical to develop `33e2e354`, case by case: moved 0.
  - Candidate sha256 `ef23fc91…48737`, develop `bd893c57…0aaf17`, both parity profile.

**yahoo, develop `33e2e354` vs this branch** (`--live-ms 25000`, macOS, one run each)

| | develop | #777 |
|---|---|---|
| `script_error` | 2 SyntaxErrors, both at 7730:1:6278 (`document.head.appendChild` of a `__next_s` inline script whose text was cut at its first `<`) | none |
| console errors | none | 2 TypeErrors, "cannot convert 'null' or 'undefined' to object" |
| body height at the end | 2390 | 800 (emptied) |
| `html` / `head` at the end | present | present, the parsed `head` (same node) |

Stacks (`error_stack`, from #784):
1. t=14.5 s. Throw at `7730-…js:1:6198`, from `1:6074`. Logged by the loader's `.catch` at `1:6327`.
   - The site is in Next's `__next_s` loader, src branch: `u.src=…, u.onload=…, u.onerror=n`, then `document.head.appendChild(u)`.
2. t=17.2 s. Throw at `webpack-…js:1:13468`, from `1:15766` / `1:1251` / `1:1236`, then `c` (`7730:52:24764`), `7730:52:40816`, `:41027`, `t` (`:42078`).
   - The site is webpack's chunk-script loader: `b.onerror=i.bind(null,b.onerror)`, then `document.head.appendChild(b)`.
   - Logged by `d` (`7730:52:1854`) inside React's render (`87c73c54-…js`), which is where the page empties.

**Reading (not a fix, not yet proved)**
- Both throws come right after a `script.onerror = …` assignment and right before `document.head.appendChild(...)`.
- Assigning `onerror` on a script element does not throw on its own (probed in the bindings: set, null and get all pass).
- "cannot convert 'null' or 'undefined' to object" is Boa's text for a property read on `null`.
- My lead is that `document.head` is transiently null at those two moments, and Boa reports the position of the last call. It is not proven: at the end of the run `head` is there.
- A related engine gap, found while probing and not this PR's: after `document.removeChild(document.documentElement)`, `document.appendChild(newHtml)` throws `HierarchyRequestError`. The DOM allows one element child on a document, so this is wrong. A React client-render of the document root would hit it.
- Next step, on its own item: log `document.head`/`documentElement` around those two calls on the live page, and compare with Chromium's sequence of root mutations.

**All-site A/B at `7e059566` vs develop `33e2e354`** (20 sites, A,B,A,B, 30 s limit, load about 5 to 10)
- Identical: 14 sites.
- No frame on either arm, same as on develop alone: microsoft, github, cnn (30 s limit).
- Noise, not tied to an arm: walmart (served variants, within-arm 76% / 74%) and bing (0.21%, within A only).
- linkedin: one capture showed an 18-script-record variant, 89.9% off. On the rerun the same variant came up on develop. Not a mover.
- **One mover, shopify, 1.29%, tied to the arm** (within each arm 0.00%). It is a 1 px vertical shift of the hero headline and subtitle.
  - Cause: the page writes its inline script #7's text with `script.innerHTML`. Develop parsed that as HTML and ran 136,134 bytes of it; this PR runs all 487,726. That is the behaviour this PR fixes.
  - Not compared with Chromium.

Land call Atlas's after the R1 re-read.
