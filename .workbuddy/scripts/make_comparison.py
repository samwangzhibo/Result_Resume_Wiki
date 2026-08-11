#!/usr/bin/env python3
"""生成压缩前后对比图（原图来自备份目录），用于人工检查清晰度。"""
import os
from PIL import Image, ImageDraw

ROOT = "/Users/wzb/Library/Mobile Documents/com~apple~CloudDocs/Documents/快手/icloud文稿/Knowledge_Ability/Result/Result_Resume_Wiki"
BACKUP = os.path.join(ROOT, "WorkBuddyRaw", "临时", "图片压缩备份", "2026-08-10")
OUT = os.path.join(ROOT, "WorkBuddyRaw", "临时", "压缩效果对比")

SAMPLES = [
    "连屏/连屏技术领域洞察/assets/out-20260605163010121.png",  # 6512px 超宽大图
    "连屏/领域建模/assets/out-20260605161409089.png",           # 1534px 未缩放
    "连屏/连屏技术领域洞察/assets/out-20260605163003608.png",   # 竖图 1080x2336
]

os.makedirs(OUT, exist_ok=True)
DISPLAY_W = 480

for rel in SAMPLES:
    orig = os.path.join(BACKUP, rel)
    new = os.path.join(ROOT, rel)
    if not (os.path.exists(orig) and os.path.exists(new)):
        print(f"缺少文件: {rel}")
        continue
    a = Image.open(orig)
    b = Image.open(new)
    a.thumbnail((DISPLAY_W, DISPLAY_W * 4), Image.LANCZOS)
    b.thumbnail((DISPLAY_W, DISPLAY_W * 4), Image.LANCZOS)
    if a.mode != "RGB":
        a = a.convert("RGB")
    if b.mode != "RGB":
        b = b.convert("RGB")
    h = max(a.size[1], b.size[1])
    canvas = Image.new("RGB", (DISPLAY_W * 2 + 20, h + 30), "white")
    canvas.paste(a, (0, 30))
    canvas.paste(b, (DISPLAY_W + 20, 30))
    d = ImageDraw.Draw(canvas)
    d.text((10, 8), "原图", fill="black")
    d.text((DISPLAY_W + 30, 8), "压缩后", fill="black")
    d.text((10, h - 14), f"{os.path.getsize(orig)/1048576:.2f}MB", fill="red")
    d.text((DISPLAY_W + 30, h - 14), f"{os.path.getsize(new)/1048576:.2f}MB", fill="red")
    name = rel.replace("/", "_").replace(".png", "")
    canvas.save(os.path.join(OUT, f"对比_{name}.png"))
    print(f"已生成对比图: {name}")

# 额外做一张局部放大对比（检查文字清晰度）
rel = "连屏/连屏技术领域洞察/assets/out-20260605163010121.png"
orig = os.path.join(BACKUP, rel)
new = os.path.join(ROOT, rel)
a = Image.open(orig).convert("RGB")
b = Image.open(new).convert("RGB")
# 取左上角 400x300 区域放大 2 倍看细节
a_crop = a.crop((0, 0, 400, 300)).resize((800, 600), Image.NEAREST)
b_crop = b.crop((0, 0, 400, 300)).resize((800, 600), Image.NEAREST)
canvas = Image.new("RGB", (1620, 600), "white")
canvas.paste(a_crop, (0, 0))
canvas.paste(b_crop, (820, 0))
d = ImageDraw.Draw(canvas)
d.text((10, 5), "原图局部放大2x", fill="red")
d.text((830, 5), "压缩后局部放大2x", fill="red")
canvas.save(os.path.join(OUT, "细节放大对比.png"))
print("已生成细节放大对比图")
