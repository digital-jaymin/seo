# Innova Retail SEO Workflow — Step-by-Step Guide

## Overview

This workflow produces one rank-ready Shopify blog draft per run.
Final publishing is always manual. Claude handles content generation.
You handle keyword validation and final approval.

The system operates with **persistent SEO memory** and a **checkpoint/recovery system**
so work can be safely paused and resumed across sessions.

---

## Session Start Protocol (READ FIRST — EVERY SESSION)

**Before doing any work in a new Claude session:**

```
1. Read:  workflows/workflow-state.json
2. Run:   python scripts/seo_memory.py
3. Check: git log --oneline -5
4. Confirm current_state.status and next_action with user
5. Only then proceed
```

If `status` is `paused_usage_limit` — ask the user to confirm before resuming
the paused task. Do not auto-start large tasks without confirmation.

---

## Usage Limit Safety Rule

**Before starting any large task** (blog writing, HTML conversion, full QA):

1. Estimate if the current context window can hold the full task
2. If the session is more than ~60% through context — **do not start**
3. Instead:
   - Update `workflow-state.json` → `status: paused_usage_limit`
   - Commit and push
   - End the session cleanly
4. Resume in a fresh session

**Tasks that are safe to run near context limit:**
- Updating workflow-state.json
- Git commit and push
- Running seo_memory.py
- Running blog_folder_creator.py
- Short file edits

**Tasks that require fresh context:**
- Blog writing (1,500–2,200 words)
- HTML conversion
- Full QA review

---

## Checkpoint Rule (Every Major Step)

Every major step MUST:

1. **Before starting:** update `workflow-state.json`:
   - Set `current_stage` to the step name
   - Set `status` to `running`
   - Set `pending_inputs` to what is needed
   - Set `expected_outputs` to what will be produced

2. **After completing:** update `workflow-state.json`:
   - Set `status` to `waiting_for_next_step` (or `waiting_for_input` if blocked)
   - Set `last_completed_stage` to this step
   - Set `next_action` to the next step
   - Move outputs to `completed_outputs`
   - Append entry to `stage_history`

3. **Commit and push** the updated state before moving to the next major step.

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
2. Every blog must support a collection (informational/comparison/guide intent)
3. Never suggest a topic already covered by a published blog
4. Detect cannibalization before recommending any new topic
5. Every topic must include all 5 required memory fields
6. Topics must strengthen topical authority — no isolated blog ideas

**Run memory report:**
```bash
python scripts/seo_memory.py
```

---

## One-Time Setup

1. Fill in `config/site-config.json` — replace all `TODO:` values
2. Copy `config/api-keys.example.json` → `config/api-keys.json` — add SERPAPI key (optional)
3. Verify Python 3.8+: `python3 --version`

---

## STEP 1 — Sitemap Discovery

**Goal:** Load full site inventory into memory. Detect content clusters and gaps.

**Checkpoint — before starting:**
```json
{ "current_stage": "sitemap_analysis", "status": "running" }
```

**Run:**
```bash
python scripts/sitemap_fetcher.py
```
If outbound HTTP is blocked, paste sitemap XML manually.

**Output:** `data/sitemap/sitemap-urls.json`

**Ask Claude:**
> "Run Step 1 sitemap analysis. Memory report: [paste seo_memory.py output]. Sitemap data: [paste sitemap-urls.json]"

Follow: `prompts/sitemap-analysis-prompt.md`

**Claude will:**
- Register all existing blog topics in content-index.json
- Populate topical-authority-map.json
- Flag cannibalization risks

**Checkpoint — after completing:**
```json
{
  "last_completed_stage": "sitemap_analysis",
  "status": "waiting_for_next_step",
  "next_action": "run_keyword_discovery",
  "completed_outputs": ["data/sitemap/sitemap-urls.json", "data/content-database/content-index.json"]
}
```
**→ Commit and push before continuing.**

---

## STEP 2 — Keyword Discovery

**Goal:** Generate memory-validated keyword opportunities from content gaps.

**Checkpoint — before starting:**
```json
{ "current_stage": "keyword_discovery", "status": "running" }
```

**Run memory report first:**
```bash
python scripts/seo_memory.py
```

**Ask Claude:**
> "Run Step 2: Keyword Discovery. Memory report: [paste output]. Content gaps: [paste from sitemap-urls.json]"

Follow: `prompts/keyword-discovery-prompt.md`

**Validate Claude's output:**
```bash
python scripts/keyword_table_builder.py new-keywords.csv
```

**Output:** `data/keywords/keyword-opportunities.csv`

**Checkpoint — after completing:**
```json
{
  "last_completed_stage": "keyword_discovery",
  "status": "waiting_for_next_step",
  "next_action": "upload_keywords_to_ubersuggest_or_semrush"
}
```
**→ Commit and push before continuing.**

---

## STEP 3 — Keyword Validation (Ubersuggest / SEMrush)

**Goal:** Get real search volume, KD, and CPC. Select top cluster for production.

**Checkpoint — before starting:**
```json
{ "current_stage": "keyword_validation", "status": "waiting_for_input",
  "pending_inputs": ["ubersuggest or semrush export CSV"] }
```

**Manual step (you do this):**
1. Open `data/semrush-uploads/keywords-to-check-in-semrush.csv`
2. Run TIER-1 keywords in Ubersuggest or SEMrush → India
3. Export CSV → save to `data/semrush-uploads/[tool]-YYYY-MM-DD.csv`

**Ask Claude:**
> "Run keyword validation. Memory: [paste seo_memory.py output]. Validation data: [paste CSV]"

Follow: `prompts/semrush-validation-prompt.md`

**Output:**
- `data/keywords/selected-topics.json` — approved topics with all memory fields
- `output/validated-cluster-strategy.md` — cluster blueprint

**Checkpoint — after completing:**
```json
{
  "last_completed_stage": "keyword_validation",
  "status": "waiting_for_next_step",
  "next_action": "create_article_folder_and_run_serp_analysis",
  "active_cluster": "[selected cluster]",
  "active_article": "[article 1 slug]"
}
```
**→ Commit and push before continuing.**

---

## STEP 4 — Blog Folder Setup

**Goal:** Create the memory-validated folder for Article 1.

**Checkpoint — before starting:**
```json
{ "current_stage": "blog_folder_setup", "status": "running",
  "active_article": "[slug]" }
```

```bash
python scripts/blog_folder_creator.py \
  --keyword "hp victus vs hp omen" \
  --cluster "Gaming Laptops" \
  --intent "comparison"
```

The script runs full memory validation before creating anything.

**Output:** `blogs/drafts/[slug]/` with all 6 template files + metadata.json

**Checkpoint — after completing:**
```json
{
  "last_completed_stage": "blog_folder_setup",
  "status": "waiting_for_next_step",
  "next_action": "run_serp_analysis"
}
```
**→ Commit and push.**

---

## STEP 5 — SERP Analysis

**Goal:** Understand what's currently ranking and why.

**Checkpoint — before starting:**
```json
{ "current_stage": "serp_analysis", "status": "running" }
```

```bash
# With SERPAPI key:
python scripts/serpapi_fetcher.py --keyword "your keyword"

# Without key:
python scripts/serpapi_fetcher.py --keyword "your keyword" --manual
```

**Ask Claude:**
> "Analyze SERP for [keyword]. Memory: [paste seo_memory.py output]. SERP data: [paste serp-analysis.json]"

Follow: `prompts/serp-analysis-prompt.md`

**Output:** `blogs/drafts/[slug]/serp-analysis.json`

**Checkpoint — after completing:**
```json
{
  "last_completed_stage": "serp_analysis",
  "status": "waiting_for_next_step",
  "next_action": "create_blog_blueprint"
}
```
**→ Commit and push.**

---

## STEP 6 — Blog Blueprint

**Goal:** Plan the full article structure before writing.

**⚠ Usage limit check:** If context is >60% used, stop here. Checkpoint and push.

**Checkpoint — before starting:**
```json
{ "current_stage": "blueprint", "status": "running" }
```

**Ask Claude:**
> "Create blueprint. Memory: [paste seo_memory.py output]. SERP: [paste serp-analysis.json]. Metadata: [paste metadata.json]"

Follow: `prompts/blog-blueprint-prompt.md`

Blueprint must include:
- All `internal_link_targets` from metadata.json
- CTA pointing to `supported_collection_page`
- Cluster pillar cross-link if one exists

**Output:** `blogs/drafts/[slug]/blueprint.md`

**Review and approve before proceeding.**

**Checkpoint — after approval:**
```json
{
  "last_completed_stage": "blueprint",
  "status": "waiting_for_next_step",
  "next_action": "write_article"
}
```
**→ Commit and push.**

---

## STEP 7 — Write the Article

**Goal:** Generate the full SEO article.

**⚠ Usage limit check:** Blog writing uses significant context. Start only with fresh session.

**Checkpoint — before starting:**
```json
{ "current_stage": "article_writing", "status": "running" }
```

**Ask Claude:**
> "Write full article. Blueprint: [paste blueprint.md]. Metadata: [paste metadata.json]"

Follow: `prompts/blog-writing-prompt.md`

**Output:** `blogs/drafts/[slug]/article.md`

**Checkpoint — after completing:**
```json
{
  "last_completed_stage": "article_writing",
  "status": "waiting_for_next_step",
  "next_action": "html_conversion"
}
```
**→ Commit and push.**

---

## STEP 8 — HTML Conversion

**Goal:** Convert Markdown to Shopify-safe HTML.

**⚠ Usage limit check:** HTML conversion uses significant context. Start only with fresh session.

**Checkpoint — before starting:**
```json
{ "current_stage": "html_conversion", "status": "running" }
```

**Ask Claude:**
> "Convert to Shopify HTML. Article: [paste article.md]"

Follow: `prompts/html-conversion-prompt.md`

**Output:** `blogs/drafts/[slug]/article.html`

**Checkpoint — after completing:**
```json
{
  "last_completed_stage": "html_conversion",
  "status": "waiting_for_next_step",
  "next_action": "run_qa"
}
```
**→ Commit and push.**

---

## STEP 9 — SEO & HTML QA

**Goal:** Score the blog. Minimum 85/100 required to proceed.

**Checkpoint — before starting:**
```json
{ "current_stage": "qa_review", "status": "running" }
```

```bash
python scripts/qa_checker.py --slug "your-keyword-slug"
```

**Ask Claude for deep QA:**
> "Full SEO QA. Memory: [paste seo_memory.py output]. article.md: [paste]. article.html: [paste]"

Follow: `prompts/seo-qa-prompt.md`

**Output:** `blogs/drafts/[slug]/qa-report.md`

If score < 85: fix issues and re-run. Do not proceed until ≥ 85.

**Checkpoint — after passing:**
```json
{
  "last_completed_stage": "qa_review",
  "status": "waiting_for_next_step",
  "next_action": "prepare_shopify_draft"
}
```
**→ Commit and push.**

---

## STEP 10 — Shopify Draft Preparation

**Goal:** Create publish-ready JSON for Shopify.

**Checkpoint — before starting:**
```json
{ "current_stage": "shopify_draft", "status": "running" }
```

**Ask Claude:**
> "Prepare Shopify draft. article.html: [paste]. blueprint: [paste]. metadata: [paste metadata.json]"

Follow: `prompts/shopify-draft-prompt.md`

**Output:** `blogs/drafts/[slug]/shopify-draft.json`

**Checkpoint — after completing:**
```json
{
  "last_completed_stage": "shopify_draft",
  "status": "waiting_for_next_step",
  "next_action": "commit_push_and_review_for_publishing"
}
```
**→ Commit and push.**

---

## STEP 11 — GitHub Commit (Final)

```bash
git add blogs/drafts/[slug]/
git add data/keywords/
git add data/content-database/
git add data/topical-authority/
git add workflows/workflow-state.json
git commit -m "feat: complete blog draft — [keyword]"
git push -u origin claude/setup-connection-e8W80
```

Update `workflow-state.json`:
```json
{
  "last_completed_stage": "article_committed",
  "next_action": "manual_review_and_publish",
  "active_article_order": 2
}
```

---

## STEP 12 — Publish (Manual Only)

1. Use Zapier/Make with `shopify-draft.json` to create a Shopify draft
2. Go to Shopify Admin → Blog Posts → find your draft
3. Add feature image
4. Replace all `#TODO` links with real URLs
5. Preview on mobile and desktop
6. Click **Publish** — manually

**Claude will NEVER auto-publish.**

After publishing, update `content-index.json`:
- Change `status` from `"draft"` to `"published"`
- Add `shopify_url` and `lastmod` date
- Run `python scripts/seo_memory.py` to confirm new blog is in memory
- Update `workflow-state.json` → `articles_completed` count in cluster_queue

---

## Quick Reference

```bash
# Session start — always run first
cat workflows/workflow-state.json
python scripts/seo_memory.py

# Step 4: Create blog folder (memory validated)
python scripts/blog_folder_creator.py \
  --keyword "keyword" \
  --cluster "Gaming Laptops" \
  --intent "comparison"

# Step 5: SERP fetch
python scripts/serpapi_fetcher.py --keyword "keyword"
python scripts/serpapi_fetcher.py --keyword "keyword" --manual

# Step 9: QA check
python scripts/qa_checker.py --slug "keyword-slug"

# Keyword tools
python scripts/keyword_table_builder.py
python scripts/keyword_table_builder.py data/semrush-uploads/new-export.csv
```

---

## Workflow State Reference

| Status | Meaning |
|--------|---------|
| `pending` | Step not yet started |
| `running` | Step is actively in progress |
| `waiting_for_input` | Blocked — needs user-provided data (e.g. SERP export) |
| `waiting_for_next_step` | Step complete — ready for next step |
| `paused_usage_limit` | Stopped before a large task due to context limit |
| `completed` | Article fully done and published |
| `failed` | Step failed — see stage_history for reason |

---

## Memory File Locations

| File | Purpose |
|------|---------|
| `workflows/workflow-state.json` | **READ FIRST** — checkpoint and recovery |
| `data/sitemap/sitemap-urls.json` | Full site structure + content gaps |
| `data/content-database/content-index.json` | All blogs with memory fields |
| `data/keywords/keyword-opportunities.csv` | All researched keywords |
| `data/keywords/selected-topics.json` | Approved topics queued for writing |
| `data/sitemap/collections-urls.txt` | Collection page index |
| `data/topical-authority/topical-authority-map.json` | Cluster health map |
| `scripts/seo_memory.py` | Memory system — run at session start |
