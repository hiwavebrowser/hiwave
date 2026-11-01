#!/usr/bin/env python3
"""#853 R1 fix: units and keywords ignore case, CSS numbers only, calc()/min()/max()/clamp() in angles and numbers, perspective takes no negative length."""
P = "/Users/petecopeland/Repos/.worktrees/z-c10b2-r1/crates/rustkit-engine/src/lib.rs"
s = open(P).read()


def sub(old, new):
    global s
    assert s.count(old) == 1, old
    s = s.replace(old, new)


sub(
    """fn parse_transform(value: &str) -> Option<rustkit_css::TransformList> {
    let value = value.trim();
    if value == "none" {
        return Some(rustkit_css::TransformList::none());
    }

    let mut ops = Vec::new();
    let mut remaining = value;
""",
    """fn parse_transform(value: &str) -> Option<rustkit_css::TransformList> {
    // Function names, units and keywords all ignore case.
    let value = value.trim().to_ascii_lowercase();
    // `transform` does not inherit, so these all mean its initial value.
    if matches!(value.as_str(), "none" | "initial" | "unset" | "revert" | "revert-layer") {
        return Some(rustkit_css::TransformList::none());
    }

    let mut ops = Vec::new();
    let mut remaining = value.as_str();
""",
)

sub(
    """    /// `<number> | <percentage>`.
    fn factor(s: &str) -> Option<f32> {
        match s.strip_suffix('%') {
            Some(p) => p.parse::<f32>().ok().map(|v| v / 100.0),
            None => s.parse::<f32>().ok(),
        }
    }
    /// `<angle> | 0`: a bare number other than zero is not an angle here.
    fn angle(s: &str) -> Option<f32> {
        match s.parse::<f32>() {
            Ok(n) if n != 0.0 => None,
            _ => parse_angle(s),
        }
    }
    /// `<length-percentage>`: a bare number other than zero is not a length.
    fn length(s: &str) -> Option<rustkit_css::Length> {
        match s.parse::<f32>() {
            Ok(n) if n != 0.0 => None,
            _ => parse_length(s),
        }
    }
""",
    """    /// `<number> | <percentage>`.
    fn factor(s: &str) -> Option<f32> {
        if let Some(math) = transform_math(s) {
            return match math {
                (v, TransformMathKind::Number) => Some(v),
                (v, TransformMathKind::Percent) => Some(v / 100.0),
                (_, TransformMathKind::Angle) => None,
            };
        }
        match s.strip_suffix('%') {
            Some(p) => css_number(p).map(|v| v / 100.0),
            None => css_number(s),
        }
    }
    /// `<angle> | 0`: a bare number other than zero is not an angle here, nor
    /// is a math function that comes to a number.
    fn angle(s: &str) -> Option<f32> {
        if let Some(math) = transform_math(s) {
            return match math {
                (v, TransformMathKind::Angle) => Some(if v.is_finite() { v } else { 0.0 }),
                _ => None,
            };
        }
        match css_number(s) {
            Some(n) => (n == 0.0).then_some(0.0),
            None => css_angle(s),
        }
    }
    /// `<length-percentage>`: a bare number other than zero is not a length,
    /// and `inf` or `nan` before a unit is no number.
    fn length(s: &str) -> Option<rustkit_css::Length> {
        if s.trim_start_matches(['+', '-']).starts_with(['i', 'n']) {
            return None;
        }
        match s.parse::<f32>() {
            Ok(n) if n != 0.0 => None,
            _ => parse_length(s),
        }
    }
""",
)

sub(
    """    fn number(s: &str) -> Option<f32> {
        s.parse::<f32>().ok()
    }
    let still =""",
    """    fn number(s: &str) -> Option<f32> {
        match transform_math(s) {
            Some((v, TransformMathKind::Number)) => Some(v),
            Some(_) => None,
            None => css_number(s),
        }
    }
    let still =""",
)

sub(
    """            if !p.eq_ignore_ascii_case("none") {
                depth(p)?;
            }
            Some(still())
""",
    """            if *p != "none" {
                depth(p)?;
                // A math function is clamped to zero, not refused.
                if p.starts_with('-') && length(p)?.to_px(16.0, 16.0, 0.0) < 0.0 {
                    return None;
                }
            }
            Some(still())
""",
)

sub(
    """/// Parse a CSS angle value (e.g., "45deg", "1rad", "0.5turn") into degrees.
fn parse_angle(""",
    """/// A CSS `<number>`, which `f32`'s own parser is wider than: no `inf`, no
/// `nan`, no `5.`. Too large for an `f32` is the largest one.
fn css_number(s: &str) -> Option<f32> {
    let plain = s.ends_with(|c: char| c.is_ascii_digit())
        && !s.contains(".e")
        && s.chars().all(|c| c.is_ascii_digit() || matches!(c, '.' | '+' | '-' | 'e'));
    if !plain {
        return None;
    }
    s.parse::<f32>().ok().map(|v| v.clamp(-f32::MAX, f32::MAX))
}

/// `parse_angle` for a value with a unit and a CSS `<number>` before it.
fn css_angle(s: &str) -> Option<f32> {
    let digits = s.strip_suffix("grad").or(s.strip_suffix("turn")).or(s.strip_suffix("deg")).or(s.strip_suffix("rad"))?;
    css_number(digits)?;
    parse_angle(s)
}

/// What a math function in a transform comes to.
#[derive(Clone, Copy, PartialEq)]
enum TransformMathKind {
    Number,
    /// In degrees.
    Angle,
    Percent,
}

/// The value of `calc()`, `min()`, `max()` or `clamp()` over numbers, angles
/// and percentages, in lower case, for the places a transform takes a number
/// or an angle. Lengths go to `parse_length`. `None` when `s` is not one, or
/// its types do not add up.
fn transform_math(s: &str) -> Option<(f32, TransformMathKind)> {
    use TransformMathKind::{Angle, Number, Percent};

    fn sum(r: &mut &str) -> Option<(f32, TransformMathKind)> {
        let (mut value, kind) = product(r)?;
        loop {
            let after = r.trim_start();
            // `+` and `-` need white space on both sides.
            let spaced = after.len() < r.len() && after.get(1..).is_some_and(|tail| tail.starts_with(char::is_whitespace));
            let sign = match after.chars().next() {
                Some('+') if spaced => 1.0,
                Some('-') if spaced => -1.0,
                _ => return Some((value, kind)),
            };
            *r = &after[1..];
            let (next, next_kind) = product(r)?;
            if next_kind != kind {
                return None;
            }
            value += sign * next;
        }
    }
    fn product(r: &mut &str) -> Option<(f32, TransformMathKind)> {
        let (mut value, mut kind) = unit(r)?;
        loop {
            let after = r.trim_start();
            match after.chars().next() {
                Some('*') => {
                    *r = &after[1..];
                    let (next, next_kind) = unit(r)?;
                    kind = match (kind, next_kind) {
                        (k, Number) => k,
                        (Number, k) => k,
                        _ => return None,
                    };
                    value *= next;
                }
                Some('/') => {
                    *r = &after[1..];
                    let (next, next_kind) = unit(r)?;
                    if next_kind != Number {
                        return None;
                    }
                    value /= next;
                }
                _ => return Some((value, kind)),
            }
        }
    }
    fn unit(r: &mut &str) -> Option<(f32, TransformMathKind)> {
        *r = r.trim_start();
        if let Some(inner) = r.strip_prefix('(') {
            *r = inner;
            let value = sum(r)?;
            *r = r.trim_start().strip_prefix(')')?;
            return Some(value);
        }
        if let Some(value) = function(r) {
            return value;
        }
        let end = r.find(|c: char| c.is_whitespace() || matches!(c, ')' | ',' | '*' | '/')).unwrap_or(r.len());
        let (token, rest) = r.split_at(end);
        *r = rest;
        if let Some(percent) = token.strip_suffix('%') {
            return Some((css_number(percent)?, Percent));
        }
        match css_number(token) {
            Some(number) => Some((number, Number)),
            None => Some((css_angle(token)?, Angle)),
        }
    }
    /// `Some` when `r` starts with a math function; inside, `None` when it is bad.
    fn function(r: &mut &str) -> Option<Option<(f32, TransformMathKind)>> {
        let open = r.find('(')?;
        let name = &r[..open];
        if !matches!(name, "calc" | "min" | "max" | "clamp") {
            return None;
        }
        let mut inner = &r[open + 1..];
        let mut args = Vec::new();
        loop {
            let Some(arg) = sum(&mut inner) else {
                return Some(None);
            };
            args.push(arg);
            let after = inner.trim_start();
            match after.chars().next() {
                Some(',') => inner = &after[1..],
                Some(')') => {
                    inner = &after[1..];
                    break;
                }
                _ => return Some(None),
            }
        }
        *r = inner;
        let kind = args[0].1;
        if args.iter().any(|arg| arg.1 != kind) {
            return Some(None);
        }
        let values: Vec<f32> = args.iter().map(|arg| arg.0).collect();
        let value = match (name, values.as_slice()) {
            ("calc", [v]) => *v,
            ("min", all) => all.iter().copied().fold(f32::INFINITY, f32::min),
            ("max", all) => all.iter().copied().fold(f32::NEG_INFINITY, f32::max),
            ("clamp", [low, v, high]) => v.min(*high).max(*low),
            _ => return Some(None),
        };
        Some(Some((value, kind)))
    }

    let mut rest = s;
    let value = function(&mut rest)?;
    if !rest.trim().is_empty() {
        return None;
    }
    value
}

/// Parse a CSS angle value (e.g., "45deg", "1rad", "0.5turn") into degrees.
fn parse_angle(""",
)
open(P, "w").write(s)
print("ok")
