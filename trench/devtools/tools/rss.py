"""rss.py <binary> <html file> <runs>: max RSS (MB) of parity-capture on a fixture, with and without --shield, one child per run."""
import resource
import subprocess
import sys

binary, page, runs = sys.argv[1], sys.argv[2], int(sys.argv[3])
code = (
    "import resource,subprocess,sys;"
    "subprocess.run(sys.argv[1:],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=120);"
    "print(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)"
)
for label, extra in (("off", []), ("shield", ["--shield"])):
    vals = []
    for _ in range(runs):
        out = subprocess.run(["python3", "-c", code, binary, "--html-file", page] + extra, capture_output=True, text=True)
        vals.append(int(out.stdout.strip()) / (1024 * 1024))  # macOS ru_maxrss is bytes
    print(label, " ".join("%.1f" % v for v in vals), "MB")
