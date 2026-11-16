# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HiWave is a privacy-first browser built from scratch in Rust, designed to help users browse less through features like The Shelf (tab decay), Workspaces, and built-in ad/tracker blocking. The project consists of:

- **hiwave-macos/** - macOS platform (RustKit engine; the reference tree, where engine work lands first)
- **hiwave-windows/** - Windows platform (RustKit engine; synced from macOS)
- **hiwave-linux/** - Linux platform (RustKit engine; synced from macOS)
- **test-infrastructure/** - Performance testing harness
- **churn-report/** - Code churn analysis tool

The three platform directories and `churn-report/` are git submodules pinned to each repo's `master`. Status as of 2026-11: see `docs/PROGRESS-2026-11.md`. Generated output (`badges/`, `charts/parity-trend.svg`, `charts/perf-trend.svg`, `charts/platform-comparison.svg`, `metrics/unified.json`, `metrics/parity_results.json`, `churn-reports/`) is written by the workflows in `.github/workflows/`; do not edit it by hand.

## Build Commands

### Windows
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
./scripts/run-rustkit.sh        # RustKit mode (default; the WebKit content fallback was removed in October 2026)
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

Custom browser engine written in Rust. Key crates, in each platform repo's `crates/` directory (the list below was written against hiwave-windows in January 2026; check the repo for the current set):

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
- **macOS**: RustKit for all page content
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
