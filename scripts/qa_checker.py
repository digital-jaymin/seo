#!/usr/bin/env python3
"""
qa_checker.py
Runs automated SEO and HTML QA checks on a blog draft.
Scores the blog out of 100 and saves results to qa-report.md.

Usage:
  python scripts/qa_checker.py --slug "best-hp-laptop-for-business-india"
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

BLOGS_DIR = Path("blogs/drafts")
CONTENT_INDEX_PATH = Path("data/content-database/content-index.json")
MIN_SCORE = 85


def load_file(path):
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def load_json(path):
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


class QAResult:
    def __init__(self, check, score, max_score, notes=""):
        self.check = check
        self.score = score
        self.max_score = max_score
        self.notes = notes

    def passed(self):
        return self.score == self.max_score


def check_meta_title(metadata):
    title = metadata.get("meta_title", "")
    length = len(title)
    if 50 <= length <= 60:
        return QAResult("Meta title length (50–60 chars)", 5, 5, f"{length} chars — OK")
    elif title:
        return QAResult("Meta title length (50–60 chars)", 2, 5, f"{length} chars — should be 50–60")
    return QAResult("Meta title length (50–60 chars)", 0, 5, "Missing meta_title in metadata.json")


def check_meta_description(metadata):
    desc = metadata.get("meta_description", "")
    length = len(desc)
    if 140 <= length <= 155:
        return QAResult("Meta description length (140–155 chars)", 5, 5, f"{length} chars — OK")
    elif desc:
        return QAResult("Meta description length (140–155 chars)", 2, 5, f"{length} chars — should be 140–155")
    return QAResult("Meta description length (140–155 chars)", 0, 5, "Missing meta_description in metadata.json")


def check_slug(metadata):
    slug = metadata.get("slug", "")
    slug_path = slug.lstrip("/blogs/").strip("/")
    if not slug_path:
        return QAResult("Slug quality", 0, 5, "Missing slug")
    issues = []
    if slug_path != slug_path.lower():
        issues.append("not lowercase")
    if " " in slug_path:
        issues.append("contains spaces")
    if re.search(r"[^a-z0-9-]", slug_path):
        issues.append("contains invalid characters")
    if issues:
        return QAResult("Slug quality", 2, 5, f"Issues: {', '.join(issues)}")
    return QAResult("Slug quality", 5, 5, f"OK: {slug}")


def check_single_h1_in_md(article_md):
    h1s = re.findall(r"^# .+", article_md, re.MULTILINE)
    # Also check YAML front matter title — that's fine
    # Count only markdown H1 outside front matter
    body = re.sub(r"^---.*?^---", "", article_md, flags=re.MULTILINE | re.DOTALL).strip()
    h1s_in_body = re.findall(r"^# .+", body, re.MULTILINE)
    if len(h1s_in_body) == 1:
        return QAResult("Only one H1 in article.md", 5, 5, "OK")
    elif len(h1s_in_body) == 0:
        return QAResult("Only one H1 in article.md", 3, 5, "No H1 found in article body")
    return QAResult("Only one H1 in article.md", 0, 5, f"{len(h1s_in_body)} H1s found — must be exactly 1")


def check_no_h1_in_html(article_html):
    h1s = re.findall(r"<h1[\s>]", article_html, re.IGNORECASE)
    if not h1s:
        return QAResult("No H1 in article.html body", 5, 5, "OK — no H1 tag in HTML")
    return QAResult("No H1 in article.html body", 0, 5, f"Found {len(h1s)} H1 tag(s) — remove them (Shopify adds H1)")


def check_heading_hierarchy(article_md):
    body = re.sub(r"^---.*?^---", "", article_md, flags=re.MULTILINE | re.DOTALL).strip()
    headings = re.findall(r"^(#{1,6}) .+", body, re.MULTILINE)
    issues = []
    prev_level = 1
    for h in headings:
        level = len(h)
        if level > prev_level + 1:
            issues.append(f"Jumped from H{prev_level} to H{level}")
        prev_level = level
    if not issues:
        return QAResult("Logical H2 → H3 hierarchy", 5, 5, "OK")
    return QAResult("Logical H2 → H3 hierarchy", 2, 5, f"Issues: {'; '.join(issues[:3])}")


def check_keyword_in_h1(article_md, keyword):
    body = re.sub(r"^---.*?^---", "", article_md, flags=re.MULTILINE | re.DOTALL).strip()
    h1_match = re.search(r"^# (.+)", body, re.MULTILINE)
    if not h1_match:
        return QAResult("Primary keyword in H1", 0, 5, "No H1 found")
    h1_text = h1_match.group(1).lower()
    kw_words = keyword.lower().split()
    found = sum(1 for w in kw_words if w in h1_text)
    if found >= len(kw_words) * 0.7:
        return QAResult("Primary keyword in H1", 5, 5, "OK")
    return QAResult("Primary keyword in H1", 2, 5, f"Keyword '{keyword}' not clearly in H1: '{h1_match.group(1)}'")


def check_keyword_in_first_100_words(article_md, keyword):
    body = re.sub(r"^---.*?^---", "", article_md, flags=re.MULTILINE | re.DOTALL).strip()
    # Remove markdown headers and symbols
    plain = re.sub(r"^#{1,6} .+\n", "", body, flags=re.MULTILINE)
    plain = re.sub(r"[#*_`\[\]()]", "", plain)
    words = plain.split()[:100]
    first_100 = " ".join(words).lower()
    kw_words = keyword.lower().split()
    found = sum(1 for w in kw_words if w in first_100)
    if found >= len(kw_words) * 0.7:
        return QAResult("Primary keyword in first 100 words", 5, 5, "OK")
    return QAResult("Primary keyword in first 100 words", 0, 5, f"Keyword not found in first 100 words")


def check_keyword_in_h2s(article_md, keyword):
    body = re.sub(r"^---.*?^---", "", article_md, flags=re.MULTILINE | re.DOTALL).strip()
    h2s = re.findall(r"^## (.+)", body, re.MULTILINE)
    kw_core = keyword.lower().split()[0]
    matched = sum(1 for h in h2s if kw_core in h.lower())
    if matched >= 2:
        return QAResult("Primary keyword in ≥2 H2s", 5, 5, f"Found in {matched} H2s")
    return QAResult("Primary keyword in ≥2 H2s", 2, 5, f"Only found in {matched} H2(s) — aim for 2+")


def check_keyword_in_conclusion(article_md, keyword):
    lines = article_md.split("\n")
    last_300_words = " ".join(lines[-50:]).lower()
    kw_words = keyword.lower().split()
    found = sum(1 for w in kw_words if w in last_300_words)
    if found >= len(kw_words) * 0.7:
        return QAResult("Primary keyword in conclusion", 5, 5, "OK")
    return QAResult("Primary keyword in conclusion", 2, 5, "Keyword not clearly in last section")


def check_secondary_keywords(article_md, metadata):
    secondary = metadata.get("secondary_keywords", [])
    if not secondary:
        return QAResult("≥4 secondary keywords used naturally", 3, 5, "No secondary keywords in metadata.json")
    body = article_md.lower()
    found = [kw for kw in secondary if kw.lower() in body]
    if len(found) >= 4:
        return QAResult("≥4 secondary keywords used naturally", 5, 5, f"Found: {len(found)}/{len(secondary)}")
    return QAResult("≥4 secondary keywords used naturally", 2, 5, f"Only {len(found)}/{len(secondary)} secondary keywords found in text")


def check_keyword_stuffing(article_md, keyword):
    body = re.sub(r"^---.*?^---", "", article_md, flags=re.MULTILINE | re.DOTALL).strip()
    plain = re.sub(r"[#*_`\[\]()]", "", body)
    words = plain.lower().split()
    if not words:
        return QAResult("No keyword stuffing", 5, 5, "No body text found")
    kw_count = sum(1 for w in words if w in keyword.lower())
    density = kw_count / len(words) * 100
    if density <= 2.0:
        return QAResult("No keyword stuffing", 5, 5, f"Density: {density:.1f}% — OK")
    return QAResult("No keyword stuffing", 0, 5, f"Keyword density: {density:.1f}% — too high (keep under 2%)")


def check_word_count(article_md, metadata):
    body = re.sub(r"^---.*?^---", "", article_md, flags=re.MULTILINE | re.DOTALL).strip()
    plain = re.sub(r"[#*_`\[\]()]", "", body)
    count = len(plain.split())
    target = metadata.get("word_count_target", 1000)
    if count >= target:
        return QAResult("Word count meets minimum", 5, 5, f"{count} words (target: {target})")
    return QAResult("Word count meets minimum", 1, 5, f"{count} words — below target of {target}")


def check_thin_sections(article_md):
    body = re.sub(r"^---.*?^---", "", article_md, flags=re.MULTILINE | re.DOTALL).strip()
    sections = re.split(r"^## .+", body, flags=re.MULTILINE)
    thin = []
    for i, section in enumerate(sections[1:], 1):
        plain = re.sub(r"[#*_`\[\]()]", "", section)
        words = len(plain.split())
        if words < 80:
            thin.append(f"Section {i} ({words} words)")
    if not thin:
        return QAResult("No thin sections (each H2 >80 words)", 5, 5, "All sections have 80+ words")
    return QAResult("No thin sections (each H2 >80 words)", 1, 5, f"Thin sections: {', '.join(thin[:3])}")


def check_india_context(article_md):
    india_terms = ["india", "indian", "₹", "rupee", "inr", "delhi", "mumbai", "bangalore",
                   "chennai", "hyderabad", "gst", "pan india", "across india"]
    body = article_md.lower()
    found = [t for t in india_terms if t in body]
    if len(found) >= 3:
        return QAResult("India-specific context included", 5, 5, f"Found: {', '.join(found[:5])}")
    return QAResult("India-specific context included", 2, 5, f"Only {len(found)} India-specific terms found")


def check_faq(article_md):
    faq_match = re.search(r"## .*(faq|frequently asked|questions).*", article_md, re.IGNORECASE)
    if not faq_match:
        return [
            QAResult("FAQ section with ≥5 questions", 0, 3, "No FAQ section found"),
            QAResult("FAQ answers 50–100 words each", 0, 2, "No FAQ section found"),
        ]
    faq_start = faq_match.start()
    faq_content = article_md[faq_start:]
    questions = re.findall(r"^### .+", faq_content, re.MULTILINE)
    q_score = 3 if len(questions) >= 5 else 1
    q_result = QAResult("FAQ section with ≥5 questions", q_score, 3, f"{len(questions)} questions found")

    # Check answer lengths (rough estimate)
    answers = re.split(r"^### .+", faq_content, flags=re.MULTILINE)[1:]
    short = sum(1 for a in answers if len(a.split()) < 40 or len(a.split()) > 150)
    a_score = 2 if short == 0 else 1 if short <= 2 else 0
    a_result = QAResult("FAQ answers 50–100 words each", a_score, 2, f"{short} answers outside range" if short else "OK")

    return [q_result, a_result]


def check_internal_links(article_md):
    links = re.findall(r"\[INTERNAL LINK[^\]]*\]|\[#TODO-INTERNAL-LINK[^\]]*\]|href=\"#TODO-INTERNAL", article_md)
    if len(links) >= 3:
        return QAResult("≥3 internal link placeholders", 5, 5, f"{len(links)} placeholders found")
    return QAResult("≥3 internal link placeholders", 2, 5, f"Only {len(links)} internal link placeholders — need 3+")


def check_cta_blocks(article_md):
    ctas = re.findall(r"\[CTA BLOCK[^\]]*\]", article_md, re.IGNORECASE)
    if len(ctas) >= 2:
        q_result = QAResult("≥2 CTA blocks", 3, 3, f"{len(ctas)} CTA blocks found")
    else:
        q_result = QAResult("≥2 CTA blocks", 1, 3, f"Only {len(ctas)} CTA block(s) — need at least 2")

    # Check CTA copy quality (basic heuristic)
    cta_texts = " ".join(ctas).lower()
    action_words = ["browse", "shop", "get", "contact", "explore", "view", "buy", "quote"]
    found_action = any(w in cta_texts for w in action_words)
    a_result = QAResult("CTA copy is compelling", 2 if found_action else 1, 2,
                        "Action word found" if found_action else "Add action words (Browse, Get, Shop, etc.)")
    return [q_result, a_result]


def check_html_quality(article_html):
    results = []

    # No html/head/body tags
    bad_tags = re.findall(r"<(html|head|body)[\s>]", article_html, re.IGNORECASE)
    results.append(QAResult("No html/head/body tags in HTML", 0 if bad_tags else 2, 2,
                            f"Found: {bad_tags}" if bad_tags else "OK"))

    # No H1 in HTML
    h1s = re.findall(r"<h1[\s>]", article_html, re.IGNORECASE)
    results.append(QAResult("No H1 in HTML", 0 if h1s else 2, 2,
                            f"Found {len(h1s)} H1(s)" if h1s else "OK"))

    # No external CSS links
    ext_css = re.findall(r'<link[^>]+rel=["\']stylesheet', article_html, re.IGNORECASE)
    results.append(QAResult("Inline CSS only (no external stylesheets)", 0 if ext_css else 2, 2,
                            "External stylesheet found — use inline CSS only" if ext_css else "OK"))

    # CTA blocks styled
    cta_blocks = re.findall(r'background:\s*#0057b7', article_html)
    results.append(QAResult("CTA blocks styled correctly", 2 if cta_blocks else 0, 2,
                            f"{len(cta_blocks)} styled CTA block(s)" if cta_blocks else "CTA blocks missing Innova blue (#0057b7)"))

    # Mobile wrapper
    wrapper = re.search(r'max-width:\s*800px', article_html)
    results.append(QAResult("Mobile wrapper div present", 2 if wrapper else 0, 2,
                            "OK" if wrapper else "Add max-width: 800px wrapper div"))

    return results


def check_cannibalization(metadata, content_index):
    primary_kw = metadata.get("primary_keyword", "").lower()
    blog_id = metadata.get("blog_id", "")
    kw_words = set(primary_kw.split())
    issues = []

    for blog in content_index.get("blogs", []):
        if blog.get("blog_id") == blog_id:
            continue
        existing_kw = blog.get("primary_keyword", "").lower()
        existing_words = set(existing_kw.split())
        if not existing_words:
            continue
        overlap = kw_words & existing_words
        pct = len(overlap) / max(len(kw_words), 1)
        if pct >= 0.7:
            issues.append(f"'{blog.get('title') or blog.get('primary_keyword')}' ({int(pct*100)}% overlap)")

    if not issues:
        return QAResult("Cannibalization check", 0, 0, "No overlap detected")
    return QAResult("Cannibalization check", -10, 0, f"RISK: {'; '.join(issues)}")


def build_report(slug, checks, cannibalization, metadata):
    total = sum(c.score for c in checks)
    max_total = sum(c.max_score for c in checks)
    cannibal_penalty = cannibalization.score if cannibalization.score < 0 else 0
    final_score = max(0, total + cannibal_penalty)
    status = "APPROVED" if final_score >= MIN_SCORE else "NEEDS REVISION"

    lines = [
        f"# QA Report: {metadata.get('title') or metadata.get('primary_keyword', slug).title()}",
        f"",
        f"**Keyword:** {metadata.get('primary_keyword', '')}",
        f"**Slug:** {metadata.get('slug', '')}",
        f"**QA Date:** {datetime.now().strftime('%Y-%m-%d')}",
        f"**Reviewer:** qa_checker.py (automated)",
        f"",
        f"---",
        f"",
        f"## Final Score: {final_score} / {max_total}",
        f"",
        f"**Status: {status}**",
        f"",
        f"> Minimum passing score: {MIN_SCORE}/100",
        f"",
        f"---",
        f"",
        f"## Score Breakdown",
        f"",
        f"| Check | Score | Max | Notes |",
        f"|-------|-------|-----|-------|",
    ]

    issues = []
    for c in checks:
        lines.append(f"| {c.check} | {c.score} | {c.max_score} | {c.notes} |")
        if not c.passed() and c.max_score > 0:
            issues.append(f"- **{c.check}**: {c.notes}")

    if cannibalization.score < 0:
        lines.append(f"| Cannibalization penalty | {cannibalization.score} | 0 | {cannibalization.notes} |")
        issues.append(f"- **Cannibalization**: {cannibalization.notes}")

    lines += [
        f"| **TOTAL** | **{final_score}** | **{max_total}** | |",
        f"",
        f"---",
        f"",
        f"## Cannibalization Check",
        f"",
        cannibalization.notes,
        f"",
        f"---",
        f"",
        f"## Issues Found",
        f"",
    ]

    if issues:
        lines.extend(issues)
    else:
        lines.append("No issues found.")

    lines += [
        f"",
        f"---",
        f"",
        f"## Next Steps",
        f"",
        f"- [ ] Create `shopify-draft.json` (Step 9)" if status == "APPROVED" else "- [ ] Fix issues above and re-run QA",
        f"- [ ] Commit all blog files to GitHub (Step 10)",
    ]

    return "\n".join(lines), final_score, status


def main():
    parser = argparse.ArgumentParser(description="Run SEO QA check on a blog draft")
    parser.add_argument("--slug", required=True, help="Blog slug (folder name under blogs/drafts/)")
    args = parser.parse_args()

    slug = args.slug.strip("/")
    blog_dir = BLOGS_DIR / slug

    if not blog_dir.exists():
        print(f"ERROR: Blog folder not found: {blog_dir}")
        print(f"Run: python scripts/blog_folder_creator.py --keyword \"your keyword\"")
        raise SystemExit(1)

    print(f"Running QA for: {slug}")

    article_md = load_file(blog_dir / "article.md")
    article_html = load_file(blog_dir / "article.html")
    metadata = load_json(blog_dir / "metadata.json")
    content_index = load_json(CONTENT_INDEX_PATH)

    keyword = metadata.get("primary_keyword", "")
    if not keyword:
        print("WARNING: primary_keyword not set in metadata.json — some checks will be skipped")

    checks = []

    checks.append(check_meta_title(metadata))
    checks.append(check_meta_description(metadata))
    checks.append(check_slug(metadata))
    checks.append(check_single_h1_in_md(article_md))
    checks.append(check_no_h1_in_html(article_html))
    checks.append(check_heading_hierarchy(article_md))

    if keyword:
        checks.append(check_keyword_in_h1(article_md, keyword))
        checks.append(check_keyword_in_first_100_words(article_md, keyword))
        checks.append(check_keyword_in_h2s(article_md, keyword))
        checks.append(check_keyword_in_conclusion(article_md, keyword))
        checks.append(check_secondary_keywords(article_md, metadata))
        checks.append(check_keyword_stuffing(article_md, keyword))

    checks.append(check_word_count(article_md, metadata))
    checks.append(check_thin_sections(article_md))
    checks.append(check_india_context(article_md))
    checks.extend(check_faq(article_md))
    checks.append(check_internal_links(article_md))
    checks.extend(check_cta_blocks(article_md))
    checks.extend(check_html_quality(article_html))

    cannibalization = check_cannibalization(metadata, content_index)
    report_text, final_score, status = build_report(slug, checks, cannibalization, metadata)

    report_path = blog_dir / "qa-report.md"
    report_path.write_text(report_text, encoding="utf-8")

    print(f"\nQA Score: {final_score}/100 — {status}")
    print(f"Report saved: {report_path}")

    if status == "APPROVED":
        print("\nNext: Run Step 9 — Shopify Draft (prompts/shopify-draft-prompt.md)")
    else:
        print(f"\nScore below {MIN_SCORE}. Fix the issues above, then re-run:")
        print(f"  python scripts/qa_checker.py --slug {slug}")


if __name__ == "__main__":
    main()
