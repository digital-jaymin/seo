#!/usr/bin/env python3
"""
serper_fetcher.py
Fetches SERP data for a given keyword using Serper.dev.
Reads SERPER_API_KEY from environment variable (set by GitHub Actions secret).
Saves results to blogs/drafts/[slug]/serp-analysis.json

Usage (local):
  SERPER_API_KEY=your_key python scripts/serper_fetcher.py --keyword "hp victus vs hp omen"

Usage (GitHub Actions):
  Set SERPER_API_KEY env var from secrets.SERPER_API_KEY and run the same command.
"""

import argparse
import json
import os
import sys
import requests
from datetime import datetime
from pathlib import Path

SERPER_ENDPOINT = "https://google.serper.dev/search"


def load_api_key():
    key = os.environ.get("SERPER_API_KEY", "").strip()
    if not key or key == "PASTE_SERPER_KEY_HERE":
        print("ERROR: SERPER_API_KEY environment variable is not set.")
        print("In GitHub Actions: add SERPER_API_KEY to repository secrets.")
        sys.exit(1)
    return key


def keyword_to_slug(keyword):
    slug = keyword.lower().strip().replace(" ", "-")
    slug = "".join(c for c in slug if c.isalnum() or c == "-")
    return "-".join(filter(None, slug.split("-")))


def fetch_serp(keyword, api_key, country="in", language="en", num=10):
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "q": keyword,
        "gl": country,
        "hl": language,
        "num": num,
    }
    try:
        response = requests.post(SERPER_ENDPOINT, headers=headers, json=payload, timeout=20)
        if response.status_code != 200:
            print(f"ERROR: Serper returned HTTP {response.status_code}")
            print(f"Response: {response.text[:300]}")
            sys.exit(1)
        return response.json()
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out after 20 seconds.")
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Network error: {e}")
        sys.exit(1)


def parse_organic_results(data):
    results = []
    for item in data.get("organic", []):
        results.append({
            "position": item.get("position"),
            "title": item.get("title", ""),
            "url": item.get("link", ""),
            "domain": item.get("displayedLink", ""),
            "meta_description": item.get("snippet", ""),
            "content_type": "unknown",
            "estimated_word_count": None,
            "content_angle": "",
            "da_estimate": "unknown",
        })
    return results


def parse_paa(data):
    return [q.get("question", "") for q in data.get("peopleAlsoAsk", [])]


def parse_related_searches(data):
    return [s.get("query", "") for s in data.get("relatedSearches", [])]


def parse_featured_snippet(data):
    box = data.get("answerBox", {})
    content = box.get("answer") or box.get("snippet") or ""
    snippet_type = box.get("type", "none") if box else "none"
    return {
        "present": bool(box),
        "type": snippet_type,
        "content": content,
    }


def build_serp_analysis(keyword, country_code, data):
    organic = parse_organic_results(data)
    paa = parse_paa(data)
    related = parse_related_searches(data)
    snippet = parse_featured_snippet(data)

    country_name = "India" if country_code == "in" else country_code.upper()

    serp_features = {
        "shopping_results": bool(data.get("shopping")),
        "image_pack": bool(data.get("images")),
        "video_results": bool(data.get("videos")),
        "local_pack": bool(data.get("places")),
        "knowledge_panel": bool(data.get("knowledgeGraph")),
    }

    return {
        "keyword": keyword,
        "country": country_name,
        "search_date": datetime.now().isoformat(),
        "data_source": "Serper.dev",
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
    print(f"Saved: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Fetch SERP data via Serper.dev")
    parser.add_argument("--keyword", required=True, help="Keyword to search (e.g. 'hp victus vs hp omen')")
    parser.add_argument("--country", default="in", help="Country code (default: in for India)")
    args = parser.parse_args()

    keyword = args.keyword.strip()
    slug = keyword_to_slug(keyword)

    print(f"Keyword : {keyword}")
    print(f"Slug    : {slug}")
    print(f"Country : {args.country}")

    api_key = load_api_key()
    print("Fetching SERP data from Serper.dev...")

    data = fetch_serp(keyword, api_key, country=args.country)
    analysis = build_serp_analysis(keyword, args.country, data)
    output_path = save_result(slug, analysis)

    print(f"\nOrganic results : {len(analysis['top_10_results'])}")
    print(f"PAA questions   : {len(analysis['people_also_ask'])}")
    print(f"Related searches: {len(analysis['related_searches'])}")
    print(f"Featured snippet: {'yes' if analysis['featured_snippet']['present'] else 'no'}")
    print(f"\nNext: Ask Claude to create blueprint using {output_path}")


if __name__ == "__main__":
    main()
