import json, os, re
import pandas as pd

# GitHub raw 图片基础地址
GITHUB_RAW = 'https://raw.githubusercontent.com/wangmeiyi411830/RCC/main'

# ── 脚本所在目录（路径自动适应，无论放在哪个文件夹都能运行）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── 1. Load unit data ──────────────────────────────────────────────────────────
df = pd.read_excel(os.path.join(BASE_DIR, '待租单元.xlsx'), header=1)
unit_data = {}

for _, row in df.iterrows():
    unit_str = str(row['单元号']).strip()
    area = float(row['面积（㎡）'])
    price = float(row['单价（元/㎡）'])
    special = int(row['开门红特惠'])
    note = str(row['备注']).strip()

    if unit_str.startswith('13A'):
        floor_key = '13A'
    elif '+' in unit_str:
        base = unit_str.split('+')[0]
        floor_key = str(int(base[:2]))
    elif '-' in unit_str:
        base = unit_str.split('-')[0]
        floor_key = str(int(base[0])) if len(base) == 3 else str(int(base[:2]))
    else:
        num = unit_str
        if len(num) == 3:
            floor_key = str(int(num[0]))
        elif len(num) == 4:
            floor_key = str(int(num[:2]))
        else:
            floor_key = '?'

    if floor_key not in unit_data:
        unit_data[floor_key] = []
    unit_data[floor_key].append({
        'unit': unit_str,
        'area': area,
        'price': price,
        'special': special,
        'note': note
    })

print('Unit data loaded OK')

# ── 2. Floor images → GitHub URL ──────────────────────────────────────────────
floors_order = [1,2,4,5,6,7,8,9,10,12,'13A',15,16,17,18,19,20,22]
floor_images = {}
img_dir = os.path.join(BASE_DIR, 'floor_images')
for floor in floors_order:
    fpath = f'{img_dir}/floor_{floor}.jpg'
    if os.path.exists(fpath):
        floor_images[str(floor)] = f'{GITHUB_RAW}/floor_images/floor_{floor}.jpg'
        print(f'Floor {floor} -> GitHub URL')
    else:
        print(f'WARNING: Missing floor_{floor}.jpg')

# ── 3. Unit photos → GitHub URL ───────────────────────────────────────────────
unit_photo_dir = os.path.join(BASE_DIR, 'unit_images')
unit_photos = {}

def sort_key(fname):
    m = re.match(r'^(.+?)-(\d+)\.(jpg|jpeg|png)$', fname, re.IGNORECASE)
    if m:
        return (m.group(1), int(m.group(2)))
    return (fname, 0)

for fname in sorted(os.listdir(unit_photo_dir), key=sort_key):
    m = re.match(r'^(.+?)-(\d+)\.(jpg|jpeg|png)$', fname, re.IGNORECASE)
    if m:
        unit_key = m.group(1)
        ext = m.group(3).lower()
        url = f'{GITHUB_RAW}/unit_images/{fname}'
        if unit_key not in unit_photos:
            unit_photos[unit_key] = []
        unit_photos[unit_key].append(url)
        print(f'Unit photo: {fname} -> GitHub URL')

print(f'Total unit photo groups: {len(unit_photos)}')

# ── 4. Build HTML ──────────────────────────────────────────────────────────────
floors_json = json.dumps(unit_data, ensure_ascii=False)
images_js = json.dumps(floor_images, ensure_ascii=False)
unit_photos_js = json.dumps(unit_photos, ensure_ascii=False)
floors_list_js = json.dumps([str(f) for f in floors_order])

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>招商展示系统 · 待租单元可视化</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
    background: #0f1923;
    color: #e8eaf0;
    min-height: 100vh;
    overflow-x: hidden;
  }}

  /* ── Header ── */
  .header {{
    background: linear-gradient(135deg, #1a2740 0%, #0d1b2a 100%);
    border-bottom: 1px solid #2a3f5f;
    padding: 16px 32px;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 2px 20px rgba(0,0,0,0.4);
  }}
  .header-logo {{
    width: 44px; height: 44px;
    background: linear-gradient(135deg, #f97316, #ef4444);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; font-weight: 900; color: #fff;
    flex-shrink: 0;
  }}
  .header-text h1 {{
    font-size: 20px; font-weight: 700; color: #f0f4ff;
    letter-spacing: 1px;
  }}
  .header-text p {{
    font-size: 12px; color: #7a8fa8; margin-top: 2px;
  }}
  .header-badge {{
    margin-left: auto;
    background: linear-gradient(135deg, #dc2626, #f97316);
    color: #fff;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    animation: pulse 2s infinite;
  }}
  @keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.75; }}
  }}

  /* ── Main layout ── */
  .main {{
    display: flex;
    height: calc(100vh - 77px);
    overflow: hidden;
  }}

  /* ── Floor selector sidebar ── */
  .sidebar {{
    width: 82px;
    background: #141f2e;
    border-right: 1px solid #1e2f45;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 16px 8px;
    gap: 6px;
    overflow-y: auto;
    flex-shrink: 0;
  }}
  .sidebar-label {{
    font-size: 10px;
    color: #4a5f78;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 4px;
  }}
  .floor-btn {{
    width: 58px; height: 44px;
    border: 1px solid #1e3050;
    background: #1a2a3d;
    border-radius: 8px;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    position: relative;
  }}
  .floor-btn:hover {{
    border-color: #3a6aa8;
    background: #1e3558;
  }}
  .floor-btn.active {{
    border-color: #f97316;
    background: linear-gradient(135deg, #1e2f1a, #2a1e0f);
    box-shadow: 0 0 12px rgba(249,115,22,0.25);
  }}
  .floor-btn .floor-num {{
    font-size: 14px; font-weight: 700; color: #c8d8f0;
    line-height: 1;
  }}
  .floor-btn.active .floor-num {{ color: #fb923c; }}
  .floor-btn .floor-label {{ font-size: 9px; color: #4a5f78; margin-top: 2px; }}
  .floor-btn.active .floor-label {{ color: #f97316; }}
  .floor-btn .dot {{
    position: absolute; top: 5px; right: 5px;
    width: 6px; height: 6px; border-radius: 50%;
    background: #22c55e;
  }}

  /* ── Content area ── */
  .content {{
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: #0f1923;
  }}

  .floor-titlebar {{
    padding: 12px 24px;
    background: #141f2e;
    border-bottom: 1px solid #1e2f45;
    display: flex;
    align-items: center;
    gap: 16px;
  }}
  .floor-titlebar h2 {{
    font-size: 18px; font-weight: 700; color: #e8f0ff;
  }}
  .floor-titlebar .units-count {{
    font-size: 12px; color: #7a8fa8;
    background: #1a2a3d;
    padding: 3px 10px; border-radius: 10px;
  }}
  .floor-titlebar .avail-count {{
    font-size: 12px; font-weight: 600; color: #22c55e;
    background: rgba(34,197,94,0.1);
    padding: 3px 10px; border-radius: 10px;
    border: 1px solid rgba(34,197,94,0.2);
  }}

  .split {{
    display: flex;
    flex: 1;
    overflow: hidden;
  }}

  .plan-panel {{
    flex: 1;
    min-width: 0;
    padding: 16px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #0a1420;
    position: relative;
  }}
  .plan-panel img {{
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    border-radius: 8px;
    box-shadow: 0 4px 32px rgba(0,0,0,0.5);
    transition: opacity 0.3s;
  }}
  .plan-panel .plan-legend {{
    position: absolute;
    bottom: 20px; left: 20px;
    background: rgba(20,31,46,0.85);
    border: 1px solid #2a3f5f;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 11px;
    color: #8a9fbc;
    backdrop-filter: blur(4px);
  }}
  .plan-panel .plan-legend span {{
    display: inline-flex; align-items: center; gap: 5px; margin-right: 14px;
  }}
  .legend-dot {{
    width: 10px; height: 10px; border-radius: 2px; display: inline-block;
  }}

  .carousel {{
    width: 100%; height: 100%;
    display: none;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
  }}
  .carousel.active {{ display: flex; }}
  .carousel-track {{
    position: relative;
    width: 100%; height: 100%;
    overflow: hidden;
    border-radius: 8px;
  }}
  .carousel-slide {{
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    display: flex; align-items: center; justify-content: center;
    transition: transform 0.4s cubic-bezier(.4,0,.2,1), opacity 0.4s;
    opacity: 0;
  }}
  .carousel-slide.cur {{ opacity: 1; transform: translateX(0); z-index: 1; }}
  .carousel-slide.prev {{ opacity: 0; transform: translateX(-100%); z-index: 0; }}
  .carousel-slide.next-slide {{ opacity: 0; transform: translateX(100%); z-index: 0; }}
  .carousel-slide img {{
    max-width: 100%; max-height: 100%;
    object-fit: contain;
    border-radius: 8px;
    box-shadow: 0 4px 32px rgba(0,0,0,0.5);
  }}
  .carousel-btn {{
    position: absolute; top: 50%; transform: translateY(-50%);
    width: 40px; height: 40px; border-radius: 50%;
    background: rgba(15,25,35,0.75);
    border: 1px solid rgba(255,255,255,0.15);
    color: #e8f0ff; font-size: 18px; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    z-index: 10; transition: background 0.2s;
    backdrop-filter: blur(4px);
  }}
  .carousel-btn:hover {{ background: rgba(249,115,22,0.5); border-color: #f97316; }}
  .carousel-btn.left {{ left: 12px; }}
  .carousel-btn.right {{ right: 12px; }}
  .carousel-dots {{
    position: absolute; bottom: 14px; left: 50%; transform: translateX(-50%);
    display: flex; gap: 6px; z-index: 10;
  }}
  .carousel-dot {{
    width: 7px; height: 7px; border-radius: 50%;
    background: rgba(255,255,255,0.3); cursor: pointer;
    transition: background 0.2s, transform 0.2s;
  }}
  .carousel-dot.active {{ background: #f97316; transform: scale(1.3); }}
  /* ── Loading skeleton ── */
  .img-wrap {{
    width: 100%; height: 100%;
    display: flex; align-items: center; justify-content: center;
    position: relative;
  }}
  .img-skeleton {{
    position: absolute; inset: 0;
    background: linear-gradient(90deg, #1a2a3d 25%, #223048 50%, #1a2a3d 75%);
    background-size: 200% 100%;
    animation: shimmer 1.4s infinite;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    color: #3a5070; font-size: 13px;
  }}
  @keyframes shimmer {{
    0% {{ background-position: 200% 0; }}
    100% {{ background-position: -200% 0; }}
  }}
  .img-skeleton.hidden {{ display: none; }}

  .carousel-back-tip {{
    position: absolute; top: 12px; left: 12px; z-index: 10;
    background: rgba(15,25,35,0.75); border: 1px solid #2a3f5f;
    border-radius: 6px; padding: 5px 10px;
    font-size: 11px; color: #7a8fa8;
    backdrop-filter: blur(4px);
  }}
  .carousel-label {{
    position: absolute; top: 12px; left: 50%; transform: translateX(-50%); z-index: 10;
    background: rgba(249,115,22,0.15); border: 1px solid rgba(249,115,22,0.3);
    border-radius: 6px; padding: 5px 12px;
    font-size: 12px; font-weight: 600; color: #fb923c;
    backdrop-filter: blur(4px);
    white-space: nowrap;
  }}
  .plan-panel.photo-mode > img,
  .plan-panel.photo-mode > .plan-legend {{ display: none !important; }}
  .plan-panel.photo-mode .carousel {{ display: flex; }}

  .cards-panel {{
    width: 360px;
    flex-shrink: 0;
    background: #141f2e;
    border-left: 1px solid #1e2f45;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}
  .cards-panel::-webkit-scrollbar {{ width: 4px; }}
  .cards-panel::-webkit-scrollbar-track {{ background: #0f1923; }}
  .cards-panel::-webkit-scrollbar-thumb {{ background: #2a3f5f; border-radius: 4px; }}

  .cards-header {{
    font-size: 11px;
    color: #4a5f78;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    padding-bottom: 8px;
    border-bottom: 1px solid #1e2f45;
  }}

  .unit-card {{
    background: linear-gradient(135deg, #1a2740 0%, #162035 100%);
    border: 1px solid #2a3f5f;
    border-radius: 12px;
    padding: 16px;
    transition: all 0.25s;
    position: relative;
    overflow: hidden;
  }}
  .unit-card::before {{
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #f97316, #fbbf24);
    border-radius: 12px 12px 0 0;
  }}
  .unit-card:hover {{
    border-color: #f97316;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(249,115,22,0.15);
  }}
  .unit-card.has-photos {{ cursor: pointer; }}
  .unit-card.has-photos:hover {{ border-color: #60a5fa; box-shadow: 0 8px 24px rgba(96,165,250,0.2); }}
  .unit-card.selected {{
    border-color: #60a5fa !important;
    box-shadow: 0 0 0 2px rgba(96,165,250,0.3), 0 8px 24px rgba(96,165,250,0.2) !important;
  }}
  .unit-photo-hint {{
    font-size: 11px; color: #60a5fa;
    margin-bottom: 8px; margin-top: -4px;
    opacity: 0.8;
  }}

  .unit-header {{
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 10px;
  }}
  .unit-number {{
    font-size: 20px; font-weight: 800; color: #f0f4ff;
    letter-spacing: 0.5px;
  }}
  .unit-tag {{
    font-size: 11px;
    background: rgba(249,115,22,0.15);
    color: #fb923c;
    border: 1px solid rgba(249,115,22,0.3);
    padding: 3px 8px;
    border-radius: 6px;
    font-weight: 600;
    white-space: nowrap;
  }}

  .unit-note {{
    font-size: 12px;
    color: #7ab8f5;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 5px;
  }}
  .unit-note::before {{
    content: '★';
    color: #fbbf24;
    font-size: 11px;
  }}

  .unit-metrics {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }}
  .metric {{
    background: rgba(255,255,255,0.04);
    border-radius: 8px;
    padding: 8px 10px;
    border: 1px solid rgba(255,255,255,0.06);
  }}
  .metric-label {{
    font-size: 10px; color: #4a5f78; margin-bottom: 3px;
  }}
  .metric-value {{
    font-size: 14px; font-weight: 700; color: #e8f0ff;
  }}
  .metric-value.area {{ color: #60a5fa; }}
  .metric-value.price {{ color: #a78bfa; }}
  .metric-value.special {{ color: #f97316; font-size: 15px; }}

  .special-row {{
    grid-column: 1 / -1;
    background: linear-gradient(135deg, rgba(249,115,22,0.12), rgba(239,68,68,0.08));
    border-color: rgba(249,115,22,0.25);
  }}
  .special-row .metric-label {{ color: #f97316; }}
  .special-row .metric-value {{ font-size: 18px; }}
  .metric-sub-price {{
    font-size: 12px;
    color: #fbbf24;
    margin-top: 4px;
    opacity: 0.85;
  }}

  .empty-state {{
    text-align: center; padding: 40px 20px; color: #4a5f78;
  }}
  .empty-state .icon {{ font-size: 36px; margin-bottom: 10px; }}
  .empty-state p {{ font-size: 13px; line-height: 1.6; }}

  @media (max-width: 900px) {{
    .split {{ flex-direction: column; }}
    .cards-panel {{ width: 100%; height: 300px; border-left: none; border-top: 1px solid #1e2f45; }}
  }}
</style>
</head>
<body>

<div class="header">
  <div class="header-logo">招</div>
  <div class="header-text">
    <h1>写字楼招商管理系统</h1>
    <p>待租单元可视化展示平台</p>
  </div>
  <div class="header-badge">🔥 RCC湖湾里 · 特惠季</div>
</div>

<div class="main">
  <div class="sidebar">
    <div class="sidebar-label">楼层</div>
    <div id="floorBtns"></div>
  </div>

  <div class="content">
    <div class="floor-titlebar">
      <h2 id="floorTitle">选择楼层</h2>
      <span class="units-count" id="unitsTotal"></span>
      <span class="avail-count" id="availCount"></span>
    </div>
    <div class="split">
      <div class="plan-panel" id="planPanel">
        <div class="img-skeleton" id="planSkeleton" style="border-radius:8px;">平面图加载中…</div>
        <img id="planImg" src="" alt="平面图" style="opacity:0;transition:opacity 0.35s;" />
        <div class="plan-legend">
          <span><span class="legend-dot" style="background:#e8973a;"></span>已租单元</span>
          <span><span class="legend-dot" style="background:#e8e8e8;"></span>待租单元</span>
        </div>
        <div class="carousel" id="carousel">
          <div class="carousel-back-tip">← 点击左侧楼层按钮返回平面图</div>
          <div class="carousel-label" id="carouselLabel"></div>
          <div class="carousel-track" id="carouselTrack"></div>
          <button class="carousel-btn left" id="carouselPrev">&#8249;</button>
          <button class="carousel-btn right" id="carouselNext">&#8250;</button>
          <div class="carousel-dots" id="carouselDots"></div>
        </div>
      </div>
      <div class="cards-panel">
        <div class="cards-header">待租单元 · 详细信息</div>
        <div id="unitCards"></div>
      </div>
    </div>
  </div>
</div>

<script>
const floorsOrder = {floors_list_js};
const floorUnits = {floors_json};
const floorImages = {images_js};
const unitPhotos = {unit_photos_js};

let carouselIndex = 0;
let carouselPhotos = [];

// ── 后台预加载所有图片 ──────────────────────────────────────
const preloadCache = {{}};
function preloadAll() {{
  // 先加载所有楼层平面图
  Object.values(floorImages).forEach(src => {{
    if (!preloadCache[src]) {{
      const img = new Image();
      img.src = src;
      preloadCache[src] = img;
    }}
  }});
  // 再加载所有单元图片（延迟500ms，不抢平面图带宽）
  setTimeout(() => {{
    Object.values(unitPhotos).forEach(photos => {{
      photos.forEach(src => {{
        if (!preloadCache[src]) {{
          const img = new Image();
          img.src = src;
          preloadCache[src] = img;
        }}
      }});
    }});
  }}, 500);
}}

function showCarousel(unitKey, unitLabel) {{
  const photos = unitPhotos[unitKey];
  if (!photos || photos.length === 0) return;

  carouselPhotos = photos;
  carouselIndex = 0;

  const track = document.getElementById('carouselTrack');
  track.innerHTML = photos.map((src, i) => {{
    const cached = preloadCache[src] && preloadCache[src].complete;
    return `<div class="carousel-slide ${{i === 0 ? 'cur' : 'next-slide'}}" data-idx="${{i}}">
      <div class="img-wrap">
        <div class="img-skeleton${{cached ? ' hidden' : ''}}" id="sk-${{unitKey}}-${{i}}">图片加载中…</div>
        <img src="${{src}}" alt="${{unitLabel}} 图${{i+1}}"
          style="opacity:${{cached ? 1 : 0}};transition:opacity 0.3s;"
          onload="this.style.opacity=1;var sk=document.getElementById('sk-${{unitKey}}-${{i}}');if(sk)sk.classList.add('hidden');" />
      </div>
    </div>`;
  }}).join('');

  const dots = document.getElementById('carouselDots');
  dots.innerHTML = photos.map((_, i) =>
    `<div class="carousel-dot ${{i === 0 ? 'active' : ''}}" data-idx="${{i}}"></div>`
  ).join('');
  dots.querySelectorAll('.carousel-dot').forEach(dot => {{
    dot.addEventListener('click', () => goToSlide(parseInt(dot.dataset.idx)));
  }});

  document.getElementById('carouselPrev').style.display = photos.length > 1 ? 'flex' : 'none';
  document.getElementById('carouselNext').style.display = photos.length > 1 ? 'flex' : 'none';
  dots.style.display = photos.length > 1 ? 'flex' : 'none';

  document.getElementById('carouselLabel').textContent = `${{unitLabel}} · 实景/户型图`;
  document.getElementById('planPanel').classList.add('photo-mode');
}}

function goToSlide(newIdx) {{
  const slides = document.querySelectorAll('.carousel-slide');
  const dots = document.querySelectorAll('.carousel-dot');
  if (slides.length === 0) return;

  const oldIdx = carouselIndex;
  if (newIdx === oldIdx) return;

  const dir = newIdx > oldIdx ? 1 : -1;

  slides[oldIdx].classList.remove('cur');
  slides[oldIdx].classList.add(dir > 0 ? 'prev' : 'next-slide');
  slides[newIdx].style.transform = `translateX(${{dir * 100}}%)`;
  slides[newIdx].classList.remove('prev', 'next-slide');
  slides[newIdx].classList.add('cur');

  slides[newIdx].offsetHeight;
  slides[newIdx].style.transform = 'translateX(0)';
  slides[oldIdx].style.transform = `translateX(${{-dir * 100}}%)`;

  dots.forEach((d, i) => d.classList.toggle('active', i === newIdx));
  carouselIndex = newIdx;
}}

function hideCarousel() {{
  document.getElementById('planPanel').classList.remove('photo-mode');
  carouselPhotos = [];
  carouselIndex = 0;
}}

document.getElementById('carouselPrev').addEventListener('click', () => {{
  if (carouselPhotos.length < 2) return;
  goToSlide((carouselIndex - 1 + carouselPhotos.length) % carouselPhotos.length);
}});
document.getElementById('carouselNext').addEventListener('click', () => {{
  if (carouselPhotos.length < 2) return;
  goToSlide((carouselIndex + 1) % carouselPhotos.length);
}});

const btnContainer = document.getElementById('floorBtns');
floorsOrder.forEach(floor => {{
  const hasUnits = floorUnits[floor] && floorUnits[floor].length > 0;
  const btn = document.createElement('div');
  btn.className = 'floor-btn';
  btn.dataset.floor = floor;
  btn.innerHTML = `
    <span class="floor-num">${{floor}}<span style="font-size:9px;font-weight:400">F</span></span>
    <span class="floor-label">${{floor === '13A' ? '14层' : ''}}</span>
    ${{hasUnits ? '<span class="dot"></span>' : ''}}
  `;
  btn.addEventListener('click', () => selectFloor(floor));
  btnContainer.appendChild(btn);
}});

function selectFloor(floor) {{
  hideCarousel();

  document.querySelectorAll('.floor-btn').forEach(b => b.classList.remove('active'));
  const btn = document.querySelector(`.floor-btn[data-floor="${{floor}}"]`);
  if (btn) btn.classList.add('active');

  const label = floor === '13A' ? '13A层（14层）' : floor + '层';
  document.getElementById('floorTitle').textContent = label + ' · 平面图';

  const img = document.getElementById('planImg');
  const skeleton = document.getElementById('planSkeleton');
  if (floorImages[floor]) {{
    const cached = preloadCache[floorImages[floor]] && preloadCache[floorImages[floor]].complete;
    if (cached) {{
      img.src = floorImages[floor];
      img.style.opacity = '1';
      skeleton.classList.add('hidden');
    }} else {{
      img.style.opacity = '0';
      skeleton.classList.remove('hidden');
      img.src = floorImages[floor];
      img.onload = () => {{
        img.style.opacity = '1';
        skeleton.classList.add('hidden');
      }};
    }}
  }}

  const units = floorUnits[floor] || [];
  document.getElementById('availCount').textContent = units.length > 0 ? `${{units.length}} 个待租单元` : '暂无待租单元';
  document.getElementById('unitsTotal').textContent = `${{label}}`;

  const cardsEl = document.getElementById('unitCards');
  if (units.length === 0) {{
    cardsEl.innerHTML = `
      <div class="empty-state">
        <div class="icon">✅</div>
        <p>该楼层暂无待租单元<br>所有单元均已出租</p>
      </div>`;
    return;
  }}
  cardsEl.innerHTML = units.map(u => {{
    const hasPhotos = unitPhotos[u.unit] && unitPhotos[u.unit].length > 0;
    const photoHint = hasPhotos
      ? `<div class="unit-photo-hint">📷 点击查看实景/户型图</div>`
      : '';
    return `
    <div class="unit-card${{hasPhotos ? ' has-photos' : ''}}" data-unit="${{u.unit}}" data-label="${{u.unit}} 室">
      <div class="unit-header">
        <div class="unit-number">${{u.unit}} 室</div>
        <div class="unit-tag">${{getTag(u.note)}}</div>
      </div>
      <div class="unit-note">${{u.note}}</div>
      ${{photoHint}}
      <div class="unit-metrics">
        <div class="metric">
          <div class="metric-label">建筑面积</div>
          <div class="metric-value area">${{u.area}} ㎡</div>
        </div>
        <div class="metric">
          <div class="metric-label">挂牌单价</div>
          <div class="metric-value price">¥${{u.price}} /㎡</div>
        </div>
        <div class="metric special-row">
          <div class="metric-label">🔥 特惠季总价（仅限4月30日前签约）</div>
          <div class="metric-value special">¥${{u.special.toLocaleString()}} 元/月</div>
          <div class="metric-sub-price">￥${{(u.special / u.area).toFixed(2)}} 元/㎡/月</div>
        </div>
      </div>
    </div>`;
  }}).join('');

  cardsEl.querySelectorAll('.unit-card.has-photos').forEach(card => {{
    card.addEventListener('click', () => {{
      showCarousel(card.dataset.unit, card.dataset.label);
      cardsEl.querySelectorAll('.unit-card').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
    }});
  }});
}}

function getTag(note) {{
  if (note.includes('小面积')) return '精品小单元';
  if (note.includes('大通间')) return '大通间';
  if (note.includes('阳台')) return '赠阳台';
  if (note.includes('带装修')) return '带装修';
  if (note.includes('双边采光')) return '双边采光';
  if (note.includes('方正')) return '方正户型';
  return '待租';
}}

selectFloor(floorsOrder[0]);

// 页面加载完后后台静默预加载所有图片
window.addEventListener('load', preloadAll);
</script>
</body>
</html>"""

output_path = os.path.join(BASE_DIR, 'index.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"HTML saved to: {output_path}")
print(f"File size: {os.path.getsize(output_path) // 1024} KB")
