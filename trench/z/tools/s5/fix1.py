#!/usr/bin/env python3
"""S5 fix part 1: ComputedStyle.clip + parse_clip (rustkit-css), cascade arms (engine)."""
import sys
wt = sys.argv[1]
p = wt + '/crates/rustkit-css/src/lib.rs'; s = open(p).read()
a = """    pub clip_path: String,
    pub visibility: Visibility,"""
assert s.count(a) == 1
s = s.replace(a, """    pub clip_path: String,
    /// The legacy `clip` property (CSS 2.1 §11.1.2, CSS Masking 1 §6.1):
    /// `None` for `auto`. Only an absolutely or fixed positioned box is
    /// clipped by it. Not inherited.
    pub clip: Option<ClipRect>,
    pub visibility: Visibility,""")
a = "pub fn parse_opacity(value: &str) -> Option<f32> {"
assert s.count(a) == 1
s = s.replace(a, '''/// `clip: rect(<top>, <right>, <bottom>, <left>)`: each side a length or
/// `auto`; `right` and `bottom` are measured from the box's left and top
/// border edges, as `top` and `left` are (CSS 2.1 §11.1.2).
#[derive(Debug, Clone, PartialEq, Default)]
pub struct ClipRect {
    pub top: Option<Length>,
    pub right: Option<Length>,
    pub bottom: Option<Length>,
    pub left: Option<Length>,
}

/// Parses the `clip` property: `Some(None)` for `auto`, `Some(Some(rect))`
/// for `rect()` with four sides separated by commas or by white space, as
/// Chromium takes both (Bootstrap writes `rect(0,0,0,0)`, others
/// `rect(0 0 0 0)`). A percentage or anything else refuses the declaration.
pub fn parse_clip(value: &str) -> Option<Option<ClipRect>> {
    let value = value.trim().to_ascii_lowercase();
    if value == "auto" {
        return Some(None);
    }
    let inner = value.strip_prefix("rect(")?.strip_suffix(')')?;
    let parts: Vec<&str> = if inner.contains(',') {
        inner.split(',').map(str::trim).collect()
    } else {
        inner.split_whitespace().collect()
    };
    let [top, right, bottom, left] = parts.as_slice() else {
        return None;
    };
    let side = |token: &str| -> Option<Option<Length>> {
        match token {
            "auto" => Some(None),
            "" => None,
            t => match parse_length(t)? {
                Length::Percent(_) | Length::Auto | Length::FitContent => None,
                l => Some(Some(l)),
            },
        }
    };
    Some(Some(ClipRect {
        top: side(top)?,
        right: side(right)?,
        bottom: side(bottom)?,
        left: side(left)?,
    }))
}

pub fn parse_opacity(value: &str) -> Option<f32> {''')
open(p, 'w').write(s)

p = wt + '/crates/rustkit-engine/src/lib.rs'; s = open(p).read()
a = '''            "filter" | "-webkit-filter" => {
                let value = value.trim().to_ascii_lowercase();'''
assert s.count(a) == 1
s = s.replace(a, '''            "clip" => {
                if let Some(clip) = rustkit_css::parse_clip(value) {
                    style.clip = clip;
                }
            }
''' + a)
a = '''            "clip-path" | "-webkit-clip-path" => style.clip_path.clear(),'''
assert s.count(a) == 1
s = s.replace(a, a + '''\n            "clip" => style.clip = None,''')
open(p, 'w').write(s)
print("ok")
