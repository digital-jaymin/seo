# Innova Retail SEO Workflow — Step-by-Step Guide

## Overview

This workflow produces one rank-ready Shopify blog draft per run.
Final publishing is always manual. Claude handles content generation.
You handle SEMrush research and final approval.

The system operates with **persistent SEO memory** — every recommendation
is validated against all existing site data before being accepted.

---

## SEO Memory System

Before any keyword or topic recommendation is made, the system loads and
checks all 6 memory sources in order:

| Memory Source | Path | What It Enforces |
|--------------|------|-----------------|
| Sitemap data | `data/sitemap/sitemap-urls.json` | What content already exists |
| Content index | `data/content-database/content-index.json` | Published + draft blog keywords |
| Keyword table | `data/keywords/keyword-opportunities.csv` | What's already been researched |
| Selected topics | `data/keywords/selected-topics.json` | What's queued for writing |
| Collection URLs | `data/sitemap/collections-urls.txt` | Transactional keyword ownership |
| Topical authority map | `data/topical-authority/topical-authority-map.json` | Cluster health + gaps |

**Core memory rules:**

1. Collection pages own transactional keywords — blogs never compete with them
2. Every blog must support a collection (informational / comparison / guide intent)
3. Never suggest a topic already covered by an existing published blog
4. Detect cannibalization before recommending any new topic
5. Every topic must include all 5 required memory fields (see below)
6. Topics must strengthen topical authority — no isolated blog ideas

**Required memory fields for every topic:**
```
target_page_type         → "blog" or "collection"
parent_cluster           → which cluster this belongs to
supported_collection_page → the collection page this blog supports
cannibalization_risk     → "none" | "medium" | "high" | "collection_conflict"
internal_link_targets    → list of existing blog slugs + collection URLs to link to
```

**Run memory report at any time:**
```bash
python scripts/seo_memory.py
```

---

## One-Time Setup

1. Fill in `config/site-config.json` — replace all `TODO:` values
2. Copy `config/api-keys.example.json` → `config/api-keys.json` — add SERPAPI key (optional)
3. Verify Python 3.8+ is installed: `python3 --version`

---

## STEP 1 — Sitemap Discovery

**Goal:** Load full site inventory into memory. Detect content clusters and gaps.

**Run:**
```bash
python scripts/sitemap_fetcher.py
```
If outbound HTTP is blocked, paste sitemap XML manually and ask Claude to process it.

**Output:** `data/sitemap/sitemap-urls.json`

**Then ask Claude:**
> "Run Step 1 sitemap analysis. Here is the sitemap data: [paste sitemap-urls.json]"

Follow the prompt in: `prompts/sitemap-analysis-prompt.md`

**Claude will:**
- Register all existing blog topics in content-index.json
- Identify content gaps by cluster
- Populate `topical-authority-map.json` with cluster health scores
- Flag any cannibalization risks in content-index.json

---

## STEP 2 — Keyword Discovery

**Goal:** Generate keyword opportunities from content gaps — all memory-validated.

**Memory check before this step:**
```bash
python scripts/seo_memory.py
```
Review the memory report. Understand what's already covered before generating new keywords.

**Ask Claude:**
> "Run Step 2: Keyword Discovery. Memory report: [paste seo_memory.py output]. Content gaps: [paste content_gaps from sitemap-urls.json]"

Follow the prompt in: `prompts/keyword-discovery-prompt.md`

**Claude will only suggest topics that:**
- Are NOT already covered by existing blogs or collections
- Have informational/comparison/guide intent (not transactional)
- Support a specific collection page
- Include all 5 required memory fields

**Output:** Paste Claude's CSV into keyword-opportunities.csv via:
```bash
python scripts/keyword_table_builder.py new-keywords.csv
```
This runs memory validation on every keyword — blocking collection-owned transactional terms.

---

## STEP 3 — SEMrush Validation (Manual)

**Goal:** Get real search volume, KD, and CPC for your keywords.

1. Open `data/semrush-uploads/keywords-to-check-in-semrush.csv` — these are pre-prioritized
2. Go to SEMrush → Keyword Magic Tool → Country: India
3. Run TIER-1 keywords first, then TIER-2
4. Export CSV for each batch
5. Save files to `data/semrush-uploads/` as: `semrush-YYYY-MM-DD-[group].csv`

**Then ask Claude:**
> "Analyze this SEMrush upload. Memory report: [paste seo_memory.py output]. SEMrush data: [paste CSV]"

Follow the prompt in: `prompts/semrush-validation-prompt.md`

**Claude will:**
- Fill SEMrush volume/KD/CPC into keyword-opportunities.csv
- Re-run memory validation with real data
- Select top 2–3 topics
- Save selections to `data/keywords/selected-topics.json` with all required memory fields

---

## STEP 4 — Blog Folder Setup

**Goal:** Create the standard folder for your selected blog topic. Memory validated.

```bash
python scripts/blog_folder_creator.py \
  --keyword "best gaming laptop under 70000" \
  --cluster "Gaming Laptops" \
  --intent "informational"
```

The script will:
1. Run full memory validation — blocks collection-owned transactional keywords
2. Detect cannibalization against all published/draft blogs
3. Resolve `supported_collection_page` and `internal_link_targets` automatically
4. Create `blogs/drafts/[slug]/` with all template files
5. Register blog in `content-index.json` with all memory fields
6. Update `topical-authority-map.json`

**If the topic is blocked:**
- The script explains why (collection conflict or cannibalization)
- Adjust keyword framing to informational angle, then re-run

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
> "Analyze this SERP data for [keyword]. Memory report: [paste seo_memory.py output]. SERP data: [paste serp-analysis.json]"

Follow the prompt in: `prompts/serp-analysis-prompt.md`

---

## STEP 6 — Blog Blueprint

**Goal:** Plan the full article structure. Internal link targets are pre-loaded from memory.

**Ask Claude:**
> "Create a blog blueprint. Memory report: [paste seo_memory.py output]. SERP analysis: [paste serp-analysis.json]. Metadata: [paste metadata.json]"

Follow the prompt in: `prompts/blog-blueprint-prompt.md`

Blueprint must include:
- All `internal_link_targets` from metadata.json woven into the article structure
- CTA linking to `supported_collection_page`
- Cluster pillar article cross-link if one exists

**Output:** `blogs/drafts/[slug]/blueprint.md`

**Review and approve before proceeding.**

---

## STEP 7 — Write the Article

**Goal:** Generate the full SEO article.

**Ask Claude:**
> "Write the full article using this blueprint: [paste blueprint.md]. Memory: [paste metadata.json]"

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

**Goal:** Score the blog against 25 checks. Minimum score: 85/100.

**Run automated checks:**
```bash
python scripts/qa_checker.py --slug "your-keyword-slug"
```

**Then ask Claude for deep QA:**
> "Run full SEO QA. Memory: [paste seo_memory.py output]. article.md: [paste]. article.html: [paste]."

Follow the prompt in: `prompts/seo-qa-prompt.md`

**QA checks include:**
- All `internal_link_targets` from metadata.json are present in article
- CTA links to `supported_collection_page`
- No keyword cannibalization with published blogs
- India/Ahmedabad/local context where applicable

**Output:** `blogs/drafts/[slug]/qa-report.md`

**If score < 85:** Fix issues and re-run. Do not proceed.

---

## STEP 10 — Shopify Draft Preparation

**Goal:** Create publish-ready JSON for Shopify.

**Ask Claude:**
> "Prepare the Shopify draft JSON. article.html: [paste]. blueprint: [paste]. metadata: [paste metadata.json]"

Follow the prompt in: `prompts/shopify-draft-prompt.md`

**Output:** `blogs/drafts/[slug]/shopify-draft.json`

---

## STEP 11 — GitHub Commit

**Goal:** Save all work to GitHub.

```bash
git add blogs/drafts/[slug]/
git add data/keywords/
git add data/content-database/
git add data/topical-authority/
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

After publishing, update `content-index.json`:
- Change `status` from `"draft"` to `"published"`
- Add `shopify_url` and `lastmod` date
- Run `python scripts/seo_memory.py` to confirm the new blog is in memory

---

## Quick Reference

```bash
# Load memory and print current state
python scripts/seo_memory.py

# Step 4: Create blog folder (memory validated)
python scripts/blog_folder_creator.py \
  --keyword "keyword" \
  --cluster "Gaming Laptops" \
  --intent "informational"

# Step 5: Fetch SERP data
python scripts/serpapi_fetcher.py --keyword "keyword"
python scripts/serpapi_fetcher.py --keyword "keyword" --manual

# Step 9: Run QA check
python scripts/qa_checker.py --slug "keyword-slug"

# Rebuild keyword table (recalculate + refresh memory fields)
python scripts/keyword_table_builder.py

# Import new keywords from CSV (with full memory validation)
python scripts/keyword_table_builder.py data/semrush-uploads/new-export.csv
```

---

## Memory File Locations

| File | Purpose |
|------|---------|
| `data/sitemap/sitemap-urls.json` | Full site structure + content gaps |
| `data/content-database/content-index.json` | All blogs (published + draft) with memory fields |
| `data/keywords/keyword-opportunities.csv` | All researched keywords with validation status |
| `data/keywords/selected-topics.json` | Approved topics queued for writing |
| `data/sitemap/collections-urls.txt` | Collection page index (transactional keyword owners) |
| `data/sitemap/blog-urls.txt` | Published blog URL index |
| `data/topical-authority/topical-authority-map.json` | Cluster health + pillar/spoke map + gaps |
| `scripts/seo_memory.py` | Memory system — import in all scripts |
