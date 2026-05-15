# Prompt: HTML Conversion (Step 7)

Use this prompt to convert article.md into Shopify-safe HTML.

---

## Input Required

- `blogs/drafts/[slug]/article.md`
- `templates/shopify-html-template.html`

---

## Prompt to Use

```
You are a Shopify HTML developer for Innova Retail (India).

Convert the following Markdown article into Shopify-safe HTML.

Article: [PASTE article.md content]

## HTML Conversion Rules

### Shopify Safety
- Do NOT include <html>, <head>, or <body> tags — Shopify adds these
- Do NOT include <script> tags unless absolutely necessary
- Do NOT include external CSS links
- All styling must be inline CSS only
- Do NOT use Shopify Liquid tags ({{ }} or {% %})

### Heading Rules
- Do NOT add H1 in the HTML body — Shopify adds H1 from the blog title field
- Use <h2> for all ## headings
- Use <h3> for all ### headings
- Never nest H3 inside a non-H2 section

### Typography & Spacing
- Wrap all paragraphs in <p> tags
- Add style="margin-bottom: 16px; line-height: 1.7; color: #333333;" to all <p>
- Use <strong> for bold text
- Use <em> for italic
- Add style="margin: 24px 0;" to all <h2>
- Add style="margin: 16px 0;" to all <h3>

### Lists
- Use <ul> with style="padding-left: 20px; margin-bottom: 16px;"
- Use <li> with style="margin-bottom: 8px;"
- For ordered lists, use <ol> with same spacing

### CTA Blocks
Replace [CTA BLOCK: ...] with:
<div style="background: #0057b7; padding: 24px; border-radius: 8px; text-align: center; margin: 32px 0;">
  <p style="color: #ffffff; font-size: 18px; font-weight: bold; margin-bottom: 12px;">[CTA HEADING]</p>
  <a href="[LINK PLACEHOLDER]" style="background: #ffffff; color: #0057b7; padding: 12px 28px; border-radius: 4px; text-decoration: none; font-weight: bold; display: inline-block;">[CTA BUTTON TEXT]</a>
</div>

### Internal Link Placeholders
Replace [INTERNAL LINK: description] with:
<a href="#TODO-INTERNAL-LINK" style="color: #0057b7;">[link text]</a>

### Tables
Wrap all tables in:
<div style="overflow-x: auto; margin-bottom: 24px;">
<table style="width: 100%; border-collapse: collapse; font-size: 14px;">
  <thead><tr style="background: #f0f4f8;">
    <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">...</th>
  </tr></thead>
  <tbody>
    <tr><td style="padding: 10px; border: 1px solid #ddd;">...</td></tr>
  </tbody>
</table>
</div>

### FAQ Section
Wrap the entire FAQ section in:
<div style="background: #f9f9f9; padding: 24px; border-radius: 8px; margin: 32px 0;">
  <h2 style="margin-top: 0;">Frequently Asked Questions</h2>
  [FAQ content here]
</div>

### Mobile Responsiveness
Add this meta-compatible wrapper around the full content:
<div style="max-width: 800px; margin: 0 auto; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 16px; color: #333333;">
  [all content here]
</div>

### Images (placeholder)
Where images would logically go, add:
<!-- IMAGE: [description of ideal image] -->

Output: Complete Shopify-safe HTML as a single file.
```

---

## Output Storage

Save to: `blogs/drafts/[slug]/article.html`

Then proceed to Step 8: SEO QA.
