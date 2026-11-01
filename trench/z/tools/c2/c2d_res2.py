#!/usr/bin/env python3
"""Resolve #851's merge with develop + the fixed-rect PR. One entry per conflict, in file order."""
import re

WT = "/Users/petecopeland/Repos/.worktrees/z-c2d-rework/crates/"
TOK = re.compile(r"^<<<<<<< [^\n]*\n(.*?)^=======\n(.*?)^>>>>>>> [^\n]*\n", re.S | re.M)


def resolve(path, choices):
    text = open(WT + path).read()
    it = iter(choices)

    def pick(m):
        c = next(it)
        return c(m.group(1), m.group(2))

    text = TOK.sub(pick, text)
    assert next(it, None) is None
    assert "<<<<<<<" not in text
    open(WT + path, "w").write(text)


ours = lambda a, b: a
theirs = lambda a, b: b

TRANSFORMED_RECT = """    /// The rect of a box under a transform, its own or one above it, as x, y,
    /// width, height: the bounding box of its corners taken up the chain. At
    /// each box its transform, about where layout put it, then its sticky
    /// shift, which carries the transform's origin along; then the scroll of
    /// the scroller above, inside that scroller's own transform. `None` when
    /// no transform is on the chain, and `moved_by` is the whole answer.
    fn transformed_rect(&self, geometry: &BoxGeometry) -> Option<(f32, f32, f32, f32)> {
        let mut chain = vec![(None, geometry)];
        let mut at = geometry.scroller;
        while let Some((node, above)) = at.and_then(|node| Some((node, self.geometry.get(&node)?))) {
            chain.push((Some(node), above));
            at = above.scroller;
        }
        if chain.iter().all(|(_, g)| g.transform.is_none()) {
            return None;
        }
        let scrolls = self.element_scrolls.borrow();
        // Each shift depends on those above it, so these go from the top.
        let mut shifts = vec![(0.0, 0.0); chain.len()];
        let mut moved = MovedBy::default();
        for (i, (node, g)) in chain.iter().enumerate().rev() {
            let before = moved.stuck;
            self.add_sticky(g, &scrolls.offsets, &mut moved);
            shifts[i] = (moved.stuck.0 - before.0, moved.stuck.1 - before.1);
            if node.is_some() && g.scrolls {
                moved.above = (0.0, 0.0);
            }
        }
        let (x, y, r, b) = (geometry.x, geometry.y, geometry.x + geometry.width, geometry.y + geometry.height);
        let mut corners = [(x, y), (r, y), (x, b), (r, b)];
        for (i, (node, g)) in chain.iter().enumerate() {
            let scroll = node.filter(|_| g.scrolls).and_then(|node| scrolls.offsets.get(&node));
            let (dx, dy) = scroll.copied().unwrap_or((0.0, 0.0));
            for c in corners.iter_mut() {
                let (px, py) = (c.0 - dx, c.1 - dy);
                let (tx, ty) = match g.transform {
                    Some(m) => (m[0] * px + m[2] * py + m[4], m[1] * px + m[3] * py + m[5]),
                    None => (px, py),
                };
                *c = (tx + shifts[i].0, ty + shifts[i].1);
            }
        }
        let (mut left, mut top) = corners[0];
        let (mut right, mut bottom) = corners[0];
        for c in &corners[1..] {
            left = left.min(c.0);
            top = top.min(c.1);
            right = right.max(c.0);
            bottom = bottom.max(c.1);
        }
        Some((left, top, right - left, bottom - top))
    }

"""

GEOM = """                        // The first two and the last two are for rects: where
                        // the scrollers, sticky boxes and transforms put the
                        // box. The rest, `offsetTop` among them, leave the
                        // scrollers and transforms out.
                        let moved = host.moved_by(g);
                        let (x, y) = (g.x + moved.stuck.0, g.y + moved.stuck.1);
                        let (rx, ry, rw, rh) = host
                            .transformed_rect(g)
                            .unwrap_or((x - moved.scrolled.0, y - moved.scrolled.1, g.width, g.height));
                        // The rect's reader takes the window's scroll off.
                        let page = if g.held { host.window_scroll() } else { (0.0, 0.0) };
                        JsValue::String(format!(
                            "{} {} {} {} {} {} {} {} {} {} {} {} {} {} {}",
                            n(rx + page.0), n(ry + page.1), n(g.width), n(g.height), n(g.border_left), n(g.border_top),
                            n(g.client_width), n(g.client_height), n(g.scroll_width), n(g.scroll_height), g.position,
                            n(x), n(y), n(rw), n(rh)
"""

resolve(
    "rustkit-bindings/src/dom.rs",
    [
        ours,
        lambda a, b: TRANSFORMED_RECT,
        ours,
        lambda a, b: GEOM,
        lambda a, b: "                            // A sticky or transformed box on the chain moves\n                            // the box, but cannot be scrolled.\n",
    ],
)

resolve(
    "rustkit-engine/src/lib.rs",
    [
        lambda a, b: """        let sticky = b.sticky_rule.get();
        // A transform does not apply to a plain inline box, as in Chrome.
        let transform = match b.box_type {
            BoxType::Inline => None,
            _ if b.node_id.is_none() => None,
            _ => own_transform_affine(b),
        };
        let transformed = transform.is_some();
        let inner = if scrolls || transformed || sticky.is_some() { b.node_id } else { scroller };
        let positioned = b.position != Position::Static || b.style.position != rustkit_css::Position::Static;
""",
        ours,
        ours,
    ],
)
print("resolved")
