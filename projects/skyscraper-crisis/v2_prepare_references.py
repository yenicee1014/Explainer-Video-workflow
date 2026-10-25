"""Record the selected, visually checked architectural reference photographs."""
from pathlib import Path
import json

from bs4 import BeautifulSoup

from full_film import dump
from v2_research import CACHE, PAGES, fetch_page, photo, resolve_image


def prepare():
    CACHE.mkdir(parents=True, exist_ok=True)
    records = []
    esb = fetch_page("esb", PAGES["esb"])
    for a in esb.find_all("article"):
        value = a.get_text(" ", strip=True)
        for year, key in [("1930", "esb_build"), ("1931", "esb_open"), ("1981", "esb_photo")]:
            if value.startswith(year + " "):
                target = CACHE / f"{key}.jpg"
                if key == "esb_photo" and target.exists() and not (CACHE / "esb_facade_reference.jpg").exists():
                    target.rename(CACHE / "esb_facade_reference.jpg")
                records.append(photo(
                    key, resolve_image(a.find("img")["src"], PAGES["esb"]), PAGES["esb"],
                    "Modern whole-building reference; not a 1931 or 1981 archive photo."
                    if key == "esb_photo" else "Official page assigns this historical image to " + year,
                    "Empire State Building official site; rights retained by source.",
                ))
    som = fetch_page("som", "https://www.som.com/projects/burj-khalifa/")
    first = next(e for e in som.find_all("img") if e.get("alt") == "Burj"
                 and "N2590_large" in e.get("data-image", ""))
    url = json.loads(first["data-image"])["sources"][0]["src"]
    target = CACHE / "burj_photo.jpg"
    if target.exists() and not (CACHE / "burj_facade_reference.jpg").exists():
        target.rename(CACHE / "burj_facade_reference.jpg")
    records.append(photo(
        "burj_photo", url, "https://www.som.com/projects/burj-khalifa/",
        "Whole-tower project photograph from architect SOM; appearance reference, not a dated opening archive.",
        "SOM project photography; rights retained by source.",
    ))
    pcp = fetch_page("pcp", "https://pcparch.com/work/petronas-towers/")
    first = next(e for e in pcp.find_all("source") if e.get("type") == "image/jpeg"
                 and "petronas-towers-hero" in e.get("data-srcset", ""))
    url = first["data-srcset"].split(",")[-2].strip().split(" ")[0]
    records.append(photo(
        "petronas_photo", url, "https://pcparch.com/work/petronas-towers/",
        "Whole twin towers and skybridge photograph from architect; not a 1992 archive image.",
        "Pelli Clarke & Partners project photography; rights retained by source.",
    ))
    dump(CACHE / "photos.json", records)
    dump(CACHE / "source-status.json", {
        "accessed": "2026-10-25", "pages": PAGES,
        "additional": ["https://www.som.com/projects/burj-khalifa/", "https://pcparch.com/work/petronas-towers/"],
        "archival_claims": ["esb_build:1930", "esb_open:1931"],
        "modern_architecture_references": ["esb_photo", "burj_photo", "petronas_photo"],
    })
    for record in records:
        print(record["id"], record["size"], flush=True)
    return records


if __name__ == "__main__":
    prepare()
