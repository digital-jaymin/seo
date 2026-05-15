# Prompt: SEMrush Validation & Topic Selection (Step 3)

Use this prompt after uploading a SEMrush CSV to `data/semrush-uploads/`.

---

## Input Required

- File: `data/keywords/keyword-opportunities.csv`
- File: `data/semrush-uploads/[uploaded-file].csv`
- File: `data/content-database/content-index.json`

---

## Prompt to Use

```
You are an SEO strategist for Innova Retail (India).

I have uploaded a SEMrush keyword report. Here is the data:
[PASTE SEMrush CSV content here]

Here is the current keyword opportunities table:
[PASTE keyword-opportunities.csv content here]

Here is the existing content index (to check cannibalization):
[PASTE content-index.json here]

Please do the following:

1. Match SEMrush data to the keywords in the opportunities table.
2. Fill in semrush_volume, semrush_kd, semrush_cpc for each matched keyword.
3. Recalculate priority_score using:
   priority_score = (commercial_score × 0.4) + (informational_score × 0.2) + 
                    (volume_score × 0.3) + (low_kd_bonus × 0.1)
   where:
   - volume_score = 10 if volume > 5000, 7 if > 1000, 4 if > 300, 1 if < 300
   - low_kd_bonus = 10 if KD < 30, 6 if KD < 50, 2 if KD < 70, 0 if KD >= 70

4. Flag any keywords that would cannibalize existing content in content-index.json.
5. Remove or deprioritize cannibalistic keywords.
6. Select the top 2–3 blog topics based on final priority_score.
7. For each selected topic, provide:
   - primary_keyword
   - why_selected (2 sentences)
   - estimated_traffic_potential
   - content_angle_suggestion
   - cluster
   - intent

Output:
- Updated keyword-opportunities.csv (full table)
- Selected topics in JSON format matching templates/blog-metadata-template.json structure
```

---

## Output Storage

1. Replace `data/keywords/keyword-opportunities.csv` with updated table
2. Save selected topics to `data/keywords/selected-topics.json`
3. Proceed to Step 4: SERP Analysis for each selected topic
