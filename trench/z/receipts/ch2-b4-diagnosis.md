# CH2.B4 diagnosis — 2026-11-05 03:10 ET (Z lane)

Branch: `atlas/z-ch2-b4-gcs-null` @ `599b5f93` (red only, no fix, no PR). Base develop `82893eac`.

## What the row said
"`cannot convert null/undefined to object` at getPropertyValue: find which getComputedStyle call returns null/undefined (Chart.js on report.html and github's bundle, S24)."

## What it is
- `HTMLCanvasElement.prototype.getContext` returns `null` for every kind (`crates/rustkit-bindings/src/dom.rs:2098`; the comment there gives github's `getContext("webgl")` as the reason).
- report.html `renderActivityChart`: `getContext('2d')` → null → `new Chart(null)` logs "Failed to create chart: can't acquire context from the given item", and a Chart with no canvas stays in `Chart.instances`.
- `renderProtectionChart`: `new Chart(null)` → the constructor's "Canvas is already in use" check finds the first chart (its canvas is also null) and reads `o.canvas.id` → TypeError. Stack: `at An (inline#2:19:89730)` = the Chart constructor in chart.umd.min.js 4.4.0.
- Boa throws `cannot convert 'null' or 'undefined' to object` for ANY property read on null/undefined (`var u; u.foo` gives the same message), so the message names no callee.
- `loadReport` catches it → "Failed to load analytics data: cannot convert 'null' or 'undefined' to object" in `#error-container`. The top domains and workspace stats never render, because they come after the charts in `renderReport`.

## S24 is not this
S24's suggested red, `getComputedStyle(document.documentElement, '::before').getPropertyValue('content')`, already passes on develop (`"none"`; `::after` none, `::marker` normal, `bogus` "", `::placeholder` a CSSStyleDeclaration). github's throw needs its own stack.

## Red (Chromium 143.0.7499.4, `ch2-b4-oracle-check.mjs`)
| check | develop | Chromium |
|---|---|---|
| `[ctx!==null, ctx.canvas===c, getContext again===ctx, toString]` | `[false,null,true,"null"]` | `[true,true,true,"[object CanvasRenderingContext2D]"]` |
| report.html `[error text, console errors, #stat-trackers, chart1.canvas, chart2.canvas]` | `["Failed to load analytics data: cannot convert 'null' or 'undefined' to object",["Failed to create chart: can't acquire context from the given item"],"311",false,false]` | `["",[],"311",true,true]` |

## Decision needed (Atlas/Pete)
- (A, recommended) a new row, CH2.E10 **canvas 2D**: wire `crates/rustkit-canvas` (1418 lines: paths, state, transforms, gradients, DrawCommand list; no JS bindings, no renderer hook, no glyphs) into bindings and paint. Multi-session. The red above is its first test.
- (B) an interim no-draw context: the charts stay blank, the rest of the report renders. This contradicts `rustkit-bindings/src/web_interfaces.js:8-13` ("CanvasRenderingContext2D … deliberately NOT defined … a constructor that exists but does nothing would send them down the wrong path. Those arrive with real behaviour"), so only on an explicit ruling.
