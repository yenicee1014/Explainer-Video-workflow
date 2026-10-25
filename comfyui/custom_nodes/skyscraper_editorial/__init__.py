"""Portable V2 ComfyUI nodes for the skyscraper editorial project."""
import importlib.util
import os
from pathlib import Path

from comfy_api.latest import InputImpl


def project_dir() -> Path:
    configured = os.environ.get("SC_PROJECT_DIR")
    if configured:
        root = Path(configured).expanduser().resolve()
    else:
        root = Path(__file__).resolve().parents[3] / "projects" / "skyscraper-crisis"
    if not (root / "v2_visuals.py").is_file():
        raise RuntimeError(
            "Set SC_PROJECT_DIR to the cloned repository's projects/skyscraper-crisis directory."
        )
    return root


def load_module(filename: str, name: str):
    path = project_dir() / filename
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load project module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SkyscraperFullChapter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "chapter": ("INT", {"default": 1, "min": 1, "max": 8}),
                "revision": ("INT", {"default": 21, "min": 20, "max": 100}),
            }
        }

    RETURN_TYPES = ("VIDEO", "STRING")
    RETURN_NAMES = ("video", "file_path")
    FUNCTION = "execute"
    CATEGORY = "Skyscraper Editorial"
    OUTPUT_NODE = True

    def execute(self, chapter, revision):
        renderer = load_module("v2_visuals.py", "skyscraper_v2_visuals")
        path = renderer.render(chapter, revision)
        return {"ui": {"text": [path]}, "result": (InputImpl.VideoFromFile(path), path)}


class SkyscraperSceneBatch:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "chapter": ("INT", {"default": 1, "min": 1, "max": 8}),
                "workers": ("INT", {"default": 3, "min": 1, "max": 3}),
                "revision": ("INT", {"default": 3, "min": 1, "max": 100}),
            },
            "optional": {"previous": ("VIDEO",)},
        }

    RETURN_TYPES = ("VIDEO", "STRING")
    RETURN_NAMES = ("last_shot", "file_path")
    FUNCTION = "execute"
    CATEGORY = "Skyscraper Editorial"
    OUTPUT_NODE = True

    def execute(self, chapter, workers, revision, previous=None):
        producer = load_module("v2_generate.py", "skyscraper_v2_generate")
        path = producer.generate_chapter_inside_comfy(chapter, workers)
        return {"ui": {"text": [path]}, "result": (InputImpl.VideoFromFile(path), path)}


NODE_CLASS_MAPPINGS = {
    "SCFullChapter": SkyscraperFullChapter,
    "SCSceneBatch": SkyscraperSceneBatch,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SCFullChapter": "繁荣的高度 · 本地逐章合成",
    "SCSceneBatch": "繁荣的高度 · 按章生成情境素材",
}
