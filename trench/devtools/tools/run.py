"""run.py <binary> <stderr file> <args...>: run a built binary, stderr to a file, stdout tail printed."""
import subprocess
import sys

binary, err = sys.argv[1], sys.argv[2]
with open(err, "w") as e:
    r = subprocess.run([binary] + sys.argv[3:], stdout=subprocess.PIPE, stderr=e, text=True, timeout=280)
print(r.stdout[-1500:])
print("exit", r.returncode)
