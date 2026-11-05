#!/usr/bin/env python3
"""#851 23:55 order: engine, css and census edits in worktree argv[1]."""
import sys

C = sys.argv[1]


def edit(path, pairs):
    p = C + path
    s = open(p).read()
    for a, b in pairs:
        assert s.count(a) == 1, a
        s = s.replace(a, b)
    open(p, "w").write(s)


edit("/crates/rustkit-engine/src/lib.rs", [
    ('''"isolation" | "mix-blend-mode" | "perspective" | "transform-style" | "backdrop-filter"
            | "-webkit-backdrop-filter" => {''', '''"isolation" | "mix-blend-mode" | "perspective" | "transform-style" | "backdrop-filter"
            | "content-visibility" | "view-transition-name" => {'''),
    ('''"backdrop-filter" | "-webkit-backdrop-filter" => style.stacks &= !rustkit_css::STACKS_BACKDROP,
''', '''"backdrop-filter" => style.stacks &= !rustkit_css::STACKS_BACKDROP,
            "content-visibility" => style.stacks &= !rustkit_css::STACKS_CONTENT_VISIBILITY,
            "view-transition-name" => style.stacks &= !rustkit_css::STACKS_VIEW_TRANSITION,
'''),
    ('''                | "-webkit-mask"
                | "isolation"
                | "mix-blend-mode"
                | "z-index"
                | "position"
''', '''                | "-webkit-mask"
                | "mask-image"
                | "-webkit-mask-image"
                | "isolation"
                | "mix-blend-mode"
                | "view-transition-name"
                | "z-index"
                | "position"
'''),
    ('''        "backdrop-filter" | "-webkit-backdrop-filter" => {
            if value == "none" {
                Some((rustkit_css::STACKS_BACKDROP, false))
            } else if value.ends_with(')') {
                Some((rustkit_css::STACKS_BACKDROP, true))
            } else {
                None
            }
        }
''', '''        "backdrop-filter" => {
            if value == "none" {
                Some((rustkit_css::STACKS_BACKDROP, false))
            } else if value.ends_with(')') {
                Some((rustkit_css::STACKS_BACKDROP, true))
            } else {
                None
            }
        }
        "content-visibility" => match value.as_str() {
            "auto" | "hidden" => Some((rustkit_css::STACKS_CONTENT_VISIBILITY, true)),
            "visible" => Some((rustkit_css::STACKS_CONTENT_VISIBILITY, false)),
            _ => None,
        },
        "view-transition-name" => {
            let starts_as_ident = value.starts_with(|c: char| c.is_ascii_alphabetic() || c == '-' || c == '_');
            if value == "none" || value == "auto" {
                Some((rustkit_css::STACKS_VIEW_TRANSITION, false))
            } else if starts_as_ident && !value.contains(char::is_whitespace) {
                Some((rustkit_css::STACKS_VIEW_TRANSITION, true))
            } else {
                None
            }
        }
'''),
])
edit("/crates/rustkit-css/src/lib.rs", [
    ('''pub const STACKS_BACKDROP: u8 = 32;
''', '''pub const STACKS_BACKDROP: u8 = 32;
/// `ComputedStyle::stacks`: `content-visibility: auto` or `hidden`.
pub const STACKS_CONTENT_VISIBILITY: u8 = 64;
/// `ComputedStyle::stacks`: a `view-transition-name` other than `none` or `auto`.
pub const STACKS_VIEW_TRANSITION: u8 = 128;
'''),
])
edit("/scripts/declaration_census.py", [
    ('''CUSTOM_PROPERTY_PREFIX = "--"
''', '''CUSTOM_PROPERTY_PREFIX = "--"

# Arms that only set a `ComputedStyle::stacks` bit, read by the hit test to tell
# a stacking context. Nothing paints or lays out by them, so a declaration of
# one is still dropped as far as the page's look goes: they count as no arm.
STACKING_ONLY_ARMS = frozenset(
    {
        "isolation",
        "mix-blend-mode",
        "perspective",
        "transform-style",
        "backdrop-filter",
        "content-visibility",
        "view-transition-name",
    }
)
'''),
    ('''        props.update(name.lower() for name in re.findall(r'"([A-Za-z-]+)"', arm))
    return props
''', '''        props.update(name.lower() for name in re.findall(r'"([A-Za-z-]+)"', arm))
    return props - STACKING_ONLY_ARMS
'''),
])
print("edited")
