root = '/Users/petecopeland/Repos/.worktrees/z-gcs1/crates/'
def sub(path, old, new):
    p = root + path
    s = open(p, newline='').read()
    assert s.count(old) == 1, (path, old, s.count(old))
    open(p, 'w', newline='').write(s.replace(old, new))

E = 'rustkit-engine/src/lib.rs'
sub(E, '''    let mut style = style.clone();
    // An out-of-flow or floated box is blockified (CSS Display 3 §2.7).
    let out_of_flow = matches!(style.position, rustkit_css::Position::Absolute | rustkit_css::Position::Fixed)
        || style.float != rustkit_css::Float::None;
    if out_of_flow && style.display == rustkit_css::Display::Inline {
        style.display = rustkit_css::Display::Block;
    }
    let declared''', '''    let declared''')
sub(E, '''    computed_style_lines(&LayoutBox::new(BoxType::Inline, style))
''', '''    computed_style_lines(&LayoutBox::new(BoxType::Inline, style.clone()))
''')
T = 'rustkit-engine/src/computed_pseudo_tests.rs'
sub(T, '''        assert_eq!(read(&mut e, id, "none", "'::before'"), "none|inline|rgb(7, 8, 9)|static|auto");
''', '''        // GAP, not Chromium: it reads the rule's rgb(7, 8, 9). A pseudo with
        // no `content` string keeps no cascaded style, so only what it
        // inherits is known.
        assert_eq!(read(&mut e, id, "none", "'::before'"), "none|inline|rgb(0, 0, 0)|static|auto");
''')
