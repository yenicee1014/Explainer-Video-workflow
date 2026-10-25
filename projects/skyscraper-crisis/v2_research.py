"""Freeze public source pages and reference photographs for editorial research."""
import argparse
import json
import re
import subprocess
from urllib.parse import parse_qs, unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from PIL import Image

from full_film import dump
from v2_plan import V2

CACHE = V2 / "research"
PAGES = {
    "esb": "https://www.esbnyc.com/about/history",
    "petronas": "https://www.petronastwintowers.com.my/the-towers/the-stories/",
    "burj": "https://properties.emaar.com/",
    "crash": "https://www.federalreservehistory.org/essays/stock-market-crash-of-1929",
    "refinance": "https://www.occ.gov/news-issuances/bulletins/2024/bulletin-2024-29.html",
    "cre": "https://www.stlouisfed.org/on-the-economy/2024/may/commercial-real-estate-focus",
}


def fetch_page(key, url, verify=True):
    CACHE.mkdir(parents=True, exist_ok=True)
    html = CACHE / f"{key}.html"
    if not html.exists():
        try:
            response = requests.get(url, timeout=25, verify=verify)
            response.raise_for_status()
            value = response.content.decode("utf-8")
        except requests.exceptions.SSLError:
            value = subprocess.run(
                ["curl", "-fsSL", "--max-time", "25", url],
                check=True, capture_output=True,
            ).stdout.decode("utf-8")
        html.write_text(value, encoding="utf-8")
    soup = BeautifulSoup(html.read_text(), "html.parser")
    clean = BeautifulSoup(str(soup), "html.parser")
    for e in clean(["script", "style", "nav", "header", "footer"]):
        e.decompose()
    (CACHE / f"{key}.txt").write_text(clean.get_text("\n", strip=True), encoding="utf-8")
    return soup


def resolve_image(url, base):
    url = urljoin(base, url)
    if "/_next/image?" in url:
        inner = parse_qs(urlparse(url).query).get("url", [url])[0]
        url = urljoin(base, inner)
    return url


def photo(key, url, page, note, rights):
    destination = CACHE / f"{key}.jpg"
    if not destination.exists():
        try:
            r = requests.get(url, timeout=35, headers={"Referer": page})
            r.raise_for_status()
            body = r.content
        except requests.exceptions.SSLError:
            body = subprocess.run(
                ["curl", "-fsSL", "--max-time", "35", url],
                check=True, capture_output=True,
            ).stdout
        from io import BytesIO
        image = Image.open(BytesIO(body)).convert("RGB")
        image.thumbnail((2200, 2200))
        image.save(destination, quality=95)
    return {
        "id": key, "file": str(destination), "url": url, "page": page,
        "note": note, "rights": rights, "purpose": "architecture reference and attributed private demo",
        "size": Image.open(destination).size,
    }


def run():
    records = []
    failures = []
    soups = {}
    for key, url in PAGES.items():
        try:
            soups[key] = fetch_page(key, url)
            print("SOURCE", key, "saved", flush=True)
        except Exception as e:
            failures.append({"id": key, "url": url, "error": type(e).__name__})
            print("SOURCE", key, type(e).__name__, flush=True)
    if "esb" in soups:
        records.append(photo(
            "esb_photo", resolve_image(soups["esb"].find("img")["src"], PAGES["esb"]),
            PAGES["esb"], "History page architecture reference; photograph date unspecified.",
            "Empire State Building official site; no public-domain claim.",
        ))
        for a in soups["esb"].find_all("article"):
            value = a.get_text(" ", strip=True)
            key = "esb_build" if value.startswith("1930 ") else "esb_open" if value.startswith("1931 ") else None
            if key:
                image = a.find("img")
                records.append(photo(
                    key, resolve_image(image["src"], PAGES["esb"]), PAGES["esb"], value,
                    "Empire State Building official site; no public-domain claim.",
                ))
    if "burj" in soups:
        for im in soups["burj"].find_all("img"):
            if im.get("alt", "") == "Burj Khalifa, Downtown Dubai":
                records.append(photo(
                    "burj_photo", resolve_image(im["src"], PAGES["burj"]), PAGES["burj"],
                    "Official Emaar photograph labelled Burj Khalifa, Downtown Dubai; not a 2010 archive image.",
                    "Emaar official site; rights retained by source.",
                ))
                break
    if "petronas" in soups:
        candidates = []
        for im in soups["petronas"].find_all("img"):
            u = im.get("data-src") or im.get("src", "")
            if u and not any(x in u.lower() for x in ["logo", ".svg", "icon", "fb.png", "ig.png"]):
                candidates.append({"alt": im.get("alt", ""), "url": resolve_image(u, PAGES["petronas"])})
        dump(CACHE / "petronas-image-candidates.json", candidates)
    # Save the exact Crossref publisher metadata; do not invent a study cover.
    try:
        url = "https://api.crossref.org/works"
        data = requests.get(url, params={
            "query.title": "Skyscraper height and the business cycle separating myth from reality",
            "rows": 2,
        }, timeout=25).json()["message"]["items"]
        dump(CACHE / "crossref-study.json", data)
        print("STUDY", [(d.get("title"), d.get("DOI")) for d in data], flush=True)
    except Exception as e:
        failures.append({"id": "crossref", "error": type(e).__name__})
    dump(CACHE / "photos.json", records)
    dump(CACHE / "source-status.json", {
        "pages": PAGES, "saved": list(soups), "failures": failures,
        "accessed": "2026-10-25",
    })
    print("PHOTOS", json.dumps(records, ensure_ascii=False), flush=True)
    for key in ["petronas", "burj"]:
        if key in soups:
            soup = soups[key]
            for im in soup.find_all("img"):
                u = im.get("data-src") or im.get("src", "")
                if u and "logo" not in u.lower():
                    print("CANDIDATE", key, im.get("alt", "")[:80], resolve_image(u, PAGES[key]), flush=True)
    return records


if __name__ == "__main__":
    run()
