"""Resolve the SetLoading conflict: keep ChromeUi eval + #901's macOS gate."""
p = '/Users/petecopeland/Repos/.worktrees/z-ch3-a2/crates/hiwave-app/src/main.rs'
s = open(p).read()
start = s.index('<<<<<<< HEAD\n')
end = s.index('>>>>>>> origin/atlas/z-ch2-e9-ipc-push\n') + len('>>>>>>> origin/atlas/z-ch2-e9-ipc-push\n')
assert s.count('<<<<<<<') == 1
s = s[:start] + '''                        let _ = chrome_for_events.eval(&script);
                        // Inject context menu handler and audio detector when page finishes loading.
                        // Not on macOS: the content view is RustKit, which never
                        // ran these WebKit helpers (no SetLoading was sent there
                        // before CH2.E9), and they post to the WebKit IPC.
                        #[cfg(not(target_os = "macos"))]
''' + s[end:]
open(p, 'w').write(s)
print('ok', s.count('wry::WebView::evaluate_script('))
