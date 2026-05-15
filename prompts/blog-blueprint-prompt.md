# Prompt: Blog Blueprint (Step 5)

Use this prompt to create the SEO blueprint before writing the article.

---

## Input Required

- `blogs/drafts/[slug]/serp-analysis.json`
- `data/keywords/selected-topics.json` (selected topic entry)
- `data/content-database/content-index.json` (for internal link suggestions)
- `config/site-config.json`

---

## Prompt to Use

```
You are an SEO content strategist for Innova Retail (India), a B2B retailer of
HP laptops, business IT products, and ELV products (Smart Locks, Parking Barriers,
Dahua products).

Primary keyword: [KEYWORD]
Secondary keywords: [LIST FROM SELECTED TOPICS]
SERP analysis: [PASTE serp-analysis.json]
Existing content index: [PASTE content-index.json]

Create a detailed blog blueprint with the following sections:

## 1. Search Intent
- Primary intent (Informational / Commercial / Transactional)
- User goal in one sentence
- Stage in buyer journey

## 2. Keyword Map
- Primary keyword
- 5–8 secondary keywords
- 8–12 semantic/LSI keywords
- 3–5 question keywords (from PAA)

## 3. Target Audience
- Who is reading this in India?
- What problem are they solving?
- What decision are they trying to make?

## 4. Recommended Title
- 3 title options (each under 60 characters)
- Mark the recommended one

## 5. URL Slug
- Clean, hyphenated, keyword-first
- Example: /blogs/best-hp-laptop-for-business-india

## 6. Meta Title
- Under 60 characters
- Include primary keyword near the start
- Include "India" or year if appropriate

## 7. Meta Description
- 140–155 characters exactly
- Include primary keyword
- Include a value hook or CTA phrase

## 8. Heading Structure (H1 → H2 → H3)
- H1 (only one — the article title)
- H2 sections (6–10)
- H3 subsections where needed
- Include FAQ H2 with 5 questions

## 9. Content Sections Plan
For each H2, write:
- Section purpose (what question does it answer?)
- Approximate word count
- Key points to cover
- Data or stats to include if possible

## 10. Internal Link Opportunities
- List 3–5 existing Innova Retail pages to link from this article
- List 2–3 pages this article should be linked from
- Use [PLACEHOLDER] if exact URLs are not known

## 11. CTA Plan
- Primary CTA (what action should the reader take?)
- CTA placement (after intro, mid-article, end)
- CTA copy suggestion

## 12. Competitor Gap Analysis
- What are the top 3 things competitors are NOT covering?
- How will this article be better?

## 13. Content Angle
- One-sentence unique angle for Innova Retail
- India-specific angle
- B2B buyer focus points

## 14. Estimated Word Count
- Minimum to be competitive: [X] words
- Target: [X] words

Output format: Save as blueprint.md in the blog folder.
```

---

## Output Storage

Save to: `blogs/drafts/[slug]/blueprint.md`

Then proceed to Step 6: Blog Writing.
