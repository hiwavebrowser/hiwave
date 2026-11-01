#!/usr/bin/env python3
"""keep851.py: #851's shopify frames beside the other dated frame folders, kept at this seat and not committed."""
import os
import shutil

W = "/Users/petecopeland/Repos/.worktrees/"
d = W + "renders-private/2026-11-01-851-shopify"
os.makedirs(d, exist_ok=True)
for n in ("shopify-base.png", "shopify-cand.png"):
    shutil.copyfile(W + "z-c2d-g/scratch/" + n, d + "/" + n)
print(sorted(os.listdir(d)))
