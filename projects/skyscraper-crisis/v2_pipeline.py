"""Sequential ComfyUI generation, verified chapter renders, and V2 delivery."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import uuid

import requests
from PIL import Image, ImageDraw, ImageFont

from full_film import ROOT, BASE, FFMPEG, PRODUCTION, INPUT_DIR, dump, probe, queue_once, wait_prompt, write_srt
from v2_plan import V2, ASSETS, OLD, make_plan


def generate():
    for number in range(1, 9):
        record = V2 / f"generation-{number:02d}.json"
        if record.exists():
            status = json.loads(record.read_text())
            if not status["failed"] and all(Path(p).exists() for p in status["completed"]):
                print(f"GENERATION_CACHED {number:02d}", flush=True)
                continue
        directory = V2 / f"{number:02d}"
        directory.mkdir(exist_ok=True)
        graph = {"1": {"class_type": "SCSceneBatch", "inputs": {"chapter": number, "workers": 3, "revision": 3}}}
        dump(directory / "workflow-generate-api.json", graph)
        prompt_id = queue_once(directory, "batch-r3", graph)
        print(f"V2_CHAPTER_GENERATING {number:02d} {prompt_id}", flush=True)
        wait_prompt(prompt_id, f"V2 chapter {number:02d} scenes")
        print(f"V2_CHAPTER_ASSETS_COMPLETE {number:02d}", flush=True)


def render(revision=20):
    for number in range(1, 9):
        directory = V2 / f"{number:02d}"
        directory.mkdir(exist_ok=True)
        record = directory / "verification.json"
        if record.exists() and json.loads(record.read_text()).get("revision", 0) >= revision:
            print(f"RENDER_CACHED {number:02d}", flush=True)
            continue
        graph = {
            "1": {"class_type": "SCFullChapter", "inputs": {"chapter": number, "revision": revision}},
        }
        dump(directory / "workflow-render-api.json", graph)
        prompt_id = queue_once(directory, f"render-r{revision}", graph)
        print(f"V2_CHAPTER_RENDERING {number:02d} {prompt_id}", flush=True)
        wait_prompt(prompt_id, f"V2 chapter {number:02d} render")
        print(f"V2_CHAPTER_COMPLETE {number:02d}", flush=True)


def assemble():
    paths = [V2 / f"{n:02d}/chapter-{n:02d}.mp4" for n in range(1, 9)]
    if not all(p.exists() for p in paths):
        raise RuntimeError("Eight revised chapter outputs are required.")
    listing = V2 / "concat.txt"
    listing.write_text("".join(f"file '{p}'\n" for p in paths), encoding="utf-8")
    output = V2 / "繁荣的高度-V2-情节重制完整版.mp4"
    subprocess.run([
        FFMPEG, "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
        "-c", "copy", "-movflags", "+faststart", str(output),
    ], check=True, timeout=180)
    subtitles, chapters, elapsed = [], [], 0
    for number, path in enumerate(paths, 1):
        d = float(probe(path)["format"]["duration"])
        title = make_plan()[number - 1]["title"]
        chapters.append({"chapter": number, "title": title, "start": elapsed, "duration": d})
        subtitles += [{**s, "start": s["start"] + elapsed, "end": s["end"] + elapsed}
                      for s in json.loads((path.parent / "subtitles.json").read_text())]
        elapsed += d
    write_srt(V2 / "繁荣的高度-V2-完整版.srt", subtitles)
    dump(V2 / "chapters.json", chapters)
    verify(output)
    print(f"V2_FILM_COMPLETE {output}", flush=True)
    return output


def verify(output):
    from v2_visuals import Media
    media = Media()
    chapters = make_plan()
    audit = []
    for ch in chapters:
        number = ch["chapter"]
        scenes = json.loads((V2 / f"{number:02d}/timeline.json").read_text())
        original = json.loads((PRODUCTION / f"{number:02d}/voice.json").read_text())
        if [s["narration"] for s in scenes] != [p["text"] for p in original["paragraphs"]]:
            raise AssertionError("Approved narration changed.")
        for scene in scenes:
            for key in scene["assets"]:
                if key not in {"paper_study", "paper_debate", "dubai_notice"} and not media.path(key).exists():
                    raise AssertionError("Unfulfilled scene asset " + key)
        target = json.loads((V2 / f"{number:02d}/verification.json").read_text())
        video = target["probe"]
        durations = {s["codec_type"]: float(s.get("duration", 0)) for s in video["streams"]}
        if abs(durations["video"] - original["duration"]) > .1 or abs(durations["audio"] - original["duration"]) > .1:
            raise AssertionError("Chapter audio/video duration mismatch.")
        audit.append({
            "chapter": number, "paragraphs": len(scenes),
            "photographic_beats": sum(len(s["beats"]) for s in scenes),
            "assets": sorted({a for s in scenes for a in s["assets"]}),
            "narration_unchanged": True, "duration": original["duration"],
        })
    subprocess.run([FFMPEG, "-v", "error", "-i", str(output), "-f", "null", "-"], check=True, timeout=180)
    dump(V2 / "content-audit.json", {
        "approved_script_sha256": hashlib.sha256((ROOT / "SCRIPT_FULL_V1.md").read_bytes()).hexdigest(),
        "chapters": audit, "paragraphs": sum(a["paragraphs"] for a in audit),
        "photographic_beats": sum(a["photographic_beats"] for a in audit),
        "new_generated_clips": len(list((V2 / "assets").glob("*/result.json"))),
        "accepted_new_mechanism_clips": len(ASSETS),
        "landmark_generated_candidates_excluded": [
            k for k in ["esb_motion", "burj_motion", "petronas_motion"]
            if (V2 / "assets" / k / "result.json").exists()
        ],
        "landmark_final_source": "Verified whole-building photographs, with motion composed in ComfyUI.",
        "distinct_media": sorted({a for ch in audit for a in ch["assets"]}),
        "full_decode_passed": True, "final_probe": probe(output),
        "manual_visual_review": "Contact sheets and selected moving excerpts reviewed separately; see visual-review.json.",
    })
    print("V2_VERIFIED decode, narration, source presence, chapter timing", flush=True)


def highlights():
    """Six representative scenes with their real aligned narration."""
    chapters = {c["chapter"]: c for c in json.loads((V2 / "chapters.json").read_text())}
    final = V2 / "繁荣的高度-V2-情节重制完整版.mp4"
    selected = [
        (1, 3, "工人失业"), (3, 4, "借贷签约"), (4, 6, "工地竞争"),
        (6, 2, "租户减少"), (6, 4, "再融资"), (7, 6, "证据检验"),
    ]
    directory = V2 / "highlights"
    directory.mkdir(exist_ok=True)
    segments = []
    font_path = os.environ.get("SC_FONT", "/System/Library/Fonts/STHeiti Medium.ttc")
    face = ImageFont.truetype(font_path, 33)
    for i, (number, scene_number, label) in enumerate(selected):
        scene = json.loads((V2 / f"{number:02d}/timeline.json").read_text())[scene_number - 1]
        start = chapters[number]["start"] + scene["start"]
        duration = scene["end"] - scene["start"]
        part = directory / f"{i + 1:02d}.mp4"
        subprocess.run([
            FFMPEG, "-y", "-v", "error", "-ss", str(start), "-i", str(final),
            "-t", str(duration), "-map", "0:v", "-map", "0:a",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "160k",
            "-movflags", "+faststart", str(part),
        ], check=True, timeout=60)
        segments.append(part)
    # A clean six-panel contact sheet, keeping each full video frame intact.
    board = Image.new("RGB", (1920, 1740), (230, 230, 228))
    draw = ImageDraw.Draw(board)
    for i, (number, scene_number, label) in enumerate(selected):
        x, y = (i % 2) * 960, (i // 2) * 580
        draw.text((x + 20, y + 3), f"{i + 1:02d}  {label}", font=face, fill=(164, 36, 39))
        file = sorted((V2 / f"{number:02d}").glob(f"scene-{scene_number:02d}-beat-*.jpg"))[0]
        with Image.open(file) as image:
            board.paste(image.resize((960, 540)), (x, y + 40))
    board.save(V2 / "六类情节画面核对.jpg", quality=94)
    listing = directory / "concat.txt"
    listing.write_text("".join(f"file '{p}'\n" for p in segments), encoding="utf-8")
    output = V2 / "六类经济现象-画面核对片.mp4"
    subprocess.run([
        FFMPEG, "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
        "-c", "copy", "-movflags", "+faststart", str(output),
    ], check=True, timeout=60)
    print("V2_HIGHLIGHTS", output, flush=True)


def node(n, kind, pos, size, title, widgets, inputs=None, outputs=None):
    return {
        "id": n, "type": kind, "pos": pos, "size": size, "flags": {}, "order": n, "mode": 0,
        "inputs": inputs or [], "outputs": outputs or [],
        "properties": {"Node name for S&R": kind}, "widgets_values": widgets, "title": title,
    }


def workflow(nodes, links, scale):
    return {
        "id": str(uuid.uuid4()), "revision": 0, "version": .4, "last_node_id": max(n["id"] for n in nodes),
        "last_link_id": len(links), "nodes": nodes, "links": links, "groups": [], "config": {},
        "extra": {"ds": {"scale": scale, "offset": [20, 20]}},
    }


def workflows(final=False):
    nodes, links = [], []
    for i, ch in enumerate(make_plan()):
        n = i + 1
        x, y = (i % 4) * 560 + 40, (i // 4) * 430 + 220
        inputs = [{"name": "previous", "type": "VIDEO", "link": i if i else None}]
        outputs = [
            {"name": "last_shot", "type": "VIDEO", "links": [n] if n < 8 else None, "slot_index": 0},
            {"name": "file_path", "type": "STRING", "links": None, "slot_index": 1},
        ]
        nodes.append(node(n, "SCSceneBatch", [x, y], [500, 230], f"{n:02d}｜{ch['title']} · 情境素材", [n, 3, 1], inputs, outputs))
        if i:
            links.append([i, i, 0, n, 0, "VIDEO"])
    nodes.append(node(9, "Note", [40, 20], [2180, 150], "V2 · 逐段台词对应情节", [
        "01—08 顺序制备具体情境素材。每章最多并行3条；已保存的素材直接复用。\n"
        "工厂停工 / 银行签约 / 多工地抢租户 / 企业搬离 / 到期续贷 / 估值 / 完整样本检验。\n"
        "具名建筑使用核实实景照片的黑白动态拼贴；人物经济机制由ComfyUI生成。\n"
        "中文金额、日期由后期准确排版。"
    ]))
    data = workflow(nodes, links, .58)
    dest = ROOT / "comfy-user/default/workflows"
    dump(dest / "繁荣的高度 V2 - 01至08情境素材生成.json", data)
    dump(V2 / "workflow-generation.json", data)
    if final:
        name = "skyscraper-v2-full-film.mp4"
        source = V2 / "繁荣的高度-V2-情节重制完整版.mp4"
        INPUT_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, INPUT_DIR / name)
        nodes = [
            node(1, "LoadVideo", [40, 210], [490, 420], "V2 完整版 · 情节重制", [name],
                 outputs=[{"name": "VIDEO", "type": "VIDEO", "links": [1], "slot_index": 0}]),
            node(2, "SaveVideo", [630, 210], [560, 470], "播放 V2 / 导出", ["skyscraper_v2/繁荣的高度-V2", "auto", "auto"],
                 inputs=[{"name": "video", "type": "VIDEO", "link": 1}],
                 outputs=[{"name": "video", "type": "VIDEO", "links": None}]),
            node(3, "Note", [40, 20], [1150, 150], "新版内容", [
                "V2 · 78段旁白 / 01—08顺序成片 / 新增人物、合同、搬离、再融资与证据检验镜头。\n"
                "历史图片有来源，生成影像标注情境重建。完整字幕与配音沿用获准台词。\n"
                "此预览只读取本地成片。素材生成工作流另存，旧版成片保留。"
            ]),
        ]
        preview = workflow(nodes, [[1, 1, 0, 2, 0, "VIDEO"]], .8)
        dump(dest / "繁荣的高度 V2 - 完整版预览.json", preview)
        dump(V2 / "workflow-preview.json", preview)
    print("V2_WORKFLOWS_READY", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["generate", "render", "assemble", "highlights", "workflows", "run"])
    parser.add_argument("--revision", type=int, default=20)
    args = parser.parse_args()
    if args.action == "run":
        generate()
        render(args.revision)
        assemble()
        highlights()
        workflows(True)
    elif args.action == "generate":
        generate()
    elif args.action == "render":
        render(args.revision)
    elif args.action == "assemble":
        assemble()
    elif args.action == "highlights":
        highlights()
    else:
        workflows((V2 / "繁荣的高度-V2-情节重制完整版.mp4").exists())
