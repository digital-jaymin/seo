#!/usr/bin/env python3
"""
serpapi_fetcher.py
Fetches SERP data for a given keyword using the SERPAPI free tier.
Saves results to blogs/drafts/[slug]/serp-analysis.json

Usage:
  python scripts/serpapi_fetcher.py --keyword "hp laptop for office use"
  python scripts/serpapi_fetcher.py --keyword "hp laptop for office use" --country in
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

CONFIG_PATH = Path("config/site-config.json")
API_KEYS_PATH = Path("config/api-keys.json")
TEMPLATE_PATH = Path("templates/serp-analysis-template.json")

SERPAPI_ENDPOINT = "https://serpapi.com/search.json"


def load_api_key():
    if not API_KEYS_PATH.exists():
        print("ERROR: config/api-keys.json not found.")
        print("Copy config/api-keys.example.json to config/api-keys.json and add your SERPAPI key.")
        sys.exit(1)
    with open(API_KEYS_PATH) as f:
        keys = json.load(f)
    key = keys.get("serpapi_key", "")
    if not key or key == "PASTE_SERPAPI_KEY_HERE":
        print("ERROR: serpapi_key not set in config/api-keys.json")
        print("Get a free SERPAPI key at https://serpapi.com/")
        sys.exit(1)
    return key


def keyword_to_slug(keyword):
    slug = keyword.lower().strip()
    slug = slug.replace(" ", "-")
    slug = "".join(c for c in slug if c.isalnum() or c == "-")
    slug = "-".join(filter(None, slug.split("-")))
    return slug


def fetch_serp(keyword, api_key, country="in", language="en", num=10):
    params = {
        "engine": "google",
        "q": keyword,
        "gl": country,
        "hl": language,
        "num": str(num),
        "api_key": api_key,
    }
    url = SERPAPI_ENDPOINT + "?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "InnovaRetailSEOBot/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"ERROR: SERPAPI returned HTTP {e.code}: {body}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Network error: {e}")
        sys.exit(1)


def parse_organic_results(data):
    results = []
    for item in data.get("organic_results", []):
        results.append({
            "position": item.get("position"),
            "title": item.get("title", ""),
            "url": item.get("link", ""),
            "domain": item.get("displayed_link", ""),
            "meta_description": item.get("snippet", ""),
            "content_type": "unknown",
            "estimated_word_count": None,
            "content_angle": "",
            "da_estimate": "unknown",
        })
    return results


def parse_paa(data):
    return [q.get("question", "") for q in data.get("related_questions", [])]


def parse_related_searches(data):
    return [s.get("query", "") for s in data.get("related_searches", [])]


def parse_featured_snippet(data):
    answer_box = data.get("answer_box", {})
    snippet_type = answer_box.get("type", "none")
    content = answer_box.get("answer") or answer_box.get("snippet") or ""
    return {
        "present": bool(answer_box),
        "type": snippet_type if snippet_type else "none",
        "content": content,
    }


def build_serp_analysis(keyword, data):
    organic = parse_organic_results(data)
    paa = parse_paa(data)
    related = parse_related_searches(data)
    snippet = parse_featured_snippet(data)

    serp_features = {
        "shopping_results": bool(data.get("shopping_results")),
        "image_pack": bool(data.get("images_results")),
        "video_results": bool(data.get("inline_videos")),
        "local_pack": bool(data.get("local_results")),
        "knowledge_panel": bool(data.get("knowledge_graph")),
    }

    return {
        "keyword": keyword,
        "country": "India",
        "search_date": datetime.now().isoformat(),
        "data_source": "SERPAPI",
        "top_10_results": organic,
        "people_also_ask": paa,
        "related_searches": related,
        "featured_snippet": snippet,
        "serp_features": serp_features,
        "competitor_analysis": {
            "average_word_count": None,
            "common_h2_topics": [],
            "content_gaps": [],
            "winning_angle_for_innova": "TODO: Analyze results and fill this in",
        },
    }


def save_result(slug, analysis):
    output_dir = Path(f"blogs/drafts/{slug}")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "serp-analysis.json"
    with open(output_path, "w") as f:
        json.dump(analysis, f, indent=2)
    print(f"Saved SERP analysis to {output_path}")
    return output_path


def create_manual_instruction(keyword, slug):
    """Create a manual SERP research instruction file when no API key is available."""
    output_dir = Path(f"blogs/drafts/{slug}")
    output_dir.mkdir(parents=True, exist_ok=True)
    instruction_path = output_dir / "serp-manual-research.md"

    content = f"""# Manual SERP Research Instructions

**Keyword:** {keyword}
**Country:** India (search on google.co.in or with location set to India)

## Steps

1. Open an incognito window
2. Go to google.co.in
3. Search: `{keyword}`
4. Copy the following for each of the top 10 results:
   - Position (1–10)
   - Title
   - URL
   - Meta description snippet
5. Copy all **People Also Ask** questions
6. Copy all **Related searches** from the bottom
7. Note any featured snippet (paragraph, list, or table)

## Fill in the SERP Analysis

Paste your findings into `serp-analysis.json` using the template at:
`templates/serp-analysis-template.json`

Then ask Claude to analyze the SERP data using:
`prompts/serp-analysis-prompt.md`
"""
    with open(instruction_path, "w") as f:
        f.write(content)
    print(f"Manual research instructions saved to {instruction_path}")


def main():
    parser = argparse.ArgumentParser(description="Fetch SERP data via SERPAPI")
    parser.add_argument("--keyword", required=True, help="Keyword to fetch SERP for")
    parser.add_argument("--country", default="in", help="Country code (default: in for India)")
    parser.add_argument("--manual", action="store_true", help="Skip API, create manual research instructions")
    args = parser.parse_args()

    keyword = args.keyword.strip()
    slug = keyword_to_slug(keyword)

    print(f"Keyword: {keyword}")
    print(f"Slug: {slug}")

    if args.manual:
        create_manual_instruction(keyword, slug)
        return

    api_key = load_api_key()
    print("Fetching SERP data from SERPAPI...")
    data = fetch_serp(keyword, api_key, country=args.country)
    analysis = build_serp_analysis(keyword, data)
    output_path = save_result(slug, analysis)

    print(f"\nTop results found: {len(analysis['top_10_results'])}")
    print(f"PAA questions: {len(analysis['people_also_ask'])}")
    print(f"Related searches: {len(analysis['related_searches'])}")
    print(f"\nNext: Ask Claude to analyze {output_path} using prompts/serp-analysis-prompt.md")


if __name__ == "__main__":
    main()
