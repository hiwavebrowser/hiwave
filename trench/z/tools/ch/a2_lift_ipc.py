"""CH3.A2 step 2: lift the WebKit chrome's IPC closure into handle_chrome_ipc()."""
p = '/Users/petecopeland/Repos/.worktrees/z-ch3-a2/crates/hiwave-app/src/main.rs'
lines = open(p).read().split('\n')
# 1-indexed: 845 `.with_ipc_handler(move |message| {`, 846 `let body = message.body();`,
# 1271 `        })`
assert lines[844].strip() == '.with_ipc_handler(move |message| {', lines[844]
assert lines[845].strip() == 'let body = message.body();', lines[845]
assert lines[1270] == '        })', lines[1270]
assert lines[1271].strip() == '.build_as_child(&window)', lines[1271]
body = lines[846:1270]
fn_body = []
for l in body:
    if l.startswith('        '):
        fn_body.append(l[8:])
    else:
        assert l.strip() == '', l
        fn_body.append(l)
new_call = [
    '        .with_ipc_handler(move |message| {',
    '            handle_chrome_ipc(message.body(), &chrome_proxy, &chrome_state, &settings_proxy_for_handler)',
    '        })',
]
lines = lines[:844] + new_call + lines[1271:]
# put the fn before `fn sync_tabs_to_chrome`
idx = next(i for i, l in enumerate(lines) if l.startswith('fn sync_tabs_to_chrome('))
fn = [
    '/// The chrome\'s `window.ipc` messages, as the WebKit chrome view hands',
    '/// them over. A function, not the handler closure, so the RustKit chrome',
    '/// view (CH3.A2) can feed it the same messages.',
    'fn handle_chrome_ipc(',
    '    body: &str,',
    '    chrome_proxy: &tao::event_loop::EventLoopProxy<UserEvent>,',
    '    chrome_state: &Arc<Mutex<AppState>>,',
    '    settings_proxy_for_handler: &tao::event_loop::EventLoopProxy<UserEvent>,',
    ') {',
] + fn_body + ['}', '']
lines = lines[:idx] + fn + lines[idx:]
open(p, 'w').write('\n'.join(lines))
print('ok', len(fn_body))
