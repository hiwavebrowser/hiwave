import sys, urllib.request
url, line, col = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15 HiWave/1.0"
body = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30).read().decode("utf-8", "replace")
lines = body.split("\n")
print("bytes", len(body), "lines", len(lines))
text = lines[line - 1]
for c in (col - 1, col):
    print("col", c, repr(text[max(0, c - 160):c]), "<<HERE>>", repr(text[c:c + 120]))
