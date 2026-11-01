#!/usr/bin/env python3
"""conflicts.py <file>: print each merge conflict with its line numbers."""
import sys

on = False
for i, line in enumerate(open(sys.argv[1], errors="replace"), 1):
    if line.startswith("<<<<<<<"):
        on = True
    if on:
        print(i, line, end="")
    if line.startswith(">>>>>>>"):
        on = False
        print("-----")
