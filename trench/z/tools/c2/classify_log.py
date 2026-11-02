#!/usr/bin/env python3
"""classify_log.py <test log>: each failed test by cause: guard (GPU guard), tls (root store), or assert (first line). A count alone can hide the environment."""
import re
import sys

text = open(sys.argv[1], errors="replace").read()
causes = {"guard": [], "tls": [], "assert": []}
for block in re.split(r"(?m)^---- ", text)[1:]:
    name = block.split(" stdout")[0].split("::")[-1]
    if "to finish with the GPU" in block:
        causes["guard"].append(name)
    elif "no usable platform root" in block:
        causes["tls"].append(name)
    else:
        lines = [l for l in block.splitlines()[2:8] if l.strip()]
        causes["assert"].append(name + " | " + " / ".join(l[:170] for l in lines[1:3]))
for cause, names in causes.items():
    print(cause, len(names))
for line in causes["assert"]:
    print("  " + line)
for line in text.splitlines():
    if line.startswith("test result"):
        print(line)
