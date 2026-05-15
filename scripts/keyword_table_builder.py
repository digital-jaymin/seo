#!/usr/bin/env python3
"""
keyword_table_builder.py
Builds and updates keyword-opportunities.csv.
Merges new Claude-generated keywords with existing table.
Deduplicates, recalculates priority scores, and sorts by priority.
"""

import csv
import json
import sys
from pathlib import Path
from datetime import datetime

KEYWORDS_PATH = Path("data/keywords/keyword-opportunities.csv")
CONTENT_INDEX_PATH = Path("data/content-database/content-index.json")

COLUMNS = [
    "keyword", "intent", "cluster", "source",
    "commercial_score", "informational_score", "priority_score",
    "semrush_volume", "semrush_kd", "semrush_cpc",
    "status", "notes"
]


def load_existing_keywords():
    if not KEYWORDS_PATH.exists():
        return {}
    with open(KEYWORDS_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["keyword"].lower().strip(): row for row in reader}


def calculate_priority(row):
    try:
        commercial = float(row.get("commercial_score") or 0)
        informational = float(row.get("informational_score") or 0)
        volume = float(row.get("semrush_volume") or 0)
        kd = row.get("semrush_kd", "")

        volume_score = 10 if volume > 5000 else 7 if volume > 1000 else 4 if volume > 300 else 1
        kd_val = float(kd) if kd else None
        kd_bonus = 10 if kd_val is not None and kd_val < 30 else \
                   6 if kd_val is not None and kd_val < 50 else \
                   2 if kd_val is not None and kd_val < 70 else 0

        if kd_val is not None:
            score = (commercial * 0.4) + (informational * 0.2) + (volume_score * 0.3) + (kd_bonus * 0.1)
        else:
            score = (commercial * 0.6) + (informational * 0.4)

        return round(score, 2)
    except (ValueError, TypeError):
        return 0.0


def check_cannibalization(keyword, content_index):
    """Simple overlap check against existing blog titles and primary keywords."""
    keyword_words = set(keyword.lower().split())
    risks = []
    for blog in content_index.get("blogs", []):
        existing_kw = blog.get("primary_keyword", "").lower()
        existing_words = set(existing_kw.split())
        overlap = keyword_words & existing_words
        overlap_pct = len(overlap) / max(len(keyword_words), 1)
        if overlap_pct >= 0.7:
            risks.append(f"Overlaps with '{blog['title']}' ({int(overlap_pct*100)}%)")
    return "; ".join(risks) if risks else ""


def load_content_index():
    if not CONTENT_INDEX_PATH.exists():
        return {"blogs": []}
    with open(CONTENT_INDEX_PATH) as f:
        return json.load(f)


def merge_keywords(existing, new_rows, content_index):
    merged = dict(existing)
    added = 0
    updated = 0

    for row in new_rows:
        key = row.get("keyword", "").lower().strip()
        if not key:
            continue

        cannibalization = check_cannibalization(key, content_index)
        row["priority_score"] = calculate_priority(row)
        if cannibalization:
            row["notes"] = (row.get("notes", "") + f" | CANNIBALIZATION RISK: {cannibalization}").strip(" |")
            row["status"] = "cannibalization_risk"

        if key in merged:
            # Update semrush fields if newly available
            existing_row = merged[key]
            for field in ["semrush_volume", "semrush_kd", "semrush_cpc"]:
                if row.get(field) and not existing_row.get(field):
                    existing_row[field] = row[field]
            existing_row["priority_score"] = calculate_priority(existing_row)
            updated += 1
        else:
            merged[key] = row
            added += 1

    print(f"Keywords: {added} added, {updated} updated, {len(merged)} total")
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
    """Import new keywords from a separate CSV file."""
    with open(import_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def main():
    content_index = load_content_index()
    existing = load_existing_keywords()

    if len(sys.argv) > 1:
        import_path = Path(sys.argv[1])
        if not import_path.exists():
            print(f"ERROR: File not found: {import_path}")
            sys.exit(1)
        print(f"Importing from: {import_path}")
        new_rows = import_from_csv(import_path)
    else:
        print("No import file specified. Recalculating priority scores for existing keywords.")
        new_rows = []

    merged = merge_keywords(existing, new_rows, content_index)
    save_keywords(merged)
    print("Done. Next: upload keyword-opportunities.csv to SEMrush for validation.")


if __name__ == "__main__":
    main()
