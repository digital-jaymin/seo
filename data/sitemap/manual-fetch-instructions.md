# Sitemap Manual Fetch Instructions

The cloud environment cannot reach external URLs.
Run the sitemap fetcher **locally** to collect the data, then paste the output here.

---

## Option A — Run the Script Locally (Recommended)

```bash
# 1. Clone the repo locally (or pull latest)
git clone https://github.com/digital-jaymin/seo.git
cd seo

# 2. Run the sitemap fetcher
python scripts/sitemap_fetcher.py

# 3. Check output
cat data/sitemap/sitemap-urls.json

# 4. Commit and push
git add data/sitemap/sitemap-urls.json
git commit -m "data: fetch Innova Retail sitemap URLs"
git push
```

---

## Option B — Browser + Manual Copy

1. Open in browser: https://innovaretail.co.in/sitemap.xml
2. If you see a sitemap index (list of other sitemaps), copy each nested URL
3. Open each nested sitemap and copy the `<loc>` URLs
4. Paste all blog/article URLs into `data/sitemap/sitemap-urls.json`

**Shopify standard sitemap structure:**
```
https://innovaretail.co.in/sitemap.xml          ← sitemap index
  ├── sitemap_products_1.xml                     ← product URLs
  ├── sitemap_collections_1.xml                  ← collection/category URLs
  ├── sitemap_pages_1.xml                        ← static pages
  └── sitemap_blogs_1.xml                        ← blog article URLs ← most important
```

---

## Option C — Google Search Console

1. Go to Google Search Console → your property
2. Left menu → Sitemaps
3. You'll see all submitted sitemaps and their URL counts
4. This gives a count without needing to open the XML

---

## After You Have the URLs

Paste the blog article URLs into `data/sitemap/sitemap-urls.json`
under the `"blog_urls"` array in this format:

```json
{
  "url": "https://innovaretail.co.in/blogs/news/article-slug",
  "slug": "article-slug",
  "topic": "Article Topic Name",
  "lastmod": "2025-01-15"
}
```

Then tell Claude:
> "Sitemap data is ready. Run Step 1 sitemap analysis."
