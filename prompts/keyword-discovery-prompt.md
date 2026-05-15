# Prompt: Keyword Discovery (Step 2)

Use this prompt with Claude to generate keyword opportunities.

---

## Input Required

- File: `data/sitemap/sitemap-urls.json` (content_gaps section)
- File: `config/site-config.json`

---

## Prompt to Use

```
You are an SEO keyword strategist for Innova Retail, an Indian B2B retailer selling:
- HP Laptops, Desktops, and Accessories
- Business IT products for SMEs and enterprises
- ELV products: Smart Locks, Smart Cleaning Robots, Parking Barriers, Dahua CCTV

Target country: India
Target audience: Business buyers, IT procurement managers, bulk laptop buyers

Based on the following content gaps:
[PASTE content_gaps from sitemap-urls.json]

Generate a keyword opportunity list with the following for each keyword:
- keyword (exact phrase)
- intent: Informational | Commercial | Transactional | Navigational
- cluster: HP Laptops | Business IT | ELV Products | Buying Guides | Comparison
- source: seed | long-tail | question | comparison | local
- commercial_score: 1–10 (how likely to drive a purchase)
- informational_score: 1–10 (how likely to drive blog traffic)
- priority_score: weighted average (commercial_score × 0.6 + informational_score × 0.4)
- semrush_volume: leave blank (to be filled after SEMrush upload)
- semrush_kd: leave blank
- semrush_cpc: leave blank
- status: pending_semrush_validation
- notes: any relevant notes

Generate at least 30 keywords. Focus on:
1. Buying intent keywords (best hp laptop for office, bulk laptop purchase india)
2. Comparison keywords (hp vs dell for business, elitebook vs probook)
3. Guide keywords (how to buy laptops for office, smart lock installation guide)
4. ELV product keywords (smart lock price india, dahua nvr setup)
5. Local/India-specific keywords (hp laptop price in india, b2b laptop supplier delhi)

Output as a CSV table with these exact column headers:
keyword,intent,cluster,source,commercial_score,informational_score,priority_score,semrush_volume,semrush_kd,semrush_cpc,status,notes
```

---

## Output Storage

Copy the CSV output into:
`data/keywords/keyword-opportunities.csv`

Then follow instructions in:
`data/semrush-uploads/README.md`

to validate keywords in SEMrush before proceeding to Step 4.
