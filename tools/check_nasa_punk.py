"""Check the NASA-punk publication archive, without claiming semantic approval."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projects/nasa-punk"
SOURCE = PROJECT / "source"


def read_json(filename):
    return json.loads(filename.read_text(encoding="utf-8"))


def sha256(filename):
    digest = hashlib.sha256()
    with filename.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []
        self.chapters = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.targets.extend(attrs[key] for key in ("href", "src", "poster") if attrs.get(key))
        if tag == "a" and "data-time" in attrs:
            self.chapters.append(attrs)


def cues(text, vtt=False):
    text = text.replace("\r\n", "\n").strip()
    if vtt:
        assert text.startswith("WEBVTT\n"), "Missing WebVTT header"
        text = text[len("WEBVTT"):].strip()
    result = []
    for block in re.split(r"\n\s*\n", text):
        number, timing, *caption = block.splitlines()
        start, end = timing.split(" --> ")

        def seconds(value):
            hours, minutes, seconds = value.replace(",", ".").split(":")
            return int(hours) * 3600 + int(minutes) * 60 + float(seconds)

        result.append((int(number), seconds(start), seconds(end), "\n".join(caption)))
    return result


def validate(media=False, report_output=None):
    checks = []

    def require(condition, name):
        assert condition, name
        checks.append(name)

    manifest = read_json(PROJECT / "delivery-manifest.json")
    timeline = read_json(SOURCE / "rebuild-timeline.json")
    inventory = read_json(SOURCE / "snapshot-manifest.json")
    video = ROOT / manifest["video"]["path"]
    expected = manifest["video"]
    require(video.stat().st_size == expected["size_bytes"], "video_size")
    require(sha256(video) == expected["sha256"], "video_sha256")
    for item in manifest["companions"]:
        filename = ROOT / item["path"]
        require(filename.stat().st_size == item["size_bytes"] and sha256(filename) == item["sha256"],
                "companion_integrity:" + item["path"])
    for item in inventory["files"]:
        require(sha256(SOURCE / item["path"]) == item["sha256"], "source_integrity:" + item["path"])
    source_files = [p for p in SOURCE.rglob("*") if p.is_file() and not p.name.startswith("._")]
    require(
        {p.relative_to(SOURCE).as_posix() for p in source_files}
        == {item["path"] for item in inventory["files"]} | {"README.md", "snapshot-manifest.json"},
        "source_inventory_is_exhaustive",
    )
    require(inventory["self_contained"] is False, "missing_dependencies_disclosed")
    for filename in PROJECT.rglob("*"):
        if not filename.is_file() or filename.name.startswith("._"):
            continue
        require(filename.suffix not in {".mp4", ".wav", ".aiff", ".aif", ".m4a", ".mp3",
                                        ".ttf", ".otf", ".woff", ".woff2", ".pdf"},
                "excluded_raw_media:" + filename.relative_to(PROJECT).as_posix())
        if filename.suffix in {".json", ".md", ".html", ".mjs", ".py", ".txt", ".srt", ".vtt"}:
            text = filename.read_text(encoding="utf-8")
            require(not re.search(r"/(?:Users|Volumes|home)/", text),
                    "no_private_path:" + filename.relative_to(PROJECT).as_posix())
            require(not re.search(r"(?:gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{32,})", text),
                    "no_known_token_pattern:" + filename.relative_to(PROJECT).as_posix())

    lines = [line for chapter in timeline["chapters"] for line in chapter["lines"]]
    srt = cues((PROJECT / "captions.srt").read_text(encoding="utf-8"))
    vtt = cues((PROJECT / "captions.vtt").read_text(encoding="utf-8"), vtt=True)
    require(srt == vtt, "srt_vtt_agree")
    require(len(lines) == len(srt) == manifest["narration_sentence_count"] == 67, "caption_count")
    require(len(timeline["chapters"]) == manifest["scene_count"] == 14, "chapter_count")
    previous_end = 0
    for index, (line, cue) in enumerate(zip(lines, srt), 1):
        number, start, end, text = cue
        require(number == index and text == line["text"], f"caption_text:{index}")
        require(abs(start - line["start"]) <= 0.001
                and abs(end - line["start"] - line["duration"]) <= 0.001,
                f"caption_measured_timing:{index}")
        require(previous_end <= start < end <= timeline["duration"], f"caption_order:{index}")
        previous_end = end
    for chapter in timeline["chapters"]:
        for line in chapter["lines"]:
            require(abs(line["start"] - chapter["start"] - line["localStart"]) < 1e-6
                    and abs(line["anchor"] - line["start"] - line["onset"]) < 1e-6,
                    "recording_anchor:" + line["key"])

    player = Links()
    player.feed((ROOT / "nasa-punk.html").read_text(encoding="utf-8"))
    require(len(player.chapters) == 14, "player_chapter_count")
    for chapter, entry, published in zip(timeline["chapters"], player.chapters, manifest["chapters"]):
        require(abs(float(entry["data-time"]) - chapter["start"]) < 1e-6
                and abs(published["start_seconds"] - chapter["start"]) < 1e-6
                and urlsplit(entry["href"]).fragment == "t=" + entry["data-time"],
                "player_chapter_time:" + chapter["id"])

    def local_target(origin, target):
        url = urlsplit(target)
        if url.scheme or url.netloc or not url.path:
            return
        filename = (origin.parent / unquote(url.path)).resolve()
        if filename == report_output:
            # The current report is written only after all validation succeeds.
            return
        require(filename.is_relative_to(ROOT) and filename.exists(),
                "local_link:" + filename.relative_to(ROOT).as_posix())

    for target in player.targets:
        local_target(ROOT / "nasa-punk.html", target)
    for filename in [ROOT / "README.md", *PROJECT.rglob("*.md")]:
        if filename.name.startswith("._"):
            continue
        for target in re.findall(r"!?\[[^\]]*\]\(([^)\s]+)\)", filename.read_text(encoding="utf-8")):
            local_target(filename, target.strip("<>"))
    for filename in SOURCE.rglob("*.py"):
        if filename.name.startswith("._"):
            continue
        compile(filename.read_text(encoding="utf-8"), str(filename), "exec")
        checks.append("python_syntax:" + filename.relative_to(SOURCE).as_posix())
    for filename in [ROOT / "tools/package_nasa_punk.mjs", *SOURCE.rglob("*.mjs")]:
        if filename.name.startswith("._"):
            continue
        subprocess.run(["node", "--check", str(filename)], check=True, capture_output=True, text=True)
        checks.append("javascript_syntax:" + filename.relative_to(ROOT).as_posix())

    production = read_json(PROJECT / "verification/final-check.json")
    require(production["craft"]["warningCount"] == manifest["review"]["craft_warning_count"] == 38,
            "production_warnings_preserved")
    require(manifest["review"]["full_speed_human_audio_visual_review"] is False
            and manifest["review"]["word_by_word_human_proofread"] is False
            and manifest["review"]["word_level_alignment"] is False,
            "review_limitations_preserved")
    if media:
        probe = json.loads(subprocess.run(
            ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(video)],
            check=True, capture_output=True, text=True,
        ).stdout)
        stream = next(s for s in probe["streams"] if s["codec_type"] == "video")
        audio = next(s for s in probe["streams"] if s["codec_type"] == "audio")
        require(abs(float(probe["format"]["duration"]) - expected["duration_seconds"]) < 1e-6
                and stream["codec_name"] == "h264"
                and (stream["width"], stream["height"], stream["r_frame_rate"])
                == (1280, 720, "30/1")
                and int(stream["nb_frames"]) == expected["frame_count"]
                and audio["codec_name"] == "aac"
                and int(audio["sample_rate"]) == 48000 and audio["channels"] == 2,
                "ffprobe_media_specifications")
        decoded = subprocess.run(
            ["ffmpeg", "-v", "error", "-xerror", "-i", str(video), "-f", "null", "-"],
            check=True, capture_output=True, text=True,
        )
        require(not decoded.stderr.strip(), "full_video_audio_decode")
    return {
        "status": "passed", "check_count": len(checks), "checks": checks,
        "video_sha256": expected["sha256"],
        "chapter_count": len(timeline["chapters"]), "caption_count": len(srt),
        "source_file_count": len(inventory["files"]), "media_probe_and_full_decode": media,
        "scope": "Published file integrity, captions against sentence timing, chapter links, local links, source syntax and excluded files. No full human semantic, spelling or rights approval.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--media", action="store_true", help="Also probe and fully decode the MP4 using FFmpeg")
    parser.add_argument("--check-only", action="store_true", help="Do not overwrite the publication report")
    args = parser.parse_args()
    report_path = PROJECT / "verification/publication-check.json"
    report = validate(media=args.media, report_output=None if args.check_only else report_path)
    if not args.check_only:
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
        )
    print(json.dumps({k: v for k, v in report.items() if k != "checks"}, ensure_ascii=False, indent=2))
