"""Submit unique V2 shot jobs through the user's running ComfyUI instance."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import unquote, urlparse

from PIL import Image, ImageDraw, ImageFont
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from full_film import BASE, FFMPEG, dump, probe, queue_once, wait_prompt
from v2_plan import ASSETS, STYLE, V2, make_plan

FONT = os.environ.get("SC_FONT", "/System/Library/Fonts/STHeiti Medium.ttc")


def graph(key):
    if key in ASSETS:
        chapter, title, subject = ASSETS[key]
        workflow = "minimax_h3_lightx2v_no_pic"
        duration = 8
        reference = None
        prompt = STYLE + subject
    else:
        references = {
            "esb_motion": ("esb_photo.jpg", "Empire State Building", 1),
            "burj_motion": ("burj_photo.jpg", "Burj Khalifa", 1),
            "petronas_motion": ("petronas_photo.jpg", "PETRONAS Twin Towers", 5),
        }
        filename, title, chapter = references[key]
        reference = V2 / "research" / filename
        if not reference.exists():
            raise FileNotFoundError(reference)
        workflow = "minimax_h3_lightx2v_v5"
        duration = 8
        prompt = (
            f"Use the supplied photograph as the strict architecture reference for the {title}. "
            "Preserve the exact number of towers, the entire recognizable silhouette, "
            "spire, stepped setbacks, proportions and any skybridge. "
            "A neutral black-and-white photographic architectural shot in soft daylight, "
            "restrained silver-gelatin print texture. A very slow gentle camera push, "
            "the whole building remains visible with no silhouette morphing. "
            "Architecture is static and coherent, no extra towers, no imaginary structures. "
            "No text, no titles, no logos, no watermark, no annotations. "
            "This is an architectural reconstruction, not historical archival footage."
        )
    fields = [
        {"name": "prompt", "type": "prompt", "slot": "ad_text_01", "required": True},
        {"name": "resolution", "type": "enum", "slot": "ad_text_02"},
        {"name": "duration", "type": "integer", "slot": "ad_int_01"},
        {"name": "seed", "type": "integer", "slot": "ad_int_02"},
    ]
    inputs = {
        "workflow_id": workflow,
        "ad_text_01": prompt, "ad_text_02": "768p横",
        "ad_int_01": duration, "ad_int_02": 2026102500 + sum((i + 1) * ord(c) for i, c in enumerate(key)),
        "timeout_seconds": 1800, "poll_interval_seconds": 5,
    }
    if reference:
        # Local paths are encoded to data URIs by the AutoDL plugin, without
        # putting a token or an expiring URL in the exported workflow.
        fields.append({"name": "ref_image_0", "type": "image", "slot": "ad_image_01", "required": True})
        inputs["ad_image_01"] = str(reference)
    inputs["schema_json"] = json.dumps({
        "version": 6, "workflow_id": workflow, "fields": fields,
        "outputs": [{"name": "video", "kind": "video"}],
    })
    return {
        "1": {"class_type": "AutoDLWorkflow", "inputs": inputs},
        "2": {"class_type": "AutoDLPreviewVideo", "inputs": {"video": ["1", 0]}},
    }, chapter, title, prompt


def generate(key):
    folder = V2 / "assets" / key
    folder.mkdir(parents=True, exist_ok=True)
    output = folder / "motion.mp4"
    if output.exists() and (folder / "result.json").exists():
        print("CACHED", key, flush=True)
        return output
    api, chapter, title, prompt = graph(key)
    dump(folder / "workflow-api.json", api)
    dump(folder / "brief.json", {
        "id": key, "chapter": chapter, "title": title, "prompt": prompt,
        "illustrative_reconstruction": True,
    })
    prompt_id = queue_once(folder, "generation-valid", api)
    print(f"GENERATING {chapter:02d} {key} {prompt_id}", flush=True)
    result = wait_prompt(prompt_id, key)
    files = result.get("outputs", {}).get("1", {}).get("autodl_files", [])
    videos = [Path(f) for f in files if Path(f).suffix.lower() in {".mp4", ".mov", ".webm"}]
    if not videos:
        raise RuntimeError(f"No saved video for {key}; original submission retained.")
    shutil.copy2(videos[0], output)
    info = probe(output)
    dump(folder / "result.json", {
        "id": key, "prompt_id": prompt_id, "source_file": str(videos[0]),
        "file": str(output), "probe": info, "chapter": chapter,
    })
    contact(key)
    print(f"ASSET_READY {key} {info['format']['duration']}s", flush=True)
    return output


def contact(key):
    folder = V2 / "assets" / key
    path = folder / "motion.mp4"
    duration = float(probe(path)["format"]["duration"])
    sheet = Image.new("RGB", (1440, 320), (229, 229, 226))
    draw = ImageDraw.Draw(sheet)
    face = ImageFont.truetype(FONT, 23)
    for i, fraction in enumerate([.12, .50, .88]):
        result = subprocess.run([
            FFMPEG, "-v", "error", "-ss", str(duration * fraction), "-i", str(path),
            "-frames:v", "1", "-vf", "scale=480:270:force_original_aspect_ratio=increase,crop=480:270",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
        ], check=True, capture_output=True)
        sheet.paste(Image.frombytes("RGB", (480, 270), result.stdout), (i * 480, 40))
        draw.text((i * 480 + 12, 6), f"{key}  {duration * fraction:.1f}s", font=face, fill=(25, 25, 25))
    sheet.save(folder / "contact.jpg", quality=92)


def all_keys():
    # Exact landmarks use sourced photographs in the compositor after the
    # first two generative candidates failed the geometry review.
    keys = list(ASSETS)
    return sorted(keys, key=lambda k: ASSETS[k][0] if k in ASSETS else 5 if k == "petronas_motion" else 1)


def generate_inside_comfy(key):
    """Called only by the project ComfyUI node; runs the installed AutoDL node."""
    import nodes
    folder = V2 / "assets" / key
    folder.mkdir(parents=True, exist_ok=True)
    output = folder / "motion.mp4"
    if output.exists() and (folder / "result.json").exists():
        return str(output)
    api, chapter, title, prompt = graph(key)
    marker = folder / "batch-v3-submission.json"
    if marker.exists():
        raise RuntimeError(f"{key}: retained prior submission; no automatic resubmission.")
    if (folder / "generation-valid-submission.json").exists():
        raise RuntimeError(f"{key}: earlier ComfyUI submission must be harvested first.")
    dump(folder / "workflow-api.json", api)
    dump(folder / "brief.json", {
        "id": key, "chapter": chapter, "title": title, "prompt": prompt,
        "illustrative_reconstruction": True,
    })
    node_class = nodes.NODE_CLASS_MAPPINGS["AutoDLWorkflow"]
    plugin = sys.modules[node_class.__module__]
    values = api["1"]["inputs"]
    slot_values = {k: v for k, v in values.items() if k.startswith("ad_")}
    try:
        body = plugin._build_synced_request_body(values["workflow_id"], values["schema_json"], "{}", slot_values)
        dump(folder / "preflight.json", {"ok": True, "remote_fields": list(body)})
    except ValueError as exc:
        dump(folder / "preflight.json", {"ok": False, "error": str(exc)})
        raise
    with marker.open("x") as handle:
        json.dump({"state": "submission_started", "via": "SCSceneBatch / AutoDLWorkflow"}, handle)
    print(f"V2_COMFY_SHOT_START {chapter:02d} {key}", flush=True)
    result = node_class().run(**values)
    files = result.get("ui", {}).get("autodl_files", [])
    videos = [Path(f) for f in files if Path(f).suffix.lower() in {".mp4", ".mov", ".webm"}]
    if not videos:
        raise RuntimeError(f"{key}: no saved video returned.")
    shutil.copy2(videos[0], output)
    dump(folder / "result.json", {
        "id": key, "source_file": str(videos[0]), "file": str(output),
        "probe": probe(output), "chapter": chapter, "via": "ComfyUI SCSceneBatch / AutoDLWorkflow",
    })
    dump(marker, {"state": "complete", "file": str(output)})
    contact(key)
    print(f"V2_COMFY_SHOT_READY {chapter:02d} {key}", flush=True)
    return str(output)


def generate_chapter_inside_comfy(chapter, workers=3):
    import nodes
    node_class = nodes.NODE_CLASS_MAPPINGS["AutoDLWorkflow"]
    plugin = sys.modules[node_class.__module__]
    original_download = plugin._download_file

    def bounded_download(url, target_directory, filename_stem, *, timeout_seconds, max_bytes):
        # Cloud media hosts can throttle a single connection. Range transfers
        # affect only downloading an already generated result, never job billing.
        try:
            with requests.get(url, headers={"Range": "bytes=0-0"}, stream=True, timeout=(15, 45)) as response:
                match = re.fullmatch(r"bytes 0-0/(\d+)", response.headers.get("Content-Range", ""))
                if response.status_code != 206 or not match:
                    return original_download(url, target_directory, filename_stem, timeout_seconds=timeout_seconds, max_bytes=max_bytes)
                length = int(match[1])
                extension = plugin._extension_for(url, response.headers.get("Content-Type", ""))
            if length > min(max_bytes, 256 * 1024 * 1024):
                return original_download(url, target_directory, filename_stem, timeout_seconds=timeout_seconds, max_bytes=max_bytes)
            ranges = [(length * i // 4, length * (i + 1) // 4 - 1) for i in range(4)]

            def fragment(bounds):
                first, last = bounds
                for attempt in range(2):
                    try:
                        r = requests.get(url, headers={"Range": f"bytes={first}-{last}"}, timeout=(15, 150))
                        if r.status_code != 206 or len(r.content) != last - first + 1:
                            raise ValueError("Incomplete result download range")
                        return r.content
                    except (requests.RequestException, ValueError):
                        if attempt:
                            raise RuntimeError("Result media range could not be downloaded; existing cloud job is retained.") from None
                raise AssertionError("unreachable")

            with ThreadPoolExecutor(max_workers=4) as downloads:
                chunks = list(downloads.map(fragment, ranges))
            destination = target_directory / f"{filename_stem}{extension}"
            if destination.exists():
                destination = target_directory / f"{filename_stem}-{time.time_ns()}{extension}"
            partial = destination.with_suffix(destination.suffix + ".v2part")
            with partial.open("wb") as handle:
                for chunk in chunks:
                    handle.write(chunk)
            if partial.stat().st_size != length:
                raise RuntimeError("Downloaded result length mismatch")
            partial.replace(destination)
            return destination
        except requests.RequestException:
            return original_download(url, target_directory, filename_stem, timeout_seconds=timeout_seconds, max_bytes=max_bytes)

    plugin._download_file = bounded_download
    keys = [k for k in all_keys() if (ASSETS[k][0] if k in ASSETS else 5 if k == "petronas_motion" else 1) == chapter]
    completed, failed = [], []
    try:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            jobs = {pool.submit(generate_inside_comfy, key): key for key in keys}
            for future in as_completed(jobs):
                try:
                    completed.append(future.result())
                except Exception as exc:
                    failed.append((jobs[future], type(exc).__name__))
    finally:
        plugin._download_file = original_download
    dump(V2 / f"generation-{chapter:02d}.json", {
        "chapter": chapter, "keys": keys, "completed": completed, "failed": failed,
    })
    if failed:
        raise RuntimeError(f"Chapter {chapter:02d} has retained failed submissions: {failed}")
    return completed[-1]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets", nargs="+")
    args = parser.parse_args()
    make_plan()
    for key in args.assets or all_keys():
        generate(key)
