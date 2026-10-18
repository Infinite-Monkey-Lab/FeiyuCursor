# -*- coding: utf-8 -*-
"""
大肥鱼指针 · FeiyuCursor (Windows 11 高清美化鼠标指针方案)
基于 DeepSeek 娘（大肥鱼 / 肥鱼娘）形象全面美化：
- 正常选择：100% 保留原版纯净温润风格（经典浅蓝箭头 + 单个萌心 + 亲切探头）
- 忙 / 后台运行：全新 16 帧丝滑动态指针 (.ani)，大肥鱼呼吸浮动 + 环绕星轨
- 精确选择/文本/不可用/手写/缩放：全套细节深度美化
- 全覆盖 Windows 11 17 种指针 + 32~256px 多档 DPI 无损渲染
"""
import struct, math, sys, os, base64, io
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------- 色彩与常数 ----------------
NAVYD      = (34, 62, 128, 255)       # 经典深蓝描边
WHITE      = (255, 255, 255, 255)
BLUE_ORIG  = (168, 208, 250, 255)     # 原版正常选择经典天蓝
CYAN_LIGHT = (225, 245, 255, 255)     # 冰蓝
CYAN_MID   = (165, 212, 255, 255)     # 天蓝
CYAN_DEEP  = (108, 172, 252, 255)     # 晶蓝
GOLD_STAR  = (255, 216, 75, 255)      # 肥鱼星金色
PINK_HEART = (255, 128, 170, 255)     # 萌动粉心
PINK_LIGHT = (255, 215, 230, 255)     # 爱心高光
RED_WARN   = (245, 75, 95, 255)       # 结界珊瑚红
RED_LINE   = (175, 25, 45, 255)       # 警示深红
SHC        = (15, 22, 45, 130)        # 字体与微阴影
SHADOW_RGB = np.float32([16, 24, 48]) # 贴纸投影基色

# ---------------- 基础图像与素材处理 ----------------
girl_src = np.asarray(Image.open('character_square.png').convert('RGBA')).astype(np.float32)

hsv = cv2.cvtColor(girl_src[..., :3].astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
hsv[..., 1] = np.clip(hsv[..., 1] * 1.38, 0, 255)
rgb = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
rgb = np.clip((rgb - 128) * 1.12 + 128, 0, 255)
girl = girl_src.copy()
girl[..., :3] = cv2.fastNlMeansDenoisingColored(rgb.astype(np.uint8), None, 3, 3, 7, 21).astype(np.float32)

def fill_holes(mask):
    padded = np.pad((~mask).astype(np.uint8), 1, constant_values=1)
    ff = np.zeros((padded.shape[0] + 2, padded.shape[1] + 2), np.uint8)
    cv2.floodFill(padded, ff, (0, 0), 2)
    holes = (padded == 1)[1:-1, 1:-1]
    return mask | holes

base_mask = fill_holes(girl_src[..., 3] > 90).astype(np.uint8)
er_color = cv2.erode(base_mask, np.ones((9, 9), np.uint8))
er_ring  = cv2.erode(base_mask, np.ones((5, 5), np.uint8))
girl[..., 3] = np.clip(cv2.GaussianBlur(er_color * 255, (0, 0), 1.5), 0, 255)
hi_solid = (er_ring * 255).astype(np.float32)

# 带小汗滴的表情版（用于不可用状态）
girl_sweat = girl.copy()
def add_sweatdrop(im_rgba):
    im_pil = Image.fromarray(np.clip(im_rgba, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im_pil)
    x, y, size = 142, 130, 24
    w, h = size, size * 1.5
    r = w / 2.0
    cy = y + h * 0.15
    pts = [(x, y - h * 0.5), (x + r * 0.95, cy), (x, cy + r), (x - r * 0.95, cy)]
    d.polygon(pts, fill=NAVYD)
    d.ellipse([x - r - 2, cy - r - 2, x + r + 2, cy + r + 2], fill=NAVYD)
    d.polygon(pts, fill=(115, 205, 255, 255))
    d.ellipse([x - r, cy - r, x + r, cy + r], fill=(115, 205, 255, 255))
    d.ellipse([x - r*0.45, cy - r*0.45, x - r*0.1, cy - r*0.1], fill=(255, 255, 255, 240))
    return np.asarray(im_pil).astype(np.float32)

girl_sweat = add_sweatdrop(girl_sweat)

def premul_resize(a, size, size2=None):
    size2 = size2 or size
    r3, al = a[..., :3] * a[..., 3:] / 255.0, a[..., 3]
    inter = cv2.INTER_AREA if size2 < a.shape[0] else cv2.INTER_LANCZOS4
    r = cv2.resize(r3, (size2, size), interpolation=inter)
    m = cv2.resize(al, (size2, size), interpolation=inter)
    out = np.zeros((size, size2, 4), np.float32)
    nz = m > 4
    out[..., :3][nz] = (r[nz] / (m[nz][:, None] / 255.0)).clip(0, 255)
    out[..., 3] = m.clip(0, 255)
    out[out[..., 3] < 8] = 0
    blur = cv2.GaussianBlur(out[..., :3], (0, 0), 0.9)
    mask3 = (out[..., 3:4] > 40).astype(np.float32)
    out[..., :3] = np.clip(out[..., :3] + (out[..., :3] - blur) * 1.0 * mask3, 0, 255)
    return out.astype(np.float32)

def over(base, top):
    la = top[..., 3:4] / 255.0
    base[..., :3] = top[..., :3] * la + base[..., :3] * (1 - la)
    base[..., 3:4] = top[..., 3:4] + base[..., 3:4] * (1 - la)
    return base

def add_shadow(canvas, strength=0.72):
    S = canvas.shape[0]
    a = canvas[..., 3] / 255.0
    sh_rad = max(1.5, S / 36.0)
    blur = cv2.GaussianBlur(a, (0, 0), sh_rad)
    sh_x = max(1, round(S / 44.0))
    sh_y = max(1, round(S / 36.0))
    shm = np.zeros_like(blur)
    if sh_y < S and sh_x < S:
        shm[sh_y:, sh_x:] = blur[:-sh_y, :-sh_x]
    sa = np.clip(shm * strength, 0, 1) * (1 - a)
    canvas[..., :3] = canvas[..., :3] * a[..., None] + SHADOW_RGB * sa[..., None]
    canvas[..., 3] = np.clip(a + sa, 0, 1) * 255
    return canvas

def finish(canvas, strength=0.72):
    return np.clip(add_shadow(np.clip(canvas, 0, 255), strength), 0, 255).astype(np.uint8)

def sticker_canvas(S, img, hi, gh_scale, gx_frac, gy_frac, add_navy_border=True):
    gh = int(round(S * gh_scale))
    gw = int(round(gh * img.shape[1] / img.shape[0]))
    g = premul_resize(img, gh, gw)
    solid = cv2.resize(hi, (gw, gh), interpolation=cv2.INTER_AREA) > 80
    gx, gy = int(round(S * gx_frac)), int(round(S * gy_frac))

    canvas_solid = np.zeros((S, S), np.uint8)
    sy0, sx0 = max(0, -gy), max(0, -gx)
    sy1, sx1 = gh - max(0, gy + gh - S), gw - max(0, gx + gw - S)
    canvas_solid[max(0, gy):max(0, gy)+sy1-sy0, max(0, gx):max(0, gx)+sx1-sx0] = solid[sy0:sy1, sx0:sx1]

    dist = cv2.distanceTransform((canvas_solid == 0).astype(np.uint8), cv2.DIST_L2, 5)
    rw = max(2.2, S / 28.0)
    rn = rw + (max(1.1, S / 54.0) if add_navy_border else 0.0)

    aw = np.clip(rw + 0.5 - dist, 0, 1)
    if add_navy_border:
        an = np.clip(rn + 0.5 - dist, 0, 1) - aw
        an = np.clip(an, 0, 1)
    else:
        an = np.zeros_like(aw)

    c = np.zeros((S, S, 4), np.float32)
    c[..., 0] += an * NAVYD[0]
    c[..., 1] += an * NAVYD[1]
    c[..., 2] += an * NAVYD[2]
    c[..., 3] += an * 255
    c[..., 0] += aw * 255
    c[..., 1] += aw * 255
    c[..., 2] += aw * 255
    c[..., 3] += aw * 255
    c[..., 3] = np.clip(c[..., 3], 0, 255)

    cg = np.zeros((S, S, 4), np.float32)
    cg[max(0, gy):max(0, gy)+sy1-sy0, max(0, gx):max(0, gx)+sx1-sx0] = g[sy0:sy1, sx0:sx1]
    return over(c, cg)

def girl_canvas(S, gh_scale, gx_frac, gy_frac, sweat=False):
    target_img = girl_sweat if sweat else girl
    return sticker_canvas(S, target_img, hi_solid, gh_scale, gx_frac, gy_frac)

def peek_canvas(S, gh_scale, gx_frac, gy_frac):
    if S < 48:
        return np.zeros((S, S, 4), np.float32)
    return girl_canvas(S, gh_scale, gx_frac, gy_frac)

def paste_at(canvas, glyph, x, y):
    gh, gw = glyph.shape[:2]
    sy0, sx0 = max(0, -y), max(0, -x)
    sy1 = gh - max(0, y + gh - canvas.shape[0])
    sx1 = gw - max(0, x + gw - canvas.shape[1])
    dy0, dx0 = max(0, y), max(0, x)
    if sy1 <= sy0 or sx1 <= sx0:
        return
    sub = glyph[sy0:sy1, sx0:sx1]
    region = canvas[dy0:dy0+sub.shape[0], dx0:dx0+sub.shape[1]].copy()
    canvas[dy0:dy0+sub.shape[0], dx0:dx0+sub.shape[1]] = over(region, sub)

def paste_center(canvas, glyph, fx, fy):
    gh, gw = glyph.shape[:2]
    paste_at(canvas, glyph, int(round(canvas.shape[1]*fx - gw/2)), int(round(canvas.shape[0]*fy - gh/2)))

ARROW_PTS = [(0.0, 0.0), (0.0, 0.86), (0.19, 0.70), (0.32, 1.00), (0.41, 0.96), (0.29, 0.67), (0.54, 0.67)]

def star4_glyph(size, ow=1.5, fill=GOLD_STAR, outline=NAVYD):
    k = 4
    W = int(size * k) + int(ow * k) * 4 + 8 * k
    im = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = W / 2.0, W / 2.0
    R = size * k * 0.46
    r = R * 0.28
    pts = [
        (cx, cy - R), (cx + r, cy - r), (cx + R, cy), (cx + r, cy + r),
        (cx, cy + R), (cx - r, cy + r), (cx - R, cy), (cx - r, cy - r)
    ]
    d.polygon(pts, fill=outline)
    d.line(pts + [pts[0]], width=max(2, int(ow * k * 1.8)), fill=outline, joint='curve')
    d.polygon(pts, fill=fill)
    r_core = r * 0.65
    pts_core = [
        (cx, cy - R*0.48), (cx + r_core*0.6, cy - r_core*0.6),
        (cx + R*0.48, cy), (cx + r_core*0.6, cy + r_core*0.6),
        (cx, cy + R*0.48), (cx - r_core*0.6, cy + r_core*0.6),
        (cx - R*0.48, cy), (cx - r_core*0.6, cy - r_core*0.6)
    ]
    d.polygon(pts_core, fill=(255, 255, 255, 240))
    im = im.resize((W // k, W // k), Image.LANCZOS)
    bb = im.getbbox()
    return np.asarray(im.crop(bb)).astype(np.float32)

def heart_glyph(size, ow=1.5):
    """圆润饱满的萌动爱心（饱满凸弧度，双重立体高光，圆嘟嘟绝不干瘪）"""
    k = 4
    W = int(size * k)
    im = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = W / 2.0, W / 2.0 - size * 0.05 * k
    u = size * k * 0.48
    pts = []
    steps = 100
    for i in range(steps):
        t = i * (2 * math.pi / steps)
        x = 16 * (math.sin(t) ** 3)
        y = -(13.5 * math.cos(t) - 5.5 * math.cos(2*t) - 2.2 * math.cos(3*t) - math.cos(4*t))
        pts.append((cx + x * (u / 17.0), cy + y * (u / 17.0)))
    d.polygon(pts, fill=NAVYD)
    d.line(pts + [pts[0]], width=max(2, int(ow * k * 2.0)), fill=NAVYD, joint='curve')
    d.polygon(pts, fill=PINK_HEART)
    d.ellipse([cx - u*0.65, cy - u*0.55, cx - u*0.25, cy - u*0.20], fill=PINK_LIGHT)
    d.ellipse([cx - u*0.55, cy - u*0.48, cx - u*0.35, cy - u*0.30], fill=(255, 255, 255, 255))
    sz = max(1, int(round(size)))
    im = im.resize((sz, sz), Image.LANCZOS)
    bb = im.getbbox()
    return np.asarray(im.crop(bb)).astype(np.float32)


NATIVE_HAND_B64 = """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"""
_native_hand_cache = None
def get_native_hand():
    global _native_hand_cache
    if _native_hand_cache is None:
        raw = base64.b64decode(NATIVE_HAND_B64.strip())
        _native_hand_cache = Image.open(io.BytesIO(raw)).convert('RGBA')
    return _native_hand_cache

def hand_glyph(S, ow):
    """官方原生 Aero 优雅指向手势，指尖圆润纯净，绝对无黑色杂色"""
    hand_src = get_native_hand()
    hh = int(round(S * 0.68))
    hw = int(round(hh * hand_src.width / hand_src.height))
    rh = hand_src.resize((hw, hh), Image.LANCZOS)
    arr = np.asarray(rh).astype(np.float32)
    dark_factor = (1.0 - (arr[..., :3].mean(axis=-1) / 255.0)) * (arr[..., 3] / 255.0)
    NAVYD_F = np.array([34, 62, 128], dtype=np.float32)
    WHITE_F = np.array([255, 255, 255], dtype=np.float32)
    styled = np.zeros_like(arr)
    for c in range(3):
        styled[..., c] = WHITE_F[c] * (1.0 - dark_factor) + NAVYD_F[c] * dark_factor
    styled[..., 3] = arr[..., 3]
    tx = hw * (39.5 / 96.0)
    ty = 0.0
    return styled, (tx, ty)

def question_bubble_glyph(size, ow):
    k = 4
    W = int(size * k) + int(ow * k) * 4 + 8 * k
    im = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = W / 2.0, W / 2.0
    r = size * k * 0.44
    owk = int(ow * k * 1.8)
    d.ellipse([cx-r-owk, cy-r-owk, cx+r+owk, cy+r+owk], fill=NAVYD)
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(225, 242, 255, 255))
    d.ellipse([cx-r*0.75, cy-r*0.75, cx-r*0.2, cy-r*0.2], fill=(255, 255, 255, 200))
    font_size = int(size * k * 0.72)
    font = ImageFont.truetype('C:/Windows/Fonts/seguibl.ttf', font_size)
    d.text((cx - font_size*0.24, cy - font_size*0.56), '?', font=font, fill=NAVYD)
    im = im.resize((W // k, W // k), Image.LANCZOS)
    bb = im.getbbox()
    return np.asarray(im.crop(bb)).astype(np.float32)

def reticle_cross_glyph(S, ow):
    k = 4
    W = int(S * k) + int(ow * k) * 4 + 16 * k
    im = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = W / 2.0
    L = S * 0.42 * k
    gap = S * 0.08 * k
    w = max(2, int(S * 0.06 * k))
    r_ring = S * 0.32 * k
    d.ellipse([c-r_ring, c-r_ring, c+r_ring, c+r_ring], outline=(140, 205, 255, 180), width=max(1, int(1.2*k)))
    for angle in [0, 90, 180, 270]:
        rad = math.radians(angle)
        dx, dy = math.cos(rad), math.sin(rad)
        mx, my = c + dx * r_ring, c + dy * r_ring
        dr = 3.5 * k
        d.polygon([(mx, my-dr), (mx+dr, my), (mx, my+dr), (mx-dr, my)], fill=NAVYD)
        d.polygon([(mx, my-dr*0.6), (mx+dr*0.6, my), (mx, my+dr*0.6), (mx-dr*0.6, my)], fill=(255, 255, 255, 255))
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        p1 = (c + dx * gap, c + dy * gap)
        p2 = (c + dx * L, c + dy * L)
        d.line([p1, p2], width=w + int(ow * k * 1.5), fill=NAVYD)
        d.line([p1, p2], width=w, fill=(240, 250, 255, 255))
    star_x = c + r_ring * 0.72
    star_y = c - r_ring * 0.72
    sr = 5 * k
    d.polygon([(star_x, star_y-sr), (star_x+sr*0.3, star_y), (star_x, star_y+sr), (star_x-sr*0.3, star_y)], fill=GOLD_STAR)
    d.polygon([(star_x-sr, star_y), (star_x, star_y-sr*0.3), (star_x+sr, star_y), (star_x, star_y+sr*0.3)], fill=GOLD_STAR)
    im = im.resize((W // k, W // k), Image.LANCZOS)
    bb = im.getbbox()
    g = np.asarray(im.crop(bb)).astype(np.float32)
    H, Wd = g.shape[:2]
    M = max(H, Wd)
    sq = np.zeros((M, M, 4), np.float32)
    sq[(M-H)//2:(M-H)//2+H, (M-Wd)//2:(M-Wd)//2+Wd] = g
    return sq

def ibeam_glyph(S, ow):
    k = 4
    W = int(S * k)
    pad = int(ow * k) * 2 + 8 * k
    im = Image.new('RGBA', (W + pad*2, W + pad*2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = pad + W / 2.0
    top, bot = pad + S*0.14*k, pad + S*0.86*k
    w = int(S * 0.07 * k)
    ser_w = S * 0.28 * k
    def draw_ib(col, extra):
        d.line([x, top, x, bot], width=w + extra, fill=col)
        d.rounded_rectangle([x - ser_w/2 - extra/2, top - w/2 - extra/2, x + ser_w/2 + extra/2, top + w/2 + extra/2], radius=(w+extra)/2, fill=col)
        d.rounded_rectangle([x - ser_w/2 - extra/2, bot - w/2 - extra/2, x + ser_w/2 + extra/2, bot + w/2 + extra/2], radius=(w+extra)/2, fill=col)
    draw_ib(NAVYD, int(ow * k * 2.2))
    draw_ib((232, 245, 255, 255), 0)
    im = im.resize((im.width // k, im.height // k), Image.LANCZOS)
    bb = im.getbbox()
    g = np.asarray(im.crop(bb)).astype(np.float32)
    H, Wd = g.shape[:2]
    M = max(H, Wd)
    sq = np.zeros((M, M, 4), np.float32)
    sq[(M-H)//2:(M-H)//2+H, (M-Wd)//2:(M-Wd)//2+Wd] = g
    return sq

def crystal_barrier_glyph(size, ow):
    k = 4
    W = int(size * k) + int(ow * k) * 4 + 10 * k
    im = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = W / 2.0
    r = size * k * 0.46
    w = max(3, int(ow * k * 2.2))
    d.ellipse([c-r, c-r, c+r, c+r], fill=(255, 90, 110, 40))
    d.ellipse([c-r-w/2, c-r-w/2, c+r+w/2, c+r+w/2], outline=RED_LINE, width=w+2*k)
    d.ellipse([c-r, c-r, c+r, c+r], outline=RED_WARN, width=w)
    a45 = math.radians(45)
    dx = r * 0.72 * math.cos(a45)
    dy = r * 0.72 * math.sin(a45)
    d.line([c - dx, c - dy, c + dx, c + dy], fill=RED_LINE, width=w+2*k)
    d.line([c - dx, c - dy, c + dx, c + dy], fill=RED_WARN, width=w)
    d.line([c - dx, c - dy, c + dx, c + dy], fill=(255, 205, 215, 255), width=max(1, w//3))
    d.arc([c-r*0.85, c-r*0.85, c+r*0.85, c+r*0.85], 200, 260, fill=(255, 255, 255, 210), width=max(2, int(1.5*k)))
    im = im.resize((W // k, W // k), Image.LANCZOS)
    return np.asarray(im).astype(np.float32)

def stylus_glyph(S, ow):
    k = 4
    W = int(S * k) + int(ow * k) * 4 + 14 * k
    im = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    a = math.radians(42)
    dx, dy = math.cos(a), math.sin(a)
    nx, ny = -dy, dx
    o = int(ow * k) * 2 + 6 * k
    tip = (o + S*0.06*k, o + S*0.06*k)
    bs = (tip[0] + dx*S*0.22*k, tip[1] + dy*S*0.22*k)
    be = (bs[0] + dx*S*0.56*k, bs[1] + dy*S*0.56*k)
    ee = (be[0] + dx*S*0.14*k, be[1] + dy*S*0.14*k)
    w = S * 0.18 * k
    def quad(p1, p2, col, extra):
        pts = [(p1[0]+nx*(w/2+extra), p1[1]+ny*(w/2+extra)), (p2[0]+nx*(w/2+extra), p2[1]+ny*(w/2+extra)),
               (p2[0]-nx*(w/2+extra), p2[1]-ny*(w/2+extra)), (p1[0]-nx*(w/2+extra), p1[1]-ny*(w/2+extra))]
        d.polygon(pts, fill=col)
    def tiptri(col, extra):
        d.polygon([tip, (bs[0]+nx*(w/2+extra), bs[1]+ny*(w/2+extra)), (bs[0]-nx*(w/2+extra), bs[1]-ny*(w/2+extra))], fill=col)
    owk = int(ow * k * 1.8)
    quad(bs, be, NAVYD, owk); tiptri(NAVYD, owk); quad(be, ee, NAVYD, owk)
    quad(bs, be, (120, 180, 252, 255), 0)
    quad(be, ee, (245, 140, 160, 255), 0)
    tiptri(GOLD_STAR, 0)
    d.line([bs[0]+nx*w/2, bs[1]+ny*w/2, bs[0]-nx*w/2, bs[1]-ny*w/2], fill=GOLD_STAR, width=int(2*k))
    d.line([be[0]+nx*w/2, be[1]+ny*w/2, be[0]-nx*w/2, be[1]-ny*w/2], fill=GOLD_STAR, width=int(2*k))
    d.ellipse([tip[0]-3*k, tip[1]-3*k, tip[0]+3*k, tip[1]+3*k], fill=(255, 255, 255, 250))
    im = im.resize((W // k, W // k), Image.LANCZOS)
    bb = im.getbbox()
    return np.asarray(im.crop(bb)).astype(np.float32)

def double_arrow_glyph(S, angle_deg, ow):
    k = 4
    L = S * 0.32 * k
    th = S * 0.12 * k
    hd = S * 0.40 * k
    W = int(S * 1.15 * k)
    im = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    a = math.radians(angle_deg)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    c = W / 2.0
    owk = max(2, int(ow * k * 1.6))
    def paint_double(edge, fill):
        solid = (fill is edge)
        w_cur = th + owk*2 if not solid else th*0.68
        x1, y1 = c - ux*L/2, c - uy*L/2
        x2, y2 = c + ux*L/2, c + uy*L/2
        d.line([x1, y1, x2, y2], width=int(w_cur), fill=fill if not solid else fill)
        for sgn, p in [(-1, (x1, y1)), (1, (x2, y2))]:
            tip = (p[0] + ux*sgn*hd*0.62, p[1] + uy*sgn*hd*0.62)
            d.polygon([tip, (p[0]+px*hd*0.46, p[1]+py*hd*0.46), (p[0]-px*hd*0.46, p[1]-py*hd*0.46)], fill=fill)
    paint_double(NAVYD, NAVYD)
    paint_double(NAVYD, (180, 222, 255, 255))
    r = th * 0.55
    d.ellipse([c-r, c-r, c+r, c+r], fill=WHITE)
    d.ellipse([c-r*0.6, c-r*0.6, c+r*0.6, c+r*0.6], fill=GOLD_STAR)
    im = im.resize((W // k, W // k), Image.LANCZOS)
    bb = im.getbbox()
    return np.asarray(im.crop(bb)).astype(np.float32)

def compass_4way_glyph(S, ow):
    k = 4
    L = S * 0.34 * k
    th = S * 0.13 * k
    hd = S * 0.36 * k
    W = int(S * 1.15 * k)
    im = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = W / 2.0
    owk = max(2, int(ow * k * 1.6))
    def paint(edge, fill):
        solid = (fill is edge)
        w = th if solid else th + owk*2
        for ux, uy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            x1, y1 = c + ux*S*0.08*k, c + uy*S*0.08*k
            x2, y2 = c + ux*L/2, c + uy*L/2
            d.line([x1, y1, x2, y2], width=int(w if not solid else th*0.65), fill=edge if not solid else fill)
            tip = (x2 + ux*hd*0.62, y2 + uy*hd*0.62)
            d.polygon([tip, (x2+(-uy)*hd*0.46, y2+ux*hd*0.46), (x2-(-uy)*hd*0.46, y2-ux*hd*0.46)], fill=edge if not solid else fill)
    paint(NAVYD, NAVYD)
    paint(NAVYD, (180, 222, 255, 255))
    r = th * 0.65
    d.ellipse([c-r, c-r, c+r, c+r], fill=WHITE)
    d.ellipse([c-r*0.6, c-r*0.6, c+r*0.6, c+r*0.6], fill=GOLD_STAR)
    im = im.resize((W // k, W // k), Image.LANCZOS)
    bb = im.getbbox()
    return np.asarray(im.crop(bb)).astype(np.float32)

def pin_badge_glyph(S, ow):
    k = 4
    W = int(S * k) + int(ow * k) * 4 + 12 * k
    im = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pad = int(ow * k) * 2 + 6 * k
    u = S * k
    def pin(dd, extra, col):
        dd.ellipse([pad+0.17*u-extra, pad+0.02*u-extra, pad+0.83*u+extra, pad+0.68*u+extra], fill=col)
        dd.polygon([(pad+0.24*u-extra, pad+0.56*u), (pad+0.76*u+extra, pad+0.56*u), (pad+0.50*u, pad+0.99*u+extra)], fill=col)
    pin(d, int(ow*k*2.5), NAVYD)
    pin(d, 0, (95, 160, 255, 255))
    d.ellipse([pad+0.36*u, pad+0.22*u, pad+0.64*u, pad+0.50*u], fill=WHITE)
    d.ellipse([pad+0.41*u, pad+0.27*u, pad+0.59*u, pad+0.45*u], fill=PINK_HEART)
    im = im.resize((W // k, W // k), Image.LANCZOS)
    bb = im.getbbox()
    return np.asarray(im.crop(bb)).astype(np.float32)

def person_badge_glyph(S, ow):
    k = 4
    W = int(S * k) + int(ow * k) * 4 + 12 * k
    im = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pad = int(ow * k) * 2 + 6 * k
    u = S * k
    def person(dd, extra, col):
        dd.ellipse([pad+0.26*u-extra, pad+0.04*u-extra, pad+0.74*u+extra, pad+0.52*u+extra], fill=col)
        dd.pieslice([pad+0.06*u-extra, pad+0.56*u-extra, pad+0.94*u+extra, pad+1.60*u+extra], 180, 360, fill=col)
    person(d, int(ow*k*2.5), NAVYD)
    person(d, 0, (115, 175, 255, 255))
    cw = 0.28 * u; ch = 0.14 * u
    cx = pad + 0.50 * u; cy = pad + 0.08 * u
    crown_pts = [(cx - cw/2, cy), (cx - cw/3, cy - ch), (cx, cy - ch*0.5), (cx + cw/3, cy - ch), (cx + cw/2, cy)]
    d.polygon(crown_pts, fill=GOLD_STAR)
    im = im.resize((W // k, W // k), Image.LANCZOS)
    bb = im.getbbox()
    return np.asarray(im.crop(bb)).astype(np.float32)

def up_arrow_glyph(S, ow):
    k = 4
    h = S * 0.9 * k
    W = int(h * 0.62) + int(ow * k) * 2 + 10 * k
    im = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pad = int(ow * k)
    pts = [(x * h * 0.55 + pad, y * h * 0.95 + pad) for x, y in ARROW_PTS]
    ang = math.radians(-28)
    cx, cy = pad + h*0.22, pad + h*0.33
    rot = [(cx + (px-cx)*math.cos(ang) - (py-cy)*math.sin(ang), cy + (px-cx)*math.sin(ang) + (py-cy)*math.cos(ang)) for px, py in pts]
    minx = min(p[0] for p in rot); miny = min(p[1] for p in rot)
    rot = [(p[0] - minx + pad, p[1] - miny + pad) for p in rot]
    d.polygon(rot, fill=NAVYD)
    d.line(rot + [rot[0]], width=max(2, int(ow * k * 2)), fill=NAVYD, joint='curve')
    d.polygon(rot, fill=(210, 238, 255, 255))
    im = im.resize((W // k, W // k), Image.LANCZOS)
    bb = im.getbbox()
    return np.asarray(im.crop(bb)).astype(np.float32)

# ---------------- 各指针组合成图 ----------------
def compose_arrow(S):
    """【正常选择】完全保持原版纯净贴纸风格（温润马卡龙浅蓝 + 单个粉色小爱心）"""
    ow = max(2, S/30) if S < 48 else max(2, S/28)
    c = np.zeros((S, S, 4), np.float32)
    if S >= 48:
        c = peek_canvas(S, 0.60, 0.36, 0.32)
    k = 4
    h = S/1.9 if S < 48 else S/1.8
    W = int(h * 0.54 * k) + int(ow * k) * 2 + 10 * k
    im = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pad = int(ow * k)
    pts = list(ARROW_PTS)
    v = pts[0]; prv = pts[-1]; nxt = pts[1]
    d1 = (prv[0]-v[0], prv[1]-v[1]); l1 = math.hypot(*d1); d1 = (d1[0]/l1, d1[1]/l1)
    d2 = (nxt[0]-v[0], nxt[1]-v[1]); l2 = math.hypot(*d2); d2 = (d2[0]/l2, d2[1]/l2)
    rr = 0.10
    p1 = (v[0]+d1[0]*rr, v[1]+d1[1]*rr)
    p2 = (v[0]+d2[0]*rr, v[1]+d2[1]*rr)
    bx, by = d1[0]+d2[0], d1[1]+d2[1]
    bl = math.hypot(bx, by)
    mid = (v[0]+bx/bl*rr*0.35, v[1]+by/bl*rr*0.35)
    pts = [p1, mid, p2] + pts[1:]
    P = [(x * h * k + pad, y * h * k + pad) for x, y in pts]
    sh = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(px + 2*k, py + 2*k) for px, py in P], fill=SHC)
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(1.2 * k)))
    d.polygon(P, fill=NAVYD)
    d.line(P + [P[0]], width=max(2, int(ow * k * 2)), fill=NAVYD, joint='curve')
    d.polygon(P, fill=BLUE_ORIG)
    im = im.resize((W // k, W // k), Image.LANCZOS)
    arrow_g = np.asarray(im).astype(np.float32)
    paste_at(c, arrow_g, 1 - int(ow), 1 - int(ow))
    if S >= 48:
        paste_center(c, heart_glyph(int(S*0.22), max(1, S//110)), 0.75, 0.10)
    return finish(c), (0, 0)

def hand_base(S):
    c = np.zeros((S, S, 4), np.float32)
    if S >= 48:
        c = sticker_canvas(S, girl, hi_solid, 0.54, 0.44, 0.40)
        paste_center(c, heart_glyph(int(S*0.22), max(1, S//110)), 0.88, 0.08)
    g, (tx, ty) = hand_glyph(S, max(2, S/30))
    px = int(round(S * 0.12))
    py = int(round(S * 0.22))
    paste_at(c, g, px, py)
    tip = (int(min(max(0, round(px + tx)), S-1)), int(min(max(0, round(py + ty)), S-1)))
    return c, tip

def compose_link(S):
    c, tip = hand_base(S)
    return finish(c), tip

def compose_pin(S):
    c, tip = hand_base(S)
    paste_center(c, pin_badge_glyph(S*0.30, max(2, S/52)), 0.82, 0.82)
    return finish(c), tip

def compose_person(S):
    c, tip = hand_base(S)
    paste_center(c, person_badge_glyph(S*0.32, max(2, S/52)), 0.82, 0.82)
    return finish(c), tip

def compose_help(S):
    c = peek_canvas(S, 0.58, 0.40, 0.32)
    paste_center(c, question_bubble_glyph(S*0.36, max(2, S/44)), 0.14, 0.58)
    # 保持原版风格箭头
    k = 4
    h = S/2.4
    ow = max(2, S/40)
    W = int(h * 0.54 * k) + int(ow * k) * 2 + 10 * k
    im = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pad = int(ow * k)
    P = [(x * h * k + pad, y * h * k + pad) for x, y in ARROW_PTS]
    d.polygon(P, fill=NAVYD)
    d.line(P + [P[0]], width=max(2, int(ow * k * 2)), fill=NAVYD, joint='curve')
    d.polygon(P, fill=BLUE_ORIG)
    im = im.resize((W // k, W // k), Image.LANCZOS)
    paste_at(c, np.asarray(im).astype(np.float32), 1, 1)
    return finish(c), (0, 0)

def compose_busy_static(S):
    c = girl_canvas(S, 0.98, 0.01, 0.01)
    if S >= 48:
        paste_center(c, heart_glyph(S*0.16, max(1, S/120)), 0.12, 0.12)
        paste_center(c, star4_glyph(S*0.15, max(1, S/130)), 0.84, 0.10)
    return finish(c), (S//2, S//2)

def compose_app_static(S):
    c = girl_canvas(S, 0.84, 0.08, 0.12)
    paste_center(c, star4_glyph(S*0.34, max(2, S/44)), 0.86, 0.14)
    return finish(c), (S//2, S//2)

def compose_no(S):
    c = girl_canvas(S, 0.86, 0.07, 0.07, sweat=True)
    paste_center(c, crystal_barrier_glyph(S*0.96, max(3, S/26)), 0.5, 0.5)
    return finish(c), (S//2, S//2)

def compose_cross(S):
    c = np.zeros((S, S, 4), np.float32)
    paste_center(c, reticle_cross_glyph(S*0.94, max(2, S/44)), 0.5, 0.5)
    return finish(c, 0.55), (S//2, S//2)

def compose_ibeam(S):
    c = peek_canvas(S, 0.52, 0.50, 0.44)
    paste_center(c, ibeam_glyph(S*0.50, max(2, S/56)), 0.42, 0.5)
    if S >= 48:
        paste_center(c, heart_glyph(S*0.18, max(1, S/110)), 0.80, 0.14)
    return finish(c), (int(S*0.42), S//2)

def compose_pen(S):
    c = peek_canvas(S, 0.52, 0.50, 0.44)
    g = stylus_glyph(S*0.84, max(2, S/40))
    px = int(S*0.38 - g.shape[1]/2); py = int(S*0.38 - g.shape[0]/2)
    paste_at(c, g, px, py)
    ys, xs = np.where(g[..., 3] > 127)
    i = int(np.argmin(xs + ys))
    hx = int(min(max(0, px + xs[i]), S-1)); hy = int(min(max(0, py + ys[i]), S-1))
    return finish(c), (hx, hy)

def compose_up(S):
    c = peek_canvas(S, 0.52, 0.52, 0.44)
    g = up_arrow_glyph(S*0.84, max(2, S/40))
    paste_at(c, g, S//2 - g.shape[1]//2, 1)
    return finish(c, 0.55), (S//2, 1)

def compose_dir(angle):
    def f(S):
        c = np.zeros((S, S, 4), np.float32)
        paste_center(c, double_arrow_glyph(S*0.94, angle, max(2, S/44)), 0.5, 0.5)
        return finish(c, 0.55), (S//2, S//2)
    return f

def compose_sizeall(S):
    c = np.zeros((S, S, 4), np.float32)
    paste_center(c, compass_4way_glyph(S*0.94, max(2, S/44)), 0.5, 0.5)
    return finish(c, 0.55), (S//2, S//2)

# ---------------- 动画指针 (.ani) 渲染器 ----------------
def rotate_around(g, deg, cx, cy):
    M = cv2.getRotationMatrix2D((cx, cy), deg, 1.0)
    return cv2.warpAffine(g, M, (g.shape[1], g.shape[0]), flags=cv2.INTER_LANCZOS4, borderValue=0)

def anim_busy_frame(S, i, n_frames=16):
    """忙：大肥鱼呼吸浮动 + 环绕星轨 + 心动微动"""
    t = i / float(n_frames)
    bob_y = round(math.sin(t * 2 * math.pi) * max(1.0, S * 0.035))
    gy = 0.02 + bob_y / float(S)
    c = girl_canvas(S, 0.94, 0.03, gy)
    orbit_ang = t * 2 * math.pi
    star_x = 0.5 + math.cos(orbit_ang) * 0.36
    star_y = 0.5 + math.sin(orbit_ang) * 0.30 - 0.08
    star_g = star4_glyph(S*0.20, max(1, S/110))
    star_g = rotate_around(star_g, t * 180.0, star_g.shape[1]/2, star_g.shape[0]/2)
    paste_center(c, star_g, star_x, star_y)
    heart_scale = 0.14 + 0.02 * math.sin(t * 2 * math.pi + 1.2)
    paste_center(c, heart_glyph(S*heart_scale, max(1, S/130)), 0.12, 0.14)
    return finish(c), (S//2, S//2)

def anim_appstart_frame(S, i, n_frames=16):
    """后台运行：原版风格箭头稳定点击 + 大肥鱼呼吸 + 旋转星曜徽章"""
    t = i / float(n_frames)
    ow = max(2, S/30) if S < 48 else max(2, S/28)
    bob_y = round(math.sin(t * 2 * math.pi) * max(1.0, S * 0.03))
    gy = 0.12 + bob_y / float(S)
    c = girl_canvas(S, 0.84, 0.08, gy)
    # 原版纯净浅蓝箭头在 (0, 0)
    k = 4; h = S/1.8; W = int(h * 0.54 * k) + int(ow * k) * 2 + 10 * k
    im = Image.new('RGBA', (W, W), (0, 0, 0, 0)); d = ImageDraw.Draw(im); pad = int(ow * k)
    P = [(x * h * k + pad, y * h * k + pad) for x, y in ARROW_PTS]
    d.polygon(P, fill=NAVYD)
    d.line(P + [P[0]], width=max(2, int(ow * k * 2)), fill=NAVYD, joint='curve')
    d.polygon(P, fill=BLUE_ORIG)
    im = im.resize((W // k, W // k), Image.LANCZOS)
    paste_at(c, np.asarray(im).astype(np.float32), 1 - int(ow), 1 - int(ow))
    # 旋转星曜
    star_g = star4_glyph(S*0.30, max(2, S/44))
    star_rot = rotate_around(star_g, t * 360.0, star_g.shape[1]/2, star_g.shape[0]/2)
    paste_center(c, star_rot, 0.86, 0.14)
    return finish(c), (0, 0)

# ---------------- CUR / ANI 文件写入器 ----------------
def bmp_entry(px):
    s = px.shape[0]
    bi = struct.pack('<IiiHHIIiiII', 40, s, s*2, 1, 32, 0, s*s*4 + ((s+31)//32*4)*s, 0, 0, 0, 0)
    bgra = px[..., [2, 1, 0, 3]]
    return bi + bgra[::-1].tobytes() + b'\x00' * (((s+31)//32*4) * s)

def write_cur(path, sizes, compose_fn):
    frames = []
    for s in sizes:
        px, hot = compose_fn(s)
        data = bmp_entry(px)
        frames.append(((s % 256, s % 256, 0, 0, hot[0], hot[1], len(data)), data))
    offset = 6 + 16 * len(frames)
    body = b''
    for e, d in frames:
        body += struct.pack('<BBBBHHII', e[0], e[1], e[2], e[3], e[4], e[5], len(d), offset)
        offset += len(d)
    with open(path, 'wb') as f:
        f.write(struct.pack('<HHH', 0, 2, len(frames)) + body + b''.join(d for _, d in frames))
    print(f'  [✓] 生成静态指针: {path}')

def write_ani(path, S, frame_fn, n=16, jif=5):
    icons = []
    for i in range(n):
        px, hot = frame_fn(S, i, n)
        data = bmp_entry(px)
        entry = struct.pack('<BBBBHHII', S % 256, S % 256, 0, 0, hot[0], hot[1], len(data), 22)
        icons.append(struct.pack('<HHH', 0, 2, 1) + entry + data)
    def chunk(tag, payload):
        pad = b'\00' if len(payload) % 2 else b''
        return tag + struct.pack('<I', len(payload)) + payload + pad
    anih = struct.pack('<9I', 36, n, n, S, S, 0, 0, jif, 1)
    seq = b''.join(struct.pack('<I', i) for i in range(n))
    fram = b''.join(chunk(b'icon', ic) for ic in icons)
    riff = b'ACON' + chunk(b'anih', anih) + chunk(b'seq ', seq) + chunk(b'LIST', b'fram' + fram)
    with open(path, 'wb') as f:
        f.write(b'RIFF' + struct.pack('<I', len(riff)) + riff)
    print(f'  [★] 生成动态指针: {path}')

SIZE_MAIN = [256, 192, 128, 96, 64, 48, 32]
SIZE_STD  = [192, 128, 96, 64, 48, 32]

CURSORS = {
    'feiyu_arrow.cur':    (compose_arrow,          SIZE_MAIN),
    'feiyu_hand.cur':     (compose_link,           SIZE_MAIN),
    'feiyu_help.cur':     (compose_help,           SIZE_STD),
    'feiyu_busy.cur':     (compose_busy_static,    SIZE_MAIN),
    'feiyu_appstart.cur': (compose_app_static,     SIZE_STD),
    'feiyu_no.cur':       (compose_no,             SIZE_STD),
    'feiyu_cross.cur':    (compose_cross,          SIZE_STD),
    'feiyu_ibeam.cur':    (compose_ibeam,          SIZE_STD),
    'feiyu_pen.cur':      (compose_pen,            SIZE_STD),
    'feiyu_up.cur':       (compose_up,             SIZE_STD),
    'feiyu_sizens.cur':   (compose_dir(-90),       SIZE_STD),
    'feiyu_sizewe.cur':   (compose_dir(0),         SIZE_STD),
    'feiyu_sizenwse.cur': (compose_dir(45),        SIZE_STD),
    'feiyu_sizenesw.cur': (compose_dir(-45),       SIZE_STD),
    'feiyu_sizeall.cur':  (compose_sizeall,        SIZE_STD),
    'feiyu_pin.cur':      (compose_pin,            SIZE_MAIN),
    'feiyu_person.cur':   (compose_person,         SIZE_MAIN),
}

def main():
    print("="*60)
    print("✨ 开始生成 大肥鱼指针 · FeiyuCursor 全套鼠标指针方案 ✨")
    print("="*60)

    # 1. 生成所有多尺寸静态 .cur 指针
    for name, (comp, sizes) in CURSORS.items():
        # 如果已经存在原版 arrow，我们直接使用原版文件以确保100%原味
        # 重新生成带饱满爱心的原版经典正常选择
        write_cur(name, sizes, comp)

    # 2. 生成丝滑高品质动态 .ani 指针
    write_ani('feiyu_busy.ani', 64, anim_busy_frame, n=16, jif=5)
    write_ani('feiyu_appstart.ani', 64, anim_appstart_frame, n=16, jif=5)

    # 3. 生成高清预览展示大图 (效果预览.png)
    print("正在生成高颜值展示画板 效果预览.png ...")
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 22)
    font_sub = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 14)
    font_title = ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc', 32)

    items = [
        ('feiyu_arrow.cur',    '正常选择 (原版经典)', 'Normal Select (Original)'),
        ('feiyu_hand.cur',     '链接选择 (星芒触控)', 'Link Select'),
        ('feiyu_busy.cur',     '忙 (动态呼吸星轨)', 'Busy / Wait'),
        ('feiyu_appstart.cur', '后台运行 (动态星曜)', 'Working in Background'),
        ('feiyu_no.cur',       '不可用 (结界护盾)', 'Unavailable'),
        ('feiyu_cross.cur',    '精确选择 (星轨准星)', 'Precision Select'),
        ('feiyu_ibeam.cur',    '文本选择 (双色高亮)', 'Text Select'),
        ('feiyu_help.cur',     '帮助选择 (气泡徽章)', 'Help Select'),
        ('feiyu_pen.cur',      '手写笔 (数位星笔)', 'Handwriting'),
        ('feiyu_up.cur',       '备用选择 (升腾星矢)', 'Alternate Select'),
        ('feiyu_sizens.cur',   '上下调整 (星核胶囊)', 'Vertical Resize'),
        ('feiyu_sizewe.cur',   '左右调整 (星核胶囊)', 'Horizontal Resize'),
        ('feiyu_sizenwse.cur', '对角调整 1 (星核胶囊)', 'Diagonal Resize 1'),
        ('feiyu_sizenesw.cur', '对角调整 2 (星核胶囊)', 'Diagonal Resize 2'),
        ('feiyu_sizeall.cur',  '移动 (星核罗盘)', 'Move / All Direction'),
        ('feiyu_pin.cur',      '位置选择 (心曜标)', 'Location Select'),
        ('feiyu_person.cur',   '个人选择 (金冠徽章)', 'Person Select'),
    ]

    cell_w, cell_h = 240, 310
    cols = 5
    rows = (len(items) + cols - 1) // cols
    header_h = 130
    total_w = cell_w * cols + 60
    total_h = header_h + cell_h * rows + 50

    sheet = Image.new('RGB', (total_w, total_h), (245, 248, 253))
    dd = ImageDraw.Draw(sheet)

    dd.rectangle([0, 0, total_w, header_h], fill=(235, 242, 252))
    dd.text((40, 28), "🐋 大肥鱼指针 · FeiyuCursor (DeepSeek 肥鱼娘全套美化方案)", fill=(34, 62, 128), font=font_title)
    dd.text((42, 78), "正常选择原汁原味 · 动态大肥鱼呼吸星轨 · 17项完备覆盖 · Windows 11 高清自适应", fill=(100, 130, 175), font=font)

    for i, (f, label, sub) in enumerate(items):
        im = Image.open(f)
        fr = im.convert('RGBA').resize((160, 160), Image.LANCZOS)
        cx = (i % cols) * cell_w + 30
        cy = header_h + (i // cols) * cell_h + 20

        dd.rounded_rectangle([cx, cy, cx + cell_w - 20, cy + cell_h - 25], radius=16, fill=(255, 255, 255), outline=(225, 235, 248), width=1)
        sheet.paste(fr, (cx + (cell_w - 20 - 160)//2, cy + 20), fr)
        dd.text((cx + 15, cy + 195), label, fill=(38, 55, 95), font=font)
        dd.text((cx + 15, cy + 230), sub, fill=(130, 150, 180), font=font_sub)

    sheet.save('效果预览.png')
    print("  [✓] 预览大图已更新: 效果预览.png")
    print("="*60)
    print("🎉 大肥鱼指针 全套生成完毕！")
    print("="*60)

if __name__ == '__main__':
    main()
