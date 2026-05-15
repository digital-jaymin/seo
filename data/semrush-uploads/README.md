# SEMrush Upload Instructions

Drop your SEMrush export files into this folder for Claude to analyze.

---

## How to Export from SEMrush

1. Go to **SEMrush → Keyword Magic Tool**
2. Enter the seed keywords listed below one by one
3. Filter: Country = **India**, Language = **English**
4. Export columns: **Keyword, Intent, Volume, KD%, CPC (USD), Trend**
5. Save as CSV
6. Name the file: `semrush-[date]-[keyword-group].csv`
   Example: `semrush-2026-05-15-hp-laptops.csv`
7. Drop into this folder

---

## Keywords to Check in SEMrush

Claude will update this list after Step 2 (Keyword Discovery).
Run Step 2 first, then come back here for the validated keyword list.

**Seed keywords to start with (based on Innova Retail niche):**

### HP Laptops & Business IT
- hp laptop price in india
- best hp laptop for business
- hp laptop for office use
- hp elitebook price india
- hp probook vs elitebook
- buy hp laptop in bulk india
- b2b laptop supplier india
- office laptop under 50000
- commercial laptop purchase india
- hp laptop distributor india

### ELV Products
- smart lock for office india
- smart cleaning robot india
- automatic parking barrier india
- dahua cctv price india
- dahua nvr price india
- best smart lock india 2024

### Buying Guides / Comparison
- best laptop for small business india
- laptop buying guide for office 2024
- hp vs dell laptop for business
- how to buy laptops in bulk for office

---

## After Uploading

Tell Claude:
> "I've uploaded a SEMrush report. File name: [file name]. Run Step 3 analysis."

Claude will:
1. Parse the CSV
2. Fill `semrush_volume`, `semrush_kd`, `semrush_cpc` in `keyword-opportunities.csv`
3. Score and rank topics
4. Save top 2–3 topics to `selected-topics.json`

---

## File Naming Convention

| Format | Example |
|--------|---------|
| `semrush-YYYY-MM-DD-[group].csv` | `semrush-2026-05-15-hp-laptops.csv` |

---

**Do not delete old uploads.** Keep all SEMrush files for historical reference.
