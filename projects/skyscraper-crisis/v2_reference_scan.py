"""A bounded contact sheet of architect-provided Burj Khalifa photographs."""
from io import BytesIO
import json

import requests
from PIL import Image, ImageDraw

from full_film import dump
from v2_research import fetch_page, CACHE


def scan():
    soup = fetch_page("som", "https://www.som.com/projects/burj-khalifa/")
    candidates = []
    seen = set()
    for im in soup.find_all("img"):
        if im.get("alt") != "Burj" or not im.get("data-image"):
            continue
        data = json.loads(im["data-image"])
        full = data["sources"][0]["src"]
        if full in seen:
            continue
        seen.add(full)
        candidates.append({"small": im["src"], "full": full})
    sheet = Image.new("RGB", (1200, 320 * ((len(candidates) + 3) // 4)), (230, 230, 228))
    draw = ImageDraw.Draw(sheet)
    for i, candidate in enumerate(candidates):
        r = requests.get(candidate["small"], timeout=12)
        image = Image.open(BytesIO(r.content)).convert("RGB")
        image.thumbnail((288, 278))
        x, y = (i % 4) * 300, (i // 4) * 320
        sheet.paste(image, (x + (300 - image.width) // 2, y + 28))
        draw.text((x + 10, y + 5), f"SOM photo {i}", fill=(10, 10, 10))
    sheet.save(CACHE / "som-contact.jpg", quality=94)
    dump(CACHE / "som-candidates.json", candidates)


if __name__ == "__main__":
    scan()
