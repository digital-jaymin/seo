# Prompt: Shopify Draft Preparation (Step 9)

Use this prompt to generate the Shopify draft JSON for Zapier or Make automation.

---

## Input Required

- `blogs/drafts/[slug]/article.html`
- `blogs/drafts/[slug]/blueprint.md` (for meta fields)
- `blogs/drafts/[slug]/qa-report.md` (must be APPROVED)
- `config/site-config.json`

---

## Prompt to Use

```
You are preparing a Shopify blog draft for Innova Retail (India).

The article has passed QA (score: [X]/100).
Do NOT publish this live. Create a draft-ready JSON only.

Article HTML: [PASTE article.html]
Blueprint (for meta): [PASTE blueprint.md]
Site config: [PASTE relevant fields from site-config.json]

Create a shopify-draft.json with this exact structure:

{
  "blog_post": {
    "title": "[H1 article title]",
    "body_html": "[FULL article.html content — escaped properly]",
    "meta_title": "[meta title under 60 chars]",
    "meta_description": "[meta description 140-155 chars]",
    "handle": "[url-slug]",
    "tags": ["tag1", "tag2", "tag3"],
    "status": "draft",
    "blog_category": "[cluster name — e.g., HP Laptops, ELV Products]",
    "published": false
  },
  "workflow_notes": {
    "qa_score": [score],
    "primary_keyword": "[keyword]",
    "secondary_keywords": ["kw1", "kw2"],
    "cluster": "[cluster]",
    "intent": "[intent]",
    "internal_links_to_add": ["[list of placeholder links to resolve before publishing]"],
    "cta_links_to_add": ["[list of CTA links to fill]"],
    "images_to_add": ["[list of image placeholders from HTML comments]"],
    "notes_for_zapier_or_make": "Upload body_html to Shopify blog using Admin API. Set status=draft. Do not publish automatically. Manually review in Shopify admin before publishing.",
    "zapier_blog_id": "TODO: Add your Shopify blog ID here",
    "ready_for_automation": true
  }
}

Rules:
- status must be "draft"
- published must be false
- Do not include any Shopify Liquid syntax
- body_html must be valid HTML with all quotes escaped for JSON
- tags should reflect: product category, content type, target audience, year
- Maximum 10 tags
```

---

## Output Storage

Save to: `blogs/drafts/[slug]/shopify-draft.json`

Then commit all blog files to GitHub (Step 10).

## After Zapier/Make Upload

1. Go to Shopify Admin → Blog Posts
2. Find the draft created by automation
3. Review title, meta, content, images
4. Add missing internal links
5. Add feature image
6. Click Publish — **manually**

Publishing is always manual. Never auto-publish.
