# Prompt: Keyword Discovery (Step 2)

Use this prompt with Claude to generate keyword opportunities.
All recommendations run through the SEO memory system before being accepted.

---

## Input Required

Before running this prompt, generate the memory report:
```bash
python scripts/seo_memory.py
```

Then paste:
1. The memory report output (full text)
2. `data/sitemap/sitemap-urls.json` → `content_gaps` section
3. `data/topical-authority/topical-authority-map.json` → full file

---

## Prompt to Use

```
You are an SEO strategist for Innova Retail (innovaretail.co.in), an HP authorized reseller
in Ahmedabad and Rajkot, India. They sell: HP Laptops, Desktops, Printers, Accessories,
and ELV products (Smart Locks, Cleaning Robots, Parking Barriers, Dahua Intercom).

=== SEO MEMORY (load before generating anything) ===
[PASTE seo_memory.py output here]
=== END MEMORY ===

=== TOPICAL AUTHORITY MAP ===
[PASTE topical-authority-map.json here]
=== END MAP ===

=== CONTENT GAPS ===
[PASTE content_gaps from sitemap-urls.json here]
=== END GAPS ===

MEMORY RULES — follow these strictly:

1. NEVER suggest a keyword already covered by a published blog (see memory report).
2. NEVER suggest transactional keywords owned by collection pages.
   Collection pages own: "best gaming laptop under 70000", "best laptop under 40000",
   "best business laptop", "best student laptop", and any keyword matching a collection slug.
   Blogs SUPPORT collections — they do NOT compete with them.
3. Every blog keyword must have INFORMATIONAL, COMPARISON, or GUIDE intent.
   Transactional and navigational intent keywords belong to collection/product pages.
4. Every topic must strengthen topical authority for an identified gap cluster.
5. Every topic must link BACK to a specific collection page (supported_collection_page).
6. Topics must generate a cluster of related content — not isolated articles.

For each keyword, you MUST provide all 5 required memory fields:
- target_page_type: always "blog" (if collection, reject it)
- parent_cluster: which cluster from the topical authority map
- supported_collection_page: the /collections/ or /pages/ URL this blog sends traffic to
- cannibalization_risk: "none" | "medium" | "high"
- internal_link_targets: list of existing blog slugs and collection URLs to link to

Generate at least 30 keyword opportunities covering HIGH-priority gaps:
1. Gaming Laptops (0 blogs, 5 collection pages)
2. Business IT / HP OmniBook (0 blogs)
3. ELV — Cleaning Robots, Parking Barriers, Dahua (0 blogs each)
4. Local SEO — HP Laptops Ahmedabad, HP Store Rajkot (missing)
5. Price guides that support the price-based collections (informational angle only)

Focus on:
- Comparison keywords ("HP Victus vs HP Omen", "gaming laptop vs regular laptop")
- Feature-focused guides ("best gaming laptop under 70000 features to check")
- Use-case content ("gaming laptop for college students", "HP laptop for CA office")
- Educational content ("what specs do I need for gaming", "how to choose a smart lock")
- Local content ("HP store Ahmedabad", "buy laptop Rajkot")

Output as CSV with these exact column headers:
keyword,intent,cluster,source,commercial_score,informational_score,priority_score,semrush_volume,semrush_kd,semrush_cpc,target_page_type,supported_collection_page,cannibalization_risk,internal_link_targets,status,notes

Leave semrush_volume, semrush_kd, semrush_cpc blank (pending SEMrush validation).
Set status to: pending_semrush
```

---

## Validation After Claude Output

Run the import to validate every keyword against memory:
```bash
python scripts/keyword_table_builder.py path/to/claude-output.csv
```

This will:
- Block any collection-owned transactional keywords
- Flag medium cannibalization risks for review
- Auto-populate `target_page_type`, `supported_collection_page`, `internal_link_targets`
- Sort by priority score

---

## Output Storage

The keyword_table_builder.py script updates:
`data/keywords/keyword-opportunities.csv`

Then follow:
`data/semrush-uploads/README.md`

to validate approved keywords in SEMrush before proceeding to Step 3.
