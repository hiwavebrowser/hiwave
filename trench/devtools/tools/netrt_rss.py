"""netrt_rss.py <binary> <runs> <url> [url ...]: max RSS (MB), peak thread
count and wall clock of parity-capture per URL, HIWAVE_NET_RUNTIME=0 vs on,
arms interleaved. Each run is measured by a fresh python (`--one`), so
ru_maxrss of its children is that run's alone. Threads: `ps -M` every 100 ms."""
import os
import resource
import subprocess
import sys
import time


def one(binary, url, arm):
    env = dict(os.environ)
    env.pop("HIWAVE_NET_RUNTIME", None)
    if arm == "off":
        env["HIWAVE_NET_RUNTIME"] = "0"
    t = time.time()
    p = subprocess.Popen([binary, "--url", url, "--width", "1280", "--height", "800", "--timeout-ms", "30000",
                          "--dump-frame", os.devnull], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
    peak = 0
    while p.poll() is None:
        out = subprocess.run(["ps", "-M", "-p", str(p.pid)], capture_output=True, text=True).stdout
        peak = max(peak, len(out.strip().splitlines()) - 1)
        time.sleep(0.1)
    secs = time.time() - t
    rss = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / (1024 * 1024)  # bytes on macOS
    print("%.1f %d %.1f %d" % (rss, peak, secs, p.returncode))


if sys.argv[1] == "--one":
    one(*sys.argv[2:5])
    sys.exit(0)

binary, runs, urls = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
for url in urls:
    for arm in ["off", "on"] * runs:
        out = subprocess.run([sys.executable, "-I", os.path.abspath(__file__), "--one", binary, url, arm],
                             capture_output=True, text=True).stdout.split()
        print("%-26s %-3s maxrss %s MB  peak threads %s  %s s  exit %s" % (url, arm, *out), flush=True)
