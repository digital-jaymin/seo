#!/usr/bin/env python3
"""
tests/test_sitemap_refresh.py
Unit tests for sitemap_refresh.py — all HTTP is mocked (no live requests).

Run:  pytest tests/test_sitemap_refresh.py -v
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Allow importing from scripts/
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import sitemap_refresh as sr  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

VALID_URLSET_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://innovaretail.co.in/blogs/insights/post-one</loc>
    <lastmod>2026-01-01</lastmod>
  </url>
  <url>
    <loc>https://innovaretail.co.in/blogs/insights/post-two</loc>
    <lastmod>2026-02-01</lastmod>
  </url>
</urlset>"""

HTML_ERROR_RESPONSE = b"""<!DOCTYPE html>
<html>
<head><title>Error</title></head>
<body><h1>404 Not Found</h1></body>
</html>"""

COLLECTIONS_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://innovaretail.co.in/collections/gaming-laptops</loc>
    <lastmod>2026-01-01</lastmod>
  </url>
  <url>
    <loc>https://innovaretail.co.in/collections/office-laptops</loc>
    <lastmod>2026-01-01</lastmod>
  </url>
</urlset>"""

DUPLICATE_URLS_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://innovaretail.co.in/products/hp-laptop</loc></url>
  <url><loc>https://innovaretail.co.in/products/hp-laptop</loc></url>
  <url><loc>https://innovaretail.co.in/products/hp-laptop</loc></url>
</urlset>"""


def _make_response(content: bytes, status_code: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.content = content
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        from requests.exceptions import HTTPError
        resp.raise_for_status.side_effect = HTTPError(response=resp)
    return resp


# ---------------------------------------------------------------------------
# Test 1: Valid XML is parsed correctly
# ---------------------------------------------------------------------------

def test_parse_valid_xml():
    entries = sr.parse_urls(VALID_URLSET_XML)
    assert len(entries) == 2
    assert entries[0]["url"] == "https://innovaretail.co.in/blogs/insights/post-one"
    assert entries[0]["lastmod"] == "2026-01-01"
    assert entries[1]["url"] == "https://innovaretail.co.in/blogs/insights/post-two"


# ---------------------------------------------------------------------------
# Test 2: HTML error response is rejected with ValueError
# ---------------------------------------------------------------------------

def test_html_error_response_rejected():
    with patch("sitemap_refresh.requests.get") as mock_get:
        mock_get.return_value = _make_response(HTML_ERROR_RESPONSE, 200)
        with pytest.raises((ValueError, SystemExit)):
            sr.fetch_xml("https://innovaretail.co.in/sitemap_blogs_1.xml")


# ---------------------------------------------------------------------------
# Test 3: Timeout triggers retry and eventually sys.exit
# ---------------------------------------------------------------------------

def test_timeout_causes_exit():
    import requests as req_lib

    with patch("sitemap_refresh.requests.get") as mock_get:
        mock_get.side_effect = req_lib.exceptions.Timeout("timed out")
        with patch("sitemap_refresh.time.sleep"):  # speed up test
            with pytest.raises(SystemExit):
                sr.fetch_xml("https://innovaretail.co.in/sitemap_blogs_1.xml", retries=2)

    assert mock_get.call_count == 2


# ---------------------------------------------------------------------------
# Test 4: Duplicate URLs are deduplicated by parse_urls
# ---------------------------------------------------------------------------

def test_duplicate_urls_deduplicated():
    entries = sr.parse_urls(DUPLICATE_URLS_XML)
    assert len(entries) == 1
    assert entries[0]["url"] == "https://innovaretail.co.in/products/hp-laptop"


# ---------------------------------------------------------------------------
# Test 5: Changed sitemap produces non-empty diff
# ---------------------------------------------------------------------------

def test_diff_detects_changes():
    prev = [
        {"url": "https://innovaretail.co.in/blogs/insights/old-post", "lastmod": ""},
    ]
    curr = [
        {"url": "https://innovaretail.co.in/blogs/insights/old-post", "lastmod": ""},
        {"url": "https://innovaretail.co.in/blogs/insights/new-post", "lastmod": ""},
    ]
    diff = sr.compute_diff(prev, curr)
    assert "https://innovaretail.co.in/blogs/insights/new-post" in diff["added"]
    assert diff["removed"] == []


# ---------------------------------------------------------------------------
# Test 6: Unchanged sitemap produces empty diff
# ---------------------------------------------------------------------------

def test_diff_no_changes():
    entries = [
        {"url": "https://innovaretail.co.in/products/hp-victus", "lastmod": ""},
        {"url": "https://innovaretail.co.in/products/hp-omen",   "lastmod": ""},
    ]
    diff = sr.compute_diff(entries, entries)
    assert diff["added"]   == []
    assert diff["removed"] == []


# ---------------------------------------------------------------------------
# Test 7: Content-gap finder skips collections already covered by blogs
# ---------------------------------------------------------------------------

def test_content_gap_skips_covered_collections():
    blog_entries = [
        {"url": "https://innovaretail.co.in/blogs/insights/gaming-laptops-guide"},
    ]
    collection_entries = [
        {"url": "https://innovaretail.co.in/collections/gaming-laptops"},
        {"url": "https://innovaretail.co.in/collections/office-laptops"},
    ]

    # Patch KW_CSV to not exist so load_existing_keyword_slugs returns empty set
    with patch.object(sr, "KW_CSV", Path("/nonexistent/path.csv")):
        gaps = sr.find_content_gaps(blog_entries, collection_entries)

    # gaming-laptops is covered (slug appears in blog URL), office-laptops is not
    gap_slugs = {g["collection_slug"] for g in gaps}
    assert "gaming-laptops" not in gap_slugs
    assert "office-laptops" in gap_slugs
