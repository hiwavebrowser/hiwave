## #786 cnn cost: where the extra forced layouts come from (22:05 note, item 2)

Head unchanged: `ce830b72` (no push this session). Fresh worktree, `--profile parity`, one cnn run with `RUST_LOG=rustkit_engine=debug,rustkit_bindings=trace`, load 11-13. Tool: hub `trench/z/tools/dirty_census.py` (groups the bindings' `DOM write dirtied the page` trace lines between consecutive `Forced layout` lines; write shapes only, no page text).

**72 forced layouts again (as on 10-27), 167-179 ms each.** What dirtied each one:

| forced layouts | preceded by |
|---|---|
| #2-#24 (23) | one `setAttr div class` each: the header hide loop |
| #26-#37, #43-#51, #63-#71 (30) | one `setAttr div style` each: the same kind of loop on inline style |
| #25, #28-#29, #38, #42, #52, #60-#62 (9) | batches of `style` writes on `div`/`a`/`nav`/`header` (one with 147 `div class` writes) |
| #53-#59 (7) | a node inserted into or removed from `body`, with writes to the detached node before insertion |
| #0, #39-#41 (4) | `head` inserts (scripts/links), a `li class`, `div` inserts |
| #1 (1) | 215 x 7 `data-zjs-*` attribute writes on links, nothing else |

**Chrome 148 writes the same sequence.** A MutationObserver installed before the page's scripts (pinned Chrome, same URL) sees a first run of **24** `div class` writes, then `div style` runs of 16, 9, 7, 10, 9, 11, ... Our 23 class-loop forced layouts plus #1 line up with Chrome's 24. So we do **not** iterate more than Chrome. Honouring `display: contents` lets the page's measure-and-hide loops run as written. Chrome also lays out for each read after a write; it's just cheap there.

**So the +4.3 s (72 vs 45 at ~170 ms) is the cost per forced layout, not the count.**
- (b) "don't mark writes no rule reads" can drop only #1, about 1 of 72 (~0.17 s). Not worth a change on its own.
- Writes to detached nodes are always followed by an insert in the same batch, so skipping them saves nothing.
- The engine's script-write incremental restyle is still "logged only" (`relayout`'s `would_path`). The forced path has nothing ready to reuse.

**Cutting it needs one of:**
- (a) an incremental forced build: restyle only the written element and its subtree/siblings from the `MutationLog` + `InvalidationIndex` and reuse the rest of the tree;
- (c) a cheaper full build (cascade + box is ~83 ms of the ~170).

Both are multi-session. **Decision for Atlas:** accept #786 at cnn 1.23x with this explanation (the frame is right and every run finishes, max 24 s), or hold #786 behind (a). Campaign + 20-site A/B at the head are owed either way, once that's decided.
