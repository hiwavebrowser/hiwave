root = '/Users/petecopeland/Repos/.worktrees/z-gcs1/crates/'
def sub(path, old, new, count=1):
    p = root + path
    # newline='' keeps CRLF files as they are.
    s = open(p, newline='').read()
    assert s.count(old) == count, (path, old, s.count(old))
    open(p, 'w', newline='').write(s.replace(old, new))

T = 'rustkit-engine/src/computed_pseudo_tests.rs'
sub(T, '''<div id=hidden></div><div id=shown></div><div id=own></div><div id=none></div>
        <div id=plain></div><div id=toggle class=on></div></body>''',
    '''<div id=hidden>x</div><div id=shown>x</div><div id=own>x</div><div id=none>x</div>
        <div id=plain>x</div><div id=toggle class=on>x</div></body>''')

E = 'rustkit-engine/src/lib.rs'
for name, var in (('before', 'before_box'), ('after', 'after_box')):
    sub(E, '''                if let Some(%s) = memoized_pseudo_style(node.id, Pseudo::%s, || {
                    self.pseudo_element_style(
                        &tag_lower,
                        attributes,
                        stylesheets,
                        ancestors,
                        siblings_before,
                        sib,
                        "::%s",
                        Some(&layout_box.style),
                    )
                })
                .inspect(container_query::note_pseudo)
''' % (var, name.capitalize(), name), '''                let %s_style = memoized_pseudo_style(node.id, Pseudo::%s, || {
                    self.pseudo_element_style(
                        &tag_lower,
                        attributes,
                        stylesheets,
                        ancestors,
                        siblings_before,
                        sib,
                        "::%s",
                        Some(&layout_box.style),
                    )
                });
                self.note_pseudo_style(node.id.raw(), "::%s", %s_style.as_ref());
                if let Some(%s) = %s_style
                .inspect(container_query::note_pseudo)
''' % (name, name.capitalize(), name, name, name, var, name))

sub(E, '''            self.with_building_lay(|lay| lay.boxless_styles.borrow_mut().clear());
''', '''            self.with_building_lay(|lay| {
                lay.boxless_styles.borrow_mut().clear();
                lay.pseudo_styles.borrow_mut().clear();
            });
''')
sub(E, '''            lay.boxless_styles.borrow_mut().insert(node, lines);
        });
    }
}
''', '''            lay.boxless_styles.borrow_mut().insert(node, lines);
        });
    }

    /// Remember the cascaded `::before`/`::after` style of `node` for
    /// `getComputedStyle(el, pseudo)`, in the map of the view being built. A
    /// `display: none` pseudo has no box to read it from, and that is the
    /// usual shape of the breakpoint idiom. `None` drops what a restyle left.
    fn note_pseudo_style(&self, node: usize, pseudo: &'static str, style: Option<&ComputedStyle>) {
        self.with_building_lay(|lay| {
            let mut styles = lay.pseudo_styles.borrow_mut();
            match style {
                Some(style) => {
                    styles.insert((node, pseudo), style.clone());
                }
                None if !styles.is_empty() => {
                    styles.remove(&(node, pseudo));
                }
                None => {}
            }
        });
    }
}
''')
sub(E, '''        let snapshot = geometry_with_root(&layout, root_element, &lay.boxless_styles.borrow());
''', '''        let snapshot = geometry_with_root(
            &layout,
            root_element,
            &lay.boxless_styles.borrow(),
            &lay.pseudo_styles.borrow(),
        );
''')
sub(E, '''                    geometry_with_root(&snapshot_of, root_element, &styled.boxless_styles.borrow())
''', '''                    geometry_with_root(
                        &snapshot_of,
                        root_element,
                        &styled.boxless_styles.borrow(),
                        &styled.pseudo_styles.borrow(),
                    )
''')
sub(E, '''/// keeps that box's style.
fn geometry_with_root(
    layout: &LayoutBox,
    root_element: Option<usize>,
    boxless: &HashMap<usize, String>,
) -> (HashMap<usize, rustkit_bindings::BoxGeometry>, HashMap<usize, String>) {
''', '''/// keeps that box's style. `pseudos` (`ViewLayout::pseudo_styles`) join their
/// element's lines, each row's name prefixed `::before ` or `::after `.
fn geometry_with_root(
    layout: &LayoutBox,
    root_element: Option<usize>,
    boxless: &HashMap<usize, String>,
    pseudos: &HashMap<(usize, &'static str), ComputedStyle>,
) -> (HashMap<usize, rustkit_bindings::BoxGeometry>, HashMap<usize, String>) {
''')
sub(E, '''        snapshot.1.entry(*node).or_insert_with(|| lines.clone());
    }
    snapshot
}
''', '''        snapshot.1.entry(*node).or_insert_with(|| lines.clone());
    }
    for ((node, pseudo), style) in pseudos {
        if let Some(lines) = snapshot.1.get_mut(node) {
            for row in pseudo_style_lines(style).lines() {
                lines.push_str(&format!("\\n{pseudo} {row}"));
            }
        }
    }
    snapshot
}

/// `computed_style_lines` for a pseudo-element's cascaded style. No box's
/// used values are read: `width`/`height` are the declared lengths, and the
/// rest of the box model reads 0.
fn pseudo_style_lines(style: &ComputedStyle) -> String {
    let mut style = style.clone();
    // An out-of-flow or floated box is blockified (CSS Display 3 §2.7).
    let out_of_flow = matches!(style.position, rustkit_css::Position::Absolute | rustkit_css::Position::Fixed)
        || style.float != rustkit_css::Float::None;
    if out_of_flow && style.display == rustkit_css::Display::Inline {
        style.display = rustkit_css::Display::Block;
    }
    let declared = |l: &rustkit_css::Length| match l {
        rustkit_css::Length::Px(p) => css_px(*p),
        _ => "auto".to_string(),
    };
    let (width, height) = (declared(&style.width), declared(&style.height));
    computed_style_lines(&LayoutBox::new(BoxType::Inline, style))
        .lines()
        .map(|row| match row.split_once('\\t') {
            Some(("width", _)) => format!("width\\t{width}"),
            Some(("height", _)) => format!("height\\t{height}"),
            _ => row.to_string(),
        })
        .collect::<Vec<_>>()
        .join("\\n")
}
''')
sub(E, '''                } else if let Some(text) = rustkit_css::content::content_string(v) {
                    // The value's strings, escapes resolved and joined. It
                    // was the text between the first and last quote as
                    // written, so an icon font's `"\\f007"` was five
                    // characters of the fallback font.
                    style.content = Some(text);
                }
''', '''                } else if let Some(text) = rustkit_css::content::content_string(v) {
                    // The value's strings, escapes resolved and joined. It
                    // was the text between the first and last quote as
                    // written, so an icon font's `"\\f007"` was five
                    // characters of the fallback font.
                    style.content = Some(text);
                } else if v.contains('(')
                    || matches!(v, "open-quote" | "close-quote" | "no-open-quote" | "no-close-quote")
                {
                    // Valid, and generating nothing here (a limit of
                    // `content_string`): it still replaces a string from a
                    // lower-precedence rule, which used to paint.
                    style.content = None;
                }
''')

L = 'rustkit-engine/src/layout_ctx.rs'
sub(L, '''            ("boxless_styles", lay.boxless_styles.try_borrow_mut().is_ok()),
''', '''            ("boxless_styles", lay.boxless_styles.try_borrow_mut().is_ok()),
            ("pseudo_styles", lay.pseudo_styles.try_borrow_mut().is_ok()),
''')
sub(L, '''    pub(crate) boxless_styles: RefCell<HashMap<usize, String>>,
}
''', '''    pub(crate) boxless_styles: RefCell<HashMap<usize, String>>,
    /// The cascaded `::before`/`::after` styles of this view's elements, by
    /// raw NodeId and pseudo name, for `getComputedStyle(el, pseudo)`. Kept
    /// like `boxless_styles`.
    pub(crate) pseudo_styles: RefCell<HashMap<(usize, &'static str), crate::ComputedStyle>>,
}
''')

B = 'rustkit-bindings/src/dom.rs'
sub(B, '''    function computedMap(el) {
        var raw = info(el, 'computed');
        var m = {};
        if (raw) {
            raw.split('\\n').forEach(function (line) {
                var i = line.indexOf('\\t');
                if (i > 0) m[line.slice(0, i)] = line.slice(i + 1);
            });
''', '''    function computedMap(el, pseudo) {
        var raw = info(el, 'computed');
        var m = {}, own = null, prefix = pseudo ? pseudo + ' ' : null;
        if (raw) {
            raw.split('\\n').forEach(function (line) {
                var i = line.indexOf('\\t');
                if (i <= 0) return;
                var name = line.slice(0, i);
                // The element's rows, then its pseudo-elements' (`::before name`).
                if (name.charAt(0) !== ':') m[name] = line.slice(i + 1);
                else if (prefix && name.indexOf(prefix) === 0) {
                    (own = own || {})[name.slice(prefix.length)] = line.slice(i + 1);
                }
            });
''')
sub(B, '''                if (v) m[name] = v;
            }
        }
        return m;
    }
    function makeComputed(el) {
        var m = computedMap(el);
''', '''                if (v) m[name] = v;
            }
        }
        return pseudo ? pseudoMap(m, own, pseudo) : m;
    }
    // What a pseudo-element reads: its own cascaded rows, or, with no rule
    // that set `content`, the initial values and what it inherits.
    var INHERITED = ['color', 'font-family', 'font-size', 'font-style', 'font-weight', 'letter-spacing',
        'line-height', 'text-align', 'text-transform', 'visibility', 'white-space'];
    function pseudoMap(m, own, pseudo) {
        var isBox = pseudo === '::before' || pseudo === '::after';
        if (own) {
            if (own.content === 'normal') own.content = 'none';
            return own;
        }
        if (!m.display) return {};
        var out = { display: 'inline', position: 'static', width: 'auto', height: 'auto',
            content: isBox ? 'none' : 'normal' };
        INHERITED.forEach(function (n) { if (m[n]) out[n] = m[n]; });
        return out;
    }
    // The canonical name of getComputedStyle's second argument, '' for the
    // element itself, or null for one that names no pseudo-element.
    function pseudoArgument(p) {
        if (p === undefined || p === null) return '';
        p = String(p).toLowerCase();
        if (p === '') return '';
        var named = /^(?:::?)?(before|after|first-line|first-letter)$/.exec(p);
        if (named) return '::' + named[1];
        return /^::(marker|selection|backdrop|placeholder)$/.test(p) ? p : null;
    }
    function makeComputed(el, pseudo) {
        var m = pseudo === null ? {} : computedMap(el, pseudo);
''')
sub(B, '''    g.getComputedStyle = function getComputedStyle(el) {
''', '''    g.getComputedStyle = function getComputedStyle(el, pseudo) {
''')
sub(B, '''        return makeComputed(el);
    };
''', '''        return makeComputed(el, pseudoArgument(pseudo));
    };
''')
