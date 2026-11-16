# Wanted: Parity Tests

> **Status note, 2026-11-16.** This page was written in January 2026. Its parity percentages, phase labels and dates describe the project at that time and have not been re-measured. For current, sourced figures see [Recent progress](https://github.com/hiwavebrowser/hiwave/blob/master/docs/PROGRESS-2026-11.md).

These are specific test cases we need to improve rendering parity. Pick one and submit a PR!

## Priority Legend

- **!!!** Critical - Blocking 80% milestone
- **!!** High - Significant parity impact
- **!** Medium - Would help but not urgent

---

## CSS Selectors (40% parity) !!!

We need tests for selector edge cases:

### Specificity
- [ ] `!important` vs inline style specificity
- [ ] Multiple classes vs ID specificity
- [ ] Nested selectors specificity calculation
- [ ] `:where()` and `:is()` specificity behavior

### Combinators
- [ ] Child combinator (`>`) with multiple levels
- [ ] Adjacent sibling (`+`) edge cases
- [ ] General sibling (`~`) with mixed elements
- [ ] Descendant combinator with deep nesting

### Pseudo-classes
- [ ] `:nth-child(odd)` vs `:nth-child(2n+1)`
- [ ] `:nth-child()` with complex formulas (`3n-1`)
- [ ] `:nth-of-type()` with mixed element types
- [ ] `:not()` with complex selectors
- [ ] `:has()` parent selector (if supported)
- [ ] `:first-child` vs `:first-of-type`
- [ ] `:empty` with whitespace-only elements
- [ ] `:focus-visible` vs `:focus`

### Attribute Selectors
- [ ] Case-insensitive attribute matching `[attr="value" i]`
- [ ] Substring matching `[attr*="val"]`
- [ ] Space-separated list `[attr~="val"]`

---

## Flexbox (55% parity) !!

### Alignment
- [ ] `justify-content: space-evenly` vs `space-around`
- [ ] `align-items: baseline` with different font sizes
- [ ] `align-self` overriding container alignment
- [ ] `align-content` with wrapped items

### Sizing
- [ ] `flex-grow` distribution with different values
- [ ] `flex-shrink` with `min-width` constraints
- [ ] `flex-basis: 0` vs `flex-basis: auto`
- [ ] `flex: 1` shorthand expansion
- [ ] Intrinsic sizing (`min-content`, `max-content`, `fit-content`)

### Wrapping
- [ ] `flex-wrap: wrap-reverse`
- [ ] Gap with wrapped items
- [ ] Wrapped items with `align-content`

### Edge Cases
- [ ] Flex container with `overflow: hidden`
- [ ] Nested flex containers
- [ ] Flex items with margins (negative margins)
- [ ] `order` property with wrapping
- [ ] Flex items with `position: absolute`

---

## CSS Grid (53% parity) !!

### Track Sizing
- [ ] `minmax()` with various units
- [ ] `fr` units mixed with fixed sizes
- [ ] `auto-fill` vs `auto-fit`
- [ ] `repeat()` with complex patterns

### Placement
- [ ] Named grid lines
- [ ] `grid-area` spanning multiple cells
- [ ] Implicit grid creation
- [ ] Dense packing algorithm

### Alignment
- [ ] `place-items` shorthand
- [ ] `justify-items` vs `justify-content`
- [ ] Grid items with different alignments

---

## Images (46% parity) !!!

### Object Fit
- [ ] `object-fit: cover` with various aspect ratios
- [ ] `object-fit: contain` centering
- [ ] `object-fit: scale-down` threshold behavior
- [ ] `object-position` with percentages

### Sizing
- [ ] Intrinsic aspect ratio preservation
- [ ] `aspect-ratio` property
- [ ] Images in flex containers
- [ ] Images in grid cells
- [ ] `max-width: 100%` on images
- [ ] Missing width/height attributes

### Replaced Elements
- [ ] `<video>` poster sizing
- [ ] `<iframe>` sizing
- [ ] `<canvas>` scaling

---

## Position: Sticky (47% parity) !!!

### Basic Behavior
- [ ] Sticky header in scrolling container
- [ ] Multiple sticky elements stacking
- [ ] Sticky with `top`, `bottom`, `left`, `right`

### Containers
- [ ] Sticky inside `overflow: auto` parent
- [ ] Sticky inside nested scroll containers
- [ ] Sticky with `overflow-x` vs `overflow-y` differences

### Edge Cases
- [ ] Sticky element larger than viewport
- [ ] Sticky with transforms on ancestors
- [ ] Sticky inside table headers

---

## Form Controls (48% parity) !!

### Inputs
- [ ] Text input default sizing
- [ ] Input with placeholder styling
- [ ] Input focus ring styling
- [ ] `input[type="number"]` spinners
- [ ] `input[type="range"]` default styling
- [ ] `input[type="color"]` swatch

### Buttons
- [ ] Button default padding
- [ ] Button with icon + text alignment
- [ ] `<button>` vs `<input type="button">`

### Select/Checkbox/Radio
- [ ] Select dropdown arrow positioning
- [ ] Checkbox/radio default sizes
- [ ] Custom checkbox styling via `:checked`

### In Flex/Grid
- [ ] Form controls as flex items
- [ ] Form controls in grid cells
- [ ] Label + input alignment

---

## Typography (50% parity) !!

### Line Height
- [ ] Unitless vs unit line-height
- [ ] Line-height with different font sizes
- [ ] First/last line baseline alignment

### Font Metrics
- [ ] `vertical-align: middle` accuracy
- [ ] Subscript/superscript positioning
- [ ] `font-size-adjust` behavior

### Text Layout
- [ ] `white-space: pre-wrap` vs `pre-line`
- [ ] `word-break: break-word` vs `overflow-wrap`
- [ ] `hyphens: auto` behavior
- [ ] `text-overflow: ellipsis` positioning

---

## Other Areas !

### Backgrounds
- [ ] Multiple backgrounds layering
- [ ] `background-clip: text`
- [ ] Gradient color stops with hints

### Borders
- [ ] `border-radius` on table cells
- [ ] `border-image` slicing
- [ ] Asymmetric border-radius

### Transforms
- [ ] 3D transforms with perspective
- [ ] Transform origin percentages
- [ ] Stacking context creation

### Filters
- [ ] `backdrop-filter` blur
- [ ] Multiple filter functions
- [ ] Filter on positioned elements

---

## How to Claim a Test

1. Comment on [this issue](https://github.com/hiwavebrowser/community/issues/1) with the test you're working on
2. Create the test following [CONTRIBUTING.md](../CONTRIBUTING.md)
3. Submit PR within 7 days (or let us know if you need more time)

Tests with **!!!** priority are most impactful. Start there if you can!
