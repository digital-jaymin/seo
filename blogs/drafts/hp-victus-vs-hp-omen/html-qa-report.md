# HTML QA Report — BLOG-029
# HP Victus vs HP Omen: Which Gaming Laptop Should You Buy in India?

**File reviewed:** `blogs/drafts/hp-victus-vs-hp-omen/final.html`  
**QA date:** 2026-05-18  
**Reviewer:** Claude (automated SEO QA pass)  
**Outcome:** 1 issue found and fixed. File is Shopify paste-ready.

---

## QA Checklist Results

### 1. Forbidden Tag Audit
| Tag | Present | Status |
|-----|---------|--------|
| `<html>` | No | ✅ Pass |
| `<head>` | No | ✅ Pass |
| `<body>` | No | ✅ Pass |
| `<h1>` | No | ✅ Pass |
| `<script>` | No | ✅ Pass |
| `<style>` | No | ✅ Pass |
| `<link>` | No | ✅ Pass |
| Liquid syntax (`{{`, `{%`) | No | ✅ Pass |

### 2. Link Audit
All links use absolute URLs pointing to `innovaretail.co.in`. No empty `href` values. No broken anchors.

| Destination | Occurrences | Status |
|------------|-------------|--------|
| /collections/hp-victus-gaming-laptop | 4 | ✅ |
| /collections/hp-omen-laptop | 3 | ✅ |
| /collections/gaming-laptops | 1 | ✅ |
| /collections/best-gaming-laptop-under-70000 | 2 | ✅ |
| /collections/best-gaming-laptop-under-1-lakh | 2 | ✅ |
| /pages/laptop-service | 1 | ✅ |

All 6 internal link targets from `metadata.json` are present.

### 3. Image References
No `<img>` tags in the file. No fake or placeholder image references. ✅

### 4. Mobile Responsiveness
- Spec comparison table wrapped in `<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;">` ✅
- Table has `min-width:560px` — scrolls horizontally on small screens rather than collapsing ✅
- CTA button links use `display:inline-block` with `margin-bottom:8px` — stack naturally on narrow viewports ✅

### 5. CSS Method
- All styling via `style=""` attributes only ✅
- No `class=` or `id=` attributes used for styling ✅
- No external stylesheet references ✅
- `-webkit-overflow-scrolling:touch` present (deprecated but harmless) ✅

### 6. CTA Buttons — Shopify Safety
**Issue found and fixed.**

Shopify's online store HTML editor can mutate or strip the CSS `background` shorthand property in inline `style=""` attributes. It interprets `background:` as a shorthand that may reset sub-properties (background-image, background-repeat, etc.), occasionally stripping the color value entirely on save.

**Fix applied:** All 24 occurrences of `background:` replaced with `background-color:` throughout the file. Affected elements:
- 13 table row `<tr>` elements (alternating shading and header)
- 3 CTA container `<div>` backgrounds
- 4 `<a>` button backgrounds
- 1 verdict callout box background
- 3 other styled containers

Verification: `grep -c "background:"` returns 0. `grep -c "background-color:"` returns 24.

### 7. FAQ Section
- 5 questions rendered as `<h3>` + `<p>` pairs ✅
- No nested lists or definition lists ✅
- No accordion/collapse markup (not needed; Shopify blog renders flat HTML) ✅
- All 4 PAA questions covered ✅
- 5th question covers "which should I buy" decision intent ✅

### 8. Duplicate Content Check
All 11 sections verified as unique. No paragraph is repeated verbatim across sections.

Sections present:
1. Intro (3 paragraphs) ✅
2. What Is the Difference ✅
3. Full Spec Comparison Table ✅
4. Display and Build Quality (4 H3 subsections) ✅
5. Gaming Performance (4 H3 subsections) ✅
6. Price in India ✅
7. CTA Block 1 — Victus ✅
8. Which Should You Buy (Buy Victus if / Buy Omen if) ✅
9. Is HP Victus Being Discontinued ✅
10. Three-Way View (Victus / Omen / Pavilion) ✅
11. CTA Block 2 — Omen ✅
12. Where to Buy (Authorized) ✅
13. FAQ (5 questions) ✅
14. The Verdict ✅
15. CTA Block 3 — End of article (all 4 collections) ✅
16. Author byline ✅

### 9. Pricing Claims
All price figures are hedged with appropriate language:

| Location | Price mentioned | Hedge present |
|----------|----------------|---------------|
| Spec table — Starting Price rows | ₹60k–65k / ₹90k–1L | "(approx.)" ✅ |
| Table footnote | — | "Prices shown are approximate market references" ✅ |
| Price section body | ₹60k–65k, ₹85k–90k, ₹90k–1L, ₹1.3L+ | "approximately" ✅ |
| Price section footnote | — | "pricing varies by stock and available configs" ✅ |
| Buy Victus if list | ₹60k–85k | Budget range, not a fixed price ✅ |
| Buy Omen if list | ₹90k+ | Budget threshold, not a fixed price ✅ |
| FAQ | ₹85k, ₹90k | Budget guidance thresholds ✅ |
| Verdict | ₹85k, ₹90k | Budget guidance thresholds ✅ |

No bare unhedged price claim present. ✅

**Note for publisher:** The ₹60,000–₹65,000 starting price for Victus entry models should be verified against live Innova Retail inventory before publishing. 2025 Victus RTX 4050 base configs may be closer to ₹70,000.

### 10. Meaning vs article.md
Verified section by section. No content has been altered, added, or omitted during HTML conversion. HTML entities used correctly throughout:
- `&mdash;` for em dashes ✅
- `&ndash;` for ranges ✅
- `&#8377;` for ₹ (Rupee sign) ✅
- `&rarr;` for → arrows ✅
- `&ldquo;`/`&rdquo;` for smart quotes ✅
- `&rsquo;` for apostrophes ✅
- `&times;` for × in QHD spec ✅
- `&amp;` for & in byline ✅

### 11. Shopify Paste-Ready Assessment
- File starts with a `<p>` tag ✅
- No forbidden tags ✅
- No JavaScript ✅
- No external CSS ✅
- No Liquid syntax ✅
- `background-color:` used throughout (not `background:` shorthand) ✅ (fixed)
- Table is scroll-wrapped for mobile ✅

---

## Issues Found

| # | Severity | Issue | Fix Applied |
|---|----------|-------|-------------|
| 1 | Medium | `background:` shorthand in all inline styles — can be stripped by Shopify HTML editor on save | ✅ Replaced all 24 occurrences with `background-color:` |

**Total issues:** 1  
**Issues fixed:** 1  
**Issues remaining:** 0  

---

## Final Status

**HTML QA: PASSED**  
`final.html` is clean, Shopify-safe, and ready for Shopify draft creation (Step 10).

---

## Next Step

Create `shopify-draft.json` with:
- `title` from metadata.json
- `body_html` — contents of `final.html` (escaped or raw depending on API method)
- `blog_id` — from Shopify admin (to be filled by user)
- `tags`, `published`, `author` fields
- `meta_title` and `meta_description` from article.md frontmatter
