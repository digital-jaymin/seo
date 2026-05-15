#!/usr/bin/env python3
"""
blog_folder_creator.py
Creates the standard blog folder structure for a new keyword/topic.
Copies all template files into the new folder.
Registers the blog in content-index.json.

Usage:
  python scripts/blog_folder_creator.py --keyword "best hp laptop for business india"
  python scripts/blog_folder_creator.py --keyword "smart lock price india" --cluster "ELV Products"
"""

import argparse
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

TEMPLATES_DIR = Path("templates")
BLOGS_DIR = Path("blogs/drafts")
CONTENT_INDEX_PATH = Path("data/content-database/content-index.json")


def keyword_to_slug(keyword):
    slug = keyword.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def next_blog_id(content_index):
    total = content_index.get("_meta", {}).get("total_blogs", 0)
    return f"BLOG-{str(total + 1).zfill(3)}"


def load_content_index():
    if not CONTENT_INDEX_PATH.exists():
        return {"_meta": {"total_blogs": 0}, "blogs": []}
    with open(CONTENT_INDEX_PATH) as f:
        return json.load(f)


def save_content_index(data):
    with open(CONTENT_INDEX_PATH, "w") as f:
        json.dump(data, f, indent=2)


def create_blog_folder(slug):
    blog_dir = BLOGS_DIR / slug
    if blog_dir.exists():
        print(f"WARNING: Folder already exists: {blog_dir}")
        return blog_dir
    blog_dir.mkdir(parents=True)
    return blog_dir


def copy_templates(blog_dir, slug, keyword, cluster, intent, blog_id, today):
    files_created = []

    # metadata.json from template
    meta_template = TEMPLATES_DIR / "blog-metadata-template.json"
    meta_dest = blog_dir / "metadata.json"
    if meta_template.exists():
        with open(meta_template) as f:
            meta = json.load(f)
        meta["blog_id"] = blog_id
        meta["primary_keyword"] = keyword
        meta["cluster"] = cluster
        meta["intent"] = intent
        meta["slug"] = f"/blogs/{slug}"
        meta["status"] = "draft"
        meta["created_date"] = today
        meta["updated_date"] = today
        meta["blog_folder"] = f"blogs/drafts/{slug}/"
        with open(meta_dest, "w") as f:
            json.dump(meta, f, indent=2)
        files_created.append("metadata.json")

    # serp-analysis.json from template
    serp_template = TEMPLATES_DIR / "serp-analysis-template.json"
    serp_dest = blog_dir / "serp-analysis.json"
    if serp_template.exists():
        with open(serp_template) as f:
            serp = json.load(f)
        serp["keyword"] = keyword
        with open(serp_dest, "w") as f:
            json.dump(serp, f, indent=2)
        files_created.append("serp-analysis.json")

    # blueprint.md from template
    blueprint_template = TEMPLATES_DIR / "blog-blueprint-template.md"
    blueprint_dest = blog_dir / "blueprint.md"
    if blueprint_template.exists():
        content = blueprint_template.read_text()
        content = content.replace("[PRIMARY KEYWORD]", keyword)
        content = content.replace("[DATE]", today)
        content = content.replace("[CLUSTER]", cluster)
        content = content.replace("[INTENT]", intent)
        blueprint_dest.write_text(content)
        files_created.append("blueprint.md")

    # article.md from template
    article_template = TEMPLATES_DIR / "article-template.md"
    article_dest = blog_dir / "article.md"
    if article_template.exists():
        shutil.copy(article_template, article_dest)
        files_created.append("article.md")

    # article.html from template
    html_template = TEMPLATES_DIR / "shopify-html-template.html"
    html_dest = blog_dir / "article.html"
    if html_template.exists():
        shutil.copy(html_template, html_dest)
        files_created.append("article.html")

    # qa-report.md from template
    qa_template = TEMPLATES_DIR / "qa-report-template.md"
    qa_dest = blog_dir / "qa-report.md"
    if qa_template.exists():
        content = qa_template.read_text()
        content = content.replace("[BLOG TITLE]", keyword.title())
        content = content.replace("[primary keyword]", keyword)
        content = content.replace("[/blogs/slug]", f"/blogs/{slug}")
        content = content.replace("[DATE]", today)
        qa_dest.write_text(content)
        files_created.append("qa-report.md")

    # shopify-draft.json placeholder
    shopify_draft = {
        "blog_post": {
            "title": keyword.title(),
            "body_html": "TODO: Generated in Step 7",
            "meta_title": "TODO: Generated in Step 5",
            "meta_description": "TODO: Generated in Step 5",
            "handle": slug,
            "tags": [cluster, "TODO"],
            "status": "draft",
            "published": False,
        },
        "workflow_notes": {
            "qa_score": None,
            "primary_keyword": keyword,
            "cluster": cluster,
            "intent": intent,
            "notes_for_zapier_or_make": "Do not publish automatically. Manual review required.",
            "ready_for_automation": False,
        },
    }
    shopify_dest = blog_dir / "shopify-draft.json"
    with open(shopify_dest, "w") as f:
        json.dump(shopify_draft, f, indent=2)
    files_created.append("shopify-draft.json")

    return files_created


def register_blog(content_index, blog_id, keyword, slug, cluster, intent, today):
    entry = {
        "blog_id": blog_id,
        "title": "",
        "primary_keyword": keyword,
        "secondary_keywords": [],
        "cluster": cluster,
        "intent": intent,
        "slug": f"/blogs/{slug}",
        "status": "draft",
        "created_date": today,
        "updated_date": today,
        "shopify_status": "not_uploaded",
        "internal_links": [],
        "cannibalization_notes": "",
        "ranking_notes": "",
    }
    content_index["blogs"].append(entry)
    content_index.setdefault("_meta", {})["total_blogs"] = len(content_index["blogs"])
    content_index["_meta"]["last_updated"] = today
    return content_index


def main():
    parser = argparse.ArgumentParser(description="Create blog folder from keyword")
    parser.add_argument("--keyword", required=True, help="Primary keyword for the blog")
    parser.add_argument("--cluster", default="General", help="Content cluster (e.g., HP Laptops, ELV Products)")
    parser.add_argument("--intent", default="Informational", help="Search intent")
    args = parser.parse_args()

    keyword = args.keyword.strip()
    slug = keyword_to_slug(keyword)
    today = datetime.now().strftime("%Y-%m-%d")

    print(f"Creating blog folder for: {keyword}")
    print(f"Slug: {slug}")
    print(f"Cluster: {args.cluster}")

    content_index = load_content_index()

    # Check for existing entry
    existing = [b for b in content_index.get("blogs", []) if b.get("primary_keyword", "").lower() == keyword.lower()]
    if existing:
        print(f"WARNING: A blog with this keyword already exists: {existing[0]['blog_id']}")
        print("To avoid cannibalization, consider a different angle.")

    blog_id = next_blog_id(content_index)
    blog_dir = create_blog_folder(slug)
    files_created = copy_templates(blog_dir, slug, keyword, args.cluster, args.intent, blog_id, today)
    content_index = register_blog(content_index, blog_id, keyword, slug, args.cluster, args.intent, today)
    save_content_index(content_index)

    print(f"\nBlog folder created: {blog_dir}")
    print(f"Blog ID: {blog_id}")
    print(f"Files created: {', '.join(files_created)}")
    print(f"\nNext steps:")
    print(f"  1. Run SERP analysis: python scripts/serpapi_fetcher.py --keyword \"{keyword}\"")
    print(f"  2. Ask Claude to create blueprint using: prompts/blog-blueprint-prompt.md")
    print(f"  3. Ask Claude to write article using: prompts/blog-writing-prompt.md")


if __name__ == "__main__":
    main()
