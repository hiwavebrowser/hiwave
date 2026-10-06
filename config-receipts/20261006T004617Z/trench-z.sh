#!/bin/bash
# trench-z.sh — the Z-phase macOS engine lane (launchd, hourly at :05, own lock).
# ONE lane for the whole machine (Pete, 2026-10-02): the real-site and cascade
# lanes are ended. Work comes ONLY from trench/z/PLAN-z.md on hub atlas/z of
# the umbrella repo; the session takes the first `open` package in priority
# order D0 -> D1 -> B0 and nothing else. Builds go through z-cargo.py (machine
# lease + sccache). Digest: trench/z/digest-z.md on the hub. Cap 2h.
set -u
# Stand-down window (Pete): skip this fire while ~/.claude/standdown is in force.
if /Users/petecopeland/.claude/bin/standdown-check.sh; then echo "[$(basename "$0") $(date '+%Y-%m-%d %H:%M:%S')] stand-down window — skipping this fire" >> /Users/petecopeland/.claude/logs/standdown.log; exit 0; fi
PATH="/Users/petecopeland/.local/bin:/Users/petecopeland/.cargo/bin:/Users/petecopeland/anaconda3/bin:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"
HUBWT="/Users/petecopeland/Repos/.worktrees/z-hub"     # umbrella hiwave, branch atlas/z
HUB="atlas/z"
LOCK_DIR="/Users/petecopeland/.claude/trench-z.lock"
LOG="/Users/petecopeland/.claude/logs/trench-z.log"
CLOG="/Users/petecopeland/.claude/logs/trench-z-claude.log"
log() { echo "[trench-z $(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG"; }
if [ -d /Users/petecopeland/.claude/board-quiet.lock ]; then log "quiet board window — skipping this fire"; exit 0; fi
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  if [ -n "$(find "$LOCK_DIR" -maxdepth 0 -mmin +180 2>/dev/null)" ]; then
    rmdir "$LOCK_DIR" 2>/dev/null; mkdir "$LOCK_DIR" 2>/dev/null || exit 0
  else
    log "a Z session holds the lock, skipping this fire"; exit 0
  fi
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null' EXIT

log "starting session"
cd "$HUBWT" || { log "hub worktree missing: $HUBWT"; exit 1; }
git fetch -q origin 2>/dev/null
git checkout -q "$HUB" 2>/dev/null && git pull -q --ff-only origin "$HUB" 2>/dev/null

PLAN=$(git show "origin/$HUB:trench/z/PLAN-z.md" 2>/dev/null)
END_DATE=$(printf '%s\n' "$PLAN" | sed -nE 's/^end_date:[[:space:]]*//p' | head -1)
if [ -n "$END_DATE" ] && [[ "$(date +%F)" > "$END_DATE" ]]; then
  log "REFUSING: end_date $END_DATE passed — Pete renews or the lane is done"; exit 0
fi
# Nothing open for the lane? Then nothing to do.
if ! printf '%s\n' "$PLAN" | grep -E '^\| (I0|D0|D1|B0) \|' | grep -qE '\| (open|in-progress) \|'; then
  log "no open lane package in PLAN-z.md; skipping"; exit 0
fi

TANK_BIN="/Users/petecopeland/anaconda3/bin/tank"
if [ -x "$TANK_BIN" ]; then
  "$TANK_BIN" go trench-z --model opus >> "$LOG" 2>&1
  if [ $? -eq 2 ]; then log "tank gate: WAIT — skipping this fire"; exit 0; fi
  "$TANK_BIN" mark trench-z --project hiwave >> "$LOG" 2>&1
fi

ATTEMPT=0
while : ; do
  ATTEMPT=$((ATTEMPT+1))
  caffeinate -is claude -p "HiWave Z-PHASE engine session (macOS seat, the ONLY macOS lane, hourly, cap 2h). Hub: $HUBWT on branch $HUB (umbrella repo). FIRST read trench/z/PLAN-z.md there and follow it exactly: RECEIPTS ARE PROMETHEUS'S AGAIN (he re-accepted the receipt step 2026-10-05 17:01 ET): do NOT run the macOS receipt step yourself unless a seat or cloud PR has had R1 CLEAR and no receipt at its head for more than 3 hours. FIRST read the 'PETE'S HAND TEST' note under Rules in PLAN-z.md and obey its CONSEQUENCE line before anything else (build Z2-I2, the real-window driver, and use it to reproduce H1-H4 on the real app, launched from your own worktree build and never from another seat's clone); otherwise take the first package whose owner is 'Z lane' and whose state is open or in-progress, in priority order I0 -> D0 -> D1 -> B0; if none of those is open, take the first 'Z lane' item from the 'Next-phase queue' table (Z2-D2, Z2-D3, Z2-D4, Z2-B1, in that order) and add it to the packages table as in-progress; do nothing from any other source. Set that package's state to in-progress in PLAN-z.md (commit+push the hub) before you start, and back to open (or blocked with a one-line decision packet) when you stop. Engine code lives in hiwave-macos: make ONE warm worktree per package under /Users/petecopeland/Repos/.worktrees/z-<package> from origin/develop (reuse it if it exists; never touch ~/Repos/hiwave-macos), branch atlas/z-<slug>, PRs to develop. BUILDS: every cargo command through 'python3 /Users/petecopeland/Repos/.worktrees/z-cargo.py <worktree> <cargo args>' (machine lease + sccache); never bare cargo. '--profile parity' for anything measured in pixels (binary at z-target/parity/parity-capture), '--release' only for timing. USE ALEPH BEFORE GREP/READ; if an Aleph call hangs past ~2 minutes, stop using it this session. CLOSURE GATES for I0, D0-SVG, D1-L0 and B0 (PLAN-z.md 'Closure gates'): a reduced failing test committed before the fix; the receipt.py output (or, until it exists, the same fields written by hand: base/candidate SHA, binary sha256, toolchain, profile, host, Chrome version, fixture hashes, raw runs) in the PR body; the 26-case campaign at the candidate SHA; an all-site A/B for anything touching paint, fetch or scripts. Prometheus R1 + Cursor R2 review; NEVER merge your own PR; small test-passing commits; NEVER force-push. STOP RULE: if this is the second consecutive session on the same package with no landed receipt, set it blocked with a one-line decision packet and move to the next. HEADLESS: cargo in the FOREGROUND; never end a turn waiting on a background task. Before stopping (cap 2h): append '## <date> <HH:MM> Z-lane <package>' to trench/z/digest-z.md on the hub (before -> after, PRs with SHAs, blockers), update PLAN-z.md state, commit, push the hub. Do not ping anyone." \
    --permission-mode acceptEdits \
    --add-dir /Users/petecopeland/Repos/.worktrees \
    --allowedTools "Bash(python3 /Users/petecopeland/Repos/.worktrees/z-cargo.py:*)" "Bash(python3:*)" "Bash(git fetch:*)" "Bash(git branch:*)" "Bash(git worktree:*)" "Bash(git checkout:*)" "Bash(git switch:*)" "Bash(git restore:*)" "Bash(git rebase:*)" "Bash(git cherry-pick:*)" "Bash(git log:*)" "Bash(git diff:*)" "Bash(git show:*)" "Bash(git status:*)" "Bash(git merge:*)" "Bash(git merge-tree:*)" "Bash(gh pr create:*)" "Bash(gh pr view:*)" "Bash(gh pr list:*)" "Bash(gh pr edit:*)" "Bash(gh pr checks:*)" "Bash(node:*)" "Bash(npm ci:*)" "Bash(cp:*)" "Bash(mkdir:*)" "Bash(env:*)" "Bash(shasum:*)" "Bash(cargo fmt:*)" "Bash(rustfmt:*)" "Bash(sample:*)" "Bash(bash trench/tools/:*)" "Bash(./trench/tools/:*)" \
    --disallowedTools "Bash(gh pr merge:*)" "Bash(git push --force:*)" "Bash(git push -f:*)" \
    >> "$CLOG" 2>&1 &
  CLAUDE_PID=$!
  ( sleep 7500; kill "$CLAUDE_PID" 2>/dev/null; sleep 15; kill -9 "$CLAUDE_PID" 2>/dev/null ) 2>/dev/null &
  WATCHDOG_PID=$!
  disown "$WATCHDOG_PID" 2>/dev/null
  wait "$CLAUDE_PID"; status=$?
  pkill -P "$WATCHDOG_PID" 2>/dev/null; kill "$WATCHDOG_PID" 2>/dev/null
  log "session exit=$status (attempt $ATTEMPT)"
  [ "$status" -ge 128 ] && log "session KILLED by watchdog"
  [ "$status" -eq 0 ] && break
  if tail -5 "$CLOG" | grep -qiE "connection closed|api error|overloaded" && [ "$ATTEMPT" -lt 3 ]; then
    log "transient API error — retrying in 2 min"; sleep 120; continue
  fi
  break
done
exit 0
