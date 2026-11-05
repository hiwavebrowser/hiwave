"""CH2.E9 part 2 red: the app's exhaustive PageEvent matches know Ipc."""
p = '/Users/petecopeland/Repos/.worktrees/z-ch2-e9/crates/hiwave-app/src/webview_rustkit.rs'
s = open(p).read()


def sub(old, new):
    global s
    assert s.count(old) == 1, old
    s = s.replace(old, new, 1)


sub('''                PageEvent::Cursor(_) | PageEvent::Unresponsive | PageEvent::Closed => {}''',
    '''                PageEvent::Ipc { .. } | PageEvent::Cursor(_) | PageEvent::Unresponsive | PageEvent::Closed => {}''')
sub('''        | PageEvent::NavigateRequested { nav_id, .. } => *nav_id,''',
    '''        | PageEvent::NavigateRequested { nav_id, .. }
        | PageEvent::Ipc { nav_id, .. } => *nav_id,''')
open(p, 'w').write(s)
print('ok')
