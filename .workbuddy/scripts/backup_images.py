#!/usr/bin/env python3
"""备份工程内全部 PNG/JPEG 原图到 WorkBuddyRaw/临时/图片压缩备份/2026-08-10/，保持相对目录结构。"""
import os
import shutil

ROOT = "/Users/wzb/Library/Mobile Documents/com~apple~CloudDocs/Documents/快手/icloud文稿/Knowledge_Ability/Result/Result_Resume_Wiki"
BACKUP_ROOT = os.path.join(ROOT, "WorkBuddyRaw", "临时", "图片压缩备份", "2026-08-10")
EXTS = (".png", ".jpg", ".jpeg")

os.makedirs(BACKUP_ROOT, exist_ok=True)

count = 0
total = 0
for dirpath, dirnames, filenames in os.walk(ROOT):
    # 跳过 .git 与 WorkBuddyRaw 自身
    if "/.git" in dirpath or "WorkBuddyRaw" in dirpath:
        continue
    for fn in filenames:
        if fn.lower().endswith(EXTS):
            src = os.path.join(dirpath, fn)
            rel = os.path.relpath(src, ROOT)
            dst = os.path.join(BACKUP_ROOT, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            count += 1
            total += os.path.getsize(src)

print(f"备份完成：{count} 张，共 {total/1048576:.1f} MB")
print(f"备份目录：{BACKUP_ROOT}")
