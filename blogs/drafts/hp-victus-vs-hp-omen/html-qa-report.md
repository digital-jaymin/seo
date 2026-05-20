# HTML QA Report — BLOG-029
# HP Victus vs HP Omen: Which Gaming Laptop Should You Buy in India?

**File reviewed:** `blogs/drafts/hp-victus-vs-hp-omen/final.html`  
**QA date:** 2026-05-18  
**Reviewer:** Claude (automated SEO QA pass)  
**Pass:** Visual redesign + em-dash removal pass  
**Outcome:** 1 minor issue found and fixed (em dash in HTML comment). File is Shopify paste-ready.

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
| `<link>` (stylesheet) | No | ✅ Pass |
| Liquid syntax (`{{`, `{%`) | No | ✅ Pass |

### 2. Em Dash Audit
All em dash characters (—) removed from both `article.md` and `final.html`.

- `article.md`: 41 replacements applied by Python script. 0 remaining.
- `final.html`: 1 em dash found in HTML comment line (`Innova Retail — Shopify Blog Post HTML`). Fixed to colon. 0 remaining.

`grep -c "—" final.html` returns **0**. ✅

### 3. Link Audit
All links use absolute URLs pointing to `innovaretail.co.in`. No empty `href` values.

| Destination | Occurrences | Status |
|------------|-------------|--------|
| /collections/hp-victus-gaming-laptop | 4 | ✅ |
| /collections/hp-omen-laptop | 3 | ✅ |
| /collections/gaming-laptops | 1 | ✅ |
| /collections/best-gaming-laptop-under-70000 | 2 | ✅ |
| /collections/best-gaming-laptop-under-1-lakh | 2 | ✅ |
| /pages/laptop-service | 1 | ✅ |

All 6 internal link targets from `metadata.json` are present. ✅

### 4. Image References
No `<img>` tags in the file. No fake or placeholder image references. ✅

### 5. Mobile Responsiveness
- Spec comparison table wrapped in `<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;">` ✅
- Table has `min-width:560px` — scrolls horizontally on narrow viewports ✅
- Two-column flex layouts use `flex-wrap:wrap` — stack vertically on mobile without media queries ✅
- CTA buttons use `display:inline-block;margin-bottom:8px` — stack naturally on small screens ✅

### 6. CSS Method
- All styling via `style=""` attributes only ✅
- No `class=` or `id=` attributes used ✅
- No external stylesheet references ✅
- No JavaScript ✅
- `background-color:` used throughout (not `background:` shorthand) ✅
  - `grep -c "background-color:"` returns **36**
  - `grep -c "background:[^-]"` returns **0**

### 7. Visual Design — New in This Pass
The file was fully redesigned for visual quality. Key elements verified present:

| Element | Implementation | Status |
|---------|---------------|--------|
| Outer max-width wrapper | `max-width:860px;margin:0 auto` | ✅ |
| System font stack | `-apple-system,BlinkMacSystemFont,'Segoe UI',...` | ✅ |
| Quick-answer card | Blue left-border callout after intro | ✅ |
| H2 underline style | `border-bottom:2px solid #e8edf2` | ✅ |
| Two-column flex cards | `display:flex;flex-wrap:wrap;gap:16px` | ✅ |
| Table header | `background-color:#0057b8;color:#ffffff` | ✅ |
| Alternating table rows | `#f8f9fb` / `#ffffff` | ✅ |
| Verdict callout | Amber left-border `#fffbea;border-left:4px solid #d4930a` | ✅ |
| CTA Block 1 (Victus) | `background-color:#0057b8`, white text/button | ✅ |
| CTA Block 2 (Omen) | `background-color:#1a0033`, white text/button | ✅ |
| CTA Block 3 (neutral) | `background-color:#f8f9fb`, 4 buttons | ✅ |
| FAQ cards | `background-color:#f8f9fb;border:1px solid #dde3ec;border-radius:8px` | ✅ |

### 8. CTA Buttons — Shopify Safety
- `background-color:` used on all buttons (not `background:` shorthand) ✅
- No hover/active states that require JavaScript or `<style>` blocks ✅
- All button `<a>` tags include `display:inline-block` for reliable rendering ✅

### 9. Structure Audit
| Section | Present | Status |
|---------|---------|--------|
| Intro (3 paragraphs + quick-answer card) | ✅ | ✅ |
| What Is the Difference (featured snippet H2) | ✅ | ✅ |
| Full Spec Comparison Table | ✅ | ✅ |
| Display and Build Quality (H3 subsections) | ✅ | ✅ |
| Gaming Performance (H3 subsections) | ✅ | ✅ |
| Price in India | ✅ | ✅ |
| CTA Block 1 — Victus | ✅ | ✅ |
| Which Should You Buy (Buy Victus if / Buy Omen if) | ✅ | ✅ |
| Is HP Victus Being Discontinued | ✅ | ✅ |
| Three-Way View (Victus / Omen / Pavilion) | ✅ | ✅ |
| CTA Block 2 — Omen | ✅ | ✅ |
| Where to Buy (Authorized) | ✅ | ✅ |
| FAQ (5 questions as H3 + P pairs) | ✅ | ✅ |
| The Verdict | ✅ | ✅ |
| CTA Block 3 — End of article | ✅ | ✅ |
| Author byline footer | ✅ | ✅ |

H2 count: **11** | H3 count: **15** ✅

### 10. Pricing Claims
All price figures hedged with appropriate language. `grep -c "approx\|approximately\|varies"` returns **8**. ✅

| Location | Price mentioned | Hedge present |
|----------|----------------|---------------|
| Spec table — Starting Price rows | ₹60k–65k / ₹90k–1L | "(approx.)" ✅ |
| Table footnote | — | "Prices shown are approximate market references" ✅ |
| Price section body | ₹60k–65k, ₹85k–90k, ₹90k–1L, ₹1.3L+ | "approximately" ✅ |
| Budget guidance cards | ₹60k–85k / ₹90k+ | Budget ranges, not fixed prices ✅ |
| FAQ | ₹85k, ₹90k | Budget guidance thresholds ✅ |
| Verdict | ₹85k, ₹90k | Budget guidance thresholds ✅ |

**Note for publisher:** Verify ₹60,000–₹65,000 entry Victus pricing against live Innova Retail stock before publishing.

### 11. Shopify Paste-Ready Assessment
- File opens with `<!-- comment -->` then `<div style="...">` ✅
- No forbidden tags ✅
- No JavaScript ✅
- No external CSS ✅
- No Liquid syntax ✅
- `background-color:` used throughout ✅
- Table wrapped in `overflow-x:auto` div ✅
- No `class=` or `id=` attributes ✅
- No em dashes ✅

---

## Issues Found and Fixed

| # | Severity | Issue | Fix Applied |
|---|----------|-------|-------------|
| 1 | Low | Em dash (—) in HTML comment: `Innova Retail — Shopify Blog Post HTML` | ✅ Replaced with colon |

**Total issues:** 1  
**Issues fixed:** 1  
**Issues remaining:** 0  

---

## Final Status

**HTML QA: PASSED**  
`final.html` is visually redesigned, em-dash-free, Shopify-safe, and ready for Shopify draft creation (Step 10).

---

## Next Step

Create `shopify-draft.json` with:
- `title` from metadata.json
- `body_html` — contents of `final.html`
- `blog_id` — from Shopify admin (to be filled by user)
- `tags`, `published`, `author` fields
- `meta_title` and `meta_description` from article.md frontmatter
