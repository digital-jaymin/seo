# Prompt: Sitemap Analysis (Step 1)

Use this prompt with Claude to analyze the sitemap output.

---

## Input Required

- File: `data/sitemap/sitemap-urls.json` (populated by `scripts/sitemap_fetcher.py`)
- File: `config/site-config.json`

---

## Prompt to Use

```
You are an SEO analyst for Innova Retail, an Indian retailer selling HP laptops,
business IT products, and ELV products (Smart Locks, Cleaning Robots, Parking Barriers,
Dahua products).

I have fetched the sitemap. Here is the sitemap data:
[PASTE sitemap-urls.json content here]

Please do the following:

1. List all existing blog topics found in the sitemap.
2. Identify what topics are already covered.
3. Identify content gaps — topics that Innova Retail should cover but hasn't yet.
4. Group the gaps into clusters: HP Laptops, Business IT, ELV Products, Buying Guides.
5. Note any cannibalization risks between existing pages.
6. Summarize in a table: Existing Topic | URL | Gap Level (High/Medium/Low).

Output format: Markdown table + bullet list of top 5 content gap opportunities.
```

---

## Output Storage

Save the gap analysis as a comment or note in:
`data/sitemap/sitemap-urls.json` → `content_gaps` array

Then proceed to Step 2: Keyword Discovery.
