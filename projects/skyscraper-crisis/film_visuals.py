"""Narration-aligned paper collage, documentary inserts, and financial diagrams."""
from pathlib import Path
from functools import lru_cache
import bisect
import json
import math
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from full_film import FPS, FFMPEG, PRODUCTION, dump, plan, probe, write_srt

W, H = 1280, 720
RED = (164, 36, 39)
INK = (28, 28, 29)
MUTED = (101, 101, 103)
PAPER = (230, 230, 228)
PALE = (199, 199, 198)
FONT = os.environ.get("SC_FONT", "/System/Library/Fonts/STHeiti Medium.ttc")
SERIF = os.environ.get("SC_SERIF_FONT", "/System/Library/Fonts/Supplemental/Songti.ttc")
LATIN = os.environ.get("SC_LATIN_FONT", "/System/Library/Fonts/Supplemental/Arial.ttf")


def ease(p):
    p = max(0, min(1, p))
    return 1 - (1 - p) ** 3


@lru_cache(maxsize=32)
def font(size, serif=False, latin=False):
    return ImageFont.truetype(LATIN if latin else SERIF if serif else FONT, size)


@lru_cache(maxsize=1024)
def text_image(value, size, color, serif, latin):
    face = font(size, serif, latin)
    left, top, right, bottom = face.getbbox(value)
    image = Image.new("RGBA", (max(1, right - left + 6), max(1, bottom - top + 6)))
    ImageDraw.Draw(image).text((3 - left, 3 - top), value, font=face, fill=(*color, 255))
    return image


def text(image, xy, value, size=30, color=INK, center=False, serif=False, latin=False, max_width=None):
    value = str(value)
    if max_width:
        while font(size, serif, latin).getlength(value) > max_width and size > 16:
            size -= 1
    item = text_image(value, size, color, serif, latin)
    x, y = xy
    if center:
        x -= item.width / 2
    image.paste(item, (round(x), round(y)), item)


def line(image, points, fill=RED, width=3):
    ImageDraw.Draw(image).line(points, fill=fill, width=width, joint="curve")


def arrow(image, start, end, fill=RED, width=3):
    line(image, [start, end], fill, width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    d = 11
    pts = [end, (end[0] - d * math.cos(angle - .45), end[1] - d * math.sin(angle - .45)),
           (end[0] - d * math.cos(angle + .45), end[1] - d * math.sin(angle + .45))]
    ImageDraw.Draw(image).polygon(pts, fill=fill)


def paper(dark=False):
    rng = np.random.default_rng(20261024 + dark)
    base = 29 if dark else 230
    values = np.clip(base + rng.normal(0, 1.5, (H, W)), 0, 255).astype("uint8")
    image = Image.fromarray(values).convert("RGB")
    draw = ImageDraw.Draw(image)
    for y in range(4, H, 8):
        for x in range(4 + y % 16, W, 8):
            draw.point((x, y), fill=(43, 43, 43) if dark else (215, 215, 213))
    return image


def person(image, x, y, scale=1, color=INK):
    draw = ImageDraw.Draw(image)
    r = 12 * scale
    draw.ellipse((x - r, y, x + r, y + 2 * r), fill=color)
    draw.polygon([(x - 18 * scale, y + 28 * scale), (x + 18 * scale, y + 28 * scale),
                  (x + 23 * scale, y + 75 * scale), (x - 23 * scale, y + 75 * scale)], fill=color)
    line(image, [(x - 10 * scale, y + 70 * scale), (x - 10 * scale, y + 108 * scale)], color, max(2, int(8 * scale)))
    line(image, [(x + 10 * scale, y + 70 * scale), (x + 10 * scale, y + 108 * scale)], color, max(2, int(8 * scale)))


def office(image, x, base, width=100, height=210, occupied=1, progress=1, color=INK):
    draw = ImageDraw.Draw(image)
    top = base - height * max(.05, progress)
    draw.rectangle((x, top, x + width, base), outline=color, width=3)
    for yy in range(round(top + 12), round(base - 8), 24):
        for xx in range(round(x + 10), round(x + width - 8), 18):
            fill = color if ((xx + yy) % 100) / 100 < occupied else PALE
            draw.rectangle((xx, yy, xx + 8, yy + 10), fill=fill)
    line(image, [(x - 15, base + 5), (x + width + 15, base + 5)], color, 2)


def crane(image, x, y, size=1):
    line(image, [(x, y + 130 * size), (x, y)], INK, 3)
    line(image, [(x - 45 * size, y + 14 * size), (x + 105 * size, y + 14 * size)], INK, 4)
    line(image, [(x - 30 * size, y + 14 * size), (x, y), (x + 80 * size, y + 14 * size)], INK, 2)
    line(image, [(x + 80 * size, y + 14 * size), (x + 80 * size, y + 80 * size)], RED, 2)


def page(image, x, y, width=250, height=280, heading="借款合同", stamp=None):
    draw = ImageDraw.Draw(image)
    draw.rectangle((x, y, x + width, y + height), fill=(241, 241, 238), outline=INK, width=2)
    text(image, (x + 20, y + 18), heading, 30, max_width=width - 40)
    line(image, [(x + 20, y + 64), (x + width - 20, y + 64)], INK, 2)
    for n in range(4):
        line(image, [(x + 22, y + 98 + n * 31), (x + width - 28 - (n % 2) * 36, y + 98 + n * 31)], PALE, 2)
    if stamp:
        text(image, (x + width / 2, y + height - 65), stamp, 32, RED, center=True, max_width=width - 26)


def calendar(image, x, y, label="到期日", value="续借"):
    draw = ImageDraw.Draw(image)
    draw.rectangle((x, y, x + 230, y + 255), fill=(242, 242, 239), outline=INK, width=3)
    draw.rectangle((x, y, x + 230, y + 52), fill=INK)
    text(image, (x + 115, y + 12), label, 28, (242, 242, 239), center=True)
    text(image, (x + 115, y + 111), value, 54, RED, center=True, max_width=210)
    for xx in [x + 45, x + 185]:
        line(image, [(xx, y - 10), (xx, y + 15)], INK, 6)


def bank(image, x, y, width=160):
    draw = ImageDraw.Draw(image)
    draw.polygon([(x - 8, y + 44), (x + width / 2, y), (x + width + 8, y + 44)], fill=INK)
    for xx in np.linspace(x + 16, x + width - 25, 4):
        draw.rectangle((xx, y + 55, xx + 12, y + 155), fill=INK)
    draw.rectangle((x, y + 160, x + width, y + 175), fill=INK)
    text(image, (x + width / 2, y + 190), "贷款机构", 25, center=True)


def tower(image, x, base, height=370, kind="artdeco"):
    draw = ImageDraw.Draw(image)
    if kind == "burj":
        widths = [120, 98, 80, 63, 45, 28, 12]
        for i, width in enumerate(widths):
            bottom = base - height * i / 8
            top = base - height * (i + 1) / 8
            draw.rectangle((x - width / 2, top, x + width / 2, bottom), fill=(75 + 10 * i,) * 3)
        line(image, [(x, base - height * 7 / 8), (x, base - height - 25)], INK, 3)
    else:
        for i, width in enumerate([128, 102, 77, 50, 22]):
            bottom = base - height * i / 6
            top = base - height * (i + 1) / 6
            draw.rectangle((x - width / 2, top, x + width / 2, bottom), fill=(70 + 12 * i,) * 3)
            for xx in range(round(x - width / 2 + 8), round(x + width / 2 - 5), 14):
                line(image, [(xx, top + 5), (xx, bottom - 4)], (188, 188, 185), 3)
        line(image, [(x, base - height * 5 / 6), (x, base - height - 15)], INK, 4)


def flow(image, labels, p=1, y=365, start=165, spacing=310):
    for i, value in enumerate(labels):
        x = start + spacing * i
        if p * len(labels) >= i:
            text(image, (x, y - 6), value, 32, RED if i == len(labels) - 1 else INK, center=True, max_width=spacing - 45)
            text(image, (x, y + 55), f"0{i + 1}", 18, MUTED, center=True, latin=True)
        if i < len(labels) - 1:
            arrow(image, (x + spacing * .30, y + 12), (x + spacing * .67, y + 12), RED)


class Photos:
    def __init__(self, directory):
        path = directory / "motion.mp4"
        result = subprocess.run([
            FFMPEG, "-v", "error", "-i", str(path), "-vf",
            "fps=8,scale=832:468:force_original_aspect_ratio=increase,crop=832:468,format=gray",
            "-frames:v", "48", "-f", "rawvideo", "-pix_fmt", "gray", "-",
        ], check=True, capture_output=True)
        count = len(result.stdout) // (832 * 468)
        if count < 10:
            raise RuntimeError("The chapter motion insert could not be decoded.")
        self.frames = [
            Image.frombytes("L", (832, 468), result.stdout[i * 832 * 468:(i + 1) * 832 * 468]).convert("RGB")
            for i in range(count)
        ]

    def draw(self, image, box, progress, label="情境重建示意"):
        x, y, width, height = box
        index = min(len(self.frames) - 1, int(ease(progress) * (len(self.frames) - 1)))
        source = self.frames[index]
        zoom = 1 + .035 * max(0, min(1, progress))
        sw, sh = source.size
        source = source.crop(((sw - sw / zoom) / 2, (sh - sh / zoom) / 2,
                              (sw + sw / zoom) / 2, (sh + sh / zoom) / 2))
        fitted = ImageOps.fit(source, (round(width), round(height)), method=Image.Resampling.BILINEAR)
        image.paste(fitted, (round(x), round(y)))
        line(image, [(x, y + height + 4), (x + width, y + height + 4)], INK, 2)
        text(image, (x + 5, y + height - 26), label, 16, (241, 241, 238))


def subtitles_for(voice):
    subtitles = []
    for item in voice["paragraphs"]:
        body = item["text"]
        words = item["words"]
        positions = []
        plain = "".join(c for c in body if c.isalnum())
        cursor = 0
        for word in words:
            token = "".join(c for c in word["text"] if c.isalnum())
            location = plain.find(token, cursor) if token else cursor
            if location < 0:
                location = cursor
            positions.append((location, word["offset"] / 10000000, word["duration"] / 10000000))
            cursor = location + len(token)
        chunks = []
        chunk = ""
        for c in body:
            chunk += c
            if c in "，。？！；：" and len(chunk) >= 7 or len(chunk) >= 28:
                chunks.append(chunk)
                chunk = ""
        if chunk:
            if chunks and len(chunk) < 5 and len(chunks[-1]) + len(chunk) < 31:
                chunks[-1] += chunk
            else:
                chunks.append(chunk)
        offset = 0
        timed = []
        for chunk in chunks:
            location = offset
            offset += len("".join(c for c in chunk if c.isalnum()))
            exact = [p for p in positions if p[0] <= location]
            at = exact[-1][1] if exact else item["duration"] * location / max(1, len(plain))
            timed.append({"start": item["start"] + at, "text": chunk})
        for i, sub in enumerate(timed):
            sub["end"] = timed[i + 1]["start"] if i + 1 < len(timed) else item["end"]
            if sub["end"] > sub["start"]:
                subtitles.append(sub)
    return subtitles


def cash_bars(image, good, p):
    incoming = 5000 if good else 3500
    interest = 2400 if good else 3600
    baseline = 561
    for x, value, label, color in [(270, incoming, "净运营收入", INK), (680, interest, "年利息", RED)]:
        height = value / 5000 * 230 * ease(p * 2)
        ImageDraw.Draw(image).rectangle((x, baseline - height, x + 190, baseline), fill=color)
        text(image, (x + 95, baseline - height - 48), f"{value} 万", 40, color, center=True)
        text(image, (x + 95, 578), label, 24, center=True)
    line(image, [(205, baseline + 1), (980, baseline + 1)], MUTED, 2)
    if not good:
        text(image, (1045, 359), "缺口", 30, RED, center=True)
        text(image, (1045, 404), "100 万", 39, RED, center=True)


def draw_scene(image, mode, p, t, photos, chapter):
    draw = ImageDraw.Draw(image)
    q = ease(p * 2.4)
    if mode in {"photo", "plea", "substance"}:
        photos.draw(image, (65, 205, 806, 411), p)
        words = {
            "plea": ["再给一点", "时间", "谁来补钱？"],
            "substance": ["需求", "偿债", "现金流"],
        }.get(mode, {
            1: ["企业收缩", "工人失业", "银行承压"],
            2: ["股灾已发生", "工程才开始", "先后不能倒置"],
            3: ["贷款申请", "签署合同", "预测未来租金"],
            4: ["多家开发商", "同时开工", "争取同批租户"],
            5: ["施工继续", "市场已变", "不能立即退出"],
            6: ["租户减少", "现金变少", "债务仍到期"],
            7: ["查看证据", "检查反例", "接受数据检验"],
            8: ["实际租户", "真实租约", "使用与需求"],
        }[chapter])
        for i, value in enumerate(words):
            text(image, (1040, 280 + i * 90), value, 40 if i == 1 else 27, RED if i == 1 else INK, center=True)
    elif mode in {"opening", "height", "closing", "return"}:
        asset_path = ROOT / "assets/building-cutout.png"
        with Image.open(asset_path) as source:
            item = source.convert("RGBA")
            height = round(405 + 8 * p)
            item = item.resize((round(item.width * height / item.height), height), Image.Resampling.BILINEAR)
        image.paste(item, (895, 610 - item.height), item)
        text(image, (1110, 601), "建筑示意", 15, MUTED)
        if mode == "opening":
            text(image, (65, 260), "1931", 110, RED, latin=True)
            text(image, (70, 391), "纽约 · 帝国大厦", 42)
            text(image, (75, 465), "5 月 1 日 / 正式开幕", 27, MUTED)
        elif mode == "height":
            text(image, (75, 270), "100+", 132, RED, latin=True)
            text(image, (80, 431), "楼层向上，技术向前", 36)
            line(image, [(805, 590), (805, 590 - 350 * q)], RED, 3)
            for yy in range(250, 600, 35):
                line(image, [(795, yy), (815, yy)], MUTED, 1)
        elif mode == "return":
            page(image, 80, 240, 350, 330, "同一个项目", "借款 6 亿元")
            arrow(image, (485, 401), (790, 401))
        else:
            calendar(image, 75, 275, "下一笔利息", "到期")
            text(image, (365, 324), "未来，仍待验证", 38)
            text(image, (365, 397), "义务，已有日期", 38, RED)
    elif mode == "contrast":
        photos.draw(image, (65, 252, 610, 330), p)
        tower(image, 990, 581, 310)
        text(image, (370, 202), "街道与就业", 29, center=True)
        text(image, (990, 202), "高度纪录", 29, RED, center=True)
        text(image, (990, 602), "建筑示意", 15, MUTED, center=True)
    elif mode == "dubai":
        tower(image, 1090, 600, 345, "burj")
        text(image, (70, 250), "2009.11", 66, RED, latin=True)
        text(image, (75, 331), "迪拜世界债务风波", 34)
        arrow(image, (145, 391), (145, 439))
        text(image, (70, 459), "2010.01.04", 58, INK, latin=True)
        text(image, (75, 532), "哈利法塔正式开幕", 34)
        text(image, (1050, 607), "建筑示意", 15, MUTED, center=True)
    elif mode in {"question", "index", "no_prediction", "limit", "correct"}:
        photos.draw(image, (70, 250, 500, 320), p)
        if mode == "correct":
            text(image, (900, 290), "先后顺序", 54, center=True)
            text(image, (900, 387), "不能倒置", 59, RED, center=True)
        elif mode in {"no_prediction", "limit"}:
            text(image, (900, 285), "关联", 62, center=True)
            text(image, (900, 381), "≠", 72, RED, center=True)
            text(image, (900, 485), "确定预测", 52, center=True)
        else:
            text(image, (900, 263), "?", 220, RED, center=True, latin=True)
            text(image, (900, 519), "需要检验", 34, center=True)
    elif mode in {"ledger", "certainty", "obligation"}:
        page(image, 135, 242, 330, 330, "借款合同", "必须兑现")
        page(image, 785, 242, 330, 330, "未来租金", "仍是预测")
        arrow(image, (520, 400), (730, 400))
        if mode in {"certainty", "obligation"}:
            text(image, (624, 485), "风险在这里", 26, RED, center=True)
    elif mode in {"dates", "windows"}:
        line(image, [(160, 400), (1120, 400)], INK, 3)
        for x, year, caption in [(300, "1929.10", "股市崩盘"), (960, "1930.03", "帝国大厦开工")]:
            draw.ellipse((x - 7, 393, x + 7, 407), fill=RED)
            text(image, (x, 288), year, 55, RED, center=True, latin=True)
            text(image, (x, 451), caption, 32, center=True)
        if mode == "windows":
            for i in range(3):
                x = 150 + i * 300 + int(100 * p)
                draw.rectangle((x, 360, x + 245, 430), outline=RED, width=2)
            text(image, (640, 556), "检验范围不能随案例临时改变", 29, MUTED, center=True)
    elif mode in {"stages", "costs", "blueprint", "decision"}:
        labels = ["宣布", "开工", "封顶", "营业"]
        if mode == "costs":
            labels = ["拿地", "建造", "出租", "还款"]
        for i, x in enumerate([185, 485, 785, 1085]):
            if i == 0:
                page(image, x - 65, 280, 130, 170, "项目", "计划")
            elif i == 1:
                crane(image, x - 20, 296, 1.1)
            elif i == 2:
                office(image, x - 50, 465, 100, 185, progress=q)
            else:
                person(image, x, 307, 1.25)
            text(image, (x, 509), labels[i], 32, center=True)
            if i < 3:
                arrow(image, (x + 95, 391), (x + 205, 391))
        if mode in {"blueprint", "decision"}:
            text(image, (640, 581), "今天的决定，要由未来的需求兑现", 27, RED, center=True)
    elif mode == "loan":
        page(image, 100, 238, 330, 340, "借款合同", "本金 6 亿元")
        text(image, (835, 252), "6 亿 × 4%", 66, RED, center=True)
        text(image, (835, 354), "=", 48, center=True, latin=True)
        text(image, (835, 433), "2400 万元 / 年", 57, center=True)
    elif mode in {"cash_good", "cash_bad"}:
        cash_bars(image, mode == "cash_good", p)
    elif mode == "income":
        office(image, 230, 538, 150, 255)
        for k in range(5):
            person(image, 180 + k * 58, 563, .42)
        arrow(image, (485, 403), (700, 403))
        text(image, (960, 240), "净运营收入", 35, center=True)
        text(image, (960, 313), "5000 万元 / 年", 46, RED, center=True)
        text(image, (960, 432), "租金收入", 32, center=True)
        text(image, (960, 493), "－ 日常运营费用", 29, MUTED, center=True)
    elif mode in {"income_drop", "demand_shift", "mismatch"}:
        before, after = ("5000 万", "3500 万") if mode == "income_drop" else ("预计租户", "实际租户")
        for i, x in enumerate([320, 930]):
            office(image, x - 70, 538, 140, 238, occupied=1 if i == 0 else .35)
            n = 6 if i == 0 else 3
            for k in range(n):
                person(image, x - 145 + k * 56, 562, .44, INK if i == 0 else RED)
            text(image, (x, 226), before if i == 0 else after, 43, RED if i else INK, center=True)
        arrow(image, (545, 403), (710, 403))
    elif mode in {"financing", "fixed", "refinance", "check_maturity"}:
        if mode == "refinance":
            for x, rate, interest in [(130, "4%", "2400 万 / 年"), (825, "6%", "3600 万 / 年")]:
                page(image, x, 239, 310, 330, "6 亿元借款", rate)
                text(image, (x + 155, 590), interest, 30, RED, center=True)
            calendar(image, 525, 280, "贷款到期", "续借")
        elif mode == "fixed":
            page(image, 120, 243, 345, 333, "原有固定利率", "4% 保持")
            text(image, (875, 286), "市场利率 ↑", 52, RED, center=True)
            text(image, (875, 400), "旧合同未到期", 36, center=True)
            text(image, (875, 469), "不立即重定价", 36, center=True)
        elif mode == "check_maturity":
            calendar(image, 140, 270, "贷款到期", "续借")
            office(image, 930, 569, 180, 265, occupied=.3)
            arrow(image, (450, 395), (820, 395))
            text(image, (640, 470), "稳定收租了吗？", 32, RED, center=True)
        else:
            bank(image, 170, 286, 180)
            arrow(image, (420, 380), (770, 380))
            office(image, 905, 564, 150, 280, progress=.6 + .4 * q)
            text(image, (620, 457), "融资负担 ↓", 45, RED, center=True)
    elif mode in {"expect_growth", "dependency", "no_margin"}:
        labels = ["租金", "地价", "企业需求"]
        for i, x in enumerate([220, 640, 1060]):
            text(image, (x, 260), labels[i], 39, center=True)
            arrow(image, (x - 110, 515), (x + 100, 335), RED, 4)
            text(image, (x, 554), "继续变好？", 27, center=True)
        if mode in {"dependency", "no_margin"}:
            line(image, [(95, 471), (1180, 471)], MUTED, 2)
            text(image, (640, 598), "一旦增长低于预期，是否还留有余地？", 27, RED, center=True)
    elif mode in {"competition", "forecast", "bank", "tenants", "capacity"}:
        for i, x in enumerate([120, 410, 700, 990]):
            office(image, x, 470, 115, 125 + i * 26, occupied=.55, progress=q)
            crane(image, x + 105, 255 - i * 10, .5)
            text(image, (x + 58, 488), f"开发商 {chr(65 + i)}", 25, center=True)
        if mode == "bank":
            line(image, [(180, 559), (1045, 559)], RED, 3)
            for x in [180, 470, 760, 1045]:
                arrow(image, (x, 525), (x, 559))
            text(image, (640, 581), "同一家或不同银行 / 申请贷款", 27, RED, center=True)
        elif mode == "tenants":
            for i in range(6):
                person(image, 495 + i * 58, 556, .43, RED)
            for x in [178, 468, 758, 1048]:
                arrow(image, (x, 530), (640, 558), RED, 2)
        elif mode == "capacity":
            text(image, (640, 558), "四份预测相加，是否超过实际需求？", 31, RED, center=True)
        else:
            text(image, (640, 560), "同一个片区，同一个未来", 33, RED, center=True)
    elif mode in {"benefits", "benefits_real"}:
        for i, (x, label) in enumerate([(240, "地标知名度"), (640, "观光收入"), (1040, "周边吸引力")]):
            if i == 0:
                tower(image, x, 475, 200)
            elif i == 1:
                for k in range(3):
                    person(image, x - 55 + 55 * k, 326, .95)
            else:
                for k in range(3):
                    office(image, x - 105 + 78 * k, 475, 58, 105 + 32 * k, .5)
            text(image, (x, 530), label, 31, center=True)
        if mode == "benefits_real":
            text(image, (640, 590), "需要逐项核实，不能一概否定", 27, RED, center=True)
    elif mode in {"expectations", "beliefs", "two_sides"}:
        points = [(640, 242), (235, 490), (1045, 490)]
        labels = ["开发商", "银行", "投资者"]
        beliefs = ["企业会来", "抵押物值钱", "有人接手"]
        for i, ((x, y), label, belief) in enumerate(zip(points, labels, beliefs)):
            person(image, x, y, .65)
            text(image, (x, y + 85), label, 28, center=True)
            text(image, (x, y + 126), belief, 25, RED, center=True)
        arrow(image, (535, 345), (360, 450))
        arrow(image, (367, 533), (910, 533))
        arrow(image, (960, 437), (740, 337))
    elif mode in {"clock", "speed"}:
        for x, label, speed in [(320, "建设周期", 1), (950, "市场变化", 5)]:
            draw.ellipse((x - 125, 255, x + 125, 505), outline=INK, width=3)
            angle = t * .18 * speed - math.pi / 2
            line(image, [(x, 380), (x + 93 * math.cos(angle), 380 + 93 * math.sin(angle))], RED, 5)
            text(image, (x, 548), label, 36, center=True)
        arrow(image, (525, 380), (745, 380))
    elif mode == "petronas":
        for x in [950, 1080]:
            tower(image, x, 565, 265)
        line(image, [(973, 430), (1055, 430)], INK, 7)
        text(image, (75, 280), "1992", 87, RED, latin=True)
        text(image, (75, 386), "开始规划", 33)
        arrow(image, (365, 348), (500, 348))
        text(image, (560, 280), "1999", 87, INK, latin=True)
        text(image, (560, 386), "正式开幕", 33)
        text(image, (1010, 585), "双子塔 · 建筑示意", 18, MUTED, center=True)
    elif mode == "commitment":
        page(image, 110, 248, 290, 310, "订单", "可以取消")
        line(image, [(140, 360), (365, 510)], RED, 7)
        office(image, 880, 565, 180, 280, occupied=.1, progress=.65)
        crane(image, 1090, 260, 1.2)
        text(image, (950, 587), "施工中的资本", 27, center=True)
        text(image, (640, 362), "≠", 75, RED, center=True)
    elif mode == "lag":
        flow(image, ["开工决定", "持续建设", "最终交付"], q, 300, 230, 410)
        points = [(130, 539), (330, 440), (550, 445), (770, 499), (1120, 568)]
        line(image, points[:max(2, round(2 + q * 3))], RED, 5)
        text(image, (640, 588), "概念示意：市场可能先于工程转向", 27, MUTED, center=True)
    elif mode == "bank_questions":
        bank(image, 140, 290, 190)
        for i, value in enumerate(["谁来补钱？", "抵押物值多少？", "出售能回收多少？"]):
            text(image, (790, 255 + i * 112), value, 42, RED if i == 1 else INK, center=True)
            line(image, [(520, 325 + i * 112), (1100, 325 + i * 112)], PALE, 1)
    elif mode == "valuation":
        text(image, (270, 300), "收入 ↓", 57, center=True)
        text(image, (270, 429), "回报要求 ↑", 48, center=True)
        arrow(image, (545, 397), (735, 397))
        text(image, (1010, 327), "估值承压", 55, RED, center=True)
        text(image, (1010, 441), "融资更困难", 37, center=True)
    elif mode in {"credit", "transmission", "system"}:
        if mode == "credit":
            bank(image, 150, 275, 180)
            office(image, 1000, 565, 140, 220, .35)
            arrow(image, (450, 370), (875, 370))
            line(image, [(660, 293), (660, 450)], RED, 16)
            text(image, (660, 512), "放贷收紧", 40, RED, center=True)
        elif mode == "system":
            flow(image, ["单栋亏损", "多处承压", "系统风险？"], q, 320, 210, 430)
            text(image, (640, 463), "规模  /  银行能力  /  融资结构  /  应对", 32, RED, center=True)
            text(image, (640, 550), "能否传导、传导多远，取决于这些条件", 27, MUTED, center=True)
        else:
            flow(image, ["收入变少", "偿债变难", "资产重估", "融资收紧"], q, 385, 160, 320)
    elif mode in {"cases", "headline", "selection", "counterexamples"}:
        for row in range(2):
            for col in range(4):
                x, y = 78 + col * 304, 242 + row * 174
                draw.rectangle((x, y, x + 210, y + 126), outline=PALE, width=2)
                text(image, (x + 105, y + 20), f"案例 {row * 4 + col + 1}", 26, center=True)
                selected = (row, col) in {(0, 0), (1, 2)}
                text(image, (x + 105, y + 72), "相符" if selected else "待检验", 25, RED if selected else MUTED, center=True)
                if selected:
                    draw.rectangle((x - 4, y - 4, x + 214, y + 130), outline=RED, width=3)
        text(image, (640, 597), "样本筛选示意，不代表真实研究数据", 21, MUTED, center=True)
    elif mode in {"rules", "test", "finding", "study", "debate"}:
        if mode == "study":
            page(image, 90, 234, 370, 350, "研究资料", "2015")
            text(image, (810, 251), "《应用经济学》", 45, center=True)
            text(image, (810, 329), "Barr / Mizrach / Mundra", 25, MUTED, center=True, latin=True)
            for i, value in enumerate(["美国 · 加拿大", "中国 · 香港地区", "纪录日期与经济周期"]):
                text(image, (810, 404 + i * 64), value, 31, RED if i == 2 else INK, center=True)
        elif mode == "finding":
            text(image, (640, 281), "未发现很强的周期对应关系", 48, center=True)
            text(image, (640, 396), "未支持高度作为可靠领先指标", 45, RED, center=True)
            text(image, (640, 525), "该研究的检验结论", 27, MUTED, center=True)
        elif mode == "debate":
            page(image, 125, 245, 350, 330, "关联性检验", "预测证据不足")
            page(image, 805, 245, 350, 330, "不同理论解释", "仍支持信号说")
            text(image, (640, 367), "争论", 47, RED, center=True)
        else:
            flow(image, ["预先定标准", "纳入反例", "新数据检验"], q, 350, 225, 415)
            text(image, (640, 508), "公布成功，也公布失败", 39, RED, center=True)
    elif mode in {"four", "check_demand", "check_funding", "check_stress"}:
        if mode == "check_demand":
            photos.draw(image, (65, 241, 650, 350), p)
            page(image, 900, 254, 255, 320, "真实租约", "谁来使用？")
        elif mode == "check_funding":
            page(image, 125, 250, 350, 320, "自有资金", "承担损失")
            page(image, 805, 250, 350, 320, "借款", "必须偿还")
            text(image, (640, 363), "+", 64, RED, center=True, latin=True)
        elif mode == "check_stress":
            text(image, (350, 284), "租金 ↓", 68, center=True)
            text(image, (930, 284), "利息 ↑", 68, RED, center=True)
            text(image, (640, 463), "还承受得住吗？", 62, RED, center=True)
        else:
            for i, (x, value) in enumerate([(200, "需求"), (490, "资金"), (780, "到期"), (1070, "承受")]):
                text(image, (x, 275), f"0{i + 1}", 82, RED, center=True, latin=True)
                text(image, (x, 425), value, 48, center=True)
    else:
        raise ValueError(f"No content-specific drawing implemented for {mode!r}")


def render(chapter_id, revision):
    if revision >= 20:
        import importlib
        import v2_visuals
        return importlib.reload(v2_visuals).render(chapter_id, revision)
    chapter = plan()[chapter_id - 1]
    directory = PRODUCTION / f"{chapter_id:02d}"
    voice = json.loads((directory / "voice.json").read_text())
    subtitles = subtitles_for(voice)
    dump(directory / "subtitles.json", subtitles)
    write_srt(directory / f"chapter-{chapter_id:02d}.srt", subtitles)
    photos = Photos(directory)
    light = paper()
    output = directory / f"chapter-{chapter_id:02d}.mp4"
    picture = directory / "picture.mp4"
    total_frames = round(voice["duration"] * FPS)
    encoder = subprocess.Popen([
        FFMPEG, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(picture),
    ], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    scene_starts = [max(0, p["start"] - .12) for p in voice["paragraphs"]]
    scene_starts[0] = 0
    subtitle_starts = [s["start"] for s in subtitles]
    snapshots = []
    snapshot_frames = {}
    for i, para in enumerate(voice["paragraphs"]):
        end = scene_starts[i + 1] if i + 1 < len(scene_starts) else voice["duration"]
        snapshot_frames[round((scene_starts[i] + (end - scene_starts[i]) * .6) * FPS)] = i
    coverage = []
    for i, (paragraph, shot) in enumerate(zip(voice["paragraphs"], chapter["shots"])):
        coverage.append({
            "scene": i + 1, "start": scene_starts[i],
            "end": scene_starts[i + 1] if i + 1 < len(scene_starts) else voice["duration"],
            "narration": paragraph["text"], "visual": shot[0], "title": shot[1], "detail": shot[2],
        })
    dump(directory / "timeline.json", coverage)
    try:
        for index in range(total_frames):
            t = index / FPS
            scene = max(0, bisect.bisect_right(scene_starts, t) - 1)
            shot = chapter["shots"][scene]
            start = scene_starts[scene]
            end = scene_starts[scene + 1] if scene + 1 < len(scene_starts) else voice["duration"]
            p = (t - start) / max(.1, end - start)
            image = light.copy()
            text(image, (58, 28), "繁荣的高度", 19, MUTED)
            text(image, (250, 30), "THE HEIGHT OF A BOOM", 13, MUTED, latin=True)
            text(image, (1200, 28), f"{chapter_id:02d} / 08", 17, MUTED, center=True, latin=True)
            line(image, [(60, 68), (1220, 68)], PALE, 1)
            text(image, (62, 98), shot[1], 48, max_width=1150)
            line(image, [(65, 168), (65 + 160 * ease(p * 4), 168)], RED, 3)
            draw_scene(image, shot[0], p, t - start, photos, chapter_id)
            text(image, (640, 636), shot[2], 22, MUTED, center=True, max_width=1135)
            draw = ImageDraw.Draw(image)
            draw.rectangle((0, 665, W, H), fill=INK)
            draw.rectangle((0, 662, round(W * t / voice["duration"]), 665), fill=RED)
            sub_index = bisect.bisect_right(subtitle_starts, t) - 1
            if sub_index >= 0 and t <= subtitles[sub_index]["end"] + .08:
                text(image, (640, 679), subtitles[sub_index]["text"], 28, (247, 247, 244),
                     center=True, serif=True, max_width=1170)
            if chapter_id in {3, 4, 5, 6}:
                text(image, (1090, 187), "机制与项目示意", 15, MUTED)
            encoder.stdin.write(image.tobytes())
            if index in snapshot_frames:
                number = snapshot_frames[index]
                dest = directory / f"scene-{number + 1:02d}.jpg"
                image.save(dest, quality=91)
                snapshots.append(dest)
            if index % 250 == 0:
                print(f"CHAPTER_FRAME {chapter_id:02d} {index}/{total_frames}", flush=True)
        encoder.stdin.close()
        errors = encoder.stderr.read().decode()
        if encoder.wait() != 0:
            raise RuntimeError(errors[-2000:])
    finally:
        if encoder.poll() is None:
            encoder.kill()
            encoder.wait()
    subprocess.run([
        FFMPEG, "-y", "-v", "error", "-i", str(picture), "-i", voice["mix"],
        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
        "-t", str(voice["duration"]), "-movflags", "+faststart", str(output),
    ], check=True, timeout=120)
    rows = math.ceil(len(snapshots) / 3)
    contact = Image.new("RGB", (1440, rows * 270), (235, 235, 233))
    for i, path in enumerate(snapshots):
        with Image.open(path) as item:
            contact.paste(item.resize((480, 270)), ((i % 3) * 480, (i // 3) * 270))
    contact.save(directory / "contact-sheet.jpg", quality=90)
    verification = {
        "video": str(output), "probe": probe(output),
        "narration_paragraphs": len(voice["paragraphs"]), "scenes": len(coverage),
        "subtitle_count": len(subtitles), "voice_provider": voice["provider"],
        "motion": str(directory / "motion.mp4"),
        "historical_material": "AI reconstruction and architectural illustration; no generated footage presented as archival evidence.",
        "revision": revision,
    }
    dump(directory / "verification.json", verification)
    return str(output)
