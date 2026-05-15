# Prompt: SEO & HTML QA (Step 8)

Use this prompt to quality-check the article before approving it.

---

## Input Required

- `blogs/drafts/[slug]/article.md`
- `blogs/drafts/[slug]/article.html`
- `blogs/drafts/[slug]/blueprint.md`
- `data/content-database/content-index.json`

---

## Prompt to Use

```
You are an SEO QA auditor for Innova Retail (India).

Review the following blog draft and score it out of 100.

Article MD: [PASTE article.md]
Article HTML: [PASTE article.html]
Blueprint: [PASTE blueprint.md]
Content index (for cannibalization check): [PASTE content-index.json]

## QA Checklist

Score each item. Total must reach 85+ to approve.

### Meta & Slug (15 points)
[ ] Meta title: 50–60 characters (5 pts)
[ ] Meta description: 140–155 characters (5 pts)
[ ] Slug: lowercase, hyphenated, keyword-first, no stop words (5 pts)

### Heading Structure (15 points)
[ ] Only one H1 in article.md (5 pts)
[ ] No H1 in article.html body (5 pts)
[ ] Logical H2 → H3 hierarchy, no skipped levels (5 pts)

### Keyword Placement (20 points)
[ ] Primary keyword in H1 (5 pts)
[ ] Primary keyword in first 100 words (5 pts)
[ ] Primary keyword in at least 2 H2s (5 pts)
[ ] Primary keyword in conclusion (5 pts)

### Secondary Keywords (10 points)
[ ] At least 4 secondary keywords used naturally in body (5 pts)
[ ] No keyword stuffing detected (5 pts)

### Content Quality (15 points)
[ ] Minimum word count met (from blueprint) (5 pts)
[ ] No thin sections (each H2 section > 80 words) (5 pts)
[ ] India-specific context included (5 pts)

### FAQ (5 points)
[ ] FAQ section present with 5+ questions (3 pts)
[ ] Answers are 50–100 words each (2 pts)

### Internal Links (5 points)
[ ] At least 3 internal link placeholders present (5 pts)

### CTA (5 points)
[ ] At least 2 CTA blocks present (3 pts)
[ ] CTA copy is compelling and action-oriented (2 pts)

### HTML Quality (10 points)
[ ] No <html>/<head>/<body> tags (2 pts)
[ ] No H1 in HTML body (2 pts)
[ ] All inline CSS, no external stylesheets (2 pts)
[ ] CTA blocks styled correctly (2 pts)
[ ] Mobile wrapper div present (2 pts)

### Cannibalization Check (bonus — deduct if failed)
[ ] No keyword overlap > 70% with existing content-index.json entries (-10 pts if failed)

## Output Format

Provide a full QA report in this format:

**Total Score: [X]/100**
**Status: APPROVED / NEEDS REVISION**

| Check | Score | Max | Notes |
|-------|-------|-----|-------|
| Meta Title | | 5 | |
...

**Issues Found:**
- [List each issue with the fix required]

**Improvements Made:**
- [List any changes you made directly to the article]

If score < 85, make the necessary fixes to article.md and article.html,
then re-run the QA checklist and confirm the final score.
```

---

## Output Storage

Save to: `blogs/drafts/[slug]/qa-report.md`

If score >= 85: proceed to Step 9: Shopify Draft Preparation.
If score < 85: fix issues, then re-run QA.
