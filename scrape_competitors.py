#!/usr/bin/env python3
import json
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
SOURCES_PATH = ROOT / "sources.json"
NEWS_PATH = ROOT / "data" / "news.json"
JOBS_PATH = ROOT / "data" / "jobs.json"
REG_PATH = ROOT / "data" / "regulatory.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; competitor-monitor/1.0; +https://example.com)"
}


def load_json(path: Path):
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def fetch_html(url: str):
    try:
        r = requests.get(url, timeout=20, headers=HEADERS)
        r.raise_for_status()
        return r.text
    except Exception:
        return ""


def normalize_text(value):
    if value is None:
        return ""
    return " ".join(value.replace("\xa0", " ").split())


def get_visible_text(soup, selector):
    tags = soup.select(selector)
    texts = []
    for tag in tags:
        txt = normalize_text(tag.get_text(" ", strip=True))
        if txt:
            texts.append(txt)
    return texts


def extract_news_from_page(url: str, company: str):
    html = fetch_html(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    out = []
    seen = set()

    for a in soup.find_all("a", href=True):
        text = normalize_text(a.get_text(" ", strip=True))
        href = a["href"]
        if not text or not href:
            continue

        if any(k in text.lower() for k in ["press", "news", "aktuality", "tisk", "announcement", "release"]):
            full = urljoin(url, href)
            if full not in seen:
                seen.add(full)
                out.append({
                    "company": company,
                    "title": text,
                    "publication_date": "",
                    "source_url": full,
                    "summary": "Scraped from official newsroom page; review and enrich manually if needed.",
                    "tags": ["news"]
                })

    return out[:12]


def extract_jobs_from_page(url: str, company: str):
    html = fetch_html(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    out = []
    seen = set()

    for a in soup.find_all("a", href=True):
        text = normalize_text(a.get_text(" ", strip=True))
        href = a["href"]
        if not text or not href:
            continue

        lowered = text.lower()
        if any(k in lowered for k in ["kariera", "career", "vacancy", "jobs", "job", "pozice", "nabídka"]):
            full = urljoin(url, href)
            if full not in seen:
                seen.add(full)
                out.append({
                    "company": company,
                    "title": text,
                    "published_at": "",
                    "source_url": full,
                    "location": "Czech Republic",
                    "department": "General",
                    "summary": "Scraped from official career page; review and enrich manually if needed."
                })

    return out[:10]


def scrape_sources():
    sources = load_json(SOURCES_PATH)
    news = []
    jobs = []
    regulatory = []

    for source in sources:
        s_type = source.get("type")
        company = source.get("company", "Unknown")
        url = source.get("url")
        if not url:
            continue

        if s_type == "news":
            news.extend(extract_news_from_page(url, company))
        elif s_type == "careers":
            jobs.extend(extract_jobs_from_page(url, company))
        elif s_type == "regulatory":
            html = fetch_html(url)
            if not html:
                continue
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                text = normalize_text(a.get_text(" ", strip=True))
                href = a["href"]
                if not text or not href:
                    continue
                lowered = text.lower()
                if any(k in lowered for k in ["regulation", "market", "energy", "news", "press release", "monitoring", "balancing", "dufvo", "dufmo", "cer", "eru", "ote"]):
                    full = urljoin(url, href)
                    regulatory.append({
                        "authority": company,
                        "title": text,
                        "publication_date": "",
                        "source_url": full,
                        "summary": "Scraped from official regulatory source; review and enrich manually if needed.",
                        "tags": ["regulatory"]
                    })

    # Deduplicate using a stable key
    def dedupe(items, key_fn):
        seen = set()
        unique = []
        for item in items:
            k = key_fn(item)
            if k not in seen:
                seen.add(k)
                unique.append(item)
        return unique

    news = dedupe(news, lambda x: x.get("source_url", ""))
    jobs = dedupe(jobs, lambda x: x.get("source_url", ""))
    regulatory = dedupe(regulatory, lambda x: x.get("source_url", ""))

    NEWS_PATH.write_text(json.dumps(news, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    JOBS_PATH.write_text(json.dumps(jobs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REG_PATH.write_text(json.dumps(regulatory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Saved {len(news)} news items")
    print(f"Saved {len(jobs)} job items")
    print(f"Saved {len(regulatory)} regulatory items")


if __name__ == "__main__":
    scrape_sources()
