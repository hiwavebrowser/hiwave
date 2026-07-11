# Atlas-ready unit: flex §11b definite cross size

**Lane:** Prometheus design → Atlas implements.  
**Verified against:** `hiwave-macos` master `c305ef0` (post-#22).  
**Prior memo correction:** there is **no** `has_explicit_cross_size` / `explicit_cross_size` on `FlexItem` today. Fix must read **`style.height` / `style.width`** (or add those fields). Do not search for a field that does not exist.

---

## Repro (on master)

`parity-tests/repro/toggle-height.html`

| Case | Structure | Chrome height | Bug shape |
|------|-----------|---------------|-----------|
| A | `.toggle` alone in block | 26 | should stay 26 |
| B | `.toggle` as **flex item** in `.row` | 26 | RustKit grows ~40+ |

`.toggle { display: inline-flex; width: 48px; height: 26px; }`

---

## Exact code (master `flex.rs`)

**§11b** starts ~L289. Comment says “only if fallback”; **code never checks definite size**:

```289:320:crates/rustkit-layout/src/flex.rs
    // 11b. Recompute cross sizes now that children are laid out
    for line in &mut lines {
        for item in &mut line.items {
            if !item.layout_box.children.is_empty() {
                let children_height: f32 = item.layout_box.children
                    .iter()
                    .map(|c| c.dimensions.margin_box().height)
                    .sum();

                if children_height > 0.0 && children_height > item.cross_size {
                    item.cross_size = children_height.max(item.min_cross_size).min(item.max_cross_size);
                    // also mutates content height/width by cross_axis …
                }
            }
        }
        // recompute line.cross_size …
    }
```

**Second bug in same block (ledger, optional same PR if cheap):**  
`match cross_axis` arm `Axis::Horizontal` assigns **`children_height` into `content.width`**. For column-flex (main = vertical), cross = horizontal, so it can write **height-sum into width**. Athena session-2 review already flagged this family. Prefer fix definite-cross first; axis-correct the assignment if you touch the match.

---

## Recommended fix (minimal)

Before expanding in §11b, resolve **author definite cross size**:

```rust
// Pseudocode for main_axis == Horizontal (row): cross = height
fn definite_cross_size(item: &FlexItem, main_axis: Axis, container_cross: f32, viewport: (f32,f32)) -> Option<f32> {
    let len = match main_axis {
        Axis::Horizontal => &item.layout_box.style.height, // cross = height
        Axis::Vertical => &item.layout_box.style.width,   // cross = width
    };
    match len {
        Length::Px(px) if *px > 0.0 => Some(*px),
        // if % is resolved elsewhere already, include when non-auto
        _ => None,
    }
}
```

Then:

```rust
if definite_cross_size(item, main_axis, …).is_some() {
    continue; // keep used cross size; do not grow past height/width
}
// else existing children_height expansion
```

Also set content box cross size from the **definite** length when present so absolute children (`inset:0` slider) get a correct CB.

**Regression test:** layout `toggle-height.html` Case B → toggle content height **26** (tolerance 0.5), not ~40.

---

## Success criteria (2h unit)

1. Full suite on master @ CfT 148 → committed N/26 (post-#22 baseline).  
2. §11b skip when height/width definite.  
3. Case B height = 26.  
4. **settings** moves toward/through t15; zero lost passes.  
5. Cap 2h; do not stack absolute-inset PR unless settings still fails after A.

---

## PR title

`fix(rustkit-layout): do not expand flex items past definite cross size (§11b)`

---

— Prometheus · verified on tree 2026-07-10 morning · discounted-trust friendly: surgical, testable, no architecture rewrite
