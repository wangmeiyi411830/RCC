# AI 项目交接文档 · 招商电子图册

> 读完此文件即可完整接手该项目，无需追问背景。

---

## 一、项目本质

用户是某写字楼招商负责人，需要一个**在线楼层平面图+单元实景图展示系统**，供招商销售同事通过微信链接直接打开查看待租单元。

**线上地址（唯一正式链接）**：https://wangmeiyi411830.github.io/RCC/

---

## 二、完整路径地图

```
GitHub 本地仓库（唯一工作目录）：
C:\Users\31718\Desktop\RCC\
├── build_vis_github.py     ← 核心构建脚本（每次更新必须运行这个）
├── 待租单元.xlsx           ← 单元数据源（面积、单价、备注等）
├── floor_images\           ← 楼层平面图（floor_4.jpg ~ floor_22.jpg）
├── unit_images\            ← 单元图片（504-1.png, 504-2.jpg ...）
├── index.html              ← 由脚本自动生成，不要手动编辑
└── AI_HANDOFF.md           ← 本文件
```

**注意：** 桌面上原来的 `待租单元可视化\` 文件夹已合并到 `RCC\`，**今后所有操作只在 `RCC\` 里进行**。脚本使用相对路径，直接在 `RCC\` 目录下运行即可，无需手动同步图片到其他目录。

---

## 三、标准更新流程（每次新增/修改图片）

### Step 1：压缩图片（手机原图必做）
```powershell
python -c "
from PIL import Image
from pathlib import Path
img_dir = Path(r'C:\Users\31718\Desktop\RCC\unit_images')
for f in img_dir.glob('*.jpg'):
    size = f.stat().st_size
    if size > 300 * 1024:
        before = size // 1024
        img = Image.open(f)
        w, h = img.size
        if max(w, h) > 1600:
            ratio = 1600 / max(w, h)
            img = img.resize((int(w*ratio), int(h*ratio)), Image.LANCZOS)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        img.save(f, 'JPEG', quality=72, optimize=True)
        after = f.stat().st_size // 1024
        print(f.name + ': ' + str(before) + 'KB -> ' + str(after) + 'KB')
print('完成')
"
```

### Step 2：重新生成 index.html
```powershell
cd "C:\Users\31718\Desktop\RCC"
python build_vis_github.py
```

### Step 3：推送（用户自己操作）
用户打开 **GitHub Desktop** → 填写 Summary → **Commit to main** → **Push origin** → 等1-2分钟生效。

---

## 四、图片命名规则

| 类型 | 规则 | 示例 |
|------|------|------|
| 单元图片 | `{单元号}-{序号}.jpg` 或 `.png` | `504-1.png`、`1207-3.jpg` |
| 楼层平面图 | `floor_{楼层}.jpg` | `floor_4.jpg`、`floor_13A.jpg` |

- 序号从 1 开始，不能跳号
- 脚本按数字顺序排序（sort_key函数），不是字母顺序
- 支持 `.jpg`、`.jpeg`、`.png`、`.jfif`

---

## 五、当前图片清单（截至 2026-03-26）

### 单元图片 unit_images/
```
504-1.png, 504-2.jpg, 504-3.jpg
510-1.png, 510-2.jpg, 510-3.jpg
602-1.png
615-1.png
806-1.png, 806-2.jpg
807-1-1.png
1003-1.png
1006-1.png, 1006-2.jpg, 1006-3.jpg, 1006-4.jpg, 1006-5.jpg
1010-1.png, 1010-2.jpg, 1010-3.jpg, 1010-4.jpg
1207-1.png, 1207-2.jpg, 1207-3.jpg, 1207-4.jpg
1212-1.png, 1212-2.jpg, 1212-3.jpg
1213-1.png, 1213-2.jpg, 1213-3.jpg, 1213-4.jpg
13A02-1.png, 13A02-2.jpg, 13A02-3.jfif
13A15-1.png
1605+1606-1.png
1609-2-1.png
1702-1.png
1802-1.png
1809-1.png
1810-1.png, 1810-2.jpg, 1810-3.jpg
1815-1.png
1902-1.png
1904-1.png, 1904-2.jpg, 1904-3.jpg
1907-1.png
1916-1.png, 1916-2.jpg, 1916-3.jpg
2002-1.png
2007-1.png, 2007-2.jpg, 2007-3.jpg, 2007-4.jpg
2008-1.png, 2008-2.jpg, 2008-3.jpg
2009-1.png, 2009-2.jpg, 2009-3.jpg, 2009-4.jpg
2012-1.png
2013-1.png, 2013-2.jpg, 2013-3.jpg
2015-1.png
```

### 楼层平面图 floor_images/
```
floor_4.jpg ~ floor_22.jpg（共16层：4,5,6,7,8,9,10,12,13A,15,16,17,18,19,20,22）
```

---

## 六、技术架构

- **托管**：GitHub Pages（https://wangmeiyi411830.github.io/RCC/），微信内可直接打开，无需VPN
- **图片**：GitHub raw 外链（`https://raw.githubusercontent.com/wangmeiyi411830/RCC/main/...`），不内嵌进HTML
- **HTML大小**：约30KB（纯结构+逻辑，无图片数据）
- **数据源**：`待租单元.xlsx`，第2行为表头，含列：单元号、面积（㎡）、单价（元/㎡）、开门红特惠、备注
- **楼层解析逻辑**：3位单元号取第1位为楼层，4位取前2位，13A开头特判
- **图片加载优化**：页面打开后后台静默预加载所有图片 + 骨架屏动画
- **已弃用**：腾讯云 COS（2024年后新建桶强制触发下载，无法在微信渲染）

---

## 七、已知坑和注意事项

1. **构建脚本是 `build_vis_github.py`**，不是 `build_vis.py`（后者是旧版内嵌图片版，已废弃）
2. **图片同步步骤不能省**：脚本只生成 HTML，不会自动把图片复制到 RCC 仓库
3. **手机原图必须压缩**：超过 300KB 的 JPG 需压缩（最长边1600px，quality=72），否则加载极慢（raw.githubusercontent.com 国内访问每张约3-4秒）
4. **GitHub Pages 有1-2分钟延迟**：推送后需等待，不是即时生效
5. **`807-1-1.png` 这种命名**：单元号是 `807-1`，序号是 `1`，脚本能正确识别（sort_key 正则匹配最后一个 `-数字`）

---

## 八、如何验证更新是否生效

```python
import urllib.request, json, re

url = 'https://wangmeiyi411830.github.io/RCC/'
r = urllib.request.urlopen(url, timeout=15)
content = r.read().decode('utf-8')

m = re.search(r'const unitPhotos = (\{.*?\});', content, re.DOTALL)
if m:
    photos = json.loads(m.group(1))
    for unit, urls in photos.items():
        if len(urls) > 1:
            print(unit + ': ' + str([p.split('/')[-1] for p in urls]))
    print('--- 单元总数:', len(photos), '---')
```

---

*此文件由AI生成，最后更新：2026-03-26。每次项目有重大变更时请同步更新本文件。*
