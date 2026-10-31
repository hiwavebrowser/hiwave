#!/usr/bin/env python3
"""logfind.py <log> <text> [after=12]: print each line holding text and the lines after it."""
import sys
lines = open(sys.argv[1], errors='replace').read().splitlines()
after = int(sys.argv[3]) if len(sys.argv) > 3 else 12
for i, l in enumerate(lines):
    if sys.argv[2] in l:
        print('\n'.join(x[:200] for x in lines[i:i + after + 1]))
        print('--')
