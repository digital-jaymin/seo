# Innova Retail SEO Workflow — Step-by-Step Guide

## Overview

This workflow produces one rank-ready Shopify blog draft per run.
Final publishing is always manual. Claude handles content generation.
You handle SEMrush research and final approval.

---

## Before You Start

**One-time setup:**
1. Fill in `config/site-config.json` — replace all `TODO:` values
2. Copy `config/api-keys.example.json` → `config/api-keys.json` — add SERPAPI key (optional)
3. Verify Python 3.8+ is installed: `python3 --version`

---

## STEP 1 — Sitemap Discovery

**Goal:** Understand what content already exists. Find gaps.

**Run:**
```bash
python scripts/sitemap_fetcher.py
```

**Output:** `data/sitemap/sitemap-urls.json`

**Then ask Claude:**
> "Run Step 1 sitemap analysis. Here is the sitemap data: [paste sitemap-urls.json]"

Follow the prompt in: `prompts/sitemap-analysis-prompt.md`

**Claude will:**
- List existing blog topics
- Identify content gaps by cluster
- Populate `sitemap-urls.json → content_gaps`

---

## STEP 2 — Keyword Discovery

**Goal:** Generate 30+ keyword opportunities from content gaps.

**Ask Claude:**
> "Run Step 2: Keyword Discovery. Here are the content gaps: [paste content_gaps from sitemap-urls.json]"

Follow the prompt in: `prompts/keyword-discovery-prompt.md`

**Output:** Paste Claude's CSV into `data/keywords/keyword-opportunities.csv`

```bash
# Optional: rebuild and deduplicate the CSV
python scripts/keyword_table_builder.py
```

---

## STEP 3 — SEMrush Validation (Manual)

**Goal:** Get real search volume, KD, and CPC for your keywords.

1. Open `data/semrush-uploads/README.md` — see which keywords to check
2. Go to SEMrush → Keyword Magic Tool → Country: India
3. Export CSV for each keyword group
4. Save files to `data/semrush-uploads/` with format: `semrush-YYYY-MM-DD-[group].csv`

**Then ask Claude:**
> "Analyze this SEMrush upload and select top topics. File: [paste CSV content]"

Follow the prompt in: `prompts/semrush-validation-prompt.md`

**Claude will:**
- Fill SEMrush data into keyword-opportunities.csv
- Select top 2–3 topics
- Save to `data/keywords/selected-topics.json`

---

## STEP 4 — Blog Folder Setup

**Goal:** Create the standard folder for your selected blog topic.

```bash
python scripts/blog_folder_creator.py \
  --keyword "your primary keyword here" \
  --cluster "HP Laptops" \
  --intent "Commercial"
```

This creates: `blogs/drafts/[slug]/` with all template files.

---

## STEP 5 — SERP Analysis

**Goal:** Understand what's currently ranking and why.

**If SERPAPI key is available:**
```bash
python scripts/serpapi_fetcher.py --keyword "your keyword"
```

**If no API key:**
```bash
python scripts/serpapi_fetcher.py --keyword "your keyword" --manual
```
Follow the manual research instructions created in the blog folder.

**Then ask Claude:**
> "Analyze this SERP data for [keyword]. Here is the data: [paste serp-analysis.json]"

Follow the prompt in: `prompts/serp-analysis-prompt.md`

---

## STEP 6 — Blog Blueprint

**Goal:** Plan the full article structure before writing.

**Ask Claude:**
> "Create a blog blueprint for: [keyword]. SERP analysis: [paste serp-analysis.json]"

Follow the prompt in: `prompts/blog-blueprint-prompt.md`

**Output:** `blogs/drafts/[slug]/blueprint.md`

**Review and approve the blueprint before proceeding.**

---

## STEP 7 — Write the Article

**Goal:** Generate the full SEO article.

**Ask Claude:**
> "Write the full article using this blueprint: [paste blueprint.md]"

Follow the prompt in: `prompts/blog-writing-prompt.md`

**Output:** `blogs/drafts/[slug]/article.md`

---

## STEP 8 — HTML Conversion

**Goal:** Convert Markdown to Shopify-safe HTML.

**Ask Claude:**
> "Convert this article to Shopify-safe HTML: [paste article.md]"

Follow the prompt in: `prompts/html-conversion-prompt.md`

**Output:** `blogs/drafts/[slug]/article.html`

---

## STEP 9 — SEO & HTML QA

**Goal:** Score the blog and catch issues before publishing.

**Run automated checks:**
```bash
python scripts/qa_checker.py --slug "your-keyword-slug"
```

**Then ask Claude for deep QA:**
> "Run full SEO QA on this article. article.md: [paste]. article.html: [paste]."

Follow the prompt in: `prompts/seo-qa-prompt.md`

**Output:** `blogs/drafts/[slug]/qa-report.md`

**If score < 85:** Fix issues and re-run. Do not proceed until score ≥ 85.

---

## STEP 10 — Shopify Draft Preparation

**Goal:** Create automation-ready JSON for Zapier or Make.

**Ask Claude:**
> "Prepare the Shopify draft JSON. article.html: [paste]. blueprint: [paste]."

Follow the prompt in: `prompts/shopify-draft-prompt.md`

**Output:** `blogs/drafts/[slug]/shopify-draft.json`

---

## STEP 11 — GitHub Commit

**Goal:** Save all work to GitHub.

```bash
git add blogs/drafts/[slug]/
git add data/keywords/
git add data/content-database/
git commit -m "feat: add SEO blog draft — [keyword]"
git push -u origin claude/setup-connection-e8W80
```

---

## STEP 12 — Publish (Manual Only)

1. Use Zapier/Make with `shopify-draft.json` to create a Shopify blog draft
2. Go to Shopify Admin → Blog Posts → find your draft
3. Add feature image
4. Replace all `#TODO` links with real URLs
5. Preview on mobile and desktop
6. Click **Publish** — manually

**Claude will NEVER auto-publish.**

---

## Quick Reference Commands

```bash
# Step 1: Fetch sitemap
python scripts/sitemap_fetcher.py

# Step 4: Create blog folder
python scripts/blog_folder_creator.py --keyword "keyword" --cluster "HP Laptops"

# Step 5: Fetch SERP data
python scripts/serpapi_fetcher.py --keyword "keyword"

# Step 5 (no API): Manual SERP instructions
python scripts/serpapi_fetcher.py --keyword "keyword" --manual

# Step 9: Run QA check
python scripts/qa_checker.py --slug "keyword-slug"

# Rebuild keyword table
python scripts/keyword_table_builder.py
```
