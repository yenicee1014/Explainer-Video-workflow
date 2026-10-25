"""Photo-led, narration-aligned V2 editorial compositor."""
from functools import lru_cache
from pathlib import Path
import argparse
import bisect
import importlib
import json
import math
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageOps

from full_film import ROOT, FFMPEG, FPS, PRODUCTION, dump, probe, write_srt
from film_visuals import W, H, RED, INK, PAPER, MUTED, PALE, text, line, arrow, paper, subtitles_for
from v2_plan import V2, OLD, ASSETS, make_plan

WHITE = (245, 245, 242)
KEYWORDS = {
    (1, 3): ["工人失业", "银行体系"], (1, 5): ["2010年1月4日"],
    (1, 8): ["开发商的账本"],
    (2, 2): ["帝国大厦正式开工"], (2, 4): ["正式开工", "开门营业"],
    (3, 3): ["建造", "楼盖好之后"], (3, 7): ["账本里的租金"],
    (3, 8): ["押进了今天"], (3, 10): ["更贵的地"],
    (3, 11): ["问题出现在", "未来持续变好"],
    (4, 7): ["周边土地"], (4, 11): ["风险就已经"],
    (5, 4): ["建到一半的核心筒"], (5, 5): ["几年后"],
    (5, 7): ["市场已经"], (6, 2): ["租金让步"],
    (6, 8): ["抵押物现在"], (6, 9): ["想靠抵押"],
    (6, 11): ["偿债变难", "资产重估", "融资收紧"],
    (8, 3): ["项目又借了多少债"], (8, 4): ["贷款就需要续借"],
    (8, 7): ["城市需求增长"], (8, 9): ["翻一翻账本"],
}
FINANCE = {
    "loan", "income", "cash_good", "return", "income_drop", "fixed", "refinance",
    "cash_bad", "valuation", "check_funding", "check_maturity", "check_stress",
    "closing", "obligation",
}
DUAL = {"contrast", "dates", "decision", "certainty", "capacity", "commitment", "demand_shift", "mismatch"}
LABELS = {
    "esb_open": "历史影像 / 帝国大厦官网 · 1931",
    "esb_build": "历史影像 / 帝国大厦官网 · 1930",
    "esb_motion": "建筑实景 / 帝国大厦官网 · 现代参考照片",
    "burj_motion": "建筑实景 / SOM 项目摄影",
    "petronas_motion": "建筑实景 / Pelli Clarke & Partners",
    "petronas_photo": "建筑照片 / Pelli Clarke & Partners",
    "paper_study": "论文书目信息 / Crossref · 10.1080/00036846.2014.967380",
    "paper_debate": "评论书目信息 / Crossref · 10.2139/ssrn.2641910",
    "dubai_notice": "事件时间线 / 原创排版 · 非公告原件",
}


def plain(value):
    return "".join(c for c in value if c.isalnum())


def phrase_time(paragraph, phrase):
    target = plain(paragraph["text"]).find(plain(phrase))
    if target < 0:
        return None
    full = plain(paragraph["text"])
    cursor = 0
    prior = .0
    for word in paragraph["words"]:
        token = plain(word["text"])
        pos = full.find(token, cursor) if token else cursor
        if pos < 0:
            pos = cursor
        if pos > target:
            return prior
        prior = word["offset"] / 10000000
        if pos <= target < pos + len(token):
            return prior
        cursor = pos + len(token)
    return prior


def timelines(chapter, voice):
    starts = [max(0, p["start"] - .12) for p in voice["paragraphs"]]
    starts[0] = 0
    result = []
    for i, (scene, paragraph) in enumerate(zip(chapter["scenes"], voice["paragraphs"])):
        start = starts[i]
        end = starts[i + 1] if i + 1 < len(starts) else voice["duration"]
        count = len(scene["assets"])
        cuts = [start + (end - start) * j / count for j in range(1, count)]
        phrases = KEYWORDS.get((chapter["chapter"], i + 1), [])
        if len(phrases) == count - 1:
            exact = [phrase_time(paragraph, p) for p in phrases]
            if all(t is not None for t in exact):
                proposed = [paragraph["start"] + t for t in exact]
                if all(b - a >= .55 for a, b in zip([start] + proposed, proposed + [end])):
                    cuts = proposed
        boundaries = [start] + cuts + [end]
        result.append({
            **scene, "start": start, "end": end,
            "beats": [
                {"asset": key, "start": a, "end": b}
                for key, a, b in zip(scene["assets"], boundaries, boundaries[1:])
            ],
        })
    return result


class Media:
    def __init__(self):
        self.cache = V2 / "frame-cache"
        self.cache.mkdir(exist_ok=True)

    def path(self, key):
        if key in OLD:
            return PRODUCTION / f"{OLD[key]:02d}/motion.mp4"
        if key in {"esb_open", "esb_build", "petronas_photo"}:
            return V2 / f"research/{key}.jpg"
        if key in {"esb_motion", "burj_motion", "petronas_motion"}:
            return V2 / f"research/{key.replace('_motion', '_photo')}.jpg"
        return V2 / f"assets/{key}/motion.mp4"

    @lru_cache(maxsize=6)
    def frames(self, key):
        path = self.path(key)
        if not path.exists():
            raise FileNotFoundError(f"Required exact scene media missing: {key}: {path}")
        if path.suffix == ".jpg":
            return ImageOps.grayscale(Image.open(path)).convert("RGB")
        cache = self.cache / f"{key}.npy"
        if not cache.exists():
            data = subprocess.run([
                FFMPEG, "-v", "error", "-i", str(path), "-vf",
                "fps=10,scale=960:540:force_original_aspect_ratio=decrease,pad=960:540:(ow-iw)/2:(oh-ih)/2:color=0xe6e6e4,format=gray",
                "-an", "-f", "rawvideo", "-pix_fmt", "gray", "-",
            ], check=True, capture_output=True).stdout
            frames = np.frombuffer(data, np.uint8).reshape((-1, 540, 960))
            if len(frames) < 10:
                raise ValueError(f"Cannot decode motion for {key}")
            np.save(cache, frames)
        return np.load(cache, mmap_mode="r")

    def image(self, key, p, scene):
        if key in {"paper_study", "paper_debate", "dubai_notice"}:
            return document(key)
        frames = self.frames(key)
        if isinstance(frames, Image.Image):
            return frames.copy()
        # Short narration beats take a central excerpt at natural speed; longer
        # beats slow the source slightly, without looping a human action.
        duration = (len(frames) - 1) / 10
        matching = [b for b in scene["beats"] if b["asset"] == key]
        beat_duration = matching[0]["end"] - matching[0]["start"] if matching else scene["end"] - scene["start"]
        span = min(duration, max(1.5, beat_duration))
        offset = max(0, (duration - span) / 2)
        index = min(len(frames) - 1, round((offset + span * min(1, max(0, p))) * 10))
        return Image.fromarray(np.asarray(frames[index])).convert("RGB")

    def draw(self, canvas, key, box, p, scene, contain=False, label=True):
        x, y, width, height = [round(n) for n in box]
        source = self.image(key, p, scene)
        landmark = key in {"esb_motion", "burj_motion", "petronas_motion", "petronas_photo"}
        contain = contain or landmark or key == "sites"
        if key in {"esb_open", "esb_build"}:
            zoom = 1 + .018 * p
            sw, sh = source.size
            source = source.crop(((sw - sw / zoom) / 2, (sh - sh / zoom) / 2,
                                  (sw + sw / zoom) / 2, (sh + sh / zoom) / 2))
        if contain:
            fitted = ImageOps.contain(source, (width - 16, height - 16), Image.Resampling.BILINEAR)
            if landmark:
                zoom = 1 + .012 * p
                fitted = fitted.resize((round(fitted.width * zoom), round(fitted.height * zoom)), Image.Resampling.BILINEAR)
            canvas.paste(fitted, (x + (width - fitted.width) // 2, y + (height - fitted.height) // 2))
        else:
            fitted = ImageOps.fit(source, (width, height), Image.Resampling.BILINEAR, centering=(.5, .46))
            canvas.paste(fitted, (x, y))
        # Irregular narrow paper edges maintain the cut-print vocabulary.
        draw = ImageDraw.Draw(canvas)
        draw.line([(x, y + height), (x + width, y + height)], fill=INK, width=2)
        if label:
            value = LABELS.get(key, "AI 情境重建 / 机制示意")
            label_width = min(width - 12, len(value) * 15 + 16)
            draw.rectangle((x + 6, y + height - 27, x + 6 + label_width, y + height - 4), fill=PAPER)
            text(canvas, (x + 12, y + height - 25), value, 15, INK, max_width=label_width - 12)


@lru_cache(maxsize=3)
def document(key):
    image = paper()
    if key == "dubai_notice":
        text(image, (90, 88), "迪拜的两条消息", 48)
        text(image, (90, 215), "2009.11", 94, RED, latin=True)
        text(image, (95, 336), "迪拜世界 · 债务延期偿付风波", 37)
        line(image, [(95, 420), (1170, 420)], PALE, 2)
        text(image, (95, 465), "2010.01.04", 76, INK, latin=True)
        text(image, (100, 563), "哈利法塔开幕 / 开发商 Emaar", 36)
        text(image, (95, 650), "不同主体、不同事件；不能据此建立因果关系", 23, MUTED)
    else:
        comment = key == "paper_debate"
        text(image, (76, 58), "RESEARCH RECORD", 22, RED, latin=True)
        line(image, [(80, 110), (1190, 110)], INK, 3)
        text(image, (80, 145), "Skyscraper Height", 62, INK, latin=True)
        text(image, (80, 225), "and the Business Cycle", 59, INK, latin=True)
        text(image, (82, 320), "Separating Myth from Reality" + (", a Comment" if comment else ""), 35, INK, latin=True)
        text(image, (82, 410), "Lucas Engelhardt / Mark Thornton" if comment else "Jason Barr / Bruce Mizrach / Kusum Mundra",
             29, RED, latin=True, max_width=1100)
        text(image, (82, 481), "2015 · Working Paper / SSRN" if comment else "2015 · Applied Economics 47(2), 148–160",
             32, INK, latin=True)
        line(image, [(82, 550), (1190, 550)], PALE, 2)
        text(image, (82, 588), "10.2139/ssrn.2641910" if comment else "10.1080/00036846.2014.967380", 27, MUTED, latin=True)
        text(image, (82, 647), "来源：Crossref / 出版记录", 21, MUTED)
    return image


def header(image, chapter, scene, dark=False):
    color = WHITE if dark else INK
    muted = (185, 185, 182) if dark else MUTED
    text(image, (42, 24), "繁荣的高度", 20, muted)
    text(image, (250, 29), "THE HEIGHT OF A BOOM", 12, muted, latin=True)
    text(image, (1225, 24), f"{chapter:02d} / 08", 17, muted, center=True, latin=True)
    line(image, [(42, 62), (1238, 62)], (77, 77, 75) if dark else PALE, 1)
    text(image, (42, 82), scene["title"], 45, color, max_width=1188)
    line(image, [(44, 142), (170, 142)], RED, 4)


def annotation(image, x, y, title, value, color=RED, width=375, value_size=55):
    text(image, (x, y), title, 22, MUTED, max_width=width)
    text(image, (x, y + 36), value, value_size, color, max_width=width)


def finance(image, mode, p):
    x, width = 829, 390
    if mode in {"loan", "return"}:
        annotation(image, x, 198, "借款合同", "6 亿元", value_size=76)
        annotation(image, x, 335, "年利率", "4%", INK, value_size=63)
        annotation(image, x, 459, "每年利息", "2400 万元", value_size=47)
    elif mode == "income":
        annotation(image, x, 213, "预期净运营收入 / 每年", "5000 万元", value_size=57)
        text(image, (x, 376), "已扣日常运营费用", 27)
        text(image, (x, 430), "租约与收入仍待兑现", 25, RED)
    elif mode in {"cash_good", "cash_bad", "check_stress"}:
        bad = mode != "cash_good"
        labels = [("净运营收入", 3500 if bad else 5000, INK), ("年利息", 3600 if bad else 2400, RED)]
        for i, (label, amount, color) in enumerate(labels):
            yy = 200 + i * 157
            text(image, (x, yy), label, 23)
            text(image, (x, yy + 36), f"{amount} 万", 51, color)
            ImageDraw.Draw(image).rectangle((x, yy + 107, x + width * amount / 5500, yy + 119), fill=color)
        text(image, (x, 533), "缺口 100 万元 / 年" if bad else "尚有付息余地", 29, RED)
    elif mode == "income_drop":
        annotation(image, x, 202, "原预测 / 万元每年", "5000", INK, value_size=72)
        arrow(image, (x + 155, 335), (x + 155, 382))
        annotation(image, x, 400, "租户减少、租金让步之后", "3500", value_size=72)
    elif mode == "fixed":
        annotation(image, x, 216, "旧合同尚未到期", "固定 4%", value_size=60)
        text(image, (x, 376), "仍按旧合同付息", 31)
        text(image, (x, 441), "2400 万元 / 年", 36, INK)
        line(image, [(x, 505), (x + width - 10, 505)], PALE, 2)
        text(image, (x, 533), "市场加息 ≠ 立即重置", 25, RED)
    elif mode == "refinance":
        annotation(image, x, 201, "旧合同 → 到期续借", "4% → 6%", value_size=54)
        annotation(image, x, 368, "新贷款每年利息", "3600 万元", value_size=51)
        text(image, (x, 513), "原利息 2400 万元 / 年", 25)
        text(image, (x, 556), "本金仍为 6 亿元", 24, MUTED)
    elif mode == "valuation":
        for yy, title, value in [(202, "物业收入", "下降"), (340, "投资人要求回报", "提高"), (476, "抵押估值与融资空间", "承压")]:
            annotation(image, x, yy, title, value, value_size=46)
    elif mode == "check_funding":
        annotation(image, x, 215, "自有资金", "承担损失", INK, value_size=43)
        annotation(image, x, 408, "借入资金", "必须偿还", value_size=43)
    elif mode == "check_maturity":
        annotation(image, x, 206, "债务到期日", "何时续借？", value_size=46)
        text(image, (x, 385), "稳定收租之前", 29)
        text(image, (x, 436), "就需要重新融资？", 29, RED)
    elif mode in {"closing", "obligation"}:
        annotation(image, x, 215, "未来收入", "仍待验证", INK, value_size=44)
        annotation(image, x, 414, "下一笔利息", "已有日期", value_size=44)
    else:
        raise ValueError(mode)
    text(image, (x, 600), "虚构项目教学示例 · 不计税费及还本" if mode not in {"closing", "check_maturity", "obligation", "check_funding", "valuation"} else "检查项目本身的需求与偿债安排",
         16, MUTED, max_width=390)


def current_beat(scene, t):
    for i, beat in enumerate(scene["beats"]):
        if t < beat["end"] or i == len(scene["beats"]) - 1:
            return beat, max(0, min(1, (t - beat["start"]) / max(.1, beat["end"] - beat["start"])))


def evidence_note(image, mode):
    x = 870
    if mode in {"counterexamples", "selection", "cases"}:
        for i, (label, value) in enumerate([
            ("纳入样本", "高楼与危机相符"),
            ("也纳入样本", "有高楼，无危机"),
            ("也纳入样本", "有危机，无新纪录"),
        ]):
            text(image, (x, 220 + i * 126), label, 19, MUTED)
            text(image, (x, 253 + i * 126), value, 27, RED if i else INK, max_width=330)
        text(image, (x, 604), "分类示意 · 不是实测样本数量", 16, MUTED)
    elif mode in {"test", "rules"}:
        for i, word in enumerate(["提前多久？", "怎么算成功？", "怎么算失败？"]):
            text(image, (x, 232 + i * 115), f"0{i + 1}", 23, RED, latin=True)
            text(image, (x, 272 + i * 115), word, 31, max_width=320)
    elif mode == "finding":
        text(image, (x, 217), "该研究检验结果", 22, MUTED)
        for i, word in enumerate(["周期对应较弱", "未支持可靠", "领先预测"]):
            text(image, (x, 285 + i * 75), word, 35, RED if i else INK, max_width=325)
        text(image, (x, 567), "不是对所有因果关系的证明", 18, MUTED, max_width=325)


def frame(media, chapter_id, scene, t, light, dark):
    mode = scene["mode"]
    beat, p = current_beat(scene, t)
    key = beat["asset"]
    is_dark = mode in {"photo", "credit", "plea", "headline", "no_margin"} and chapter_id in {1, 4, 6, 7}
    image = (dark if is_dark else light).copy()
    header(image, chapter_id, scene, is_dark)
    if mode in FINANCE:
        media.draw(image, key, (42, 174, 738, 438), p, scene)
        line(image, [(804, 185), (804, 609)], PALE, 1)
        finance(image, mode, p)
    elif mode == "petronas":
        media.draw(image, "petronas_motion", (42, 174, 743, 438), (t - scene["start"]) / (scene["end"] - scene["start"]), scene)
        annotation(image, 837, 202, "吉隆坡 / 双子塔", "1992", value_size=74)
        text(image, (837, 316), "开始规划", 28)
        arrow(image, (950, 375), (950, 422))
        annotation(image, 837, 445, "1999 年 8 月", "正式开幕", value_size=45)
    elif mode == "dubai":
        media.draw(image, "burj_motion", (563, 174, 675, 438), (t - scene["start"]) / (scene["end"] - scene["start"]), scene)
        text(image, (45, 199), "2009.11", 66, RED, latin=True)
        text(image, (47, 292), "迪拜世界债务风波", 30)
        line(image, [(48, 355), (505, 355)], PALE, 2)
        text(image, (45, 402), "2010.01.04", 56, INK, latin=True)
        text(image, (48, 486), "哈利法塔开幕", 33)
        text(image, (48, 559), "开发商为 Emaar，主体不可混同", 20, MUTED, max_width=470)
    elif mode in DUAL and len(scene["assets"]) >= 2:
        first, last = scene["assets"][0], scene["assets"][-1]
        whole_p = (t - scene["start"]) / (scene["end"] - scene["start"])
        media.draw(image, first, (42, 179, 584, 397), whole_p, scene)
        media.draw(image, last, (654, 179, 584, 397), whole_p, scene)
        pair = {
            "contrast": ("高度纪录", "街道与就业"),
            "dates": ("1929.10 / 股灾", "1930.03 / 开工"),
            "decision": ("启动时的预期", "交付时的市场"),
            "certainty": ("合同已签 / 债务确定", "未来租金 / 尚未实现"),
            "capacity": ("同时交付的新增供应", "有限的企业租户"),
            "commitment": ("订单可以撤回", "核心筒不能立即变现"),
            "demand_shift": ("开工时 / 企业扩张", "交付时 / 企业收缩"),
            "mismatch": ("图纸中的需求", "来签租约的客户"),
        }[mode]
        for x, label in zip([334, 946], pair):
            text(image, (x, 590), label, 27, RED if x == 946 else INK, center=True, max_width=565)
    elif mode in {"study", "debate"}:
        if mode == "study":
            media.draw(image, "paper_study", (42, 174, 723, 438), .5, scene, contain=True, label=False)
            media.draw(image, "old_research", (795, 200, 443, 268), p, scene)
            text(image, (805, 493), "美国 · 加拿大", 29)
            text(image, (805, 540), "中国 · 香港地区", 29)
            text(image, (805, 586), "检验纪录日期与周期关系", 23, RED)
        else:
            media.draw(image, "paper_study", (42, 175, 584, 350), .5, scene, contain=True, label=False)
            media.draw(image, "paper_debate", (654, 175, 584, 350), .5, scene, contain=True, label=False)
            text(image, (333, 547), "检验未支持可靠领先预测", 26, RED, center=True, max_width=570)
            text(image, (947, 547), "评论提出支持信号说的解释", 26, INK, center=True, max_width=570)
            text(image, (640, 606), "研究方法、理论解释与实际预测能力需要分开检验", 22, MUTED, center=True)
    elif mode in {"counterexamples", "selection", "cases", "test", "rules", "finding"}:
        media.draw(image, key, (42, 174, 775, 438), p, scene)
        evidence_note(image, mode)
    else:
        media.draw(image, key, (42, 174, 1196, 438), p, scene)
        if mode == "height":
            ImageDraw.Draw(image).rectangle((70, 200, 355, 361), fill=PAPER)
            text(image, (86, 217), "102", 94, RED, latin=True)
            text(image, (91, 325), "层 / 帝国大厦", 23)
        if mode in {"competition", "photo"} and chapter_id == 4:
            text(image, (70, 187), "同一区域 · 多个项目", 25, WHITE)
        if key == "lease_competition":
            ImageDraw.Draw(image).rectangle((63, 185, 506, 225), fill=PAPER)
            text(image, (76, 193), "多栋新楼 → 同一批企业", 25, RED)
        if mode == "transmission":
            names = ["收入变少", "偿债变难", "资产重估", "融资收紧"]
            active = next(i for i, b in enumerate(scene["beats"]) if b is beat)
            for i, name in enumerate(names):
                xx = 45 + i * 298
                ImageDraw.Draw(image).rectangle((xx, 550, xx + 290, 594), fill=RED if i == active else PAPER)
                text(image, (xx + 145, 560), name, 24, WHITE if i == active else INK, center=True)
        if mode == "stages":
            for i, label in enumerate(["宣布", "开工", "封顶", "营业"]):
                x = 60 + i * 294
                ImageDraw.Draw(image).rectangle((x, 548, x + 278, 591), fill=PAPER)
                text(image, (x + 139, 558), label, 24, RED if i == 1 else INK, center=True)
        if mode == "beliefs":
            for i, label in enumerate(["开发商 / 企业会来", "银行 / 抵押物值钱", "投资者 / 有人接手"]):
                x = 60 + i * 395
                ImageDraw.Draw(image).rectangle((x, 549, x + 380, 592), fill=PAPER)
                text(image, (x + 190, 560), label, 22, RED if i == 1 else INK, center=True, max_width=365)
    text(image, (640, 632), scene["detail"], 21, (188, 188, 184) if is_dark else MUTED,
         center=True, max_width=1185)
    return image


def render(chapter_id, revision=20):
    import v2_plan
    chapter = importlib.reload(v2_plan).make_plan()[chapter_id - 1]
    directory = V2 / f"{chapter_id:02d}"
    directory.mkdir(exist_ok=True)
    voice = json.loads((PRODUCTION / f"{chapter_id:02d}/voice.json").read_text())
    scenes = timelines(chapter, voice)
    subs = subtitles_for(voice)
    dump(directory / "timeline.json", scenes)
    dump(directory / "subtitles.json", subs)
    write_srt(directory / f"chapter-{chapter_id:02d}.srt", subs)
    media = Media()
    light, dark = paper(), paper(True)
    starts = [s["start"] for s in scenes]
    sub_starts = [s["start"] for s in subs]
    output = directory / f"chapter-{chapter_id:02d}.mp4"
    picture = directory / "picture.mp4"
    encoder = subprocess.Popen([
        FFMPEG, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(picture),
    ], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    snapshots = {}
    for i, scene in enumerate(scenes):
        for b, beat in enumerate(scene["beats"]):
            snapshots[round((beat["start"] + (beat["end"] - beat["start"]) * .58) * FPS)] = (i, b)
    thumbs = []
    try:
        total = round(voice["duration"] * FPS)
        for index in range(total):
            t = index / FPS
            number = max(0, bisect.bisect_right(starts, t) - 1)
            image = frame(media, chapter_id, scenes[number], t, light, dark)
            draw = ImageDraw.Draw(image)
            draw.rectangle((0, 665, W, H), fill=INK)
            draw.rectangle((0, 662, round(W * t / voice["duration"]), 665), fill=RED)
            sub_index = bisect.bisect_right(sub_starts, t) - 1
            if sub_index >= 0 and t <= subs[sub_index]["end"] + .08:
                text(image, (640, 679), subs[sub_index]["text"], 28, WHITE, center=True,
                     serif=True, max_width=1190)
            encoder.stdin.write(image.tobytes())
            if index in snapshots:
                i, b = snapshots[index]
                destination = directory / f"scene-{i + 1:02d}-beat-{b + 1:02d}.jpg"
                image.save(destination, quality=93)
                thumbs.append(destination)
            if index % 500 == 0:
                print(f"V2_RENDER {chapter_id:02d} {index}/{total}", flush=True)
        encoder.stdin.close()
        errors = encoder.stderr.read().decode()
        if encoder.wait() != 0:
            raise RuntimeError(errors[-1600:])
    finally:
        if encoder.poll() is None:
            encoder.kill()
            encoder.wait()
    subprocess.run([
        FFMPEG, "-y", "-v", "error", "-i", str(picture), "-i", voice["mix"],
        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
        "-t", str(voice["duration"]), "-movflags", "+faststart", str(output),
    ], check=True, timeout=120)
    sheet = Image.new("RGB", (1440, math.ceil(len(thumbs) / 3) * 270), PAPER)
    for i, file in enumerate(thumbs):
        with Image.open(file) as im:
            sheet.paste(im.resize((480, 270)), ((i % 3) * 480, (i // 3) * 270))
    sheet.save(directory / "contact-sheet.jpg", quality=92)
    dump(directory / "verification.json", {
        "video": str(output), "revision": revision, "probe": probe(output),
        "narration_paragraphs": len(scenes), "photographic_beats": sum(len(s["beats"]) for s in scenes),
        "distinct_media": sorted(set(a for s in scenes for a in s["assets"])),
        "preserved_approved_narration": True,
    })
    return str(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", type=int, required=True, choices=range(1, 9))
    args = parser.parse_args()
    print(render(args.chapter))
