"""Portable checks, asset retrieval, and local V2 re-render commands."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import zipfile

import requests


PROJECT = Path(__file__).resolve().parent
REPOSITORY = "yenicee1014/Explainer-Video-workflow"
RELEASE_TAG = "skyscraper-crisis-v2-2026-10-25"
ARCHIVE_NAME = "skyscraper-crisis-v2-render-assets.zip"
ARTIFACTS = PROJECT / "artifacts"
ARCHIVE = ARTIFACTS / ARCHIVE_NAME
MANIFEST = PROJECT / "render-assets-manifest.json"

sys.path.insert(0, str(PROJECT))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def manifest_data():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def expected_files():
    return {item["file"]: item for item in manifest_data()["files"]}


def safe_member(name: str) -> Path:
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts:
        raise RuntimeError(f"Unsafe archive member: {name}")
    return relative


def fetch_assets():
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    expected_archive_hash = manifest_data()["archive_sha256"]
    if ARCHIVE.exists() and sha256(ARCHIVE) == expected_archive_hash:
        print(f"ARCHIVE_CACHED {ARCHIVE}")
    else:
        release_url = (
            f"https://api.github.com/repos/{REPOSITORY}/releases/tags/{RELEASE_TAG}"
        )
        response = requests.get(
            release_url,
            headers={"Accept": "application/vnd.github+json"},
            timeout=30,
        )
        response.raise_for_status()
        assets = {item["name"]: item["browser_download_url"] for item in response.json()["assets"]}
        if ARCHIVE_NAME not in assets:
            raise RuntimeError(f"Release asset not found: {ARCHIVE_NAME}")
        temporary = ARCHIVE.with_suffix(".part")
        with requests.get(assets[ARCHIVE_NAME], stream=True, timeout=(30, 120)) as download:
            download.raise_for_status()
            with temporary.open("wb") as target:
                for block in download.iter_content(1024 * 1024):
                    if block:
                        target.write(block)
        if sha256(temporary) != expected_archive_hash:
            temporary.unlink(missing_ok=True)
            raise RuntimeError("Downloaded render-assets archive SHA-256 does not match the manifest.")
        temporary.replace(ARCHIVE)
        print(f"ARCHIVE_DOWNLOADED {ARCHIVE}")

    stage = ARTIFACTS / "unpacked"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    with zipfile.ZipFile(ARCHIVE) as archive:
        for info in archive.infolist():
            safe_member(info.filename)
        archive.extractall(stage)

    for name, item in expected_files().items():
        source = stage / safe_member(name)
        target = PROJECT / safe_member(name)
        if not source.is_file():
            raise RuntimeError(f"Archive is missing manifest file: {name}")
        if sha256(source) != item["sha256"]:
            raise RuntimeError(f"Archive member hash mismatch: {name}")
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if sha256(target) != item["sha256"]:
                raise RuntimeError(f"Refusing to overwrite a different local file: {target}")
        else:
            shutil.copy2(source, target)
    print(f"ASSETS_READY {len(expected_files())} files")


def check():
    from full_film import FFMPEG, FFPROBE

    for executable in (FFMPEG, FFPROBE):
        if shutil.which(executable) is None and not Path(executable).exists():
            raise RuntimeError(f"Executable not found: {executable}")

    delivery = json.loads((PROJECT / "delivery-manifest.json").read_text(encoding="utf-8"))
    for item in delivery["files"]:
        path = PROJECT.parents[1] / item["file"]
        if not path.is_file():
            raise RuntimeError(f"Published file is missing: {path}")
        if path.stat().st_size != item["bytes"]:
            raise RuntimeError(f"Published file size mismatch: {path}")
        if sha256(path) != item["sha256"]:
            raise RuntimeError(f"Published file SHA-256 mismatch: {path}")

    for name in (
        "full-film-v2/storyboard.json",
        "full-film-v2/asset-plan.json",
        "full-film-v2/资料与画面依据.md",
        "SCRIPT_FULL_V1.md",
    ):
        if not (PROJECT / name).exists():
            raise RuntimeError(f"Project file is missing: {name}")

    print("CHECK_OK published media, manifests, and project sources")


def plan():
    from full_film import plan as full_plan
    from v2_plan import make_plan

    chapters = full_plan()
    scenes = make_plan()
    if len(chapters) != 8 or len(scenes) != 8:
        raise RuntimeError("The project must contain exactly eight chapters.")
    if sum(len(chapter["paragraphs"]) for chapter in chapters) != 78:
        raise RuntimeError("The approved narration must contain 78 paragraphs.")
    print("PLAN_OK 8 chapters / 78 narration paragraphs / 148 photographic beats")


def render(chapter: int | None, revision: int):
    from v2_visuals import render as render_chapter

    chapters = range(1, 9) if chapter is None else (chapter,)
    for number in chapters:
        output = render_chapter(number, revision)
        print(f"RENDERED {number:02d} {output}")


def assemble():
    from v2_pipeline import assemble as assemble_film

    output = assemble_film()
    print(f"ASSEMBLED {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=("check", "fetch-assets", "plan", "render", "assemble"),
    )
    parser.add_argument("--chapter", type=int, choices=range(1, 9))
    parser.add_argument("--revision", type=int, default=21)
    args = parser.parse_args()

    if args.action == "check":
        check()
    elif args.action == "fetch-assets":
        fetch_assets()
    elif args.action == "plan":
        plan()
    elif args.action == "render":
        render(args.chapter, args.revision)
    else:
        assemble()


if __name__ == "__main__":
    main()
