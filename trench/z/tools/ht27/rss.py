"""rss.py <binary> <url> : one capture; prints wall secs, child max RSS (MB) and the page title from --dump-scripts-free report."""
import resource, subprocess, sys, time

binary, url = sys.argv[1], sys.argv[2]
t = time.time()
r = subprocess.run([binary, '--url', url, '--width', '1280', '--height', '800', '--timeout-ms', '120000',
                    '--event-log', '/tmp/rss-ev.jsonl', '--event-log-console-text'], capture_output=True, text=True)
secs = time.time() - t
rss = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / (1024 * 1024)
print('exit %d secs %.1f maxrss %.0f MB' % (r.returncode, secs, rss))
import re
print([l[-160:] for l in open('/tmp/rss-ev.jsonl') if 'adopt=' in l][:2])
