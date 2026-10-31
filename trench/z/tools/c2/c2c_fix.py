"""C2(c) edits, applied once to the z-c2c worktree (kept as the record of the splice)."""
W = '/Users/petecopeland/Repos/.worktrees/z-c2c/crates/'


def sub(path, a, b):
    p = W + path
    s = open(p, newline='').read()
    assert s.count(a) == 1, (path, a[:60], s.count(a))
    open(p, 'w', newline='').write(s.replace(a, b))


# ---- extents
sub('rustkit-layout/src/lib.rs', '''    /// How far this box's content can scroll on each axis: what its
    /// descendants reach past its padding box.
    pub fn element_scroll_max(&self) -> (f32, f32) {
        fn reach(b: &LayoutBox, right: &mut f32, bottom: &mut f32) {
            let border = b.dimensions.border_box();
            *right = right.max(border.x + border.width);
            *bottom = bottom.max(border.y + border.height);
            for child in &b.children {
                reach(child, right, bottom);
            }
        }
        let padding = self.dimensions.padding_box();
        let (mut right, mut bottom) = (padding.x + padding.width, padding.y + padding.height);
        for child in &self.children {
            reach(child, &mut right, &mut bottom);
        }
        (right - padding.x - padding.width, bottom - padding.y - padding.height)
    }
''', '''    /// Whether what this box's content reaches past it is cut off, so it is
    /// not overflow of a scroller around it: a scroller, or `clip` both ways.
    pub fn clips_its_content(&self) -> bool {
        use rustkit_css::Overflow;
        self.is_element_scroller()
            || (self.style.overflow_x == Overflow::Clip && self.style.overflow_y == Overflow::Clip)
    }

    /// Grow (`right`, `bottom`) to what this box reaches, its descendants
    /// included, as overflow of a scroller around it.
    pub fn reach_as_overflow(&self, right: &mut f32, bottom: &mut f32) {
        let border = self.dimensions.border_box();
        *right = right.max(border.x + border.width);
        *bottom = bottom.max(border.y + border.height);
        if self.clips_its_content() {
            self.escaped_reach(right, bottom);
        } else {
            for child in &self.children {
                child.reach_as_overflow(right, bottom);
            }
        }
    }

    /// The absolute boxes under this clipping box whose containing block is
    /// above it: its clip does not cut them.
    fn escaped_reach(&self, right: &mut f32, bottom: &mut f32) {
        if self.holds_absolute_boxes() {
            return;
        }
        for child in &self.children {
            if child.position == Position::Absolute {
                child.reach_as_overflow(right, bottom);
            } else {
                child.escaped_reach(right, bottom);
            }
        }
    }

    /// How far this box's content can scroll on each axis: what its
    /// descendants reach, then its padding at that end, past its padding box.
    pub fn element_scroll_max(&self) -> (f32, f32) {
        let padding = self.dimensions.padding_box();
        let (mut right, mut bottom) = (f32::NEG_INFINITY, f32::NEG_INFINITY);
        for child in &self.children {
            child.reach_as_overflow(&mut right, &mut bottom);
        }
        let own = &self.dimensions.padding;
        (
            (right + own.right - padding.x - padding.width).max(0.0),
            (bottom + own.bottom - padding.y - padding.height).max(0.0),
        )
    }
''')

sub('rustkit-engine/src/lib.rs', '''        let extent = Some(match content {
            Some(c) => (bx.min(c.0), by.min(c.1), (bx + bw).max(c.2), (by + bh).max(c.3)),
            None => (bx, by, bx + bw, by + bh),
        });
''', '''        let extent = Some(if b.clips_its_content() {
            let (mut right, mut bottom) = (bx + bw, by + bh);
            b.reach_as_overflow(&mut right, &mut bottom);
            (bx, by, right, bottom)
        } else {
            match content {
                Some(c) => (bx.min(c.0), by.min(c.1), (bx + bw).max(c.2), (by + bh).max(c.3)),
                None => (bx, by, bx + bw, by + bh),
            }
        });
''')
sub('rustkit-engine/src/lib.rs', '''            let (right, bottom) = content.map_or((px + pw, py + ph), |e| (e.2, e.3));
''', '''            let (right, bottom) = if scrolls {
                let (x, y) = b.element_scroll_max();
                (px + pw + x, py + ph + y)
            } else {
                content.map_or((px + pw, py + ph), |e| (e.2, e.3))
            };
''')

# ---- the chain
sub('rustkit-bindings/src/dom.rs', '''Some("laidout" | "computed" | "geom" | "scroll"))''',
    '''Some("laidout" | "computed" | "geom" | "scroll" | "scrollChain"))''')
sub('rustkit-bindings/src/dom.rs', '''                (Some(node), Some(field)) => node_info(&node, field, &host.templates.borrow()),
                _ => JsValue::Null,
''', '''                // What scrolling to this element moves: "w" when the window
                // does ("f" under a fixed box), then the scrollers, innermost
                // first. "" when it has no box.
                (Some(node), Some("scrollChain")) => match host.geometry.get(&node.id.raw()) {
                    Some(g) => {
                        let mut fixed = false;
                        let mut up = Some(node.clone());
                        while let (false, Some(n)) = (fixed, up) {
                            fixed = host.geometry.get(&n.id.raw()).is_some_and(|g| g.position == 2);
                            up = n.parent();
                        }
                        let mut chain = String::from(if fixed { "f" } else { "w" });
                        let mut at = g.scroller;
                        while let Some(scroller) = at {
                            chain.push_str(&format!(" {scroller}"));
                            at = host.geometry.get(&scroller).and_then(|g| g.scroller);
                        }
                        JsValue::String(chain)
                    }
                    None => JsValue::String(String::new()),
                },
                (Some(node), Some(field)) => node_info(&node, field, &host.templates.borrow()),
                _ => JsValue::Null,
''')
sub('rustkit-bindings/src/dom.rs', '''        write: function (el, x, y) { var s = slotOf(el); N.scrollElement(s.gen, s.id, x, y); },
''', '''        write: function (el, x, y) { var s = slotOf(el); N.scrollElement(s.gen, s.id, x, y); },
        chain: function (el) {
            var raw = info(el, 'scrollChain');
            if (!raw) return null;
            var p = raw.split(' ');
            return { window: p[0] === 'w', scrollers: p.slice(1).map(function (id) { return wrap(+id); }) };
        },
''')

# ---- script
sub('rustkit-bindings/src/web_scroll.js', '''            default:
                if (start >= 0 && start + size <= view) return cur;
                if (size > view || start < 0) return cur + start;
                return cur + start + size - view;
''', '''            default:
                var end = start + size;
                if ((start >= 0 && end <= view) || (start <= 0 && end >= view)) return cur;
                if ((start < 0 && size < view) || (end > view && size > view)) return cur + start;
                return cur + start + size - view;
''')
sub('rustkit-bindings/src/web_scroll.js', '''    method(E, 'scrollIntoView', function (arg) {
        var block = 'start', inline = 'nearest';
        if (arg === false) block = 'end';
        else if (arg !== null && typeof arg === 'object') {
            if (arg.block) block = arg.block;
            if (arg.inline) inline = arg.inline;
        }
        var r = this.getBoundingClientRect(), p = pos();
        to(align(r.left, r.width, g.innerWidth, p.x, inline), align(r.top, r.height, g.innerHeight, p.y, block));
        scrolled(p);
    });
''', '''    // Each scroller around the element in turn, innermost first, then the
    // window. An absolute box skips a scroller its containing block is above,
    // and nothing moves a fixed box but the scrollers inside it. An element
    // with no box scrolls nothing.
    function intoView(el, block, inline) {
        var chain = table.chain(el);
        if (!chain) return;
        chain.scrollers.forEach(function (s) {
            var r = el.getBoundingClientRect(), b = s.getBoundingClientRect(), o = own(s);
            setOwn(s,
                align(r.left - b.left - s.clientLeft, r.width, s.clientWidth, o.x, inline),
                align(r.top - b.top - s.clientTop, r.height, s.clientHeight, o.y, block));
        });
        if (!chain.window) return;
        var r = el.getBoundingClientRect(), p = pos();
        to(align(r.left, r.width, g.innerWidth, p.x, inline), align(r.top, r.height, g.innerHeight, p.y, block));
        scrolled(p);
    }
    method(E, 'scrollIntoView', function (arg) {
        var block = 'start', inline = 'nearest';
        if (arg === false) block = 'end';
        else if (arg !== null && typeof arg === 'object') {
            if (arg.block) block = arg.block;
            if (arg.inline) inline = arg.inline;
        }
        intoView(this, block, inline);
    });

    // The indicated part of the document (HTML §7.4.6.4): an id, then a link's
    // name, as written and then percent-decoded. The empty fragment and `top`
    // are the top of the page; anything else stays where it is.
    function indicated(fragment) {
        function find(name) {
            var el = document.getElementById(name);
            if (el) return el;
            var links = document.getElementsByTagName('a');
            for (var i = 0; i < links.length; i++) {
                if (links[i].getAttribute('name') === name) return links[i];
            }
            return null;
        }
        var el = fragment ? find(fragment) : null;
        if (el) return el;
        try { fragment = decodeURIComponent(fragment); } catch (_) {}
        return fragment ? find(fragment) : null;
    }
    Object.defineProperty(g, '__rkScrollToFragment', {
        value: function (fragment) {
            var el = indicated(fragment);
            if (el) { intoView(el, 'start', 'nearest'); return; }
            if (fragment !== '' && fragment.toLowerCase() !== 'top') return;
            var p = pos();
            to(0, 0);
            scrolled(p);
        },
        configurable: true, writable: true, enumerable: false
    });
''')
sub('rustkit-bindings/src/web_history.js', '''    g.__rustkit_fragment_navigation = function (href) {
        var oldURL = loc.href;
        if (oldURL === href) return;
        entries.length = index + 1;
        entries.push({ url: href, state: null });
        index++;
        setLocation(href);
        g.dispatchEvent(new HashChangeEvent('hashchange', { oldURL: oldURL, newURL: loc.href }));
    };
''', '''    // The same URL again adds no entry and hears no `hashchange`, but scrolls.
    g.__rustkit_fragment_navigation = function (href) {
        var oldURL = loc.href;
        if (oldURL !== href) {
            entries.length = index + 1;
            entries.push({ url: href, state: null });
            index++;
            setLocation(href);
        }
        g.__rustkit_scroll_to_location_fragment();
        if (oldURL !== href) {
            g.dispatchEvent(new HashChangeEvent('hashchange', { oldURL: oldURL, newURL: loc.href }));
        }
    };
    // Scroll to what the URL's fragment names, if it has one (a URL ending in
    // a bare `#` has an empty one, whose `hash` reads as none).
    g.__rustkit_scroll_to_location_fragment = function () {
        var at = loc.href.indexOf('#');
        if (at >= 0 && typeof g.__rkScrollToFragment === 'function') g.__rkScrollToFragment(loc.href.slice(at + 1));
    };
''')

# ---- engine
sub('rustkit-engine/src/lib.rs', '''    /// Navigate to a fragment of the current document (HTML §7.4.2.3.3,
    /// §7.4.6.4): scroll to the element whose id it names (the top of the
    /// page for an empty fragment or `top`; nowhere when nothing matches),
    /// make `target` the URL and tell script, which fires `hashchange`.
    fn navigate_to_fragment(&mut self, id: EngineViewId, target: Url) {
        let fragment = String::from_utf8_lossy(&percent_decode(target.fragment().unwrap_or_default())).into_owned();
        let Some(view) = self.views.get_mut(&id) else {
            return;
        };
        let element = (!fragment.is_empty())
            .then(|| view.document.as_ref()?.get_element_by_id(&fragment))
            .flatten();
        let top = match element {
            Some(el) => view.layout.as_ref().and_then(|l| Self::box_top(l, el.id.raw())),
            None => (fragment.is_empty() || fragment.eq_ignore_ascii_case("top")).then_some(0.0),
        };
        let before = view.scroll_offset;
        if let Some(top) = top {
            view.scroll_offset.1 = top.max(0.0).min(view.max_scroll_offset.1);
        }
        let scrolled = view.scroll_offset != before;
        // Script reads the new offset from here on, `hashchange` included.
        if let (true, Some(bindings)) = (scrolled, view.bindings.as_ref()) {
            bindings.set_scroll_state(view.scroll_offset, view.max_scroll_offset);
        }
        debug!(?id, %target, offset = ?view.scroll_offset, "Navigated to a fragment");
        let script = format!("__rustkit_fragment_navigation({:?})", target.as_str());
        view.url = Some(target);
        if let Err(e) = self.execute_script(id, &script) {
            debug!(?id, ?e, "hashchange listener threw");
        }
        // The page hears the scroll, and its observers report.
        if scrolled {
            if let Some(bindings) = self.views.get(&id).and_then(|v| v.bindings.as_ref()) {
                bindings.notify_scrolled();
            }
            if let Err(e) = self.flush_script_dom_writes(id, Some(RelayoutCause::Scroll)) {
                debug!(?id, ?e, "relayout after a fragment scroll failed");
            }
        }
        // The scroll is a translate at render time; nothing was laid out.
        if let Err(e) = self.render(id) {
            debug!(?id, ?e, "Render after a fragment navigation failed");
        }
    }

    /// The top border edge of the first box `node` generated, in document
    /// coordinates.
''', '''    /// Navigate to a fragment of the current document (HTML §7.4.2.3.3,
    /// §7.4.6.4): make `target` the URL and tell script, which scrolls to
    /// what it names (web_scroll.js) and fires `hashchange`.
    fn navigate_to_fragment(&mut self, id: EngineViewId, target: Url) {
        let Some(view) = self.views.get_mut(&id) else {
            return;
        };
        debug!(?id, %target, "Navigating to a fragment");
        let script = format!("__rustkit_fragment_navigation({:?})", target.as_str());
        view.url = Some(target);
        if let Err(e) = self.execute_script(id, &script) {
            debug!(?id, ?e, "hashchange listener threw");
        }
    }

    /// A page loaded with a fragment opens at what it names, unless the page
    /// or the user has already moved the window.
    fn scroll_to_loaded_fragment(&mut self, id: EngineViewId) {
        let due = self.views.get(&id).is_some_and(|view| {
            view.scroll_offset == (0.0, 0.0) && view.url.as_ref().is_some_and(|url| url.fragment().is_some())
        });
        if due {
            if let Err(e) = self.execute_script(id, "__rustkit_scroll_to_location_fragment()") {
                debug!(?id, ?e, "scroll to the loaded fragment threw");
            }
        }
    }

    /// The top border edge of the first box `node` generated, in document
    /// coordinates.
''')
sub('rustkit-engine/src/lib.rs', '''            debug!(?id, nav_id, "Yielded load was cancelled as it finished");
            return Ok(());
        }
''', '''            debug!(?id, nav_id, "Yielded load was cancelled as it finished");
            return Ok(());
        }
        self.scroll_to_loaded_fragment(id);
''')
sub('rustkit-engine/src/lib.rs', '''            debug!(?id, %url, "Navigation cancelled as it finished");
            return Ok(());
        }

        // Finish navigation
''', '''            debug!(?id, %url, "Navigation cancelled as it finished");
            return Ok(());
        }
        self.scroll_to_loaded_fragment(id);

        // Finish navigation
''')
