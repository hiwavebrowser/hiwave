/// What a selector walk that reads an ancestor's earlier siblings from the
/// DOM needs for one build or script query ([`WalkCheckedScope`]).
#[derive(Default)]
struct WalkState {
    /// The checkedness that has left the `checked` attribute (a click, a
    /// script), by raw NodeId (`dom_sibling_key`). The subject's own
    /// siblings come with their live state from the build.
    checked: HashMap<usize, bool>,
    /// `nearest_earlier_sibling_matching` by (compound address, raw NodeId
    /// it looks back from, inclusive): the nearest element at or before it
    /// that matches. Valid for one scope: the DOM, checkedness and the
    /// prepared selectors (kept by the rule index or the query) stand
    /// still in it. None outside a scope: nothing is kept.
    memo: Option<HashMap<(usize, usize), Option<Rc<Node>>>>,
}

thread_local! {
    static WALK: std::cell::RefCell<WalkState> = std::cell::RefCell::new(WalkState::default());
}

/// Sets [`WALK`] for its lifetime, with an empty memo, and puts the
/// previous state back: around a view's build (its `checked_states`) and a
/// script query. `None` keeps the enclosing scope's checkedness.
pub(crate) struct WalkCheckedScope(WalkState);

impl WalkCheckedScope {
    pub(crate) fn enter(checked: Option<HashMap<usize, bool>>) -> Self {
        WalkCheckedScope(WALK.with(|w| {
            let checked = checked.unwrap_or_else(|| w.borrow().checked.clone());
            w.replace(WalkState { checked, memo: Some(HashMap::new()) })
        }))
    }
}

impl Drop for WalkCheckedScope {
    fn drop(&mut self) {
        let previous = std::mem::take(&mut self.0);
        WALK.with(|w| *w.borrow_mut() = previous);
    }
}

/// The element sibling right before `node` in the DOM tree. Selectors read
/// the DOM tree, so a host's light children are siblings as they stand in it.
fn previous_element_sibling(node: &Rc<Node>) -> Option<Rc<Node>> {
    let mut at = node.previous_sibling();
    while let Some(n) = at {
        if n.is_element() {
            return Some(n);
        }
        at = n.previous_sibling();
    }
    None
}

/// An earlier sibling read from the DOM as `+` / `~` see it: what the walk
/// tests once a descendant or child step has moved it up to an ancestor
/// (`.ctrl:checked + .icon .off`), with the live checkedness of the scope.
fn dom_sibling_key(node: &Rc<Node>) -> Option<SiblingKey> {
    let NodeType::Element { tag_name, attributes, .. } = &node.node_type else {
        return None;
    };
    let tag = lower_tag(tag_name).into_owned();
    let live = WALK.with(|w| w.borrow().checked.get(&node.id.raw()).copied());
    let state = match live {
        Some(on) if tag == "input" && on != attributes.contains_key("checked") => {
            let mut attributes = attributes.clone();
            if on {
                attributes.insert("checked".to_string(), String::new());
            } else {
                attributes.remove("checked");
            }
            ElementState::of(&tag, &attributes)
        }
        _ => ElementState::of(&tag, attributes),
    };
    Some((tag, element_classes(attributes), attributes.get("id").cloned(), state))
}

/// The nearest element sibling before `from` that `test` (a `~` step's
/// compound, as the sibling) accepts. Memoised in the scope's [`WalkState`]:
/// every subject under one parent asks it, and a compound that matches no
/// sibling (`.absent ~ li span`) would rescan them all per subject. The
/// siblings share their ancestors, so the answer is the same for all.
fn nearest_earlier_sibling_matching(
    from: &Rc<Node>,
    compound: &AncestorCompound,
    test: &dyn Fn(&Rc<Node>) -> bool,
) -> Option<Rc<Node>> {
    let id = compound as *const AncestorCompound as usize;
    let mut visited: Vec<usize> = Vec::new();
    let mut at = previous_element_sibling(from);
    let found = loop {
        let Some(n) = at else { break None };
        let known = WALK.with(|w| w.borrow().memo.as_ref().and_then(|m| m.get(&(id, n.id.raw())).cloned()));
        if let Some(hit) = known {
            break hit;
        }
        visited.push(n.id.raw());
        if test(&n) {
            break Some(n);
        }
        at = previous_element_sibling(&n);
    };
    WALK.with(|w| {
        if let Some(memo) = w.borrow_mut().memo.as_mut() {
            for raw in visited {
                memo.insert((id, raw), found.clone());
            }
        }
    });
    found
}

