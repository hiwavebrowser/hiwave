"""One-off: append the 21:05 FL digest and set FL back to open (2026-10-27)."""
import pathlib

hub = pathlib.Path('/Users/petecopeland/Repos/.worktrees/z-hub/trench/z')
app = hub / 'digest-z-append.md'
a = app.read_text().replace(
    'Full suite at ce830b72: SUITE_RESULT.',
    'Full suite at ce830b72: **1146/0**. Pushed (fast-forward) ce830b72; comment 6458975260 has the profile. No R1 ask yet, because the cost gate fails.')
with open(hub / 'digest-z.md', 'a') as f:
    f.write(a)
app.unlink()

p = hub / 'PLAN-z.md'
s = p.read_text().split('\n')
i = [k for k, l in enumerate(s) if l.startswith('| FL ')][0]
c = s[i].split('|')
assert c[6].strip() == 'in-progress', c[6]
c[6] = ' open '
old = ' 21:05 (10-27): interleaved paired --release timing for #812 (19:00 note) in progress.'
assert c[7].startswith(old)
new = (' 22:30 (10-27): **#812 LANDED e1093aad**. Paired --release: yahoo 0.936, reddit 0.972 (interstitial only), cnn 0.985. '
       '**#786 @ `ce830b72`**: develop e1093aad merged; `6d6ae019` fixes the #782 early display arm that shadowed #786\'s parse; '
       'guard test red-first; engine 1146/0. cnn #812+#786 is 22.55 s vs develop 18.27 s (1.234, FAILS <= 1.10). '
       'It does 72 forced layouts vs 45 with #812 alone (full rebuild ~177 ms each, cascade+box ~83 ms). '
       'Next: log the mutation that dirtied each forced layout; skip writes no rule reads, else an incremental forced build. '
       'Receipts `2026-10-27-fl-812-*`, `-786-*`.')
c[7] = new + c[7][len(old):]
s[i] = '|'.join(c)
p.write_text('\n'.join(s))
print('ok')
