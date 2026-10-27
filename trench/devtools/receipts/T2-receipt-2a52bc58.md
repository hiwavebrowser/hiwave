## Receipt (`scripts/receipt.py`) — T2 #792 independent HOLD fix

```json
{
 "base_sha": "e587d94a",
 "binary": "target/parity/parity-capture",
 "binary_sha256": "50a927e75c0e2a924a39b62668edfbf9be5581f5285063143c021e16d128d3d0",
 "campaign": {"cases": 26, "failed": 0, "passed": 26, "mean_diff_pct": 1.1078,
  "file": "scratch/camp-t2hold-2a52bc58.json",
  "sha256": "e0be064f7872fb9e96fbe5954dfe6a9ad11c3db7f856441be6133d6941959cf6"},
 "candidate_sha": "2a52bc5872444f16c766a5329867625fa821a6a5",
 "cargo_lock_sha256": "45b66585b4e1b9edd2288f242beb611d830a021f02fb81a571f534cfbe131294",
 "dirty_state": false,
 "features": "headless",
 "profile": "parity",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "utc": "2026-10-27T06:06:47.043555Z",
 "work_package": "T2"
}
```

RSS (rule_names_rss plain, max RSS, dev profile, alternating): before 112.0 / 109.9 / 109.9 MB (mean 110.6), after 89.0 / 88.3 / 90.9 MB (mean 89.4). −21.2 MB per engine.
