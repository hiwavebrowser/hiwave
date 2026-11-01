#!/usr/bin/env python3
"""The fix for the fixed-box rect PR: a `held` flag on BoxGeometry, the same name and rule #851 uses."""
WT = "/Users/petecopeland/Repos/.worktrees/z-c10-fixed-rect/crates/"


def sub(path, pairs):
    text = open(WT + path).read()
    for old, new in pairs:
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    open(WT + path, "w").write(text)


sub(
    "rustkit-bindings/src/dom.rs",
    [
        (
            """    /// Whether this box is an element scroller itself.
    pub scrolls: bool,
}
""",
            """    /// Whether this box is an element scroller itself.
    pub scrolls: bool,
    /// In a fixed box the window's scroll does not move: its rect is where
    /// layout put it, wherever the page is.
    pub held: bool,
}
""",
        ),
        (
            """    /// What the element scrollers above a box have moved it by.
    fn element_scroll_over""",
            """    /// Where the window is now, script's own scroll included.
    fn window_scroll(&self) -> (f32, f32) {
        let state = self.scroll_state.borrow();
        (state.x, state.y)
    }

    /// What the element scrollers above a box have moved it by.
    fn element_scroll_over""",
        ),
        (
            """                            (g.x - dx, g.y - dy, g.width, g.height)
                        });
""",
            """                            (g.x - dx, g.y - dy, g.width, g.height)
                        });
                        // The rect's reader takes the window's scroll off.
                        let page = if g.held { host.window_scroll() } else { (0.0, 0.0) };
""",
        ),
        (
            """                            n(rx), n(ry), n(g.width), n(g.height), n(g.border_left), n(g.border_top),
""",
            """                            n(rx + page.0), n(ry + page.1), n(g.width), n(g.height), n(g.border_left), n(g.border_top),
""",
        ),
    ],
)

sub(
    "rustkit-engine/src/lib.rs",
    [
        (
            """        absolute: Option<usize>,
        fixed: Option<usize>,
    }
    fn walk(
""",
            """        absolute: Option<usize>,
        fixed: Option<usize>,
        /// Under a fixed box the scroll does not move, and under a transform,
        /// which holds a fixed box to the page.
        held: bool,
        transformed: bool,
    }
    fn walk(
""",
        ),
        (
            """        let positioned = b.position != Position::Static || b.style.position != rustkit_css::Position::Static;
        let under = Scrollers {
""",
            """        let positioned = b.position != Position::Static || b.style.position != rustkit_css::Position::Static;
        let held = scrollers.held || (b.position == Position::Fixed && !scrollers.transformed);
        let under = Scrollers {
""",
        ),
        (
            """            fixed: if transformed { inner } else { scrollers.fixed },
        };
""",
            """            fixed: if transformed { inner } else { scrollers.fixed },
            held,
            transformed: scrollers.transformed || transformed,
        };
""",
        ),
        (
            """                transform,
                scrolls,
            };
""",
            """                transform,
                scrolls,
                held,
            };
""",
        ),
        (
            """    let none = Scrollers { flow: None, absolute: None, fixed: None };
""",
            """    let none = Scrollers { flow: None, absolute: None, fixed: None, held: false, transformed: false };
""",
        ),
        (
            """        scrolls: false,
""",
            """        scrolls: false,
        held: false,
""",
        ),
    ],
)
print("ok")
