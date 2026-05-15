# Prompt: SEMrush Validation & Topic Selection (Step 3)

Use this prompt after uploading a SEMrush CSV to `data/semrush-uploads/`.
Topic selection enforces full SEO memory rules — no topic is selected unless
it passes all memory checks.

---

## Input Required

Generate the memory report first:
```bash
python scripts/seo_memory.py
```

Then paste:
1. Memory report output
2. `data/semrush-uploads/[your-semrush-export].csv`
3. `data/keywords/keyword-opportunities.csv`

---

## Prompt to Use

```
You are an SEO strategist for Innova Retail (innovaretail.co.in), an HP authorized
reseller in Ahmedabad/Rajkot, India.

=== SEO MEMORY (load before evaluating anything) ===
[PASTE seo_memory.py output here]
=== END MEMORY ===

=== SEMRUSH EXPORT ===
[PASTE SEMrush CSV content here]
=== END SEMRUSH ===

=== KEYWORD OPPORTUNITIES TABLE ===
[PASTE keyword-opportunities.csv content here]
=== END TABLE ===

TASK — do the following in order:

STEP A — Match & Fill SEMrush Data
Match SEMrush rows to keyword-opportunities.csv by keyword.
Fill in: semrush_volume, semrush_kd, semrush_cpc for each matched keyword.
For unmatched keywords, note "not_in_semrush" in notes.

STEP B — Recalculate Priority Scores
Use this formula when SEMrush data is available:
  priority_score = (commercial_score × 0.4) + (informational_score × 0.2) +
                   (volume_score × 0.3) + (kd_bonus × 0.1)
Where:
  volume_score = 10 if volume > 5000, 7 if > 1000, 4 if > 300, 1 if < 300
  kd_bonus     = 10 if KD < 30, 6 if KD < 50, 2 if KD < 70, 0 if KD ≥ 70

STEP C — Memory Validation
Before selecting any topic:
1. Check it is NOT already covered by a published blog (see memory report)
2. Check it is NOT a transactional keyword owned by a collection page
3. Confirm it has informational/comparison/guide intent
4. Confirm target_page_type = "blog" (never "collection")
5. If cannibalization_risk is "high" — exclude from selection
6. If cannibalization_risk is "medium" — flag for review but may still select

STEP D — Select Top 3 Topics
Select the top 3 topics that:
- Pass all memory checks
- Have the highest priority_score
- Cover different clusters (avoid selecting 2 topics from same cluster)
- Have realistic ranking potential (KD < 60 preferred)

For each selected topic, provide:
  - primary_keyword
  - cluster
  - intent
  - target_page_type: "blog"
  - parent_cluster
  - supported_collection_page (the /collections/ or /pages/ URL this blog links to)
  - all_supported_collections (list all collection pages in this cluster)
  - cannibalization_risk
  - internal_link_targets (list: existing blog slugs + collection URLs to link to)
  - semrush_volume
  - semrush_kd
  - semrush_cpc
  - priority_score
  - why_selected (2 sentences)
  - content_angle (what makes this blog different from a collection page)

STEP E — Output
Output 1: Updated keyword-opportunities.csv (full table with SEMrush data filled in)
Output 2: selected-topics.json using this structure:
{
  "_meta": {
    "last_updated": "YYYY-MM-DD",
    "selection_round": [N],
    "memory_rules": { ... keep existing meta ... }
  },
  "selected_topics": [
    {
      "primary_keyword": "",
      "cluster": "",
      "intent": "",
      "target_page_type": "blog",
      "parent_cluster": "",
      "supported_collection_page": "",
      "all_supported_collections": [],
      "cannibalization_risk": "",
      "internal_link_targets": [],
      "semrush_volume": 0,
      "semrush_kd": 0,
      "semrush_cpc": "",
      "priority_score": 0,
      "why_selected": "",
      "content_angle": "",
      "status": "approved_for_writing"
    }
  ]
}
```

---

## After Claude Output

1. Save updated CSV to `data/keywords/keyword-opportunities.csv`
2. Save selected topics to `data/keywords/selected-topics.json`
3. For each selected topic, run Step 4:
```bash
python scripts/blog_folder_creator.py \
  --keyword "primary keyword from selected-topics.json" \
  --cluster "cluster from selected-topics.json" \
  --intent "informational"
```
