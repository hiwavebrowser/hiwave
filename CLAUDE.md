# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HiWave is a privacy-first browser built from scratch in Rust, designed to help users browse less through features like The Shelf (tab decay), Workspaces, and built-in ad/tracker blocking. The project consists of:

- **hiwave-windows/** - Windows platform (RustKit engine, most complete)
- **hiwave-macos/** - macOS platform (RustKit + WebKit hybrid)
- **hiwave-linux/** - Linux platform (GTK WebKit)
- **test-infrastructure/** - Performance testing harness
- **churn-report/** - Code churn analysis tool
- **ai-orchestrator/** - AI workflow orchestration

## Build Commands

### Windows (Primary Development Platform)
```powershell
# Default build (RustKit hybrid mode)
cargo build -p hiwave-app
cargo run -p hiwave-app

# Quick syntax check
cargo check -p hiwave-app

# Run modes
.\scripts\run-rustkit.ps1       # RustKit for content, WebView2 for chrome (default)
.\scripts\run-webview2.ps1      # WebView2 fallback
.\scripts\run-native-win32.ps1  # 100% RustKit (experimental)
```

### macOS
```bash
./scripts/run-rustkit.sh        # RustKit mode (default)
./scripts/run-webkit.sh         # WebKit fallback
```

### Linux
```bash
cargo run --release -p hiwave-app
./scripts/run.sh                # Release build
./scripts/run-debug.sh          # Debug with RUST_LOG=debug
```

## Testing

```bash
cargo test --workspace          # All tests
cargo test -p hiwave-shield     # Single crate
cargo test test_should_block    # Single test
cargo test -- --nocapture       # With output

cargo fmt --all                 # Format
cargo clippy --workspace -- -D warnings  # Lint
```

## Architecture

### RustKit Browser Engine

Custom browser engine written from scratch in Rust (~80,000 lines). Key crates in `hiwave-windows/crates/`:

**Core Rendering Pipeline:**
- `rustkit-html` - HTML5 tokenizer & tree builder (replaced html5ever)
- `rustkit-cssparser` - CSS tokenizer (replaced cssparser)
- `rustkit-dom` - DOM tree, events, forms
- `rustkit-css` - CSS styling, cascade, selectors
- `rustkit-layout` - Block, inline, flexbox, grid layout
- `rustkit-compositor` - GPU rendering (wgpu)
- `rustkit-renderer` - Display list execution
- `rustkit-text` - Text shaping (replaced dwrote)

**Web Platform:**
- `rustkit-js` - JavaScript (Boa engine)
- `rustkit-bindings` - JS <-> DOM bridge
- `rustkit-net` - Networking, fetch, downloads
- `rustkit-http` - HTTP client (replaced reqwest)
- `rustkit-codecs` - Image decoding (replaced image crate)
- `rustkit-canvas` - Canvas 2D API
- `rustkit-webgl` - WebGL 1.0
- `rustkit-media` - Audio/video
- `rustkit-svg` - SVG support
- `rustkit-animation` - CSS animations/transitions
- `rustkit-sw` - Service Workers
- `rustkit-idb` - IndexedDB
- `rustkit-worker` - Web Workers
- `rustkit-a11y` - Accessibility

**Engine Orchestration:**
- `rustkit-engine` - Multi-view orchestration
- `rustkit-viewhost` - Win32 window hosting
- `rustkit-core` - Task scheduling, navigation

### HiWave Application Crates

- `hiwave-app` - Main application, event loop, WebView setup
- `hiwave-core` - Shared types (TabId, WorkspaceId)
- `hiwave-shell` - Tab and workspace management
- `hiwave-shield` - Ad blocking (Brave's adblock-rust)
- `hiwave-vault` - Password manager (AES-256)
- `hiwave-analytics` - Local analytics

### Key Files

| File | Purpose |
|------|---------|
| `hiwave-app/src/main.rs` | Entry point, event loop |
| `hiwave-app/src/state.rs` | AppState, persistence, shelf logic |
| `hiwave-app/src/webview_rustkit.rs` | RustKit engine adapter |
| `hiwave-app/src/ipc/mod.rs` | IPC message definitions |
| `hiwave-app/src/ui/chrome.html` | Browser UI (HTML/CSS/JS) |

## Commit Message Prefixes

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Formatting only
- `refactor:` - Code restructuring
- `test:` - Adding tests
- `chore:` - Maintenance

## Cross-Platform Considerations

Each platform has its own WebView backend:
- **Windows**: WebView2 (Edge Chromium) or 100% RustKit
- **macOS**: WKWebView or RustKit hybrid
- **Linux**: GTK WebKit2

RustKit engine crates are shared but platform-specific code lives in:
- `rustkit-viewhost` (Windows Win32)
- Platform-specific features in `hiwave-app/src/platform/`

## Testing Infrastructure

Performance testing with Monte Carlo methodology:
```bash
cd test-infrastructure/harness
cargo build --release
./target/release/hiwave-perf --iterations 100
```

Regression detection thresholds: Total Time >5%, Individual Phases >10%, Memory >15%.

## AI Orchestrator

WorkOrder-based development tracking in `.ai/`:
- `.ai/roadmap_index.json` - Shared roadmap index
- `.ai/work_orders/` - Work order specs
- `.ai/artifacts/` - Run artifacts (gitignored)

# HiWave canon (Pete, 2026-10-07 — "write it in digital stone")

- **Endgame:** HiWave is 100% RustKit. Phase X removes wry/tao/WebKit: fallback
  feature deleted first; chrome UI rendered by RustKit behind a flag (gate:
  `chrome_rustkit` board case < 2% and a hand test of URL typing, tabs, shelf,
  find-in-page); then rustkit-viewhost owns the macOS window and tao leaves
  macOS; Windows/Linux keep tao until their viewhosts catch up; then wry goes.
- **Release to main every Friday at midnight ET** (develop → master, with notes).
- **Workers Mon–Fri only.** Every LLM seat is dormant Fri 00:00 → Mon 06:00.
  Measurement jobs with no model cost (quiet board, handtest log-only) keep running.
- **No Thursday freeze.** Thursday night = baseline (quiet board + full real-window
  run, binary banked). Fix through Friday midnight; the Thursday baseline is the
  regression reference for the release.
- **Pete hand-tests the release on the weekend** and takes notes (site, action,
  expected, seen, screenshot). Monday's queue starts from those notes.
- **One alternate baseline per week:** Windows or Linux, alternating.
- **Weekly artifact every Friday:** live-site improvement over the week (/60 and
  /75 trend, H-list closed vs open, per-site before/after in prose; frames private).
- **Codex** is the independent reviewer (Friday, on the promotion head) and a
  weekend test partner; not a code worker unless a bounded, test-pinned job fits.
