"""Stage still media for the reauthored film; no source video is mounted."""
import json
from pathlib import Path
import subprocess

import cv2
import fitz
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "rebuild"
OUT.mkdir(parents=True, exist_ok=True)
records = []


def still(index):
    return cv2.imread(str(ROOT / f"reference/frames/frame-{index:04d}.jpg"))


def crop(name, index, rect):
    image = still(index)
    x, y, w, h = rect
    cv2.imwrite(str(OUT / f"{name}.jpg"), image[y:y+h, x:x+w],
                [cv2.IMWRITE_JPEG_QUALITY, 96])
    records.append({"file": f"{name}.jpg", "source": "reference/source.mp4",
                    "frame_sample": index, "crop": rect, "use": "isolated illustrative still"})


def rectify(name, index, points, size):
    image = still(index)
    w, h = size
    matrix = cv2.getPerspectiveTransform(
        np.float32(points), np.float32([[0, 0], [w, 0], [w, h], [0, h]]))
    result = cv2.warpPerspective(image, matrix, size)
    cv2.imwrite(str(OUT / f"{name}.jpg"), result, [cv2.IMWRITE_JPEG_QUALITY, 96])
    records.append({"file": f"{name}.jpg", "source": "reference/source.mp4",
                    "frame_sample": index, "source_corners": points,
                    "use": "isolated illustrative still, perspective corrected"})


# Remove the source video's typesetting by selecting only the underlying media.
subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "0.1", "-i",
                str(ROOT / "reference/source.mp4"), "-frames:v", "1",
                "-vf", "crop=1280:610:0:85", str(OUT / "hangar.jpg")], check=True)
records.append({"file": "hangar.jpg", "source": "reference/source.mp4",
                "time": .1, "crop": [0, 85, 1280, 610], "underlying_owner": "NASA / SpaceX"})
crop("saturn", 25, [150, 85, 850, 540])
crop("starfield-landscape", 49, [0, 85, 1280, 432])
crop("storage", 57, [65, 78, 1130, 555])
rectify("astronaut", 50, [[751, 122], [1093, 137], [1077, 474], [736, 461]], (580, 580))
rectify("apollo-detail", 50, [[195, 140], [532, 123], [552, 487], [212, 500]], (530, 590))
rectify("ark", 67, [[112, 96], [1272, 111], [1269, 621], [98, 608]], (1200, 515))
rectify("ark-notice", 70, [[396, 181], [959, 205], [949, 307], [389, 286]], (900, 180))
rectify("ark-rings", 70, [[736, 360], [990, 378], [972, 627], [717, 610]], (520, 520))
rectify("ark-character", 70, [[82, 267], [271, 249], [300, 598], [115, 607]], (310, 560))
rectify("martian", 72, [[403, 25], [875, 8], [888, 293], [407, 309]], (850, 515))
rectify("preston", 72, [[401, 388], [847, 405], [833, 684], [398, 670]], (850, 540))
rectify("arc-poster", 75, [[212, 132], [1058, 111], [1071, 582], [224, 606]], (1100, 620))
# The machine still includes an in-source explanatory label; it remains documented.
rectify("arc-machine", 77, [[184, 86], [1107, 118], [1091, 623], [167, 603]], (1100, 620))
crop("arc-player", 80, [300, 85, 900, 375])
rectify("arc-bully", 81, [[210, 242], [626, 236], [629, 468], [214, 471]], (620, 350))
rectify("arc-stiletto", 81, [[685, 253], [1100, 264], [1096, 484], [681, 476]], (620, 350))

# Extract the public-domain insignia itself, leaving all source layout behind.
badge = still(5)[195:455, 265:575]
hsv = cv2.cvtColor(badge, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, (0, 100, 35), (179, 255, 255))
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
alpha = np.zeros(mask.shape, np.uint8)
cv2.drawContours(alpha, [c for c in contours if cv2.contourArea(c) > 100], -1, 255, -1)
cv2.imwrite(str(OUT / "meatball.png"), np.dstack([badge, alpha]))
records.append({"file": "meatball.png", "source": "reference/source.mp4",
                "frame_sample": 5, "underlying_owner": "NASA", "use": "insignia isolated"})

document = fitz.open(ROOT / "assets/nasa-graphics-manual.pdf")
for name, page in {"manual-cover": 0, "manual-logo": 4, "manual-color": 6,
                   "manual-misuse": 9, "manual-grid": 10, "manual-patches": 11,
                   "manual-letter": 18, "manual-type": 26, "manual-truck": 48,
                   "manual-aircraft": 54, "manual-shuttle": 55, "manual-uniform": 59}.items():
    pix = document[page].get_pixmap(matrix=fitz.Matrix(1.8, 1.8), alpha=False)
    pix.save(OUT / f"{name}.png")
    records.append({"file": f"{name}.png",
                    "source": "https://www.nasa.gov/wp-content/uploads/2015/01/nasa_graphics_manual_nhb_1430-2_jan_1976.pdf",
                    "page_zero_based": page, "license": "NASA public-domain material",
                    "edition": "January 1976 official edition of 1975 identity system"})

rng = np.random.default_rng(1975)
for name, rgb, noise in [("paper", [239, 236, 223], 1.6), ("desk", [29, 28, 23], 1.0),
                         ("metal", [220, 220, 209], 2.0)]:
    w, h = 1280, 720
    yy, xx = np.mgrid[0:h, 0:w]
    vignette = ((xx-w*.5)**2/(w*.85)**2+(yy-h*.4)**2/(h*.9)**2)
    shade = rng.normal(0, noise, (h, w)) - vignette * (14 if name != "desk" else 6)
    pixels = np.clip(np.array(rgb)[None, None, :]+shade[:, :, None], 0, 255).astype(np.uint8)
    Image.fromarray(pixels).save(OUT / f"{name}-texture.jpg", quality=95)

(OUT / "provenance.json").write_text(json.dumps(records, ensure_ascii=False, indent=2))
print(f"Prepared {len(records)} documented still assets plus three deterministic textures.")
