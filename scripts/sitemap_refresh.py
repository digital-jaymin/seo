#!/usr/bin/env python3
"""
sitemap_refresh.py
Fetches all 4 Innova Retail Shopify sitemaps from the live site,
saves raw XML, diffs against the previous snapshot, and discovers
new content opportunities.

Run via GitHub Actions (refresh-sitemaps.yml) — not locally in the
Claude cloud environment, which cannot reach innovaretail.co.in.
"""

import json
import sys
import time
import xml.etree.ElementTree as ET
from datetime import date, datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    sys.exit(1)

BASE_URL = "https://innovaretail.co.in"

SITEMAPS = {
    "products":    f"{BASE_URL}/sitemap_products_1.xml",
    "collections": f"{BASE_URL}/sitemap_collections_1.xml",
    "pages":       f"{BASE_URL}/sitemap_pages_1.xml",
    "blogs":       f"{BASE_URL}/sitemap_blogs_1.xml",
}

RAW_DIR      = Path("data/sitemaps/raw")
SITEMAP_JSON = Path("data/sitemap/sitemap-urls.json")
CHANGES_JSON = Path("data/sitemap/sitemap-changes.json")
KW_CSV       = Path("data/keywords/keyword-opportunities.csv")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; InnovaRetailSEOBot/1.0; "
        "+https://innovaretail.co.in)"
    ),
    "Accept": "text/xml,application/xml,*/*",
}

NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


# ---------------------------------------------------------------------------
# Fetch helpers
# ---------------------------------------------------------------------------

def fetch_xml(url: str, retries: int = 3) -> bytes:
    """Fetch URL with retry; raise ValueError if response is not XML."""
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            content = resp.content
            text_start = content.lstrip()[:100].decode("utf-8", errors="replace")
            if text_start.startswith("<html") or text_start.lower().startswith("<!doctype"):
                raise ValueError(
                    f"Server returned HTML instead of XML for {url}. "
                    "Shopify may be returning an error page."
                )
            return content
        except requests.exceptions.Timeout as e:
            last_err = e
            print(f"  Timeout on attempt {attempt}/{retries} — waiting {2 ** attempt}s…")
            if attempt < retries:
                time.sleep(2 ** attempt)
        except requests.exceptions.RequestException as e:
            last_err = e
            print(f"  Request error on attempt {attempt}/{retries}: {e}")
            if attempt < retries:
                time.sleep(2 ** attempt)

    print(f"ERROR: Failed to fetch {url} after {retries} attempts: {last_err}")
    sys.exit(1)


def save_raw_xml(name: str, content: bytes) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{name}.xml"
    path.write_bytes(content)
    return path


# ---------------------------------------------------------------------------
# Parse helpers
# ---------------------------------------------------------------------------

def parse_urls(content: bytes) -> list[dict]:
    """Return list of {url, lastmod} from a urlset XML."""
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        raise ValueError(f"XML parse error: {e}") from e

    entries = []
    seen = set()
    for url_el in root.findall(f"{{{NS}}}url"):
        loc = (url_el.findtext(f"{{{NS}}}loc") or "").strip()
        if not loc or loc in seen:
            continue
        seen.add(loc)
        lastmod = (url_el.findtext(f"{{{NS}}}lastmod") or "").strip()
        entries.append({"url": loc, "lastmod": lastmod})

    return entries


def urls_to_set(entries: list[dict]) -> set[str]:
    return {e["url"] for e in entries}


# ---------------------------------------------------------------------------
# Content-gap discovery
# ---------------------------------------------------------------------------

def load_existing_keyword_slugs() -> set[str]:
    """Return set of blog slugs already in keyword-opportunities.csv."""
    if not KW_CSV.exists():
        return set()
    slugs = set()
    with open(KW_CSV) as f:
        for line in f:
            parts = line.strip().split(",")
            if parts:
                raw = parts[0].lower().strip().replace(" ", "-")
                raw = "".join(c for c in raw if c.isalnum() or c == "-")
                slugs.add(raw)
    return slugs


def extract_collection_slug(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def find_content_gaps(blog_entries: list[dict], collection_entries: list[dict]) -> list[dict]:
    """
    Surface collection pages that have no corresponding blog article.
    Returns list of gap dicts — only NEW gaps not already in keyword-opportunities.csv.
    """
    existing_kw_slugs = load_existing_keyword_slugs()

    blog_slugs = {e["url"].rstrip("/").split("/")[-1] for e in blog_entries}

    gaps = []
    for entry in collection_entries:
        slug = extract_collection_slug(entry["url"])
        if slug in ("all", "frontpage", ""):
            continue
        topic = slug.replace("-", " ").title()
        topic_slug = slug

        # Skip if already covered by a blog or keyword opportunity
        already_in_blog = any(topic_slug in b for b in blog_slugs)
        already_in_kw   = topic_slug in existing_kw_slugs or slug in existing_kw_slugs

        if not already_in_blog and not already_in_kw:
            gaps.append({
                "collection_url": entry["url"],
                "collection_slug": slug,
                "suggested_topic": topic,
                "gap_type": "collection_without_blog",
            })

    return gaps


# ---------------------------------------------------------------------------
# Diff helpers
# ---------------------------------------------------------------------------

def compute_diff(prev_entries: list[dict], curr_entries: list[dict]) -> dict:
    prev_set = urls_to_set(prev_entries)
    curr_set = urls_to_set(curr_entries)
    return {
        "added":   sorted(curr_set - prev_set),
        "removed": sorted(prev_set - curr_set),
    }


# ---------------------------------------------------------------------------
# Load / save JSON
# ---------------------------------------------------------------------------

def load_existing_sitemap_json() -> dict:
    if not SITEMAP_JSON.exists():
        return {}
    with open(SITEMAP_JSON) as f:
        return json.load(f)


def load_existing_changes_json() -> dict:
    if not CHANGES_JSON.exists():
        return {"refresh_history": []}
    with open(CHANGES_JSON) as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"refresh_history": []}


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    today = date.today().isoformat()
    now   = datetime.now().isoformat()

    print("=== Innova Retail — Sitemap Refresh ===")
    print(f"Date: {today}\n")

    # Load previous snapshot
    prev = load_existing_sitemap_json()
    prev_blog_entries       = prev.get("blog_urls", [])
    prev_product_entries    = prev.get("product_urls", [])
    prev_collection_entries = prev.get("collection_urls", [])
    prev_other_entries      = prev.get("other_urls", [])

    # Fetch all 4 sitemaps
    fetched: dict[str, list[dict]] = {}
    raw_paths: dict[str, str] = {}

    for name, url in SITEMAPS.items():
        print(f"Fetching {name}: {url}")
        raw = fetch_xml(url)
        raw_path = save_raw_xml(name, raw)
        raw_paths[name] = str(raw_path)
        entries = parse_urls(raw)
        fetched[name] = entries
        print(f"  {len(entries)} URLs found → saved to {raw_path}")

    blog_entries       = fetched["blogs"]
    product_entries    = fetched["products"]
    collection_entries = fetched["collections"]
    other_entries      = fetched["pages"]

    # Compute diffs
    diff_blogs       = compute_diff(prev_blog_entries,       blog_entries)
    diff_products    = compute_diff(prev_product_entries,    product_entries)
    diff_collections = compute_diff(prev_collection_entries, collection_entries)
    diff_pages       = compute_diff(prev_other_entries,      other_entries)

    total_added   = sum(len(d["added"])   for d in [diff_blogs, diff_products, diff_collections, diff_pages])
    total_removed = sum(len(d["removed"]) for d in [diff_blogs, diff_products, diff_collections, diff_pages])
    has_changes   = total_added > 0 or total_removed > 0

    print(f"\nDiff summary:")
    print(f"  Added   : {total_added}")
    print(f"  Removed : {total_removed}")

    # Content-gap discovery
    gaps = find_content_gaps(blog_entries, collection_entries)
    print(f"\nNew content gaps discovered: {len(gaps)}")
    for g in gaps[:5]:
        print(f"  {g['collection_slug']}")
    if len(gaps) > 5:
        print(f"  … and {len(gaps) - 5} more")

    # Build blog_urls list with topic/cluster fields from previous where available
    prev_blog_map = {e["url"]: e for e in prev_blog_entries}
    new_blog_urls = []
    for entry in blog_entries:
        prev_entry = prev_blog_map.get(entry["url"], {})
        slug  = entry["url"].rstrip("/").split("/")[-1]
        topic = prev_entry.get("topic") or slug.replace("-", " ").title()
        new_blog_urls.append({
            "url":     entry["url"],
            "slug":    slug,
            "topic":   topic,
            "cluster": prev_entry.get("cluster", ""),
            "lastmod": entry.get("lastmod", ""),
        })

    # Preserve non-blog fields from previous snapshot
    preserved_keys = [
        "product_catalog_summary",
        "collection_summary",
    ]
    preserved = {k: prev[k] for k in preserved_keys if k in prev}

    # Preserve existing change_log; add new entry only if something changed
    prev_meta     = prev.get("_meta", {})
    prev_changelog = prev_meta.get("change_log", [])

    new_changelog = list(prev_changelog)
    if has_changes:
        new_changelog.append({
            "date":            today,
            "products_before": len(prev_product_entries),
            "products_after":  len(product_entries),
            "blogs_before":    len(prev_blog_entries),
            "blogs_after":     len(blog_entries),
            "added_blogs":     diff_blogs["added"],
            "removed_blogs":   diff_blogs["removed"],
            "added_products":  diff_products["added"],
            "removed_products": diff_products["removed"],
            "collections_change": (
                len(collection_entries) - len(prev_collection_entries)
            ),
            "pages_change": len(other_entries) - len(prev_other_entries),
        })

    # Merge content_gaps: keep approved, append new
    prev_gaps  = prev.get("content_gaps", [])
    prev_slugs = {g.get("collection_slug") for g in prev_gaps}
    merged_gaps = list(prev_gaps) + [g for g in gaps if g["collection_slug"] not in prev_slugs]

    # Write sitemap-urls.json
    updated = {
        "_meta": {
            "description":  prev_meta.get("description", "Full structured sitemap for innovaretail.co.in"),
            "last_fetched": today,
            "sitemap_url":  f"{BASE_URL}/sitemap.xml",
            "fetch_status": "automated_github_actions",
            "totals": {
                "products":          len(product_entries),
                "collections":       len(collection_entries),
                "pages":             len(other_entries),
                "blogs":             len(blog_entries),
                "grand_total":       (
                    len(product_entries) + len(collection_entries)
                    + len(other_entries) + len(blog_entries)
                ),
            },
            "change_log": new_changelog,
        },
        "sitemap_index": {
            "confirmed": True,
            "nested_sitemaps": [
                {"url": SITEMAPS[n], "type": n,
                 "status": "fetched", "url_count": len(fetched[n])}
                for n in ("products", "collections", "pages", "blogs")
            ],
        },
        **preserved,
        "blog_urls":       new_blog_urls,
        "product_urls":    product_entries,
        "collection_urls": collection_entries,
        "other_urls":      other_entries,
        "content_gaps":    merged_gaps,
    }
    save_json(SITEMAP_JSON, updated)
    print(f"\nUpdated: {SITEMAP_JSON}")

    # Write sitemap-changes.json
    changes_doc = load_existing_changes_json()
    run_record = {
        "run_date":  now,
        "has_changes": has_changes,
        "raw_files": raw_paths,
        "diff": {
            "blogs":       diff_blogs,
            "products":    diff_products,
            "collections": diff_collections,
            "pages":       diff_pages,
        },
        "totals_after": updated["_meta"]["totals"],
        "new_content_gaps": len(gaps),
    }
    changes_doc.setdefault("refresh_history", []).append(run_record)
    changes_doc["latest"] = run_record
    save_json(CHANGES_JSON, changes_doc)
    print(f"Updated: {CHANGES_JSON}")

    # Final summary
    print("\n=== Summary ===")
    print(f"Products    : {len(product_entries)}")
    print(f"Collections : {len(collection_entries)}")
    print(f"Pages       : {len(other_entries)}")
    print(f"Blogs       : {len(blog_entries)}")
    print(f"Changes     : {'YES — commit will be created' if has_changes else 'none — skipping commit'}")

    if not has_changes:
        print("\nNo URL changes detected since last refresh.")
    else:
        print("\nRefresh complete. Files ready to commit.")


if __name__ == "__main__":
    main()
