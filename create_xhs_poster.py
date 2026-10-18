# -*- coding: utf-8 -*-
"""
生成小红书高颜值 3:4 竖屏种草海报图 (1080 x 1440)
展示「大肥鱼指针 · FeiyuCursor」全套美化效果
"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1440
canvas = Image.new('RGB', (W, H), (243, 246, 252))
d = ImageDraw.Draw(canvas)

# 1. 柔和马卡龙氛围渐变底色
grad = np.zeros((H, W, 3), dtype=np.uint8)
for y in range(H):
    t = y / float(H)
    # 顶部温润淡紫蓝 (236, 242, 255) -> 中部清澈奶蓝 (240, 248, 255) -> 底部柔和粉白 (253, 248, 252)
    if t < 0.5:
        sub_t = t / 0.5
        r = int(232 * (1 - sub_t) + 240 * sub_t)
        g = int(240 * (1 - sub_t) + 247 * sub_t)
        b = int(255 * (1 - sub_t) + 255 * sub_t)
    else:
        sub_t = (t - 0.5) / 0.5
        r = int(240 * (1 - sub_t) + 252 * sub_t)
        g = int(247 * (1 - sub_t) + 246 * sub_t)
        b = int(255 * (1 - sub_t) + 252 * sub_t)
    grad[y, :] = [r, g, b]

canvas = Image.fromarray(grad)
d = ImageDraw.Draw(canvas)

# 背景装饰光晕球
glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
dg = ImageDraw.Draw(glow)
dg.ellipse([650, -80, 1150, 420], fill=(205, 230, 255, 120))
dg.ellipse([-100, 700, 450, 1250], fill=(255, 225, 238, 90))
dg.ellipse([700, 1000, 1180, 1480], fill=(215, 238, 255, 100))
glow = glow.filter(ImageFilter.GaussianBlur(65))
canvas.paste(glow, (0, 0), glow)
d = ImageDraw.Draw(canvas)

# 字体加载
font_badge = ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc', 26)
font_title = ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc', 60)
font_sub   = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 30)
font_tag   = ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc', 22)
font_card_t= ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc', 32)
font_card_d= ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 22)
font_mini_t= ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc', 26)
font_mini_d= ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 20)

# 2. 顶部胶囊标签
tag_txt = "💻 Windows 11 / 10 桌面美化 · 开源免费"
tag_w = int(d.textlength(tag_txt, font=font_badge)) + 48
tag_x, tag_y = (W - tag_w) // 2, 70
d.rounded_rectangle([tag_x, tag_y, tag_x + tag_w, tag_y + 50], radius=25, fill=(255, 255, 255), outline=(210, 228, 252), width=2)
d.text((tag_x + 24, tag_y + 10), tag_txt, fill=(40, 90, 185), font=font_badge)

# 3. 主副标题
t1 = "把 DeepSeek 大肥鱼"
t2 = "做成你的鼠标指针啦！🐋✨"
d.text(((W - d.textlength(t1, font=font_title)) // 2, 140), t1, fill=(25, 45, 95), font=font_title)
d.text(((W - d.textlength(t2, font=font_title)) // 2, 215), t2, fill=(35, 80, 180), font=font_title)

sub_txt = "纯净贴纸风 · 16帧呼吸动效 · 17项完备覆盖 · 一键极速换装"
d.text(((W - d.textlength(sub_txt, font=font_sub)) // 2, 295), sub_txt, fill=(95, 120, 160), font=font_sub)

# 4. 主卡片区 (双焦点卡片：正常选择 + 动态忙碌)
card_y = 360
card_h = 430
card_w = 465

def draw_glass_card(x, y, w, h, fill_rgb=(255, 255, 255), outline_rgb=(220, 235, 252), rad=28):
    # 投影
    sh = Image.new('RGBA', (w + 40, h + 40), (0, 0, 0, 0))
    dsh = ImageDraw.Draw(sh)
    dsh.rounded_rectangle([20, 20, w + 20, h + 20], radius=rad, fill=(30, 50, 90, 35))
    sh = sh.filter(ImageFilter.GaussianBlur(15))
    canvas.paste(sh, (x - 20, y - 10), sh)
    # 实体卡片
    d.rounded_rectangle([x, y, x + w, y + h], radius=rad, fill=fill_rgb, outline=outline_rgb, width=2)

# 左焦点卡片：正常选择
draw_glass_card(55, card_y, card_w, card_h)
# 贴入 feiyu_arrow.cur (放大为 220x220)
arrow_im = Image.open('feiyu_arrow.cur').convert('RGBA').resize((210, 210), Image.LANCZOS)
canvas.paste(arrow_im, (55 + (card_w - 210)//2, card_y + 35), arrow_im)

# 标签小药丸
badge1 = "最爱原版纯净蓝"
bw1 = int(d.textlength(badge1, font=font_tag)) + 24
d.rounded_rectangle([55 + (card_w - bw1)//2, card_y + 265, 55 + (card_w + bw1)//2, card_y + 300], radius=15, fill=(235, 245, 255), outline=(160, 205, 255), width=1)
d.text((55 + (card_w - bw1)//2 + 12, card_y + 270), badge1, fill=(28, 90, 195), font=font_tag)

d.text((55 + 40, card_y + 320), "正常选择 · 经典纯净", fill=(25, 45, 90), font=font_card_t)
d.text((55 + 35, card_y + 370), "奶蓝小三角+探头，完全不遮挡视野", fill=(110, 130, 160), font=font_card_d)

# 右焦点卡片：动态忙碌
draw_glass_card(560, card_y, card_w, card_h)
busy_im = Image.open('feiyu_busy.cur').convert('RGBA').resize((210, 210), Image.LANCZOS)
canvas.paste(busy_im, (560 + (card_w - 210)//2, card_y + 35), busy_im)

badge2 = "16帧星轨呼吸动效"
bw2 = int(d.textlength(badge2, font=font_tag)) + 24
d.rounded_rectangle([560 + (card_w - bw2)//2, card_y + 265, 560 + (card_w + bw2)//2, card_y + 300], radius=15, fill=(255, 242, 246), outline=(255, 185, 205), width=1)
d.text((560 + (card_w - bw2)//2 + 12, card_y + 270), badge2, fill=(225, 65, 120), font=font_tag)

d.text((560 + 40, card_y + 320), "忙碌/后台 · 治愈动画", fill=(25, 45, 90), font=font_card_t)
d.text((560 + 35, card_y + 370), "大肥鱼呼吸沉浮，环绕金色星曜", fill=(110, 130, 160), font=font_card_d)

# 5. 精选功能指针小卡片网格 (4列 x 1排 或 2x2)
grid_y = 825
grid_w = 222
grid_h = 245
spacing = 24
left_margin = 55

mini_items = [
    ('feiyu_hand.cur',  '链接选择', '星芒触控微光', (235, 248, 255), (170, 215, 255), (30, 100, 200)),
    ('feiyu_no.cur',    '不可用',   '结界护盾+汗滴', (255, 242, 245), (255, 190, 205), (220, 60, 95)),
    ('feiyu_cross.cur', '精确选择', '1px星轨准星',  (240, 245, 255), (185, 205, 255), (45, 80, 185)),
    ('feiyu_ibeam.cur', '文本选择', '高对比双色工字', (242, 248, 255), (180, 215, 255), (35, 95, 190))
]

for i, (fname, title, desc, bg_c, bord_c, text_c) in enumerate(mini_items):
    gx = left_margin + i * (grid_w + spacing)
    draw_glass_card(gx, grid_y, grid_w, grid_h, fill_rgb=(255, 255, 255), outline_rgb=(225, 238, 252), rad=20)
    
    # 指针图标
    fim = Image.open(fname).convert('RGBA').resize((115, 115), Image.LANCZOS)
    canvas.paste(fim, (gx + (grid_w - 115)//2, grid_y + 20), fim)

    # 徽章小标签
    bw = int(d.textlength(title, font=font_tag)) + 16
    d.rounded_rectangle([gx + (grid_w - bw)//2, grid_y + 145, gx + (grid_w + bw)//2, grid_y + 175], radius=10, fill=bg_c, outline=bord_c, width=1)
    d.text((gx + (grid_w - bw)//2 + 8, grid_y + 148), title, fill=text_c, font=font_tag)

    d.text((gx + (grid_w - d.textlength(desc, font=font_mini_d))//2, grid_y + 195), desc, fill=(110, 130, 160), font=font_mini_d)

# 6. 更多指针微缩横条 (展示其余手写、缩放等)
bar_y = 1095
bar_h = 105
draw_glass_card(55, bar_y, 970, bar_h, fill_rgb=(255, 255, 255), outline_rgb=(225, 238, 252), rad=22)

# 横条左边文字
d.text((85, bar_y + 25), "全套 17 款指针完备覆盖", fill=(30, 50, 95), font=font_mini_t)
d.text((85, bar_y + 60), "手写笔 / 缩放双向箭头 / 全向移动 / 位置个人", fill=(120, 140, 170), font=font_mini_d)

# 横条右边并排贴 6 个小指针
sub_cursors = ['feiyu_pen.cur', 'feiyu_sizens.cur', 'feiyu_sizewe.cur', 'feiyu_sizeall.cur', 'feiyu_pin.cur', 'feiyu_person.cur']
for idx, sc in enumerate(sub_cursors):
    sim = Image.open(sc).convert('RGBA').resize((68, 68), Image.LANCZOS)
    canvas.paste(sim, (530 + idx * 74, bar_y + 18), sim)

# 7. 底部极速安装指南横幅 (吸睛渐变)
bot_y = 1225
bot_h = 145
# 渐变胶囊
bot_grad = np.zeros((bot_h, 970, 3), dtype=np.uint8)
for x in range(970):
    t = x / 970.0
    r = int(35 * (1 - t) + 55 * t)
    g = int(85 * (1 - t) + 130 * t)
    b = int(210 * (1 - t) + 245 * t)
    bot_grad[:, x] = [r, g, b]

bot_im = Image.fromarray(bot_grad)
# 裁切圆角
mask_bot = Image.new('L', (970, bot_h), 0)
ImageDraw.Draw(mask_bot).rounded_rectangle([0, 0, 970, bot_h], radius=28, fill=255)
canvas.paste(bot_im, (55, bot_y), mask_bot)

d = ImageDraw.Draw(canvas)
d.text((95, bot_y + 30), "🚀 傻瓜式一键换装 · 解压后双击即可应用！", fill=(255, 255, 255), font=font_card_t)
d.text((98, bot_y + 80), "运行【一键安装并应用.bat】秒生效 | 附带全套 INF 安装脚本 | 32-256px 无损高清", fill=(210, 235, 255), font=font_card_d)

# 保存
poster_path = '小红书演示图.png'
canvas.save(poster_path, quality=95)
print('小红书演示图.png 生成成功！尺寸:', canvas.size)
