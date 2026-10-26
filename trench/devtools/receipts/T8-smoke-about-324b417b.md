**#799 item (4): hiwave-smoke `--html-file` check done @ 324b417b** (follow-up to the fold comment)

`hiwave-smoke` (`--profile parity`, built at 324b417b) ran `crates/hiwave-app/src/ui/about.html` with `builtins_capture.sh`'s arguments: `--width 1280 --height 800 --duration-ms 500 --dump-frame … --perf-output …`. It ran in a real window, the window locks were free, and it was 14:05 ET. I started it through a python3 subprocess wrapper, which is how this seat runs built binaries.
- It exited 0 and wrote the frame.
- The log shows `Running inline script of an HTML load source=inline#1 bytes=987`, the fixture's one script. It shows no script error and no panic.
- The frame looks right: the HIWAVE header, the tagline, the script-filled version line `v0.1.0-alpha`, the support button and the "Why HiWave Exists" card. It is not blank and nothing is missing.

So the fixtures that now run their scripts still capture cleanly. I did not run the other four builtins (new_tab, settings, chrome, shelf).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
