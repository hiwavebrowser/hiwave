**D0 root replace (Atlas 10:25 note), Z lane 2026-10-26 15:50-16:25 ET**

Branch `atlas/z-root-replace` (no PR), from develop `7b560fe1`:
- `97254ab0` test, red: three bindings tests.
  - `a_document_takes_a_new_root_once_the_old_one_is_removed`: remove `<html>`, append a new html/head/body. `documentElement`/`head`/`body` resolve to the new tree, `document.head.appendChild(script)` works, and the doctype stays first.
  - `replace_child_swaps_the_document_root`: `document.replaceChild(newHtml, documentElement)`.
  - `a_document_refuses_a_second_root_text_and_a_root_before_its_doctype`: these throw HierarchyRequestError: a second root, `replaceChild` of the doctype by an element, text, an element before the doctype, and a fragment with two elements. A comment is accepted.
  - All three are red on develop: `pre_insert` refused every Document parent, the comment included.
- `5042ac01` fix: `pre_insert` takes a Document parent under DOM §4.2.3 step 6 (`document_child_check`). `replaceChild`/`replaceWith` pass a flag so the "replace" rules apply, which do not count the child being taken out.
- `8232868c` merges develop `68f4c8e1` (#782 landed), with no conflicts.
- Gates: rustkit-bindings 380/380, rustkit-dom 78/78.
- **Campaign at `8232868c` vs develop `68f4c8e1`:** 26/26 on both arms, every case has the same diff count, 0 movers (candidate sha256 `3f08fcea...`, develop `99137129...`, parity profile, rust 1.91.0).
- **20-site A/B, A,B,A,B, no mover:**
  - github and cnn re-run at 90 s: 0.00% x4.
  - microsoft at 90 s: develop's first capture is the outlier (275 records, 86.5 s); develop's second capture equals both candidate captures at 0.00%.
  - yahoo and walmart each had one odd candidate capture; the re-run is 0.00% candidate-vs-develop on both.
  - google's 4th capture is a served variant, as in the #782 run; linkedin is its 6-record variant.
  - Tables: `2026-10-26-d0-rr-ab-*.txt`.

**yahoo `diagnose`** (develop `7b560fe1`; each arm a fresh build, parity profile, live 25 s):

| arm | document | elements | first viewport | errors |
|---|---|---|---|---|
| develop | 2366 px | 1224 | text 24, images 25 | 2x SyntaxError at 7730:1:6278 (innerHTML'd scripts) |
| develop + #777 `7e059566` | 800 px | 77 | empty (R10) | TypeError 7730:1:6198, TypeError webpack:1:13468 |
| develop + #777 + root fix | 800 px | 77 | empty (R10) | the same two TypeErrors |

**The root fix does not move yahoo.** Per the order, I logged instead (a throwaway instrumented build, not pushed):
- Every `document.head` read that answers null is printed with the document's children: **zero in the whole load.** The two TypeErrors happened in the same run (t = 10.5 s and 12.0 s). So "document.head is transiently null" is **refuted**.
- The raw message: `TypeError: cannot convert 'null' or 'undefined' to object` (Boa's to-object failure).
- The source at the two sites:
  - Next's `appBootstrap` `__next_s` loader: `let u=document.createElement("script"); r&&setAttributesFromProps(u,r), t?(u.src=t,u.onload=..,u.onerror=n):..., document.head.appendChild(u)`.
  - webpack's chunk loader: `b.src=..; ...; b.onerror=i.bind(null,b.onerror), b.onload=..., t&&document.head.appendChild(b)`.
  - Boa's column falls on the `onerror` sub-expression, but `onerror` is a plain property in the bindings (no accessor anywhere), so the column is approximate.
- What both sites share: a src-bearing script element, then `document.head.appendChild`. The error_stack holds only page frames.
- **Lead: the throw is inside the bindings' own script-insert path** (`HOOKS.scripts.inserting` / the `src` setter / `setAttributesFromProps`' attribute writes). Bootstrap frames are hidden from the stack. Not proven.
- One stray finding: one `document` getter call answers null on a generation miss (`gen 0`), once per load. That getter answers null for EVERY property when the wrapper's generation is stale (`dom.rs`, the `document_for` else branch).
