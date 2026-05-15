#!/usr/bin/env python3
"""
blog_folder_creator.py
Creates the standard blog folder for a new topic.

Before creating anything, runs full SEO memory validation:
- Blocks keywords that are collection-owned (transactional)
- Blocks topics that cannibalize existing published blogs
- Requires the topic to support a specific cluster and collection page
- Writes memory-derived fields into metadata.json

Usage:
  python scripts/blog_folder_creator.py \
    --keyword "best gaming laptop under 70000" \
    --cluster "Gaming Laptops" \
    --intent "informational"

  python scripts/blog_folder_creator.py \
    --keyword "HP laptop for office use india" \
    --cluster "Business IT" \
    --intent "informational" \
    --force   # skip confirmation prompt
"""

import argparse
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

from seo_memory import load_memory

TEMPLATES_DIR    = Path("templates")
BLOGS_DIR        = Path("blogs/drafts")
CONTENT_INDEX    = Path("data/content-database/content-index.json")
TOPICAL_MAP_PATH = Path("data/topical-authority/topical-authority-map.json")


def keyword_to_slug(keyword):
    slug = keyword.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return re.sub(r"-+", "-", slug).strip("-")


def next_blog_id(content_index):
    total = content_index.get("_meta", {}).get("total_blogs", 0)
    return f"BLOG-{str(total + 1).zfill(3)}"


def load_content_index():
    if not CONTENT_INDEX.exists():
        return {"_meta": {"total_blogs": 0}, "blogs": []}
    with open(CONTENT_INDEX) as f:
        return json.load(f)


def save_content_index(data):
    with open(CONTENT_INDEX, "w") as f:
        json.dump(data, f, indent=2)


def create_blog_folder(slug):
    blog_dir = BLOGS_DIR / slug
    if blog_dir.exists():
        print(f"WARNING: Folder already exists: {blog_dir}")
        return blog_dir
    blog_dir.mkdir(parents=True)
    return blog_dir


def copy_templates(blog_dir, slug, keyword, cluster, intent, blog_id, today, validation):
    files_created = []

    # metadata.json — enriched with memory fields
    meta_template = TEMPLATES_DIR / "blog-metadata-template.json"
    meta_dest     = blog_dir / "metadata.json"
    if meta_template.exists():
        with open(meta_template) as f:
            meta = json.load(f)
        meta["blog_id"]                  = blog_id
        meta["primary_keyword"]          = keyword
        meta["cluster"]                  = cluster
        meta["intent"]                   = intent
        meta["slug"]                     = f"/blogs/insights/{slug}"
        meta["status"]                   = "draft"
        meta["created_date"]             = today
        meta["updated_date"]             = today
        meta["blog_folder"]              = f"blogs/drafts/{slug}/"
        meta["target_page_type"]         = validation["target_page_type"]
        meta["parent_cluster"]           = validation["parent_cluster"]
        meta["supported_collection_page"] = validation["supported_collection_page"]
        meta["all_supported_collections"] = validation["all_supported_collections"]
        meta["cannibalization_risk"]     = validation["cannibalization_risk"]
        meta["internal_link_targets"]    = validation["internal_link_targets"]
        with open(meta_dest, "w") as f:
            json.dump(meta, f, indent=2)
        files_created.append("metadata.json")

    # serp-analysis.json
    serp_template = TEMPLATES_DIR / "serp-analysis-template.json"
    if serp_template.exists():
        with open(serp_template) as f:
            serp = json.load(f)
        serp["keyword"] = keyword
        with open(blog_dir / "serp-analysis.json", "w") as f:
            json.dump(serp, f, indent=2)
        files_created.append("serp-analysis.json")

    # blueprint.md
    blueprint_template = TEMPLATES_DIR / "blog-blueprint-template.md"
    if blueprint_template.exists():
        content = blueprint_template.read_text()
        content = content.replace("[PRIMARY KEYWORD]", keyword)
        content = content.replace("[DATE]", today)
        content = content.replace("[CLUSTER]", cluster)
        content = content.replace("[INTENT]", intent)
        (blog_dir / "blueprint.md").write_text(content)
        files_created.append("blueprint.md")

    # article.md
    article_template = TEMPLATES_DIR / "article-template.md"
    if article_template.exists():
        shutil.copy(article_template, blog_dir / "article.md")
        files_created.append("article.md")

    # article.html
    html_template = TEMPLATES_DIR / "shopify-html-template.html"
    if html_template.exists():
        shutil.copy(html_template, blog_dir / "article.html")
        files_created.append("article.html")

    # qa-report.md
    qa_template = TEMPLATES_DIR / "qa-report-template.md"
    if qa_template.exists():
        content = qa_template.read_text()
        content = content.replace("[BLOG TITLE]", keyword.title())
        content = content.replace("[primary keyword]", keyword)
        content = content.replace("[/blogs/slug]", f"/blogs/insights/{slug}")
        content = content.replace("[DATE]", today)
        (blog_dir / "qa-report.md").write_text(content)
        files_created.append("qa-report.md")

    # shopify-draft.json
    shopify_draft = {
        "blog_post": {
            "title": "TODO: Set in blueprint step",
            "body_html": "TODO: Generated in Step 7",
            "meta_title": "TODO: Generated in Step 5",
            "meta_description": "TODO: Generated in Step 5",
            "handle": slug,
            "tags": [cluster],
            "status": "draft",
            "published": False,
        },
        "workflow_notes": {
            "qa_score": None,
            "primary_keyword": keyword,
            "cluster": cluster,
            "intent": intent,
            "target_page_type": validation["target_page_type"],
            "supported_collection": validation["supported_collection_page"],
            "internal_link_targets": validation["internal_link_targets"],
            "cannibalization_risk": validation["cannibalization_risk"],
            "notes_for_publisher": "Do not publish automatically. Manual review required. QA score must be ≥ 85.",
            "ready_for_automation": False,
        },
    }
    with open(blog_dir / "shopify-draft.json", "w") as f:
        json.dump(shopify_draft, f, indent=2)
    files_created.append("shopify-draft.json")

    return files_created


def register_blog(content_index, blog_id, keyword, slug, cluster, intent, today, validation):
    entry = {
        "blog_id":                  blog_id,
        "title":                    "",
        "primary_keyword":          keyword,
        "secondary_keywords":       [],
        "cluster":                  cluster,
        "intent":                   intent,
        "slug":                     f"/blogs/insights/{slug}",
        "status":                   "draft",
        "created_date":             today,
        "updated_date":             today,
        "shopify_status":           "not_uploaded",
        "target_page_type":         validation["target_page_type"],
        "parent_cluster":           validation["parent_cluster"],
        "supported_collection_page": validation["supported_collection_page"],
        "internal_links":           validation["internal_link_targets"],
        "cannibalization_risk":     validation["cannibalization_risk"],
        "cannibalization_notes":    validation.get("rejection_reason", ""),
        "ranking_notes":            "",
    }
    content_index["blogs"].append(entry)
    content_index.setdefault("_meta", {})["total_blogs"] = len(content_index["blogs"])
    content_index["_meta"]["last_updated"] = today
    return content_index


def update_topical_map(slug, cluster, blog_id, today):
    if not TOPICAL_MAP_PATH.exists():
        return
    with open(TOPICAL_MAP_PATH) as f:
        tmap = json.load(f)
    cluster_data = tmap.get("clusters", {}).get(cluster, {})
    spoke_blogs  = cluster_data.get("spoke_blogs", [])
    full_slug    = f"/blogs/insights/{slug}"
    if full_slug not in spoke_blogs:
        spoke_blogs.append(full_slug)
    cluster_data["spoke_blogs"]  = spoke_blogs
    cluster_data["blog_count"]   = cluster_data.get("blog_count", 0) + 1
    cluster_data["last_updated"] = today

    # Remove from gap_articles if present
    cluster_data["gap_articles"] = [
        g for g in cluster_data.get("gap_articles", [])
        if slug not in (g.get("target_keyword", "").lower().replace(" ", "-"))
    ]

    tmap.setdefault("clusters", {})[cluster] = cluster_data
    tmap["_meta"]["last_updated"] = today
    with open(TOPICAL_MAP_PATH, "w") as f:
        json.dump(tmap, f, indent=2)


def print_validation_report(validation):
    print("\n── SEO Memory Validation ──────────────────────────────")
    print(f"  Keyword:               {validation['keyword']}")
    print(f"  Target page type:      {validation['target_page_type']}")
    print(f"  Parent cluster:        {validation['parent_cluster']}")
    print(f"  Supported collection:  {validation['supported_collection_page']}")
    print(f"  Cannibalization risk:  {validation['cannibalization_risk']}")
    if validation.get("cannibalization_conflicts"):
        for c in validation["cannibalization_conflicts"]:
            print(f"    ⚠ Conflicts with [{c['blog_id']}] {c['title']} ({c['overlap_pct']}% overlap)")
    print(f"  Internal link targets: {len(validation['internal_link_targets'])} targets")
    for t in validation["internal_link_targets"][:5]:
        print(f"    → {t}")
    print(f"  Approved for blog:     {'YES' if validation['approved_for_blog'] else 'NO — ' + str(validation.get('rejection_reason', ''))}")
    print("───────────────────────────────────────────────────────\n")


def main():
    parser = argparse.ArgumentParser(description="Create memory-validated blog folder")
    parser.add_argument("--keyword", required=True, help="Primary keyword for the blog")
    parser.add_argument("--cluster",  default="General",       help="Content cluster")
    parser.add_argument("--intent",   default="informational", help="Search intent")
    parser.add_argument("--force",    action="store_true",     help="Skip confirmation prompt")
    args = parser.parse_args()

    keyword = args.keyword.strip()
    slug    = keyword_to_slug(keyword)
    today   = datetime.now().strftime("%Y-%m-%d")

    print("Loading SEO memory...")
    memory = load_memory()

    # Full validation
    validation = memory.validate_topic(keyword, args.cluster, args.intent)
    print_validation_report(validation)

    if not validation["approved_for_blog"]:
        print(f"BLOCKED: {validation['rejection_reason']}")
        print("If this is a blog that SUPPORTS a collection (informational angle), re-run with a different keyword framing.")
        print("If you want to force creation anyway, re-run with --force")
        if not args.force:
            return

    if validation["cannibalization_risk"] == "medium" and not args.force:
        print("WARNING: Medium cannibalization risk detected. Review conflicts above.")
        confirm = input("Continue anyway? (y/N): ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            return

    content_index = load_content_index()
    blog_id  = next_blog_id(content_index)
    blog_dir = create_blog_folder(slug)
    files_created = copy_templates(blog_dir, slug, keyword, args.cluster, args.intent, blog_id, today, validation)
    content_index = register_blog(content_index, blog_id, keyword, slug, args.cluster, args.intent, today, validation)
    save_content_index(content_index)
    update_topical_map(slug, args.cluster, blog_id, today)

    print(f"Blog folder created: {blog_dir}")
    print(f"Blog ID: {blog_id}")
    print(f"Files: {', '.join(files_created)}")
    print(f"\nNext steps:")
    print(f"  1. SERP analysis:  python scripts/serpapi_fetcher.py --keyword \"{keyword}\"")
    print(f"  2. Blueprint:      Use prompts/blog-blueprint-prompt.md")
    print(f"  3. Write article:  Use prompts/blog-writing-prompt.md")
    print(f"  4. Internal links to add:")
    for t in validation["internal_link_targets"][:6]:
        print(f"     → {t}")


if __name__ == "__main__":
    main()
