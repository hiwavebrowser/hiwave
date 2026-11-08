import sys, time, re
log, limit = sys.argv[1], float(sys.argv[2])
t0 = time.time()
while time.time() - t0 < limit:
    s = open(log, errors="replace").read()
    if "test result" in s:
        break
    time.sleep(20)
s = open(log, errors="replace").read()
done = len(re.findall(r"^test .* \.\.\. (ok|FAILED|ignored)$", s, re.M))
print("tests reported:", done)
for line in s.splitlines():
    if "test result" in line or line.endswith("FAILED"):
        print(line)
