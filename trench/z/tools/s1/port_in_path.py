#!/usr/bin/env python3
"""S1 test: move the target port from a shared static into the request path (parallel-test race)."""
import sys
p = sys.argv[1] + '/crates/rustkit-engine/src/redirect_base_tests.rs'; s = open(p).read()
def rep(a, b):
    global s
    assert a in s, a
    s = s.replace(a, b)
rep('''use std::sync::atomic::{AtomicU16, Ordering};

static TARGET_PORT: AtomicU16 = AtomicU16::new(0);
''', '')
rep('''    match path {
        "/start" => {
            let to: &'static str = Box::leak(
                format!("http://127.0.0.1:{}/app/page", TARGET_PORT.load(Ordering::SeqCst)).into_boxed_str(),
            );
            (302, "text/html", vec![("Location", to)], String::new())
        }
        _ => (404, "text/plain", vec![], "not found on the first host".into()),
    }''', '''    // `/start/<port>` redirects to the second host on that port.
    match path.strip_prefix("/start/") {
        Some(port) => {
            let to: &'static str = Box::leak(format!("http://127.0.0.1:{port}/app/page").into_boxed_str());
            (302, "text/html", vec![("Location", to)], String::new())
        }
        None => (404, "text/plain", vec![], "not found on the first host".into()),
    }''')
rep('''    TARGET_PORT.store(target.url("/").port().unwrap(), Ordering::SeqCst);
''', '')
rep('''first.url("/start")''', '''first.url(&format!("/start/{}", target.url("/").port().unwrap()))''')
rep('''    assert_eq!(first_paths, vec!["/start"], "nothing relative is asked of the first host");''',
    '''    assert_eq!(first_paths.len(), 1, "nothing relative is asked of the first host: {first_paths:?}");''')
rep("first redirects to `/app/page`", "first (`/start/<port>`) redirects to `/app/page`")
open(p, 'w').write(s)
print('ok', s.count('TARGET_PORT'))
