"""split.py: fails.txt (FAILED names) and rest.txt (names with no result) from the cut suite log."""
import re

S = '/Users/petecopeland/Repos/.worktrees/.scratch-b18b/'
log = open(S + 'suite-18882673.log').read()
done = set(re.findall(r"^test (\S+) \.\.\. ", log, re.M))
fails = re.findall(r"^test (\S+) \.\.\. FAILED$", log, re.M)
names = [n for n in open(S + 'all.txt').read().split('\n') if n]
rest = [n for n in names if n not in done]
open(S + 'fails.txt', 'w').write('\n'.join(fails) + '\n')
open(S + 'rest.txt', 'w').write('\n'.join(rest) + '\n')
print('results', len(done), 'fails', len(fails), 'rest', len(rest))
