# .workbuddy/scripts 工具集

## 图片批量无损/近无损压缩工作流

适用于 markdown 文章工程中大量位图（PNG/JPEG）的体积优化，**保证视觉清晰度不变**。

### 核心原则
1. **保持格式**：截图/图表/架构图是 PNG，重压缩保持 PNG，不转 JPEG（避免文字糊）
2. **降采样 > 有损压缩**：超大图（>3000px）缩到 3000px 比 PNG 量化更安全
3. **无损优化优先**：PNG optimize=True；RGBA 全不透明 → 转 RGB
4. **原子替换**：临时文件 → 校验 → os.replace
5. **可恢复**：先备份到 WorkBuddyRaw/临时/

### 工具脚本

| 脚本 | 作用 |
|------|------|
| `analyze_images.py` | 扫描全部位图尺寸/模式/大小分布，辅助定参数 |
| `backup_images.py` | 把原图复制到 `WorkBuddyRaw/临时/图片压缩备份/<日期>/`，保持相对目录 |
| `compress_images.py` | 主压缩脚本，支持 `--limit N` 先小批量测试 / `--dry-run` 仅分析 |
| `make_comparison.py` | 生成原图 vs 压缩后对比图，用于人工校验清晰度 |

### 关键参数

```python
MAX_SIDE = 3000          # 最长边 > 此值才缩放（Lanczos）
JPEG_QUALITY = 85        # 保留文字清晰度
PNG optimize=True        # 无损重存
RGBA 转 RGB 条件：alpha 全不透明（getextrema() == (255, 255)）
```

### 使用步骤

```bash
# 1. 分析尺寸分布
python analyze_images.py

# 2. 备份原图
python backup_images.py

# 3. 先试压缩几张验证
python compress_images.py --limit 8

# 4. 生成对比图人工校验清晰度
python make_comparison.py

# 5. 全量压缩
python compress_images.py
```

### 实际效果参考（2026-08-10 Result_Resume_Wiki）

- 120 张位图（107.45 MB）
- 压缩后 69.03 MB，**节省 38.42 MB（35.7%）**
- 最大单张：11MB → 2.83MB
- 全部 120 张通过 PIL verify + load 校验
- 文字/图标/流程图视觉无损

### 注意事项

- **不要删除备份**直到确认所有 md 文章渲染正常
- PIL 装不上时用清华镜像源：`-i https://pypi.tuna.tsinghua.edu.cn/simple`
- managed venv 路径：`/Users/wzb/.workbuddy/binaries/python/envs/default/bin/python`
- .gitignore 必须排除 `WorkBuddyRaw/`，防止备份污染 git（git submodule 仓库特别重要）
- 截图型 PNG 不要尝试 PNG 量化（PIL `convert('P', palette=...)`），文字边缘会产生色带