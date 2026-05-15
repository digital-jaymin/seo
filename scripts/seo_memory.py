#!/usr/bin/env python3
"""
seo_memory.py
Persistent SEO memory system for Innova Retail.

Loads and indexes all site data (sitemap, content-index, keywords,
selected-topics, collections, blogs) before any recommendation is made.
All other scripts import from this module.

Rules enforced:
- Collection pages own transactional keywords (never duplicate in blogs)
- Blog topics must support a collection, not compete with one
- Every recommendation requires: target_page_type, parent_cluster,
  supported_collection_page, cannibalization_risk, internal_link_targets
- Cannibalization is checked against existing blogs AND collection pages
"""

import csv
import json
import re
from pathlib import Path
from datetime import datetime

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
SITEMAP_JSON     = ROOT / "data/sitemap/sitemap-urls.json"
CONTENT_INDEX    = ROOT / "data/content-database/content-index.json"
KEYWORDS_CSV     = ROOT / "data/keywords/keyword-opportunities.csv"
SELECTED_TOPICS  = ROOT / "data/keywords/selected-topics.json"
COLLECTIONS_TXT  = ROOT / "data/sitemap/collections-urls.txt"
BLOG_URLS_TXT    = ROOT / "data/sitemap/blog-urls.txt"
TOPICAL_MAP      = ROOT / "data/topical-authority/topical-authority-map.json"


class SEOMemory:
    """
    Central memory store. Load once per workflow run.
    All recommendation checks run through this object.
    """

    def __init__(self):
        self.sitemap        = {}
        self.content_index  = {"blogs": []}
        self.keywords       = {}       # keyword_lower → row dict
        self.selected       = {}
        self.collection_urls = set()   # bare slugs, e.g. "gaming-laptops"
        self.blog_slugs     = set()    # bare slugs from published blogs
        self.clusters       = {}       # cluster_name → {pillar, spokes, collections, gaps}
        self.topical_map    = {}
        self._loaded        = False

    # ── Loaders ───────────────────────────────────────────────────────────

    def load(self):
        self._load_sitemap()
        self._load_content_index()
        self._load_keywords()
        self._load_selected_topics()
        self._load_collection_urls()
        self._load_blog_urls()
        self._load_topical_map()
        self._build_cluster_index()
        self._loaded = True
        return self

    def _load_sitemap(self):
        if SITEMAP_JSON.exists():
            with open(SITEMAP_JSON) as f:
                self.sitemap = json.load(f)

    def _load_content_index(self):
        if CONTENT_INDEX.exists():
            with open(CONTENT_INDEX) as f:
                self.content_index = json.load(f)

    def _load_keywords(self):
        if KEYWORDS_CSV.exists():
            with open(KEYWORDS_CSV, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    key = row.get("keyword", "").lower().strip()
                    if key:
                        self.keywords[key] = row

    def _load_selected_topics(self):
        if SELECTED_TOPICS.exists():
            with open(SELECTED_TOPICS) as f:
                self.selected = json.load(f)

    def _load_collection_urls(self):
        if COLLECTIONS_TXT.exists():
            for line in COLLECTIONS_TXT.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    slug = line.rstrip("/").split("/collections/")[-1]
                    self.collection_urls.add(slug)

    def _load_blog_urls(self):
        if BLOG_URLS_TXT.exists():
            for line in BLOG_URLS_TXT.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    slug = line.rstrip("/").split("/blogs/insights/")[-1]
                    self.blog_slugs.add(slug)

    def _load_topical_map(self):
        if TOPICAL_MAP.exists():
            with open(TOPICAL_MAP) as f:
                self.topical_map = json.load(f)

    def _build_cluster_index(self):
        """Index blogs by cluster from content-index."""
        for blog in self.content_index.get("blogs", []):
            cluster = blog.get("cluster", "Uncategorized")
            if cluster not in self.clusters:
                self.clusters[cluster] = {
                    "pillar": None,
                    "spokes": [],
                    "collection_pages": [],
                    "gap_articles": [],
                    "blog_count": 0,
                }
            self.clusters[cluster]["blog_count"] += 1
            if blog.get("status") == "published":
                self.clusters[cluster]["spokes"].append(blog.get("slug", ""))

        # Load collection pages per cluster from topical map
        for cluster, data in self.topical_map.get("clusters", {}).items():
            if cluster not in self.clusters:
                self.clusters[cluster] = {
                    "pillar": None, "spokes": [], "collection_pages": [],
                    "gap_articles": [], "blog_count": 0,
                }
            self.clusters[cluster]["collection_pages"] = data.get("collection_pages", [])
            self.clusters[cluster]["pillar"] = data.get("pillar_blog", None)
            self.clusters[cluster]["gap_articles"] = data.get("gap_articles", [])

    # ── Core memory checks ─────────────────────────────────────────────────

    def is_collection_owned(self, keyword: str) -> dict:
        """
        Returns match info if keyword is transactional and belongs to a
        collection page. Blogs should NOT target these directly.

        Returns: {"owned": bool, "collection_slug": str, "reason": str}
        """
        kw = keyword.lower().strip()
        transactional_signals = [
            "under 70000", "under 1 lakh", "under 40000", "under 50000",
            "under 60000", "under 80000", "under 1lakh", "best gaming laptop",
            "best business laptop", "buy", "price list", "shop",
        ]
        collection_keyword_map = {
            "best-laptop-under-40000": ["under 40000", "under 40k"],
            "best-laptop-under-50000": ["under 50000", "under 50k"],
            "best-laptop-under-60000": ["under 60000", "under 60k"],
            "best-gaming-laptop-under-70000": ["gaming laptop under 70000", "gaming under 70000", "gaming under 70k"],
            "best-gaming-laptop-under-1-lakh": ["gaming laptop under 1 lakh", "gaming under 1 lakh", "gaming under 1lakh"],
            "gaming-laptops": ["best gaming laptop", "gaming laptops india"],
            "business-laptops": ["best business laptop", "business laptops india"],
            "student-laptop": ["best student laptop", "student laptops india"],
            "laptops": ["best laptops india", "laptops under"],
            "smart-lock": ["best smart door lock", "smart lock price"],
            "robotic-vacuum-cleaner": ["best robotic vacuum", "best robot vacuum"],
            "parking-barrier": ["best parking barrier", "automatic parking barrier price"],
        }
        for collection_slug, triggers in collection_keyword_map.items():
            if collection_slug in self.collection_urls:
                for trigger in triggers:
                    if trigger in kw:
                        return {
                            "owned": True,
                            "collection_slug": collection_slug,
                            "reason": f"Transactional keyword matches collection /{collection_slug}. Blogs support this page; they don't compete with it.",
                        }
        return {"owned": False, "collection_slug": None, "reason": ""}

    def check_cannibalization(self, keyword: str, threshold: float = 0.6) -> list[dict]:
        """
        Checks keyword against all published blogs in content-index.
        Returns list of conflict dicts if risk found.
        """
        kw_words = set(keyword.lower().split())
        conflicts = []
        for blog in self.content_index.get("blogs", []):
            primary = blog.get("primary_keyword", "").lower()
            primary_words = set(primary.split())
            overlap = kw_words & primary_words
            if len(primary_words) == 0:
                continue
            overlap_pct = len(overlap) / max(len(kw_words), len(primary_words))
            if overlap_pct >= threshold:
                conflicts.append({
                    "blog_id": blog.get("blog_id"),
                    "title": blog.get("title"),
                    "primary_keyword": primary,
                    "overlap_pct": round(overlap_pct * 100),
                    "status": blog.get("status"),
                })
        return conflicts

    def get_supported_collection(self, cluster: str) -> list[str]:
        """Returns collection URLs that support the given cluster."""
        cluster_collection_map = {
            "Gaming Laptops": ["/collections/gaming-laptops", "/collections/hp-victus-gaming-laptop", "/collections/hp-omen-laptop", "/collections/best-gaming-laptop-under-70000", "/collections/best-gaming-laptop-under-1-lakh"],
            "Business IT": ["/collections/business-laptops", "/collections/business-desktops"],
            "HP OmniBook": ["/collections/laptops"],
            "Laptop Buying Guide — Students": ["/collections/student-laptop", "/collections/laptops"],
            "Laptop Buying Guide — Professional": ["/collections/business-laptops"],
            "Laptop How-To": ["/collections/laptops"],
            "Printers": ["/collections/printers", "/collections/home-office-printers", "/collections/laser-printers", "/collections/wireless-printers"],
            "Large Format Printers": ["/collections/large-format-printer"],
            "ELV Products": ["/collections/smart-lock", "/collections/robotic-vacuum-cleaner", "/collections/parking-barrier", "/collections/dahua", "/collections/elv-appliances"],
            "ELV Cleaning Robots": ["/collections/robotic-vacuum-cleaner"],
            "ELV Parking Barriers": ["/collections/parking-barrier"],
            "ELV Dahua": ["/collections/dahua"],
            "Accessories": ["/collections/accessories", "/collections/laptop-bags", "/collections/mouse-keyboard", "/collections/audio-headsets", "/collections/chargers-cable", "/collections/usb-drives"],
            "Desktops AIO": ["/collections/all-in-one", "/collections/desktops", "/collections/business-desktops"],
            "Local SEO": ["/pages/hp-world-navrangpura", "/pages/hp-world-maninagar", "/pages/hp-world-chandkheda", "/pages/hp-world-prahlad-nagar", "/pages/hp-world-vastral", "/pages/hp-world-rajkot-tagore-road"],
            "Services": ["/pages/laptop-service"],
            "Tech Guide": ["/collections/laptops"],
            "Price Guide": ["/collections/best-laptop-under-40000", "/collections/best-laptop-under-50000", "/collections/best-laptop-under-60000"],
        }
        return cluster_collection_map.get(cluster, [])

    def get_internal_link_targets(self, cluster: str, keyword: str) -> list[str]:
        """
        Returns list of existing blog slugs and collection URLs
        that should be internally linked from the new article.
        """
        targets = []
        kw_lower = keyword.lower()

        # Same-cluster existing blogs
        for blog in self.content_index.get("blogs", []):
            if blog.get("cluster") == cluster and blog.get("status") == "published":
                targets.append(blog.get("slug", ""))

        # Supporting collections
        targets.extend(self.get_supported_collection(cluster))

        # Pillar article if this is a spoke
        cluster_data = self.clusters.get(cluster, {})
        if cluster_data.get("pillar") and cluster_data["pillar"] not in targets:
            targets.append(cluster_data["pillar"])

        # HP World location pages for local SEO articles
        if any(city in kw_lower for city in ["ahmedabad", "rajkot", "gujarat"]):
            local_pages = [
                "/pages/hp-world-navrangpura", "/pages/hp-world-maninagar",
                "/pages/hp-world-chandkheda", "/pages/hp-world-prahlad-nagar",
                "/pages/hp-world-vastral",
            ]
            if "rajkot" in kw_lower:
                targets.append("/pages/hp-world-rajkot-tagore-road")
            else:
                targets.extend(local_pages)

        return list(dict.fromkeys(targets))  # deduplicate preserving order

    def determine_target_page_type(self, keyword: str, intent: str) -> str:
        """
        Determines whether a keyword should be a blog or a collection.
        Returns: "blog" | "collection" | "product_page"
        """
        collection_check = self.is_collection_owned(keyword)
        if collection_check["owned"]:
            return "collection"

        kw = keyword.lower()
        if any(sig in kw for sig in ["how to", "what is", "why", "guide", "tips", "vs", "review", "best"]):
            return "blog"
        if intent.lower() in ["commercial", "transactional"]:
            collection_check2 = self.is_collection_owned(keyword)
            if collection_check2["owned"]:
                return "collection"

        return "blog"

    def validate_topic(self, keyword: str, cluster: str, intent: str) -> dict:
        """
        Full memory validation for a proposed blog topic.
        Returns structured result with all required memory fields.
        """
        conflicts      = self.check_cannibalization(keyword)
        collection_own = self.is_collection_owned(keyword)
        target_type    = self.determine_target_page_type(keyword, intent)
        collections    = self.get_supported_collection(cluster)
        link_targets   = self.get_internal_link_targets(cluster, keyword)

        cannibalization_risk = "none"
        if conflicts:
            high_risk = [c for c in conflicts if c["overlap_pct"] >= 80]
            cannibalization_risk = "high" if high_risk else "medium"
        elif collection_own["owned"]:
            cannibalization_risk = "collection_conflict"

        approved = (
            target_type == "blog"
            and cannibalization_risk not in ("high", "collection_conflict")
        )

        return {
            "keyword": keyword,
            "cluster": cluster,
            "intent": intent,
            "target_page_type": target_type,
            "parent_cluster": cluster,
            "supported_collection_page": collections[0] if collections else None,
            "all_supported_collections": collections,
            "cannibalization_risk": cannibalization_risk,
            "cannibalization_conflicts": conflicts,
            "collection_ownership": collection_own,
            "internal_link_targets": link_targets,
            "approved_for_blog": approved,
            "rejection_reason": (
                collection_own["reason"] if collection_own["owned"]
                else f"Cannibalization with: {[c['title'] for c in conflicts]}" if not approved
                else None
            ),
        }

    # ── Summary report for Claude context ─────────────────────────────────

    def generate_memory_report(self) -> str:
        """
        Generates a text summary of current SEO memory state.
        Inject this into Claude prompts to enforce memory rules.
        """
        blogs = self.content_index.get("blogs", [])
        published = [b for b in blogs if b.get("status") == "published"]
        drafts    = [b for b in blogs if b.get("status") == "draft"]

        lines = [
            "=== SEO MEMORY SNAPSHOT ===",
            f"Date: {datetime.now().strftime('%Y-%m-%d')}",
            f"Total blogs registered: {len(blogs)} ({len(published)} published, {len(drafts)} draft)",
            f"Collection pages: {len(self.collection_urls)}",
            f"Keyword opportunities tracked: {len(self.keywords)}",
            "",
            "── PUBLISHED BLOG KEYWORDS (DO NOT DUPLICATE) ──",
        ]
        for b in published:
            lines.append(f"  [{b.get('cluster','?')}] {b.get('primary_keyword','?')} → {b.get('slug','?')}")

        lines += [
            "",
            "── DRAFT BLOG KEYWORDS (IN PROGRESS) ──",
        ]
        for b in drafts:
            lines.append(f"  [{b.get('cluster','?')}] {b.get('primary_keyword','?')} → {b.get('slug','?')}")

        lines += [
            "",
            "── COLLECTION PAGES (OWN TRANSACTIONAL KEYWORDS) ──",
        ]
        for slug in sorted(self.collection_urls):
            lines.append(f"  /collections/{slug}")

        gaps = self.sitemap.get("content_gaps", [])
        lines += [
            "",
            f"── CONTENT GAPS ({len(gaps)} identified) ──",
        ]
        for g in gaps:
            lines.append(f"  [{g.get('priority','?')}] {g.get('cluster','?')}: {g.get('gap','?')}")

        lines += [
            "",
            "── MEMORY RULES IN EFFECT ──",
            "1. Never suggest a topic already covered by a published blog",
            "2. Never suggest a transactional keyword owned by a collection page",
            "3. Every blog must support a collection (informational/comparison/guide intent only)",
            "4. Every topic must include: target_page_type, parent_cluster,",
            "   supported_collection_page, cannibalization_risk, internal_link_targets",
            "5. Topics must strengthen topical authority — no isolated blog ideas",
            "=== END SEO MEMORY ===",
        ]
        return "\n".join(lines)

    # ── Topical authority map updater ──────────────────────────────────────

    def update_topical_map(self, new_blog: dict):
        """Called after a new blog is created to update the topical authority map."""
        if not TOPICAL_MAP.exists():
            return
        cluster = new_blog.get("cluster", "Uncategorized")
        data = self.topical_map.get("clusters", {}).get(cluster, {})
        if new_blog.get("is_pillar"):
            data["pillar_blog"] = new_blog.get("slug")
        else:
            spokes = data.get("spoke_blogs", [])
            slug = new_blog.get("slug")
            if slug and slug not in spokes:
                spokes.append(slug)
            data["spoke_blogs"] = spokes

        data["blog_count"] = data.get("blog_count", 0) + 1
        data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        self.topical_map.setdefault("clusters", {})[cluster] = data
        self.topical_map["_meta"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        TOPICAL_MAP.parent.mkdir(parents=True, exist_ok=True)
        with open(TOPICAL_MAP, "w") as f:
            json.dump(self.topical_map, f, indent=2)


def load_memory() -> SEOMemory:
    """Convenience function — call this at the top of any script."""
    return SEOMemory().load()


if __name__ == "__main__":
    memory = load_memory()
    print(memory.generate_memory_report())
    print(f"\nLoaded {len(memory.keywords)} keywords, {len(memory.blog_slugs)} blog slugs, {len(memory.collection_urls)} collections")
