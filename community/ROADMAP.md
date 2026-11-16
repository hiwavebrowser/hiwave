# Community Program Roadmap

> **Status note, 2026-11-16.** This page was written in January 2026. Its parity percentages, phase labels and dates describe the project at that time and have not been re-measured. For current, sourced figures see [Recent progress](https://github.com/hiwavebrowser/hiwave/blob/master/docs/PROGRESS-2026-11.md).

This document outlines how we plan to grow and utilize the HiWave community over time.

## Current Phase: Foundation (Q1 2026)

### Goals
- [ ] Launch community repository
- [ ] Establish contribution workflows
- [ ] Recruit initial parity test contributors
- [ ] Set up CI validation for submissions

### Community Roles
- **Contributors**: Submit parity tests, bug reports, compatibility reports
- **Maintainers**: Review and merge submissions (HiWave team)

### Metrics
- 50+ parity test submissions
- 100+ compatibility reports
- 10+ active contributors

---

## Phase 2: Growth (Q2 2026)

### New Capabilities

#### Beta Testing Program
```
community/
└── beta-testing/
    ├── signup.md           # How to join
    ├── builds/             # Beta build announcements
    ├── feedback/           # Structured feedback forms
    └── known-issues.md     # Current beta issues
```

- **Structured beta releases** with feedback forms
- **Tiered access**: General beta → Dev beta → Nightly
- **Crash reporting** integration with community IDs

#### Website Compatibility Database
```
community/
└── compatibility-db/
    ├── sites/
    │   ├── google.com.json
    │   ├── github.com.json
    │   └── ...
    └── schema.json
```

- **Crowdsourced compatibility data** for top 10,000 sites
- **Automatic aggregation** of compatibility reports
- **Public compatibility dashboard**

#### Community Champions Program
- Recognize top contributors with special status
- Direct communication channel with dev team
- Early access to features and roadmap
- Swag and recognition

### Metrics
- 200+ parity tests
- 500+ compatibility reports
- 50+ beta testers
- 5+ community champions

---

## Phase 3: Expansion (Q3 2026)

### New Capabilities

#### Extension Compatibility Testing
```
community/
└── extensions/
    ├── tested/             # Extensions verified to work
    ├── issues/             # Extension-specific bugs
    └── requests/           # Extensions users want supported
```

- Community tests Chrome extensions for compatibility
- Prioritize extension API implementation based on demand
- Extension developer outreach

#### Performance Benchmarking
```
community/
└── benchmarks/
    ├── submissions/        # User-submitted benchmark results
    ├── configs/            # Standard benchmark configurations
    └── leaderboard.json    # Aggregated results
```

- Crowdsourced performance data across hardware
- Identify performance regressions from user reports
- Hardware-specific optimization priorities

#### Localization Program
```
community/
└── localization/
    ├── translations/
    │   ├── es.json         # Spanish
    │   ├── fr.json         # French
    │   ├── de.json         # German
    │   ├── ja.json         # Japanese
    │   ├── zh-CN.json      # Chinese (Simplified)
    │   └── ...
    ├── glossary/
    │   └── terms.json      # Consistent terminology
    └── review/             # Translation review queue
```

- Community-driven translations
- Native speaker review process
- Regional customization suggestions

### Metrics
- 500+ parity tests
- 1000+ sites in compatibility DB
- 20+ languages started
- 100+ beta testers

---

## Phase 4: Maturity (Q4 2026+)

### New Capabilities

#### Community Moderators
- Trusted community members help triage issues
- First-response for compatibility reports
- Mentor new contributors

#### Developer Ecosystem
```
community/
└── developers/
    ├── themes/             # Community themes
    ├── userscripts/        # UserScript sharing
    └── integrations/       # Third-party integrations
```

- Theme/customization sharing
- UserScript repository
- Integration guides (1Password, Raindrop, etc.)

#### Research Participation
- Opt-in usage analytics for research
- A/B test participation
- UX research studies

#### Bug Bounty Program
- Security vulnerability rewards
- Critical bug rewards
- Leaderboard and recognition

### Long-term Metrics
- 1000+ parity tests
- 95%+ parity achieved
- 50+ languages
- 500+ active community members
- Self-sustaining moderation

---

## Community Infrastructure

### Immediate (Phase 1)
- [x] GitHub repository
- [x] Issue templates
- [x] PR validation CI
- [ ] Discord server
- [ ] Contributor guidelines

### Short-term (Phase 2)
- [ ] Community dashboard (contributions, leaderboard)
- [ ] Automated test integration pipeline
- [ ] Beta distribution system
- [ ] Compatibility database API

### Medium-term (Phase 3-4)
- [ ] Translation management platform (Crowdin/Lokalise)
- [ ] Community forum (Discourse or GitHub Discussions)
- [ ] Contributor recognition system
- [ ] Bug bounty platform

---

## Contribution Value Matrix

How different contributions help HiWave:

| Contribution | Parity Impact | User Impact | Effort Required |
|--------------|---------------|-------------|-----------------|
| Parity Test (critical) | +++ | + | Medium |
| Parity Test (minor) | + | + | Low |
| Compatibility Report | ++ | ++ | Low |
| Beta Testing Feedback | + | +++ | Low |
| Bug Report (crash) | + | +++ | Low |
| Bug Report (visual) | ++ | + | Low |
| Translation | - | ++ | Medium |
| Documentation | - | ++ | Medium |
| Extension Testing | - | ++ | Low |
| Performance Benchmark | + | + | Low |

---

## How Contributions Flow

### Parity Tests
```
Contributor submits PR
        ↓
CI validates structure
        ↓
Maintainer reviews
        ↓
Merged to approved/
        ↓
Synced to main repo (submodule update)
        ↓
Integrated into CI test suite
        ↓
Parity regression detected? → Fix implemented → Contributor credited
```

### Compatibility Reports
```
User submits issue
        ↓
Auto-categorized by severity
        ↓
Triaged by site popularity
        ↓
Converted to parity test (if applicable)
        ↓
Fix implemented
        ↓
Reporter notified
```

### Beta Feedback
```
Beta tester encounters issue
        ↓
Submits structured feedback
        ↓
Correlated with crash reports
        ↓
Prioritized for fix
        ↓
Fixed in next beta
        ↓
Tester verifies
```

---

## Success Criteria

### Phase 1 Success
- [ ] 10+ external contributors
- [ ] Parity tests integrated into CI
- [ ] Response time <72h for all submissions

### Phase 2 Success
- [ ] 50+ active contributors
- [ ] Beta program with 100+ testers
- [ ] Community-sourced tests catch real regressions

### Phase 3 Success
- [ ] Self-sustaining contribution rate
- [ ] Community moderators handling triage
- [ ] Multiple languages in production

### Phase 4 Success
- [ ] Community is a competitive advantage
- [ ] Contributors become advocates
- [ ] Sustainable long-term program

---

## Resources Required

### Tooling
- GitHub Actions (CI/CD) - included
- Discord server - free tier
- Crowdin/Lokalise - ~$200/mo for translation
- Dashboard hosting - ~$50/mo

### Team Time
- **Phase 1**: 5-10 hrs/week maintainer time
- **Phase 2**: 10-15 hrs/week + community moderators
- **Phase 3+**: 5 hrs/week + community self-sustaining

---

## Open Questions

1. **Incentive structure**: Beyond recognition, should we offer monetary rewards for high-impact contributions?

2. **Governance**: As community grows, how do we handle disagreements about priorities?

3. **Quality vs quantity**: How do we maintain test quality as volume increases?

4. **Cross-platform**: How do we handle Windows-specific vs macOS-specific issues?

5. **Privacy**: What data do we collect from beta testers and how is it protected?

---

## Next Steps

1. [ ] Finalize and publish community repo
2. [ ] Write Discord server setup guide
3. [ ] Create initial "wanted" parity tests list
4. [ ] Recruit 5-10 seed contributors
5. [ ] Set up CI validation workflow
6. [ ] Announce community program
