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


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def fetch_sitemap(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "InnovaRetailSEOBot/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read()
    except urllib.error.URLError as e:
        print(f"ERROR: Could not fetch sitemap from {url}: {e}")
        sys.exit(1)


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


def main():
    config = load_config()
    sitemap_url = config.get("sitemap_url", "")

    if sitemap_url.startswith("TODO:"):
        print("ERROR: sitemap_url is not set in config/site-config.json")
        print("Update the 'sitemap_url' field and remove the 'TODO:' prefix.")
        sys.exit(1)

    base_url = config.get("website_url", "").replace("TODO: ", "").rstrip("/")
    print(f"Fetching sitemap: {sitemap_url}")

    content = fetch_sitemap(sitemap_url)
    all_urls = parse_urls_from_xml(content)
    print(f"Total URLs found: {len(all_urls)}")

    blog_urls, product_urls, collection_urls, other_urls = categorize_urls(all_urls, base_url)
    blog_topics = extract_blog_topics(blog_urls)

    print(f"  Blog URLs: {len(blog_urls)}")
    print(f"  Product URLs: {len(product_urls)}")
    print(f"  Collection URLs: {len(collection_urls)}")
    print(f"  Other URLs: {len(other_urls)}")

    output = {
        "_meta": {
            "description": "Extracted URLs from the Innova Retail sitemap.",
            "last_fetched": datetime.now().isoformat(),
            "sitemap_url": sitemap_url,
            "total_urls": len(all_urls),
        },
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
