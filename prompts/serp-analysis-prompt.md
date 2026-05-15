# Prompt: SERP Analysis (Step 4)

Use this prompt when SERPAPI key is not available, to guide manual SERP research.
When SERPAPI key IS available, use `scripts/serpapi_fetcher.py` instead.

---

## Input Required

- Selected topic from `data/keywords/selected-topics.json`

---

## Prompt to Use (Manual SERP Research)

```
You are an SEO analyst for Innova Retail (India).

Primary keyword: [KEYWORD]
Target country: India

I will now share the top 10 Google search results for this keyword.
[PASTE top 10 results manually — title, URL, meta description for each]

Also share:
- People Also Ask questions (copy from Google)
- Related searches (bottom of Google page)
- Any featured snippet content

Please analyze and provide:

1. Top 10 competitor URLs with:
   - Domain authority estimate (high/medium/low)
   - Content type (listicle, guide, comparison, product page)
   - Approximate word count (estimate from structure)
   - Key angle used by this competitor

2. People Also Ask — list all questions found

3. Related searches — list all

4. Content gaps: What are competitors NOT covering that we should?

5. Winning content angle for Innova Retail:
   - What unique value can we offer?
   - What India-specific angle works?
   - What buyer pain points can we address better?

6. Recommended heading structure based on SERP patterns

7. Estimated content length to be competitive (words)

Output format: Use the serp-analysis-template.json structure.
```

---

## Output Storage

Save the completed analysis to:
`blogs/drafts/[keyword-slug]/serp-analysis.json`

Then proceed to Step 5: Blog Blueprint.
