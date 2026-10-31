#!/usr/bin/env python3
"""CA1-2 fix: the flex arm becomes one parse, with the keywords and a basis in either place."""
p = "/Users/petecopeland/Repos/.worktrees/z-ca1-2/crates/rustkit-engine/src/lib.rs"
s = open(p).read()

i = s.index('            "flex" => {\n                // Shorthand: flex: <grow> [<shrink>] [<basis>].')
j = s.index('            "flex-direction" => {', i)
s = s[:i] + '''            "flex" => {
                // Invalid is dropped whole (css-syntax-3 §8): `flex: 1 junk`
                // keeps the earlier declaration.
                if let Some((grow, shrink, basis)) = parse_flex_shorthand(value) {
                    style.flex_grow = grow;
                    style.flex_shrink = shrink;
                    style.flex_basis = basis;
                }
            }
''' + s[j:]

old = 'fn parse_flex_basis(value: &str) -> rustkit_css::FlexBasis {\n'
assert s.count(old) == 1
s = s.replace(old, '''/// `flex: none | [ <grow> <shrink>? || <basis> ]` (css-flexbox-1 §7.1.1).
///
/// The two factors sit next to each other and the basis goes either side of
/// them, so `10px 2 3` is valid and `2 10px 3` is not. Two rules the naive
/// positional read got wrong (hiwave-windows #66): `flex: <number>` sets the
/// basis to `0%`, which is what makes `flex: 1` divide the container instead
/// of sizing to content (the same in a row or a definite column, `content`
/// in an auto-height column, where a percentage has nothing to resolve
/// against); and a second value that is not a bare number is the basis, not
/// a shrink of 200.
fn parse_flex_shorthand(value: &str) -> Option<(f32, f32, rustkit_css::FlexBasis)> {
    use rustkit_css::FlexBasis;
    let value = value.trim();
    if value.eq_ignore_ascii_case("none") {
        return Some((0.0, 0.0, FlexBasis::Auto));
    }
    // Split outside parentheses: `calc(50% - 10px)` is one basis, not three
    // junk tokens.
    let parts = split_top_level_whitespace(value);
    if parts.is_empty() || parts.len() > 3 {
        return None;
    }
    let mut factors: Vec<f32> = Vec::new();
    let mut basis = None;
    let mut basis_after_factor = false;
    for part in parts {
        match part.parse::<f32>() {
            Ok(n) if !n.is_finite() || n < 0.0 => return None,
            // A third bare number is a basis only when it is a unitless `0`
            // (`flex: 1 1 0`); `1 2 3` is invalid.
            Ok(n) if factors.len() == 2 => {
                if n != 0.0 || basis.is_some() {
                    return None;
                }
                basis = Some(parse_flex_basis(part));
            }
            // A basis has come between the two factors: `2 10px 3`.
            Ok(_) if basis_after_factor => return None,
            Ok(n) => factors.push(n),
            Err(_) => {
                if basis.is_some() || part.starts_with('-') || !is_flex_basis_value(part) {
                    return None;
                }
                basis_after_factor = !factors.is_empty();
                basis = Some(parse_flex_basis(part));
            }
        }
    }
    match (factors.as_slice(), basis) {
        // A lone basis: `flex: 10px`, `flex: auto`.
        ([], Some(basis)) => Some((1.0, 1.0, basis)),
        ([grow], basis) => Some((*grow, 1.0, basis.unwrap_or(FlexBasis::Percent(0.0)))),
        ([grow, shrink], basis) => {
            Some((*grow, *shrink, basis.unwrap_or(FlexBasis::Percent(0.0))))
        }
        _ => None,
    }
}

''' + old)

old = '''            // Not inherited, so `unset` lands here too: the initial value is
            // `auto`, no ratio.
'''
assert s.count(old) == 1
s = s.replace(old, '''            // `flex: initial` / `unset`: 0 1 auto.
            "flex" => {
                style.flex_grow = 0.0;
                style.flex_shrink = 1.0;
                style.flex_basis = rustkit_css::FlexBasis::Auto;
            }
''' + old)
open(p, "w").write(s)
