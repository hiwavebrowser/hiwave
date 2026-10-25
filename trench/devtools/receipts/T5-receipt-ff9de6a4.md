## Receipt (`scripts/receipt.py`)

```json
{
 "base_sha": "7a908255",
 "binary": null,
 "binary_mtime_utc": null,
 "binary_sha256": null,
 "branch": "dt-t5-1840",
 "campaign": null,
 "candidate_sha": "ff9de6a46ed2db405fdf28b1f643f3a64e328ad0",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "cargo_lock_sha256": "d43bf3f40c046d3d625a2876c81a524fcaac59b37460f330942147537a4c8cb7",
 "chrome_version": null,
 "cpu": "arm",
 "dirty_state": false,
 "effective_engine_flags": {},
 "features": "headless",
 "host": null,
 "note": "test-only diff + develop merge; engine headless lib suite x3, 1068 passed 0 failed each, load 11-13 (peak 20.5)",
 "os": "macOS-26.5.2-arm64-arm-64bit",
 "profile": null,
 "raw_runs": [
  {
   "bytes": 177731,
   "file": "scratch/suite-ff9de6a4-1.log",
   "sha256": "f9a7fbffbc7a9de49e98d42cec5ffabb016f684fd61f20567d86e8fbc613f178"
  },
  {
   "bytes": 178187,
   "file": "scratch/suite-ff9de6a4-2.log",
   "sha256": "663a5d4e115eed70b915e2af31e5977713296e112f524dfbf27e9b57bd89c446"
  },
  {
   "bytes": 178366,
   "file": "scratch/suite-ff9de6a4-3.log",
   "sha256": "4123da664716946d416c116c607d36f88eda49fd9333cc28ffe50dbbdf94def0"
  }
 ],
 "repo": "https://github.com/hiwavebrowser/hiwave-macos.git",
 "rustflags": null,
 "sccache": true,
 "target": "aarch64-apple-darwin",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "utc": "2026-10-25T00:07:51.852183Z",
 "work_package": "T5"
}
```

Summary (`suite3.py` .done):
```
run 1: rc=0 1746s load1 min/median/max 11.5/12.2/14.4 test result: ok. 1068 passed; 0 failed; 6 ignored; finished in 1745.66s
run 2: rc=0 1772s load1 min/median/max 11.2/12.2/14.8 test result: ok. 1068 passed; 0 failed; 6 ignored; finished in 1771.57s
run 3: rc=0 1794s load1 min/median/max 11.3/12.4/20.5 test result: ok. 1068 passed; 0 failed; 6 ignored; finished in 1792.96s
```
