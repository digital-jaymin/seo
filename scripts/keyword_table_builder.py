#!/usr/bin/env python3
"""
keyword_table_builder.py
Builds and updates keyword-opportunities.csv using the SEO memory system.

Before adding any keyword, runs full memory validation:
- Checks if keyword is collection-owned (transactional)
- Checks cannibalization against all published/draft blogs
- Determines target_page_type (blog vs collection)
- Resolves supported_collection_page and internal_link_targets
- Only keywords that pass memory validation get status "approved"

Usage:
  python scripts/keyword_table_builder.py                  # recalculate existing
  python scripts/keyword_table_builder.py semrush.csv      # import + validate
"""

import csv
import json
import sys
from pathlib import Path
from datetime import datetime

from seo_memory import load_memory

KEYWORDS_PATH = Path("data/keywords/keyword-opportunities.csv")

COLUMNS = [
    "keyword", "intent", "cluster", "source",
    "commercial_score", "informational_score", "priority_score",
    "semrush_volume", "semrush_kd", "semrush_cpc",
    "target_page_type", "supported_collection_page",
    "cannibalization_risk", "internal_link_targets",
    "status", "notes",
]


def load_existing():
    if not KEYWORDS_PATH.exists():
        return {}
    with open(KEYWORDS_PATH, newline="", encoding="utf-8") as f:
        return {row["keyword"].lower().strip(): row for row in csv.DictReader(f)}


def calculate_priority(row):
    try:
        commercial     = float(row.get("commercial_score") or 0)
        informational  = float(row.get("informational_score") or 0)
        volume         = float(row.get("semrush_volume") or 0)
        kd             = row.get("semrush_kd", "")

        volume_score = 10 if volume > 5000 else 7 if volume > 1000 else 4 if volume > 300 else 1
        kd_val       = float(kd) if kd else None
        kd_bonus     = 10 if kd_val is not None and kd_val < 30 else \
                        6 if kd_val is not None and kd_val < 50 else \
                        2 if kd_val is not None and kd_val < 70 else 0

        if kd_val is not None:
            score = (commercial * 0.4) + (informational * 0.2) + (volume_score * 0.3) + (kd_bonus * 0.1)
        else:
            score = (commercial * 0.6) + (informational * 0.4)

        return round(score, 2)
    except (ValueError, TypeError):
        return 0.0


def merge_keywords(existing, new_rows, memory):
    merged  = dict(existing)
    added   = 0
    updated = 0
    blocked = 0

    for row in new_rows:
        key     = row.get("keyword", "").lower().strip()
        cluster = row.get("cluster", "General")
        intent  = row.get("intent", "informational")
        if not key:
            continue

        # Full memory validation
        validation = memory.validate_topic(key, cluster, intent)

        row["target_page_type"]        = validation["target_page_type"]
        row["supported_collection_page"] = validation["supported_collection_page"] or ""
        row["cannibalization_risk"]    = validation["cannibalization_risk"]
        row["internal_link_targets"]   = " | ".join(validation["internal_link_targets"][:5])
        row["priority_score"]          = calculate_priority(row)

        if not validation["approved_for_blog"]:
            row["status"] = "blocked"
            rejection = validation.get("rejection_reason", "Memory validation failed")
            row["notes"] = (row.get("notes", "") + f" | BLOCKED: {rejection}").strip(" |")
            blocked += 1
            print(f"  BLOCKED: {key} — {rejection[:80]}")
        elif validation["cannibalization_risk"] in ("medium",):
            row["status"] = "review_needed"
            conflicts = validation.get("cannibalization_conflicts", [])
            row["notes"] = (row.get("notes", "") + f" | CANNIBALIZATION WATCH: {[c['title'] for c in conflicts]}").strip(" |")

        if key in merged:
            existing_row = merged[key]
            for field in ["semrush_volume", "semrush_kd", "semrush_cpc"]:
                if row.get(field) and not existing_row.get(field):
                    existing_row[field] = row[field]
            # Always refresh memory-derived fields
            for field in ["target_page_type", "supported_collection_page", "cannibalization_risk", "internal_link_targets"]:
                existing_row[field] = row[field]
            existing_row["priority_score"] = calculate_priority(existing_row)
            updated += 1
        else:
            merged[key] = row
            added += 1

    print(f"\nKeywords: {added} added, {updated} updated, {blocked} blocked, {len(merged)} total")
    return merged


def save_keywords(merged_dict):
    rows = sorted(merged_dict.values(), key=lambda r: float(r.get("priority_score") or 0), reverse=True)
    KEYWORDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(KEYWORDS_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} keywords to {KEYWORDS_PATH}")


def import_from_csv(import_path):
    with open(import_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    print("Loading SEO memory...")
    memory   = load_memory()
    existing = load_existing()

    print(f"Memory loaded: {len(memory.keywords)} keywords, {len(memory.blog_slugs)} blogs, {len(memory.collection_urls)} collections")

    if len(sys.argv) > 1:
        import_path = Path(sys.argv[1])
        if not import_path.exists():
            print(f"ERROR: File not found: {import_path}")
            sys.exit(1)
        print(f"Importing from: {import_path}")
        new_rows = import_from_csv(import_path)
    else:
        print("No import file — recalculating scores and refreshing memory fields for existing keywords.")
        new_rows = list(existing.values())
        existing = {}

    merged = merge_keywords(existing, new_rows, memory)
    save_keywords(merged)
    print("\nDone. Next: review blocked/flagged keywords, then upload approved ones to SEMrush.")


if __name__ == "__main__":
    main()
