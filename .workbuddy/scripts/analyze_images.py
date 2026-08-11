#!/usr/bin/env python3
"""分析工程内所有位图图片的尺寸/模式/大小分布，辅助确定压缩参数。"""
import os
from collections import Counter
from PIL import Image

ROOT = "/Users/wzb/Library/Mobile Documents/com~apple~CloudDocs/Documents/快手/icloud文稿/Knowledge_Ability/Result/Result_Resume_Wiki"
EXTS = (".png", ".jpg", ".jpeg")

files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    if "/.git" in dirpath or ".workbuddy" in dirpath:
        continue
    for fn in filenames:
        if fn.lower().endswith(EXTS):
            files.append(os.path.join(dirpath, fn))

print(f"共 {len(files)} 张位图\n")

size_buckets = Counter()
mode_counter = Counter()
long_side_hist = Counter()
rows = []
for fp in files:
    try:
        with Image.open(fp) as im:
            w, h = im.size
            mode = im.mode
            size = os.path.getsize(fp)
        long_side = max(w, h)
        size_buckets[("MB>=8" if size >= 8*1048576 else
                      "4-8MB" if size >= 4*1048576 else
                      "2-4MB" if size >= 2*1048576 else
                      "1-2MB" if size >= 1048576 else
                      "500K-1M" if size >= 512*1024 else
                      "<500K")] += 1
        mode_counter[mode] += 1
        long_side_hist[(">=4096" if long_side >= 4096 else
                        "2048-4095" if long_side >= 2048 else
                        "1024-2047" if long_side >= 1024 else
                        "<1024")] += 1
        rows.append((size, long_side, mode, fp))
    except Exception as e:
        print(f"[跳过/损坏] {fp}: {e}")

print("=== 文件大小分布 ===")
order_b = [">=8MB", "4-8MB", "2-4MB", "1-2MB", "500K-1M", "<500K"]
for k in order_b:
    if k in size_buckets:
        print(f"  {k:10s}: {size_buckets[k]} 张")

print("\n=== 颜色模式分布 ===")
for k, v in mode_counter.most_common():
    print(f"  {k:8s}: {v} 张")

print("\n=== 最长边分布 ===")
order = ["<1024", "1024-2047", "2048-4095", ">=4096"]
for k in order:
    if k in long_side_hist:
        print(f"  {k:10s}: {long_side_hist[k]} 张")

print("\n=== 最大 15 张 ===")
for size, ls, mode, fp in sorted(rows, reverse=True)[:15]:
    rel = os.path.relpath(fp, ROOT)
    print(f"  {size/1048576:7.1f}MB  {ls:5d}px {mode:4s} {rel}")
