import sys
s = open(sys.argv[1] + '/suite.log').read()
for l in s.splitlines():
    if l.startswith('test result') or ' rc=' in l or l.endswith('FAILED') or l.startswith('error'):
        print(l)
