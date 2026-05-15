#!/usr/bin/env python3
"""
sitemap_fetcher.py
Fetches the Innova Retail sitemap, extracts and categorizes all URLs,
and saves results to data/sitemap/sitemap-urls.json
"""

import json
import re
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

CONFIG_PATH = Path("config/site-config.json")
OUTPUT_PATH = Path("data/sitemap/sitemap-urls.json")

SHOPIFY_NAMESPACES = {
    "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "image": "http://www.google.com/schemas/sitemap-image/1.1",
    "news": "http://www.google.com/schemas/sitemap-news/0.9",
}


SHOPIFY_SITEMAP_TYPES = {
    "sitemap_products": "products",
    "sitemap_collections": "collections",
    "sitemap_pages": "pages",
    "sitemap_blogs": "blogs",
}

LOG_PATH = Path("data/sitemap/fetch-log.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def log_fetch(url, status, result, note=""):
    log = {"fetch_attempts": []}
    if LOG_PATH.exists():
        with open(LOG_PATH) as f:
            try:
                log = json.load(f)
            except json.JSONDecodeError:
                pass
    log.setdefault("fetch_attempts", []).append({
        "url": url,
        "http_status": status,
        "timestamp": datetime.now().isoformat(),
        "result": result,
        "note": note,
    })
    log["_meta"] = {
        "description": "Sitemap fetch attempt log",
        "last_attempt": datetime.now().isoformat(),
        "sitemap_url": url,
    }
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)


def fetch_sitemap(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; InnovaRetailSEOBot/1.0; +https://innovaretail.co.in)",
        "Accept": "text/xml,application/xml,application/xhtml+xml,*/*",
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            log_fetch(url, resp.status, "success")
            return data
    except urllib.error.HTTPError as e:
        log_fetch(url, e.code, "http_error", str(e))
        print(f"ERROR: HTTP {e.code} fetching {url}: {e.reason}")
        sys.exit(1)
    except urllib.error.URLError as e:
        log_fetch(url, 0, "network_error", str(e))
        print(f"ERROR: Could not fetch sitemap from {url}: {e}")
        print("If running in a restricted environment, see data/sitemap/manual-fetch-instructions.md")
        sys.exit(1)


def detect_shopify_sitemap_type(url):
    for key, stype in SHOPIFY_SITEMAP_TYPES.items():
        if key in url:
            return stype
    return "other"


def parse_urls_from_xml(content):
    root = ET.fromstring(content)
    ns = "http://www.sitemaps.org/schemas/sitemap/0.9"

    urls = []

    # Handle sitemap index (multiple sitemaps)
    sitemaps = root.findall(f"{{{ns}}}sitemap/{{{ns}}}loc")
    if sitemaps:
        print(f"Sitemap index found with {len(sitemaps)} sub-sitemaps.")
        for sm_loc in sitemaps:
            sub_content = fetch_sitemap(sm_loc.text.strip())
            urls.extend(parse_urls_from_xml(sub_content))
        return urls

    # Handle regular urlset
    for url_el in root.findall(f"{{{ns}}}url"):
        loc = url_el.findtext(f"{{{ns}}}loc", "").strip()
        lastmod = url_el.findtext(f"{{{ns}}}lastmod", "").strip()
        if loc:
            urls.append({"url": loc, "lastmod": lastmod})

    return urls


def categorize_urls(urls, base_url):
    blog_urls = []
    product_urls = []
    collection_urls = []
    other_urls = []

    for entry in urls:
        url = entry["url"]
        path = url.replace(base_url.rstrip("/"), "")

        if "/blogs/" in url or "/articles/" in url:
            blog_urls.append(entry)
        elif "/products/" in url:
            product_urls.append(entry)
        elif "/collections/" in url:
            collection_urls.append(entry)
        else:
            other_urls.append(entry)

    return blog_urls, product_urls, collection_urls, other_urls


def extract_blog_topics(blog_urls):
    topics = []
    for entry in blog_urls:
        url = entry["url"]
        # Extract slug from URL
        slug = url.rstrip("/").split("/")[-1]
        # Convert slug to readable topic
        topic = slug.replace("-", " ").title()
        topics.append({"url": url, "slug": slug, "topic": topic, "lastmod": entry.get("lastmod", "")})
    return topics


def detect_nested_sitemaps(content, root_url):
    """If the XML is a sitemap index, return list of nested sitemap URLs."""
    root = ET.fromstring(content)
    ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    sitemaps = root.findall(f"{{{ns}}}sitemap/{{{ns}}}loc")
    return [s.text.strip() for s in sitemaps if s.text]


def main():
    config = load_config()
    sitemap_url = config.get("sitemap_url", "")

    if sitemap_url.startswith("TODO:"):
        print("ERROR: sitemap_url is not set in config/site-config.json")
        print("Update the 'sitemap_url' field and remove the 'TODO:' prefix.")
        sys.exit(1)

    base_url = config.get("website_url", "").rstrip("/")
    print(f"Fetching sitemap index: {sitemap_url}")

    root_content = fetch_sitemap(sitemap_url)

    # Detect sitemap index vs direct urlset
    nested_urls = detect_nested_sitemaps(root_content, sitemap_url)
    is_index = bool(nested_urls)

    sitemap_index_meta = {
        "confirmed": is_index,
        "nested_sitemaps": [],
    }

    all_urls = []

    if is_index:
        print(f"Sitemap index detected — {len(nested_urls)} nested sitemaps found:")
        for sm_url in nested_urls:
            stype = detect_shopify_sitemap_type(sm_url)
            print(f"  [{stype}] {sm_url}")
            sitemap_index_meta["nested_sitemaps"].append({
                "url": sm_url,
                "type": stype,
                "status": "fetching",
            })

        for i, sm_url in enumerate(nested_urls):
            stype = detect_shopify_sitemap_type(sm_url)
            print(f"  Fetching: {sm_url}")
            sub_content = fetch_sitemap(sm_url)
            sub_urls = parse_urls_from_xml(sub_content)
            all_urls.extend(sub_urls)
            sitemap_index_meta["nested_sitemaps"][i]["status"] = "fetched"
            sitemap_index_meta["nested_sitemaps"][i]["url_count"] = len(sub_urls)
    else:
        print("Direct urlset detected (no sitemap index).")
        all_urls = parse_urls_from_xml(root_content)

    print(f"\nTotal URLs found: {len(all_urls)}")

    blog_urls, product_urls, collection_urls, other_urls = categorize_urls(all_urls, base_url)
    blog_topics = extract_blog_topics(blog_urls)

    print(f"  Blog URLs:       {len(blog_urls)}")
    print(f"  Product URLs:    {len(product_urls)}")
    print(f"  Collection URLs: {len(collection_urls)}")
    print(f"  Other URLs:      {len(other_urls)}")

    output = {
        "_meta": {
            "description": "Extracted URLs from the Innova Retail sitemap.",
            "last_fetched": datetime.now().isoformat(),
            "sitemap_url": sitemap_url,
            "fetch_status": "success",
            "total_urls": len(all_urls),
        },
        "sitemap_index": sitemap_index_meta,
        "blog_urls": blog_topics,
        "product_urls": product_urls,
        "collection_urls": collection_urls,
        "other_urls": other_urls,
        "content_gaps": [],
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to {OUTPUT_PATH}")
    print("Next step: Run sitemap analysis prompt from prompts/sitemap-analysis-prompt.md")


if __name__ == "__main__":
    main()
