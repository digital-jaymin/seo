# Innova Retail — SEO Content Automation System

A semi-automated SEO blog workflow for Innova Retail. The system reduces manual effort at every stage while keeping final publishing fully under human control.

---

## What This System Does

| Step | What Happens | Who Does It |
|------|-------------|-------------|
| 1 | Fetch sitemap, extract existing blog URLs | Script / Claude |
| 2 | Generate keyword opportunities | Claude |
| 3 | Validate keywords via SEMrush | You (manual upload) |
| 4 | Analyze SEMrush data, select top topics | Claude |
| 5 | Run SERP analysis per topic | Script (SERPAPI) |
| 6 | Generate SEO blueprint | Claude |
| 7 | Write full blog article | Claude |
| 8 | Convert to Shopify-safe HTML | Claude |
| 9 | Run SEO + HTML QA, score blog | Claude |
| 10 | Prepare Shopify draft JSON | Claude |
| 11 | Commit + push everything to GitHub | Claude |
| 12 | Publish blog on Shopify | **You (manual only)** |

---

## Folder Structure

```
/config                        Site config, API key templates
/data/sitemap                  Extracted sitemap URLs
/data/keywords                 Keyword opportunity CSV, selected topics
/data/semrush-uploads          Drop SEMrush CSVs here for Claude to analyze
/data/serp                     Raw SERP API results
/data/content-database         Master content index (cannibalization tracking)
/blogs/drafts/[slug]/          One folder per blog topic
  ├── metadata.json
  ├── serp-analysis.json
  ├── blueprint.md
  ├── article.md
  ├── article.html
  ├── qa-report.md
  └── shopify-draft.json
/blogs/approved                Move here after final review
/templates                     Reusable file templates
/prompts                       Claude prompt instructions per workflow step
/scripts                       Python helper scripts
/workflows                     Step-by-step workflow guides
/output                        Final export files for Zapier / Make
/logs                          Run logs and error reports
```

---

## How to Run the Workflow

### Step 1 — Sitemap Discovery
```bash
python scripts/sitemap_fetcher.py
```
Output: `data/sitemap/sitemap-urls.json`

### Step 2 — Keyword Discovery
Ask Claude:
> "Run Step 2: Keyword Discovery for Innova Retail based on sitemap gaps."

Output: `data/keywords/keyword-opportunities.csv`

### Step 3 — SEMrush Validation (Manual)
1. Open SEMrush → Keyword Magic Tool
2. Check keywords listed in `data/semrush-uploads/README.md`
3. Export CSV → drop into `data/semrush-uploads/`
4. Ask Claude: "Analyze the SEMrush upload and select top topics."

Output: updated `keyword-opportunities.csv` + `selected-topics.json`

### Step 4 — SERP Analysis
```bash
python scripts/serpapi_fetcher.py --keyword "your keyword"
```
Or ask Claude to generate a manual SERP research file if no API key.

### Step 5–9 — Blueprint, Article, HTML, QA, Shopify Draft
Ask Claude:
> "Run Steps 5–9 for keyword: [your keyword slug]"

All files are created inside `/blogs/drafts/[slug]/`

### Step 10 — GitHub Push
Claude commits and pushes all files automatically.

### Step 11 — Publish (Manual)
Use the `shopify-draft.json` with Zapier or Make to create a Shopify blog draft.
Review it in Shopify admin → publish manually.

---

## API Keys

Copy `/config/api-keys.example.json` → `/config/api-keys.json` and fill in your keys.
**Never commit `api-keys.json` to GitHub.**

---

## Publishing Rules

- `publishing_mode: manual approval required`
- Claude will NEVER auto-publish to Shopify
- All content stays in `/blogs/drafts/` until you approve and move it
- Shopify draft JSON is prep-only — you trigger publication

---

## Content Memory

`/data/content-database/content-index.json` tracks every blog ever created.
Claude checks this file before writing new content to avoid keyword cannibalization.

---

## QA Standard

Every blog must score **85 or above** on the QA report before it moves to approved.
Score breakdown: keyword placement, heading hierarchy, meta lengths, HTML validity,
readability, FAQ quality, CTA strength, internal links, cannibalization risk.
