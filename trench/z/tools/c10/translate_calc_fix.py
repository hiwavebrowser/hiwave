#!/usr/bin/env python3
"""`translate` splits at the spaces outside functions, and flattens a depth."""
P = "/Users/petecopeland/Repos/.worktrees/z-c10-translate-calc/crates/rustkit-engine/src/lib.rs"
s = open(P).read()
old = """/// `translate: none | <length-percentage> [<length-percentage> <length>?]?`.
/// `Some(None)` is `none`; `None` is invalid. A nonzero z is 3D, which the
/// 2D painter can't honour, so the declaration is dropped rather than
/// painted flat.
fn parse_individual_translate(value: &str) -> Option<Option<rustkit_css::TransformOp>> {
    let value = value.trim();
    if value.eq_ignore_ascii_case("none") {
        return Some(None);
    }
    let parts: Vec<&str> = value.split_whitespace().collect();
    if parts.is_empty() || parts.len() > 3 {
        return None;
    }
    let x = parse_length(parts[0])?;
    let y = match parts.get(1) {
        Some(p) => parse_length(p)?,
        None => rustkit_css::Length::Zero,
    };
    if let Some(z) = parts.get(2) {
        match parse_length(z)? {
            rustkit_css::Length::Zero => {}
            rustkit_css::Length::Px(v) if v == 0.0 => {}
            _ => return None,
        }
    }
    Some(Some(rustkit_css::TransformOp::Translate(x, y)))
}
"""
new = """/// `translate: none | <length-percentage> [<length-percentage> <length>?]?`.
/// `Some(None)` is `none`; `None` is invalid. The painter is 2D: with no
/// perspective a z moves nothing on the page's plane.
fn parse_individual_translate(value: &str) -> Option<Option<rustkit_css::TransformOp>> {
    let value = value.trim();
    if value.eq_ignore_ascii_case("none") {
        return Some(None);
    }
    let parts = split_outside_functions(value);
    if parts.is_empty() || parts.len() > 3 {
        return None;
    }
    let x = parse_length(parts[0])?;
    let y = match parts.get(1) {
        Some(p) => parse_length(p)?,
        None => rustkit_css::Length::Zero,
    };
    if let Some(z) = parts.get(2) {
        parse_length(z)?;
    }
    Some(Some(rustkit_css::TransformOp::Translate(x, y)))
}

/// The parts of a value between the white space outside functions:
/// `0px calc(-100% - 1px)` is two.
fn split_outside_functions(value: &str) -> Vec<&str> {
    let (mut depth, mut start, mut parts) = (0, None, Vec::new());
    for (i, ch) in value.char_indices() {
        match ch {
            '(' => depth += 1,
            ')' => depth -= 1,
            _ => {}
        }
        match (ch.is_whitespace() && depth == 0, start) {
            (true, Some(from)) => {
                parts.push(&value[from..i]);
                start = None;
            }
            (false, None) => start = Some(i),
            _ => {}
        }
    }
    if let Some(from) = start {
        parts.push(&value[from..]);
    }
    parts
}
"""
assert s.count(old) == 1
s = s.replace(old, new)
open(P, "w").write(s)
print("ok")
