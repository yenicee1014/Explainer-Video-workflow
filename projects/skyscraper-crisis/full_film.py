"""Production plan, narration, and sequential ComfyUI execution for chapters 01-08."""
from pathlib import Path
import argparse
import asyncio
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from urllib.parse import urlparse
import uuid
import wave

import numpy as np
import requests

ROOT = Path(__file__).resolve().parent


def configured_path(name, default=None):
    value = os.environ.get(name)
    return Path(value).expanduser() if value else default


COMFY = configured_path("SC_COMFY_DIR")
PYTHON = configured_path("SC_COMFY_PYTHON", COMFY / ".venv/bin/python" if COMFY else None)
BASE = os.environ.get("SC_COMFY_URL", "http://127.0.0.1:8190")
INPUT_DIR = configured_path("SC_COMFY_INPUT", ROOT / "comfy-input")
OUTPUT = configured_path("SC_COMFY_OUTPUT", ROOT / "comfy-output")
FFMPEG = os.environ.get("SC_FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = os.environ.get("SC_FFPROBE") or shutil.which("ffprobe") or "ffprobe"
FPS = 25
PRODUCTION = ROOT / "full-film"
STYLE = (
    "A five-second black-and-white historical editorial documentary shot. "
    "Fine silver-gelatin photographic grain, neutral grayscale, soft natural light, "
    "restrained realistic human gestures, physically coherent surroundings. "
    "Locked wide shot, gentle natural motion, crisp photographic detail. "
    "No text, no subtitles, no letters, no numerals, no logos, no watermark, "
    "no split screen, no graphics, no montage, no shot changes. "
    "This is an original illustrative reconstruction, not authentic archive footage. "
)

CHAPTERS = [
    {
        "id": 1,
        "asset": "A 1930s American industrial street. Six unemployed workers in worn wool coats and flat caps wait quietly in line beside a closed factory gate. A worker looks down at an empty lunch pail, another folds his hands. Human figures and factory entrance dominate the frame. No skyscraper hero shot, no visible signs.",
        "shots": [
            ("opening", "1931.05.01", "帝国大厦开幕"),
            ("height", "超过一百层", "建筑技术向上突破"),
            ("photo", "街道另一头", "工厂收缩 · 工人失业 · 银行承压"),
            ("contrast", "同一座城市", "建筑纪录与经济下行"),
            ("dubai", "迪拜的两条消息", "2009.11 债务风波 / 2010.01 哈利法塔开幕"),
            ("index", "摩天大楼指数", "引人注意的关联，等于可靠预测吗？"),
            ("question", "一栋楼，能预言吗？", "从现象走向检验"),
            ("ledger", "把目光移到账本", "借款合同 / 租金预测"),
        ],
    },
    {
        "id": 2,
        "asset": "An early 1930s construction site in New York. Two construction workers wearing caps and work clothes inspect a large paper blueprint on a timber table, behind them a modest steel building skeleton and a crane. One points to the plan while the other nods. Emphasize workers, paper plans, steel framing, no completed skyscraper.",
        "shots": [
            ("correct", "先把时间摆对", "先后顺序不能倒置"),
            ("dates", "股灾在前，开工在后", "1929.10 → 1930.03"),
            ("photo", "危机之后才开工", "不能把竣工日期当成提前预告"),
            ("stages", "四个不同的时刻", "宣布 / 开工 / 封顶 / 营业"),
            ("windows", "换一个日期，就换一个故事", "必须预先确定检验窗口"),
            ("decision", "为何启动？为何遇冷？", "开工时的判断 / 交付时的市场"),
        ],
    },
    {
        "id": 3,
        "asset": "A contemporary commercial property developer and a bank loan officer sit opposite each other at a plain desk. The developer wears a simple dark blazer. They review blank loan documents, a small architectural model, and a calculator. The officer hands over a pen and the developer signs one page. Medium wide composition, natural hands, human decision and contract are the main subject.",
        "shots": [
            ("photo", "你是一家开发商", "虚构项目 · 从一张办公楼图纸开始"),
            ("ledger", "先算账，再开工", "成本 / 收入 / 偿债"),
            ("costs", "这栋楼，怎样收回钱？", "拿地 → 建造 → 出租 → 还款"),
            ("loan", "借款 6 亿元", "年利率 4% → 年利息 2400 万元"),
            ("income", "预期净运营收入", "每年 5000 万元 · 扣除日常运营费用"),
            ("cash_good", "5000 万进来，2400 万付息", "简化示例：暂不计税费与本金偿还"),
            ("certainty", "借款是合同，租金是预测", "确定的义务 / 尚未兑现的收入"),
            ("blueprint", "第一铲土之前", "未来的租户，已经写进今天的决定"),
            ("financing", "融资变轻，项目更容易成立", "其他条件相同的示意"),
            ("expect_growth", "每一项，都假设继续上涨", "租金 / 地价 / 企业需求"),
            ("dependency", "关键是承受能力", "真实需求 ≠ 永远增长的假设"),
        ],
    },
    {
        "id": 4,
        "asset": "A realistic wide view of a commercial construction district. Four separate mid-rise concrete office buildings are under construction at once, several tower cranes moving gently. In the foreground two property developers in plain suits stand on separate sides of a paper site plan and look toward the same district. Show many competing building sites, not one single tower.",
        "shots": [
            ("competition", "不止你一个人看好", "开发商 A / 开发商 B"),
            ("forecast", "大家都在预测同一批企业", "三年后的需求 · 示意"),
            ("bank", "拿着未来，申请今天的贷款", "多家开发商 → 银行"),
            ("photo", "工地连成一片", "第三家、第四家，也加入建设"),
            ("tenants", "新楼都在等租户", "同一批客户，被多次写进预测"),
            ("capacity", "单栋合理，合计未必合理", "分别预测 / 汇总供需"),
            ("benefits", "高度之外，也有收益", "知名度 / 观光 / 周边土地吸引力"),
            ("benefits_real", "不能一概称为虚荣工程", "收益存在，但仍需核实和测算"),
            ("expectations", "同一种期待，互相作保证", "开发商 / 银行 / 投资者"),
            ("beliefs", "三个人的算盘", "企业会来 / 抵押物值钱 / 有人接手"),
            ("no_margin", "如果没有给变差留空间", "增长一放慢，所有计划一起承压"),
        ],
    },
    {
        "id": 5,
        "asset": "A construction manager in a hard hat stands beside an unfinished concrete office building core. He holds architectural plans while a crane slowly hoists a steel beam. Unfinished open floors, workers at a safe distance. Construction activity is slow and deliberate, showing long physical commitment. Daytime, no completed landmark.",
        "shots": [
            ("clock", "时间，开始发挥作用", "建筑进度与市场速度"),
            ("petronas", "规划到开幕，跨过多年", "双子塔：1992 开始规划 → 1999 正式开幕"),
            ("speed", "市场不会等施工队", "金融预期可以迅速改变"),
            ("commitment", "订单能取消，核心筒不能变现", "施工中的资本，被锁在项目里"),
            ("demand_shift", "开工时扩张，交付时收缩", "企业需求前后对照 · 虚构示例"),
            ("mismatch", "图纸上的需求 ≠ 实际租约", "预测客户 / 签约客户"),
            ("lag", "建设兑现旧决定，市场面对新现实", "时间差示意，不是统计曲线"),
            ("limit", "能解释现象，不能包办规律", "并非每座高楼都会遇到经济下行"),
        ],
    },
    {
        "id": 6,
        "asset": "Inside a contemporary nearly empty office floor, a property manager in a dark blazer walks past vacant desks and unused chairs, holding a thin rental folder. One remaining tenant packs a cardboard box at a desk in the distance. Large windows, subdued daylight, quiet restrained mood. Focus on vacant office space and rental difficulty, no collapsing buildings.",
        "shots": [
            ("return", "回到那笔 6 亿元借款", "同一个虚构项目"),
            ("income_drop", "5000 万 → 3500 万", "租户减少 · 租金让步 · 净运营收入下降"),
            ("fixed", "固定利率未到期", "市场加息 ≠ 旧合同立即加息"),
            ("refinance", "到期再融资：4% → 6%", "年利息：2400 万 → 3600 万"),
            ("cash_bad", "3500 万进来，3600 万付息", "年现金缺口 100 万元 · 尚未计还本"),
            ("photo", "楼还在，现金却不够了", "产生现金的能力 / 支付债务的速度"),
            ("plea", "开发商：再给一点时间", "等租户回来，谁先补上缺口？"),
            ("bank_questions", "银行：抵押物还值多少？", "补充资金 / 估值 / 出售回收"),
            ("valuation", "收入下降，融资空间也可能缩小", "收入↓ + 回报要求↑ → 估值承压"),
            ("credit", "贷款损失，传向下一位借款人", "贷款机构受损 → 收紧放贷"),
            ("transmission", "一条可能的风险传导路径", "收入变少 → 偿债变难 → 资产重估 → 融资收紧"),
            ("system", "单栋亏损 ≠ 整体危机", "规模 / 银行承受能力 / 融资结构 / 政策应对"),
        ],
    },
    {
        "id": 7,
        "asset": "An economic researcher at a plain desk compares several folders and printed sheets with charts whose marks are not readable. She moves a single selected clipping aside and spreads out a larger set of research pages, then checks another page with a pencil. Focus on evaluating evidence and examining counterexamples, realistic documentary observation.",
        "shots": [
            ("cases", "把故事放回完整样本", "关联，不自动等于预测"),
            ("two_sides", "真实增长，还是过高预期？", "需要证据，不能只看高度"),
            ("question", "为什么听起来这么神？", "故事如何进入记忆"),
            ("headline", "纪录 + 危机 = 醒目的故事", "醒目程度 ≠ 预测能力"),
            ("rules", "预测，必须先定标准", "提前多久？怎么算成功？"),
            ("counterexamples", "未发生危机的楼，也要算", "有高楼无危机 / 有危机无纪录"),
            ("selection", "不能只展示答对的题", "选中的案例 / 完整试卷 · 示意"),
            ("study", "2015 ·《应用经济学》", "美国 / 加拿大 / 中国 / 香港地区"),
            ("finding", "检验未支持可靠领先预测", "纪录日期与周期对应较弱"),
            ("debate", "也有不同的研究解释", "理论争论不等于预测已被验证"),
            ("test", "标准先定，再接受新数据检验", "公布成功，也公布失败"),
            ("no_prediction", "刷新高度纪录，不是危机倒计时", "不能仅凭一座楼判断危机日期"),
        ],
    },
    {
        "id": 8,
        "asset": "A commercial tenant, a property manager, and a financial reviewer inspect a modest office space together. They sit at a simple table with a lease folder, a calendar and a calculator, review actual documents, then look around the usable workspace. Practical business discussion, natural gestures, balanced composition, no glamour skyscraper shot.",
        "shots": [
            ("four", "换成四个实际问题", "需求 / 资金 / 到期 / 承受能力"),
            ("check_demand", "01 谁来使用它？", "真实企业与租约 / 乐观的增长预测"),
            ("check_funding", "02 钱从哪里来？", "自有资金 / 借款 / 可承担损失"),
            ("check_maturity", "03 债务什么时候到期？", "稳定收租之前，是否就要续借？"),
            ("check_stress", "04 变差之后，还能运行吗？", "租金更低 / 利息更高"),
            ("substance", "比高度更值得看的，是账本", "从纪录，回到项目基本面"),
            ("photo", "高，不等于危险", "技术进步和真实需求，也能支持高楼"),
            ("obligation", "最好情况，不能是唯一情况", "乐观的预测 / 必须兑现的债务"),
            ("ledger", "庆祝高度，也翻一翻账本", "收入、支出和到期日"),
            ("closing", "未来需要验证，利息已有日期", "繁荣的高度"),
        ],
    },
]


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def probe(path):
    result = subprocess.run(
        [FFPROBE, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        check=True, capture_output=True, text=True,
    )
    return json.loads(result.stdout)


def plan():
    script = (ROOT / "SCRIPT_FULL_V1.md").read_text().split("\n---\n")[0]
    sections = re.split(r"^## ", script, flags=re.M)[1:]
    if len(sections) != 8:
        raise ValueError("Expected exactly eight approved narration chapters.")
    for section, chapter in zip(sections, CHAPTERS):
        parts = re.split(r"\n\s*\n", section.strip())
        chapter["title"] = parts[0].split("｜", 1)[1]
        chapter["paragraphs"] = parts[1:]
        if len(chapter["paragraphs"]) != len(chapter["shots"]):
            raise ValueError(f"Chapter {chapter['id']} does not have one shot per narration paragraph.")
        directory = PRODUCTION / f"{chapter['id']:02d}"
        directory.mkdir(parents=True, exist_ok=True)
        dump(directory / "storyboard.json", {
            "chapter": chapter["id"], "title": chapter["title"],
            "generation_prompt": STYLE + chapter["asset"],
            "scenes": [
                {"scene": i + 1, "narration": p, "visual": s[0], "title": s[1], "detail": s[2]}
                for i, (p, s) in enumerate(zip(chapter["paragraphs"], chapter["shots"]))
            ],
        })
    return CHAPTERS


def start():
    if COMFY is None or not COMFY.is_dir():
        raise RuntimeError("Set SC_COMFY_DIR to the local ComfyUI directory before starting ComfyUI.")
    if PYTHON is None or not PYTHON.exists():
        raise RuntimeError("Set SC_COMFY_PYTHON or install ComfyUI's Python environment.")
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    try:
        requests.get(BASE + "/object_info/SCFullChapter", timeout=2).raise_for_status()
        return
    except requests.RequestException:
        pass
    settings = COMFY / "user/default/comfy.settings.json"
    token = json.loads(settings.read_text()).get("AutoDL.API.Token", "")
    if not token:
        raise RuntimeError("The configured AutoDL token is unavailable.")
    env = os.environ.copy()
    env["AUTODL_COMFY_TOKEN"] = token
    log = (PRODUCTION / "comfy-full.log").open("ab")
    port = int(os.environ.get("SC_COMFY_PORT") or urlparse(BASE).port or 8190)
    command = [
        str(PYTHON), "-s", "main.py", "--cpu", "--port", str(port),
        "--user-directory", str(ROOT / "comfy-user"),
        "--input-directory", str(INPUT_DIR),
        "--output-directory", str(OUTPUT),
        "--disable-all-custom-nodes", "--whitelist-custom-nodes",
        "ComfyUI-AutoDL-API", "skyscraper_editorial", "--disable-api-nodes",
    ]
    process = subprocess.Popen(command, cwd=COMFY, env=env, stdout=log, stderr=log, start_new_session=True)
    dump(PRODUCTION / "server.json", {"pid": process.pid, "base": BASE})
    for _ in range(50):
        if process.poll() is not None:
            raise RuntimeError("ComfyUI startup failed; inspect the project log.")
        try:
            info = requests.get(BASE + "/object_info/SCFullChapter", timeout=2)
            if info.status_code == 200 and "SCFullChapter" in info.json():
                print("COMFY_READY " + BASE, flush=True)
                return
        except requests.RequestException:
            pass
        time.sleep(1)
    raise TimeoutError("ComfyUI startup exceeded fifty seconds.")


def compact(text):
    return "".join(ch for ch in text if ch.isalnum())


async def voice_paragraph(chapter, index, text, gate):
    voice_tools = configured_path("SC_VOICE_TOOLS")
    if voice_tools and voice_tools.is_dir():
        sys.path.insert(0, str(voice_tools))
    import edge_tts
    key = hashlib.sha256(("yunxi:+0%:-3Hz:" + text).encode()).hexdigest()[:16]
    directory = PRODUCTION / f"{chapter:02d}" / "voice"
    directory.mkdir(exist_ok=True)
    destination = directory / f"{index:02d}-{key}.mp3"
    metadata = destination.with_suffix(".json")
    if destination.exists() and metadata.exists():
        return json.loads(metadata.read_text())
    async with gate:
        events = []
        for attempt in range(2):
            try:
                speech = edge_tts.Communicate(
                    text, voice="zh-CN-YunxiNeural", rate="+0%", pitch="-3Hz", boundary="WordBoundary"
                )
                with destination.open("wb") as handle:
                    async for item in speech.stream():
                        if item["type"] == "audio":
                            handle.write(item["data"])
                        elif item["type"] == "WordBoundary":
                            events.append({k: item[k] for k in ["offset", "duration", "text"]})
                break
            except (OSError, edge_tts.exceptions.EdgeTTSException):
                if attempt:
                    raise
                events = []
                await asyncio.sleep(1)
        duration = float(probe(destination)["format"]["duration"])
        result = {"text": text, "file": str(destination), "duration": duration, "words": events}
        dump(metadata, result)
        print(f"VOICE {chapter:02d}/{index:02d} {duration:.2f}s", flush=True)
        return result


async def prepare_voices():
    chapters = plan()
    gate = asyncio.Semaphore(3)
    for chapter in chapters:
        directory = PRODUCTION / f"{chapter['id']:02d}"
        if (directory / "voice.json").exists():
            continue
        paragraphs = await asyncio.gather(*[
            voice_paragraph(chapter["id"], i + 1, text, gate)
            for i, text in enumerate(chapter["paragraphs"])
        ])
        offset = .45
        samples = []
        for item in paragraphs:
            wav = Path(item["file"]).with_suffix(".wav")
            if not wav.exists():
                subprocess.run(
                    [FFMPEG, "-y", "-v", "error", "-i", item["file"],
                     "-af", "highpass=f=65,loudnorm=I=-17:TP=-2:LRA=8",
                     "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(wav)],
                    check=True, timeout=60,
                )
            with wave.open(str(wav)) as audio:
                sound = np.frombuffer(audio.readframes(audio.getnframes()), dtype="<i2").copy()
            item.update(start=offset, end=offset + len(sound) / 48000, wav=str(wav))
            offset = item["end"] + .22
            samples.append(sound)
        duration = math.ceil((offset + .45) * FPS) / FPS
        mixed = np.zeros(round(duration * 48000), np.float32)
        for item, sound in zip(paragraphs, samples):
            start_sample = round(item["start"] * 48000)
            mixed[start_sample:start_sample + len(sound)] += sound.astype(np.float32) / 32768
        rng = np.random.default_rng(20261024 + chapter["id"])
        for item in paragraphs:
            at = max(0, round((item["start"] - .08) * 48000))
            length = min(2400, len(mixed) - at)
            mixed[at:at + length] += rng.normal(0, .008, length) * np.exp(-np.arange(length) / 350)
        mix = directory / "narration.wav"
        with wave.open(str(mix), "wb") as audio:
            audio.setparams((1, 2, 48000, 0, "NONE", "not compressed"))
            audio.writeframes((np.clip(mixed, -.98, .98) * 32767).astype("<i2").tobytes())
        dump(directory / "voice.json", {
            "chapter": chapter["id"], "provider": "Microsoft Edge zh-CN-YunxiNeural",
            "duration": duration, "mix": str(mix), "paragraphs": paragraphs,
        })
        print(f"VOICE_CHAPTER_READY {chapter['id']:02d} {duration:.2f}s", flush=True)


def generation_graph(chapter):
    schema = {
        "workflow_id": "minimax_h3_lightx2v_no_pic",
        "fields": [
            {"name": "prompt", "type": "prompt", "slot": "ad_text_01", "required": True},
            {"name": "resolution", "type": "enum", "slot": "ad_text_02"},
            {"name": "duration", "type": "integer", "slot": "ad_int_01"},
            {"name": "seed", "type": "integer", "slot": "ad_int_02"},
        ],
        "outputs": [{"name": "video", "kind": "video"}],
    }
    return {
        "1": {"class_type": "AutoDLWorkflow", "inputs": {
            "workflow_id": schema["workflow_id"], "schema_json": json.dumps(schema),
            "ad_text_01": STYLE + chapter["asset"], "ad_text_02": "768p横",
            "ad_int_01": 5, "ad_int_02": 2026102400 + chapter["id"],
            "timeout_seconds": 1800, "poll_interval_seconds": 5,
        }},
        "2": {"class_type": "AutoDLPreviewVideo", "inputs": {"video": ["1", 0]}},
    }


def queue_once(directory, name, prompt):
    record = directory / f"{name}-submission.json"
    if record.exists():
        data = json.loads(record.read_text())
        if "prompt_id" not in data:
            raise RuntimeError(f"{name}: submission outcome uncertain; no automatic resubmission.")
        return data["prompt_id"]
    with record.open("x") as handle:
        json.dump({"state": "submission_started"}, handle)
    response = requests.post(BASE + "/prompt", json={
        "prompt": prompt, "client_id": "skyscraper-full-film-20261024",
    }, timeout=30)
    response.raise_for_status()
    data = response.json()
    dump(record, data)
    return data["prompt_id"]


def wait_prompt(prompt_id, label):
    for _ in range(400):
        response = requests.get(BASE + "/history/" + prompt_id, timeout=15)
        response.raise_for_status()
        entry = response.json().get(prompt_id)
        if entry:
            if entry["status"]["status_str"] != "success":
                raise RuntimeError(f"{label} failed in ComfyUI; no cloud retry was submitted.")
            return entry
        time.sleep(5)
    raise TimeoutError(f"{label}: still unconfirmed; original task is retained.")


def generate(chapter):
    directory = PRODUCTION / f"{chapter['id']:02d}"
    cached = directory / "motion.mp4"
    if cached.exists():
        return cached
    api = generation_graph(chapter)
    dump(directory / "workflow-generate-api.json", api)
    prompt_id = queue_once(directory, "generation", api)
    print(f"CHAPTER_GENERATING {chapter['id']:02d} {prompt_id}", flush=True)
    result = wait_prompt(prompt_id, f"Chapter {chapter['id']} generation")
    paths = result.get("outputs", {}).get("1", {}).get("autodl_files", [])
    videos = [Path(p) for p in paths if Path(p).suffix.lower() in {".mp4", ".mov", ".webm"}]
    if not videos:
        raise RuntimeError("Generation succeeded but no local video was returned.")
    shutil.copy2(videos[0], cached)
    dump(directory / "generation-result.json", {
        "prompt_id": prompt_id, "source_file": str(videos[0]), "cached": str(cached),
        "illustration": True, "probe": probe(cached),
    })
    print(f"CHAPTER_ASSET_READY {chapter['id']:02d}", flush=True)
    return cached


def render_chapter(chapter, revision=1):
    directory = PRODUCTION / f"{chapter['id']:02d}"
    output = directory / f"chapter-{chapter['id']:02d}.mp4"
    if output.exists() and (directory / "verification.json").exists():
        verification = json.loads((directory / "verification.json").read_text())
        if verification.get("revision", 0) >= revision:
            return output
    while not (directory / "voice.json").exists():
        time.sleep(2)
    api = {
        "1": {"class_type": "SCFullChapter", "inputs": {"chapter": chapter["id"], "revision": revision}},
        "2": {"class_type": "SaveVideo", "inputs": {
            "video": ["1", 0], "filename_prefix": f"skyscraper_full/chapter-{chapter['id']:02d}",
            "format": "auto", "format.codec": "auto",
        }},
    }
    name = "render" if revision == 1 else f"render-r{revision}"
    dump(directory / f"workflow-{name}-api.json", api)
    prompt_id = queue_once(directory, name, api)
    print(f"CHAPTER_RENDERING {chapter['id']:02d} {prompt_id}", flush=True)
    wait_prompt(prompt_id, f"Chapter {chapter['id']} render")
    if not output.exists():
        raise RuntimeError("ComfyUI reported success but the chapter output is absent.")
    print(f"CHAPTER_COMPLETE {chapter['id']:02d} {output}", flush=True)
    return output


def assemble():
    chapters = plan()
    outputs = [PRODUCTION / f"{c['id']:02d}" / f"chapter-{c['id']:02d}.mp4" for c in chapters]
    if not all(p.exists() for p in outputs):
        raise RuntimeError("All eight chapters must exist before final assembly.")
    listing = PRODUCTION / "concat.txt"
    listing.write_text("".join(f"file '{p}'\n" for p in outputs), encoding="utf-8")
    output = PRODUCTION / "繁荣的高度-完整版.mp4"
    subprocess.run([
        FFMPEG, "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
        "-c", "copy", "-movflags", "+faststart", str(output),
    ], check=True, timeout=180)
    subtitles = []
    chapter_times = []
    elapsed = 0
    for chapter, path in zip(chapters, outputs):
        voice = json.loads((path.parent / "voice.json").read_text())
        subs = json.loads((path.parent / "subtitles.json").read_text())
        subtitles.extend({**item, "start": item["start"] + elapsed, "end": item["end"] + elapsed} for item in subs)
        duration = float(probe(path)["format"]["duration"])
        chapter_times.append({"chapter": chapter["id"], "title": chapter["title"], "start": elapsed, "duration": duration})
        elapsed += duration
    write_srt(PRODUCTION / "繁荣的高度-完整版.srt", subtitles)
    dump(PRODUCTION / "chapters.json", chapter_times)
    dump(PRODUCTION / "verification.json", {"video": str(output), "probe": probe(output), "chapters": chapter_times})
    print(f"FILM_COMPLETE {output}", flush=True)


def write_srt(path, items):
    def stamp(seconds):
        milliseconds = round(seconds * 1000)
        hours, milliseconds = divmod(milliseconds, 3600000)
        minutes, milliseconds = divmod(milliseconds, 60000)
        seconds, milliseconds = divmod(milliseconds, 1000)
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"
    Path(path).write_text("\n".join(
        f"{i + 1}\n{stamp(s['start'])} --> {stamp(s['end'])}\n{s['text']}\n"
        for i, s in enumerate(items)
    ), encoding="utf-8")


def export_workflows():
    final = PRODUCTION / "繁荣的高度-完整版.mp4"
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(final, INPUT_DIR / "skyscraper-full-film.mp4")
    chapters = plan()

    def node(number, kind, position, size, title, widgets, inputs=None, outputs=None):
        return {
            "id": number, "type": kind, "pos": position, "size": size,
            "flags": {}, "order": number, "mode": 0,
            "inputs": inputs or [], "outputs": outputs or [],
            "properties": {"Node name for S&R": kind},
            "widgets_values": widgets, "title": title,
        }

    def workflow(nodes, links, scale):
        return {
            "id": str(uuid.uuid4()), "revision": 0,
            "last_node_id": max(n["id"] for n in nodes), "last_link_id": len(links),
            "nodes": nodes, "links": links, "groups": [], "config": {},
            "extra": {"ds": {"scale": scale, "offset": [20, 20]}}, "version": .4,
        }

    preview = workflow([
        node(1, "LoadVideo", [40, 220], [480, 420], "完整版 · 本地成片", ["skyscraper-full-film.mp4"],
             outputs=[{"name": "VIDEO", "type": "VIDEO", "links": [1], "slot_index": 0}]),
        node(2, "SaveVideo", [620, 220], [520, 460], "播放 / 导出完整版",
             ["skyscraper_full/繁荣的高度-完整版", "auto", "auto"],
             inputs=[{"name": "video", "type": "VIDEO", "link": 1}],
             outputs=[{"name": "video", "type": "VIDEO", "links": None}]),
        node(3, "Note", [40, 20], [1100, 155], "完整版说明", [
            "《繁荣的高度》完整科普视频 · 01–08 顺序合成\n"
            "78 段旁白对应人物情境、合同、时间线和金融机制图解。含中文配音和字幕。\n"
            "本工作流读取已完成的本地 MP4；运行只用于预览及导出，不提交云端生成。"
        ]),
    ], [[1, 1, 0, 2, 0, "VIDEO"]], .8)
    nodes, links = [], []
    for chapter in chapters:
        index = chapter["id"] - 1
        first, second = index * 2 + 1, index * 2 + 2
        x, y = (index % 2) * 940 + 40, (index // 2) * 590 + 230
        link_id = index + 1
        verified = json.loads((PRODUCTION / f"{chapter['id']:02d}/verification.json").read_text())
        nodes.extend([
            node(first, "SCFullChapter", [x, y], [410, 145],
                 f"{chapter['id']:02d}｜{chapter['title']}",
                 [chapter["id"], verified["revision"]],
                 outputs=[
                     {"name": "video", "type": "VIDEO", "links": [link_id], "slot_index": 0},
                     {"name": "file_path", "type": "STRING", "links": None, "slot_index": 1},
                 ]),
            node(second, "SaveVideo", [x + 460, y], [410, 460], f"导出第 {chapter['id']:02d} 章",
                 [f"skyscraper_full/chapter-{chapter['id']:02d}-local", "auto", "auto"],
                 inputs=[{"name": "video", "type": "VIDEO", "link": link_id}],
                 outputs=[{"name": "video", "type": "VIDEO", "links": None}]),
        ])
        links.append([link_id, first, 0, second, 0, "VIDEO"])
    nodes.append(node(17, "Note", [40, 20], [1810, 150], "01–08 本地重剪", [
        "01–08 已按台词逐段生成。此工作流从本地素材、旁白和分镜重新合成各章。\n"
        "可在 film_visuals.py 调整画面后，提高 revision 触发本地重剪。"
        "本工作流不包含云端生成节点，不会重新提交 H3 任务。\n"
        "各章成片保存在 full-film/01 至 08；完整版另见 workflow-preview.json。"
    ]))
    recompose = workflow(nodes, links, .42)
    user_workflows = ROOT / "comfy-user/default/workflows"
    for filename, title, data in [
        ("workflow-preview.json", "繁荣的高度 - 01至08完整版预览", preview),
        ("workflow-chapters.json", "繁荣的高度 - 01至08本地分章重剪", recompose),
    ]:
        dump(PRODUCTION / filename, data)
        dump(user_workflows / f"{title}.json", data)
    print("LOCAL_WORKFLOWS_READY", flush=True)


def run():
    chapters = plan()
    start()
    for chapter in chapters:
        generate(chapter)
        render_chapter(chapter)
    assemble()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["plan", "start", "voices", "generate", "render", "run", "assemble", "workflows"])
    parser.add_argument("--chapter", type=int, default=1, choices=range(1, 9))
    parser.add_argument("--revision", type=int, default=1)
    args = parser.parse_args()
    PRODUCTION.mkdir(exist_ok=True)
    if args.action == "plan":
        plan()
        print("78 narration paragraphs mapped to 78 content-specific scenes.")
    elif args.action == "start":
        start()
    elif args.action == "voices":
        asyncio.run(prepare_voices())
    elif args.action == "generate":
        start()
        generate(plan()[args.chapter - 1])
    elif args.action == "render":
        render_chapter(plan()[args.chapter - 1], args.revision)
    elif args.action == "run":
        run()
    elif args.action == "workflows":
        export_workflows()
    else:
        assemble()
