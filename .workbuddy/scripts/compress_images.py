#!/usr/bin/env python3
"""
压缩工程内全部 PNG/JPEG 图片：
- 最长边 > 3000px 的超大图等比缩放到 3000px（Lanczos），文章显示远小于此宽度，清晰度不受影响
- PNG: optimize 重存；RGBA 且 alpha 全不透明 → 转 RGB（更小）
- JPEG: quality=85, progressive, optimize
- 先写临时文件 → 重新打开校验 → os.replace 原子替换
用法: python compress_images.py [--limit N] [--dry-run]
"""
import os
import sys
import time
import json
from PIL import Image

ROOT = "/Users/wzb/Library/Mobile Documents/com~apple~CloudDocs/Documents/快手/icloud文稿/Knowledge_Ability/Result/Result_Resume_Wiki"
REPORT_DIR = os.path.join(ROOT, "WorkBuddyRaw", "临时")
MAX_SIDE = 3000
JPEG_QUALITY = 85
EXTS = (".png", ".jpg", ".jpeg")


def compress_one(src, limit=None):
    """返回 (new_size, info) 或 None（未变化/失败）。"""
    before = os.path.getsize(src)
    try:
        with Image.open(src) as im:
            orig_mode = im.mode
            w, h = im.size
            # 降采样
            long_side = max(w, h)
            scale = 1.0
            if long_side > MAX_SIDE:
                scale = MAX_SIDE / long_side
                new_w, new_h = max(1, round(w * scale)), max(1, round(h * scale))
                im = im.convert("RGBA") if im.mode in ("RGBA", "LA") else im.convert("RGB")
                im = im.resize((new_w, new_h), Image.LANCZOS)
                w, h = new_w, new_h

            out = src + ".wb_tmp"

            if src.lower().endswith(".png"):
                # RGBA 全不透明 → 转 RGB
                if im.mode == "RGBA":
                    extrema = im.getchannel("A").getextrema()
                    if extrema[0] == 255 and extrema[1] == 255:
                        im = im.convert("RGB")
                im.save(out, "PNG", optimize=True)
            else:
                if im.mode != "RGB":
                    im = im.convert("RGB")
                im.save(out, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)

            # 校验临时文件
            with Image.open(out) as check:
                check.load()
                if check.size != (w, h):
                    os.remove(out)
                    return None, {"error": f"尺寸校验失败 {check.size} != {(w, h)}"}
    except Exception as e:
        return None, {"error": str(e), "before": before, "mode": orig_mode}

    after = os.path.getsize(out)
    if after >= before:
        # 压缩后没有变小 → 保留原文件
        os.remove(out)
        return None, {"skipped": "not_smaller", "before": before, "mode": orig_mode,
                      "size": (w, h), "resized": scale < 1.0}

    os.replace(out, src)
    return after, {"before": before, "mode": orig_mode, "size": (w, h),
                   "resized": scale < 1.0, "orig_size": (long_side, h) if scale < 1.0 else None}


def main():
    limit = None
    dry_run = "--dry-run" in sys.argv
    for i, a in enumerate(sys.argv):
        if a == "--limit":
            limit = int(sys.argv[i + 1])

    files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if "/.git" in dirpath or "WorkBuddyRaw" in dirpath or ".workbuddy" in dirpath:
            continue
        for fn in filenames:
            if fn.lower().endswith(EXTS):
                files.append(os.path.join(dirpath, fn))

    if limit:
        # 优先处理最大的
        files.sort(key=lambda f: -os.path.getsize(f))
        files = files[:limit]

    results = []
    saved = 0
    for i, fp in enumerate(files, 1):
        rel = os.path.relpath(fp, ROOT)
        if dry_run:
            with Image.open(fp) as im:
                print(f"[{i}/{len(files)}] {rel}  {im.size[0]}x{im.size[1]} {im.mode} {os.path.getsize(fp)/1024:.0f}KB")
            continue
        after, info = compress_one(fp)
        if after is None:
            if info and "skipped" in info:
                print(f"[{i}/{len(files)}] 跳过(未变小) {rel} ({info['before']/1048576:.2f}MB)")
            elif info and "error" in info:
                print(f"[{i}/{len(files)}] 失败 {rel}: {info['error']}")
            continue
        saved += info["before"] - after
        tag = "缩放+压缩" if info["resized"] else "压缩"
        print(f"[{i}/{len(files)}] {tag} {rel}: {info['before']/1048576:.2f}MB -> {after/1048576:.2f}MB "
              f"({(1-after/info['before'])*100:.0f}%↓) {info['size'][0]}x{info['size'][1]}")
        results.append({"file": rel, "before": info["before"], "after": after,
                        "resized": info["resized"]})

    if dry_run:
        return

    total_before = sum(r["before"] for r in results)
    total_after = sum(r["after"] for r in results)
    print(f"\n===== 汇总: 成功压缩 {len(results)} 张, "
          f"共节省 {saved/1048576:.1f} MB "
          f"({total_before/1048576:.1f}MB -> {total_after/1048576:.1f}MB, "
          f"{(1-total_after/total_before)*100:.0f}%↓) =====")

    os.makedirs(REPORT_DIR, exist_ok=True)
    report = os.path.join(REPORT_DIR, "图片压缩报告.json")
    with open(report, "w", encoding="utf-8") as f:
        json.dump({"time": time.strftime("%Y-%m-%d %H:%M:%S"), "max_side": MAX_SIDE,
                   "jpeg_quality": JPEG_QUALITY, "results": results}, f, ensure_ascii=False, indent=2)
    print(f"报告已保存: {report}")


if __name__ == "__main__":
    main()
