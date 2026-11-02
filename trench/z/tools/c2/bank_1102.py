#!/usr/bin/env python3
"""bank_1102.py: copy this slot's small text receipts to the hub."""
import shutil

W = "/Users/petecopeland/Repos/.worktrees/"
R = W + "z-hub/trench/z/receipts/2026-11-02-"
for src, dst in [
    ("z-c2-ab851/scratch/ab-c2final.txt", "851-ab-2efc47f6.txt"),
    ("z-c2-ab851/scratch/ab-c2goog.txt", "851-ab-google-1.txt"),
    ("z-c2-ab851/scratch/ab-c2goog2.txt", "851-ab-google-2.txt"),
    ("z-c2-ab851/scratch/ab-c2ggAA.txt", "851-ab-google-base-vs-base-1.txt"),
    ("z-c2-ab851/scratch/ab-c2ggAA2.txt", "851-ab-google-base-vs-base-2.txt"),
    ("z-c2-ab851/scratch/ab-c2cnn.txt", "851-ab-cnn-90s.txt"),
    ("851-body.md", "851-body-2efc47f6.md"),
    ("851-comment.md", "851-comment-2efc47f6.md"),
    ("opacity-pr-body.md", "861-body.md"),
    ("depth-pr-body.md", "862-body.md"),
    ("float-pr-body.md", "863-body.md"),
]:
    shutil.copy2(W + src, R + dst)
    print(dst)
