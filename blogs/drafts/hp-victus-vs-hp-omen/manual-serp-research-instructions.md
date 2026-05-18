# Manual SERP Research Instructions
**Article:** HP Victus vs HP Omen — Which Gaming Laptop Should You Buy in India?  
**Keyword:** hp victus vs hp omen  
**Created:** 2026-05-18  
**Required for:** Filling `serp-analysis.json` before blueprint creation

---

## Why This Is Needed

The SERPAPI key is not configured. SERP data must be collected manually.
This file is a step-by-step guide to do that in ~15 minutes.

Do NOT skip this step. The blueprint must be grounded in what is actually
ranking — not assumptions. Invented SERP data will produce a weak blueprint.

---

## Step 1 — Open Google India

Go to: **https://www.google.co.in/**

Set location to India if prompted. Use Chrome Incognito to avoid personalization.

---

## Step 2 — Search This Exact Query

```
hp victus vs hp omen
```

---

## Step 3 — Record the Top 10 Organic Results

For each result (skip ads, skip Google Shopping cards), note:

| # | URL | Page Title | Estimated Word Count |
|---|-----|-----------|---------------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 7 | | | |
| 8 | | | |
| 9 | | | |
| 10 | | | |

**For word count:** Open each page, select all text (Ctrl+A), paste into a word counter
(wordcounter.net), or estimate based on scroll length (short = ~500, medium = ~1500, long = ~3000+).

---

## Step 4 — Note SERP Features Present

Check which of these appear on the results page:

- [ ] Featured snippet (answer box at top)
- [ ] People Also Ask (PAA) box — list all questions shown
- [ ] Knowledge Panel (HP brand info)
- [ ] Google Shopping carousel
- [ ] Image pack
- [ ] Video results (YouTube)
- [ ] Reddit/forum threads in results

---

## Step 5 — Record People Also Ask Questions

These are gold for your H2/H3 headings. Write down ALL questions shown:

1. 
2. 
3. 
4. 
5. 

---

## Step 6 — Analyze Top 3 Results

Open the top 3 ranking pages and note:

**Result #1:**
- URL: 
- Content type: (comparison table / review / listicle / buying guide)
- H1/title: 
- Main sections covered:
- Does it include a spec table? (yes/no)
- Word count estimate:
- CTA at end: (buy link / affiliate / no CTA)

**Result #2:**
- URL:
- Content type:
- H1/title:
- Main sections covered:
- Spec table: (yes/no)
- Word count estimate:
- CTA at end:

**Result #3:**
- URL:
- Content type:
- H1/title:
- Main sections covered:
- Spec table: (yes/no)
- Word count estimate:
- CTA at end:

---

## Step 7 — Note Content Gaps in Top Results

What do the top-ranking pages NOT cover that a buyer would want to know?

Examples to look for:
- Missing India-specific pricing (₹ amounts)
- Missing battery life comparison
- No mention of use-case fit (gaming vs college work)
- No clear recommendation / verdict
- Outdated specs (2023/2024 models when 2025/2026 exist)

Gaps found:
1.
2.
3.

---

## Step 8 — Fill serp-analysis.json

Once you have collected the above data, paste it into Claude with this prompt:

> "Fill in serp-analysis.json for keyword 'hp victus vs hp omen'.
> Here is my manual SERP research: [paste your findings from above]
> Here is the current serp-analysis.json template: [paste blogs/drafts/hp-victus-vs-hp-omen/serp-analysis.json]"

Claude will populate the JSON and then move to Step 6 (blueprint creation).

---

## Alternative: Add SERPAPI Key

To automate SERP research for all future articles:

1. Get a free SERPAPI key at: https://serpapi.com (100 free searches/month)
2. Copy `config/api-keys.example.json` → `config/api-keys.json`
3. Set `"serpapi_key": "your_key_here"`
4. Run: `python scripts/serpapi_fetcher.py --keyword "hp victus vs hp omen"`

The script will auto-populate `serp-analysis.json`.

---

## When Done

After serp-analysis.json is filled:
1. Tell Claude: "SERP research complete for hp victus vs hp omen. Here is serp-analysis.json: [paste file]"
2. Claude will create `blueprint.md`
3. Review and approve blueprint before article writing begins
