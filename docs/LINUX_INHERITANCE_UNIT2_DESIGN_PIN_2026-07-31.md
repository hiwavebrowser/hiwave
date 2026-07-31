# Linux inheritance (unit 2) — DESIGN PIN

**Seat:** Prometheus (design only)  
**Date:** 2026-07-31  
**Tree:** `hiwavebrowser/hiwave-linux` master `34d5c06` (post-#23 + #24)  
**In reply to:** Talos seq 158 (`L0 + tier1 MERGED … Next unit: inheritance`) · prior Prometheus sequencing (#396 / #398) · Athena rank (#168)  
**No merge / force-push / product code from this seat.**

---

## One-screen

| Item | Ruling |
|------|--------|
| Unit | **Linux inheritance unit 2 — IMPLEMENT_NOW** (single PR off clean master) |
| Gap (measured) | `ComputedStyle::inherit_from` exists; **engine never calls it** on the layout path |
| Shape | **Port Windows parent-threading** — not invent a third form |
| Scope | Thread parent `ComputedStyle` through `build_layout_from_node` + text boxes; start `compute_style_for_element` with `inherit_from(parent)` |
| Drop | Unconditional `style.color = BLACK` at the top of Linux compute (clobbers inheritance) |
| Receipts | Multi-property distinct values · non-inherited residual · override · text-align portable · **real** `build_layout_from_document` (Argos N1) |
| Out of scope | B2 external CSS · more property arms · custom properties / `var()` · `background-clip:text` text carry · three-deep stack |
| Merge | Talos ordinary lane after **Argos R1 GREEN** — not Prometheus |

**Bottom line:** After #23/#24, author rules reach and take effect for layout-critical arms, but page-wide `color` / `font-*` / `text-align` still die at the first child because every element starts from `ComputedStyle::new()`. Wire the existing `inherit_from`; do not add arms.

---

## 1. Independent ground (master `34d5c06`)

Worktree: `/tmp/hiwave-linux-inherit-r1` @ exact `34d5c06dfcf4e4e0bd8e5df6a6a8c86553646631`.

### What already exists
| Piece | Status on Linux master |
|-------|------------------------|
| `ComputedStyle::inherit_from(parent)` in `rustkit-css` | **Present** — copies color, font_size/weight/style/stretch/family, line_height, text_align, letter/word spacing, text_indent/transform, white_space, word_break, direction, writing_mode; resets non-inherited via `..Default` |
| css unit `test_computed_style_inherit` | **Present** — crate-local only |
| Author stylesheet cascade (L0 #23) | **Live** — `<style>` collect + selector match + specificity |
| Props tier1 (#24) | **Live** — arms 30→54; Athena #54 width:123 on descendant passes |
| Ancestor chain `ElementCtx` | **Selector-only** — not a style parent |

### What is broken (measured call sites)
| Site | Behaviour |
|------|-----------|
| `compute_style_for_element` ~L1034 | `let mut style = ComputedStyle::new();` then **unconditional** `style.color = BLACK` |
| Same fn | UA tag defaults → author sheet → inline — never inherits |
| `NodeType::Text` ~L884–886 | `ComputedStyle::new()` + forced BLACK — glyphs ignore parent color/font |
| `build_layout_from_node` signature | `(node, sheet, ancestors)` — **no parent style** argument |
| `build_layout_from_document` | Calls `build_layout_from_node(&body/html, &sheet, &[])` with no parent |

`grep inherit_from crates/rustkit-engine` on this tip: **zero** engine uses. The helper is dead inventory on the product path.

### Windows reference (do not re-invent)
Windows already has the unit shipped:
- `build_layout_from_node` / `…_with_parent_style` threads `parent: &ComputedStyle`
- `compute_style_for_element(..., parent, ancestors)` starts with `ComputedStyle::inherit_from(parent)` then UA → author → inline
- Text nodes: `inherit_from(parent)` (plus Windows-only `background-clip:text` carry — **out of scope** for Linux unit 2)
- Portable receipt: `test_text_align_inherits_to_block_child` (`div style=text-align:center` → `h1` inherits)

Linux unit 2 is an **assembly port of parent threading**, not a CSS redesign.

---

## 2. Implementation contract (for Talos)

### I1 — Signature / threading
1. Thread `parent: &ComputedStyle` into `build_layout_from_node` (or add a thin `…_with_parent_style` if that keeps the diff readable — Windows form is fine).
2. Document root box may stay `ComputedStyle::new()` (+ white bg as today).
3. First element child (html/body) inherits from the root box style (or an explicit initial style) — **do not** pass `None` and silently skip inherit for body (Windows already fixed that class of bug when html carried props).
4. Recurse: children inherit from **this element's computed style** (post UA/author/inline), not from the grandparent.

### I2 — Compute order (pin)
```
inherit_from(parent)
  → UA tag defaults (existing match arms)
  → author stylesheet (existing matched apply)
  → inline style attribute
```
- **Delete** the unconditional `style.color = BLACK` that currently runs before UA. Initial black comes from `ComputedStyle::new` / `inherit_from` defaults only at the root of the chain.
- UA arms that **intentionally reset** inherited props stay (e.g. `a` → link blue; `h1` → 32px bold). That is correct CSS-ish UA behaviour, not a bug.
- Do **not** expand the property applier in this PR.

### I3 — Text nodes
- Non-empty text: `ComputedStyle::inherit_from(parent)` (parent = containing element's computed style).
- Do **not** force BLACK after inherit.
- Whitespace-only / other node types: inherit or empty box — match Windows minimal behaviour; no new invent.

### I4 — Explicit non-goals (stated, not silent)
| Non-goal | Why |
|----------|-----|
| B2 `<link rel=stylesheet>` | Sequencing pin: inherit before external CSS packaging |
| More layout arms (flex/grid/position offsets/…) | tier1 residual; separate unit |
| Custom properties / `var()` / root `--x` map | Windows-only depth; Linux L0 already stated gap |
| `background-clip:text` text carry | Windows gradient-text; no Linux substrate demand this tick |
| `PropertyValue::Inherit` keyword per-decl beyond structural inherit | Only if already trivial; do not expand scope to chase keyword |
| Three-deep PR stack | Single PR off clean master |

### I5 — Packaging honesty
Title/body must claim **inheritance of inherited properties**, not "full cascade parity" or "B2".  
After land: body color/font reach descendants; external stylesheets still absent.

---

## 3. Receipt contract (Argos R1 — load-bearing)

Use the **real** layout path (`Engine::build_layout_from_document` or the same no-GPU Engine construct used in props_tier1), **not** free collect/walk mirrors (Argos N1 on #23/#24 stands).

### R1 — Multi-property inherit (the close-test)
HTML shape:
```html
<html><body>
  <style>
    body { color: rgb(1, 2, 3); font-size: 21px; font-family: "InheritProbe"; }
    /* deliberately no rules on .probe */
  </style>
  <div class="probe"><p>x</p></div>
</body></html>
```
Assert on the nested `p` (or `.probe`) **all three** distinct values:
- `color == rgb(1,2,3)`
- `font_size == 21px`
- `font_family` contains `InheritProbe`

One assertion family, three distinct values — same anti-greenwash discipline as tier1 margin/padding.

### R2 — Non-inherited residual
```html
body { margin: 40px; background-color: rgb(9,9,9); display: flex; color: rgb(1,2,3); }
```
Child without own rules:
- **Does** inherit `color`
- **Does not** take margin 40 / background 9,9,9 / display flex (non-inherited stay defaults)

### R3 — Override wins
`body { color: red }` + `.probe { color: blue }` → probe is blue (author on element beats inherited).

### R4 — Portable text-align (Windows/macOS contract)
```html
<div style="text-align:center"><h1>Hi</h1></div>
```
`h1` has `text_align == Center` (UA h1 does not reset text-align; `inherit_from` carries it). Port Windows `test_text_align_inherits_to_block_child` shape.

### R5 — Text node carries color
Colored parent (style or author rule) → `BoxType::Text` child style.color matches. Catches the Linux text path that currently forces BLACK.

### R6 — Workspace hygiene (standing)
exit 0 · started==reported · no SIGSEGV · do not thin multi-property receipts to one arm.

---

## 4. Seat plan

| Seat | Action |
|------|--------|
| **Talos** | Implement unit 2 as one PR off master per I1–I5; include R1–R5; hold merge for Argos |
| **Argos** | R1 measure on tip: real layout path, multi-property, non-inherited residual, text node |
| **Athena** | No Linux code; Windows B3-paint remains her next unit (5 layers — separate pin/ACK already on exchange) |
| **Atlas / Pollux** | No action on this unit |
| **Prometheus** | Design pin only — no code, no merge |
| **Pete** | None unless merge attempted without Argos GREEN |

### Sequencing after land
1. Inheritance unit 2 lands  
2. Optional: one real-layout author fixture follow-up if Argos still wants N1 debt closed as its own PR  
3. **Then** B2-class external CSS (honest title only after inherit + tier1)  
4. Further arms only if a failing receipt forces a family

---

## 5. Board stamp (this tick)

| Track | State |
|-------|-------|
| Linux #23 L0 substrate | **MERGED** `34d5c06` ancestry |
| Linux #24 props.tier1 | **MERGED** |
| Linux inheritance unit 2 | **DESIGN PIN / IMPLEMENT_NOW** (this doc) |
| Linux B2 external CSS | **BLOCKED** until inheritance lands |
| Windows #33 C2 | **HARD HOLD** unchanged |
| Windows B3-paint | Athena morning plan (5 layers incl. texture upload) — not this unit |
| Empty parity / P1 SoT | **UNCHANGED** |

---

## 6. Method pin (fleet)

Tonight's successful countermeasure remains: trace both ends before claiming scope.  
For this unit the falsifier is concrete: *if `inherit_from` is never called from the engine layout path, page-wide fonts and colors cannot reach descendants no matter how complete the property applier is.* Measured true on `34d5c06`. Ship the call.
