#!/usr/bin/env python3
"""S5 fix part 2: layout paints the legacy `clip` rect, and clip-path reaches form controls."""
import sys
wt = sys.argv[1]
p = wt + '/crates/rustkit-layout/src/lib.rs'; s = open(p).read()

# 1. clip-path: form controls too (a <button> or <input> is a box of its own).
a = """    /// anonymous block is never clipped on its own: a text run carries its
    /// parent's style, and the parent's clip already covers all three.
    fn clip_path_clip(&self, layout_box: &LayoutBox) -> Option<(Rect, BorderRadius)> {
        if !matches!(layout_box.box_type, BoxType::Block | BoxType::Image { .. }) {
            return None;
        }"""
assert s.count(a) == 1
s = s.replace(a, """    /// anonymous block is never clipped on its own: a text run carries its
    /// parent's style, and the parent's clip already covers all three. A form
    /// control is clipped like a block: eBay's visually hidden header buttons
    /// are `<button>`s with `clip-path: inset(50%)`.
    fn clip_path_clip(&self, layout_box: &LayoutBox) -> Option<(Rect, BorderRadius)> {
        if !matches!(
            layout_box.box_type,
            BoxType::Block | BoxType::Image { .. } | BoxType::FormControl(_)
        ) {
            return None;
        }""")

# 2. The legacy `clip` rect, before clip_path_clip.
a = """    fn clip_path_clip(&self, layout_box: &LayoutBox) -> Option<(Rect, BorderRadius)> {"""
s = s.replace(a, """    /// The legacy `clip: rect()` of an absolutely or fixed positioned box
    /// (CSS 2.1 §11.1.2): a rect from the border box's top-left corner, each
    /// `auto` side at the border edge. It clips the box and every descendant,
    /// like `clip-path`. Static and relative boxes ignore it, as in Chromium.
    /// A right side left of the left side (or bottom above top) clips all:
    /// `rect(0,0,0,0)` and `rect(1px,1px,1px,1px)` are the visually-hidden
    /// pattern on most large sites.
    fn clip_rect_clip(&self, layout_box: &LayoutBox) -> Option<Rect> {
        let clip = layout_box.style.clip.as_ref()?;
        if !matches!(layout_box.position, Position::Absolute | Position::Fixed) {
            return None;
        }
        if !matches!(
            layout_box.box_type,
            BoxType::Block | BoxType::Image { .. } | BoxType::FormControl(_)
        ) {
            return None;
        }
        let font_size = match layout_box.style.font_size {
            Length::Px(px) => px,
            _ => 16.0,
        };
        let root = self.root_font_size;
        let border = layout_box.dimensions.border_box();
        let side = |side: &Option<Length>, auto: f32| -> f32 {
            side.as_ref()
                .map_or(auto, |l| l.to_px(font_size, root, 0.0))
        };
        let top = side(&clip.top, 0.0);
        let right = side(&clip.right, border.width);
        let bottom = side(&clip.bottom, border.height);
        let left = side(&clip.left, 0.0);
        Some(Rect::new(
            border.x + left,
            border.y + top,
            (right - left).max(0.0),
            (bottom - top).max(0.0),
        ))
    }

""" + a, 1)

# 3. Paint: push it with the clip-path clip, pop with it.
a = """        let shape_clip = self.clip_path_clip(layout_box);
        let positioned = layout_box.position != Position::Static
            || layout_box.style.position != rustkit_css::Position::Static
            || shape_clip.is_some();"""
assert s.count(a) == 1
s = s.replace(a, """        let shape_clip = self.clip_path_clip(layout_box);
        let rect_clip = self.clip_rect_clip(layout_box);
        let positioned = layout_box.position != Position::Static
            || layout_box.style.position != rustkit_css::Position::Static
            || shape_clip.is_some();""")
a = """        // `clip-path` clips the box's own painting too, so it opens before
        // the box's content, inside its transform, and closes after its
        // subtree.
        if let Some((rect, radius)) = shape_clip {"""
assert s.count(a) == 1
s = s.replace(a, """        // `clip-path` clips the box's own painting too, so it opens before
        // the box's content, inside its transform, and closes after its
        // subtree. The legacy `clip` rect is applied the same way, outside it.
        if let Some(rect) = rect_clip {
            self.commands.push(DisplayCommand::PushClip(rect));
        }
        if let Some((rect, radius)) = shape_clip {""")
a = """        if shape_clip.is_some() {
            self.commands.push(DisplayCommand::PopClip);
        }
"""
assert s.count(a) == 1
s = s.replace(a, a + """        if rect_clip.is_some() {
            self.commands.push(DisplayCommand::PopClip);
        }
""")
open(p, 'w').write(s)
print("ok")
