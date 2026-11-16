# HiWave Browser Community

> **Status note, 2026-11-16.** This page was written in January 2026. Its parity percentages, phase labels and dates describe the project at that time and have not been re-measured. For current, sourced figures see [Recent progress](https://github.com/hiwavebrowser/hiwave/blob/master/docs/PROGRESS-2026-11.md). Links to the `hiwavebrowser/community` repository and its Discussions do not currently resolve; use the [issue tracker](https://github.com/hiwavebrowser/hiwave/issues) instead.

Welcome to the HiWave Browser community repository! This repo enables community members to contribute to HiWave's development through testing, bug reports, feature feedback, and more.

## What is HiWave?

HiWave is a modern web browser built with a custom rendering engine (RustKit). We're working toward pixel-perfect web compatibility and need your help to get there.

---

## Why Your Help Matters

### Putting Things in Perspective

Building a browser is typically a massive undertaking:

| Browser | Company | Engineers | Annual Budget | Development Time |
|---------|---------|-----------|---------------|------------------|
| **Chrome** | Google | 1,000+ | ~$2-3 billion | 16+ years |
| **Firefox** | Mozilla | 750+ | ~$500 million | 20+ years |
| **Safari** | Apple | 500+ | Undisclosed (billions) | 20+ years |
| **Edge** | Microsoft | 300+ | ~$500 million | 9+ years (Chromium) |
| **HiWave** | Indie project | 1 | **~$300** | **A few weeks** |

That last row isn't a typo.

### What We've Built So Far

Starting with little more than curiosity and determination, HiWave has grown into:

- A **custom rendering engine** (RustKit) written from scratch in Rust
- **59% pixel parity** with Chrome on the January 2026 test set (see the status note above for current figures)
- Native **macOS and Windows** applications
- A working browser that renders real websites
- GPU-accelerated compositing
- CSS Flexbox, Grid, and modern layout support
- A comprehensive testing infrastructure

People say building a browser engine from scratch is nearly impossible without massive resources. HiWave is proof that passion and persistence can go a long way — but imagine what we could do *together*.

### The Goal

**Become a genuine alternative to Chrome by the end of 2026.**

Not by tearing anything down, but by building something worth choosing. A browser that's fast, respects your privacy, and puts users first.

We're not fighting against other browsers — we're building *for* people who want more choice on the web.

### Thank You to Early Contributors

This project hasn't been entirely solo. Special thanks to:

- **Claude** (yes, the AI) — Pair programming partner through countless late-night sessions
- The early testers who found bugs and helped squash them
- Everyone who offered feedback, encouragement, or just said "this is cool"

Every bit of support has made a difference.

### How You Can Be Part of This

You don't need to be an expert. You don't need to write code. Every contribution helps:

- **5 minutes**: Report a website that doesn't look right
- **30 minutes**: Create a parity test case for a CSS feature
- **An hour**: Help improve documentation or answer questions
- **Ongoing**: Spread the word and help grow the community

The best open source projects are built by communities, not individuals. HiWave has the foundation — now it needs people like you to help it grow.

---

### The Power of Community

Here's what collective effort can achieve:

- **100 contributors** submitting **10 tests each** = **1,000 test cases**
- **500 users** reporting **5 site issues each** = **2,500 compatibility fixes**
- **1,000 people** sharing with **5 friends each** = **5,000 new users**

Small contributions add up to something big.

---

**Want to help out?** Here's how to get started.

---

## How You Can Help

| Contribution Type | Difficulty | Impact | Link |
|-------------------|------------|--------|------|
| **Parity Tests** | Medium | High | [Submit a test](./parity-tests/README.md) |
| **Bug Reports** | Easy | High | [Report a bug](./bug-reports/README.md) |
| **Feature Requests** | Easy | Medium | [Request a feature](./feature-requests/README.md) |
| **UI/UX Feedback** | Easy | Medium | [Give feedback](./feedback/ui-ux/README.md) |
| **Compatibility Reports** | Easy | High | [Report site issues](./feedback/compatibility/README.md) |
| **Documentation** | Medium | Medium | [Improve docs](./docs/README.md) |
| **Translations** | Medium | Medium | [Help translate](./localization/README.md) |

## Quick Start

### Report a Website That Doesn't Render Correctly

1. Go to [Issues](https://github.com/hiwavebrowser/community/issues/new?template=compatibility-report.yml)
2. Enter the URL that has problems
3. Describe what looks wrong vs. Chrome/Safari
4. Attach screenshots if possible

### Submit a Parity Test Case

If you're technically inclined and want to help us achieve pixel-perfect rendering:

1. Read the [Parity Test Guide](./parity-tests/README.md)
2. Create a minimal HTML file that reproduces a rendering difference
3. Capture a Chrome baseline screenshot
4. Submit via PR using our template

### Join the Discussion

- [Discord](https://discord.gg/hiwave) - Real-time chat with the team
- [Discussions](https://github.com/hiwavebrowser/community/discussions) - Longer-form conversations

## Current Focus: 80%+ Parity

We're pushing to achieve **80%+ pixel parity** with Chrome. Here's where we need the most help:

| Area | Current Parity | Help Needed |
|------|----------------|-------------|
| CSS Selectors | 40% | Test cases for complex selectors |
| Image Layout | 46% | Test cases for object-fit, aspect-ratio |
| Sticky Positioning | 47% | Test cases for position:sticky |
| Flexbox | 55% | Test cases for edge cases |
| Form Controls | 48% | Cross-platform form rendering |

See [parity-tests/WANTED.md](./parity-tests/WANTED.md) for specific test cases we need.

## Repository Structure

```
community/
├── parity-tests/           # Rendering test contributions
│   ├── submissions/        # New PRs land here
│   ├── approved/           # Merged into test suite
│   └── templates/          # Submission templates
├── bug-reports/            # Bug tracking
│   ├── templates/          # Issue templates
│   └── triage/             # Triaged and categorized bugs
├── feature-requests/       # Feature ideas
├── feedback/               # General feedback
│   ├── ui-ux/              # UI/UX suggestions
│   ├── performance/        # Performance reports
│   └── compatibility/      # Site compatibility reports
├── docs/                   # Community documentation
│   ├── guides/             # How-to guides
│   └── faq/                # Frequently asked questions
└── localization/           # Translation contributions
    ├── translations/       # Language files
    └── glossary/           # Term consistency guide
```

## Recognition

Contributors are recognized in several ways:

- **Contributors Page** - Listed on our website
- **Release Notes** - Credited for specific fixes
- **Badges** - GitHub badges for different contribution types
- **Early Access** - Beta builds for active contributors

## Project Roadmap

Rendering is just the beginning. What comes next is up to you.

**[View the Full Roadmap](./PROJECT_ROADMAP.md)**

| Component | Status | What It Enables |
|-----------|--------|-----------------|
| Rendering Engine (RustKit) | **In Progress** | Display web pages correctly |
| JavaScript Engine | Community Vote | True independence from Google |
| Networking Stack | Community Vote | Privacy features, HTTP/3, QUIC |
| Developer Tools | Community Vote | Debug and inspect websites |
| Extension System | Community Vote | Use your favorite browser extensions |
| Security Sandbox | Community Vote | Site isolation, process separation |
| Media Stack | Community Vote | Full video/audio support |

**Phase 1 (Rendering) is the current focus.** After that, the community votes on what's next. This is your browser — you decide what matters.

Each of these has been called "impossible" to build independently. We're proving them wrong, one component at a time.

## Code of Conduct

We're committed to a welcoming community. Please read our [Code of Conduct](./CODE_OF_CONDUCT.md).

## License

Test cases and documentation in this repository are licensed under [MIT](./LICENSE).

---

Questions? Open a [Discussion](https://github.com/hiwavebrowser/community/discussions) or join our [Discord](https://discord.gg/hiwave).
