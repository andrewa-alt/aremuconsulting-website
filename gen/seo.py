"""Shared, build-time SEO for both page builders. No browser dependencies.

Editorial metadata lives in content/site.json and each post/project's seo field.
URLs follow Vercel cleanUrls; /case-studies is an alias for /projects, not a page.
Sources: https://vercel.com/docs/project-configuration/vercel-json#cleanurls
https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls
https://ogp.me/ and https://schema.org/LocalBusiness
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://www.aremuconsulting.com"
SITE_META = json.loads((ROOT / "content/site.json").read_text(encoding="utf-8"))
SHARE_IMAGE = SITE_URL + "/build/assets/logo.png"
BUSINESS = {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "@id": SITE_URL + "/#business",
    "name": "Aremu Consulting Ltd",
    "url": SITE_URL + "/",
    "description": "Solo-builder consultancy in Manchester, UK, providing custom website and app builds, workflow and CRM automation, and custom AI agent development.",
    "founder": {"@type": "Person", "name": "Andrew Aremu"},
    "address": {
        "@type": "PostalAddress",
        "addressLocality": "Manchester",
        "addressCountry": "GB",
    },
}


def canonical_url(path):
    """Map an output filename to its public, extensionless canonical URL."""
    path = path.strip("/")
    if path.endswith(".html"):
        path = path[:-5]
    if path == "index":
        path = ""
    return SITE_URL + "/" + path


def jsonld(value):
    # Escape '<' to prevent editorial text closing the raw-text script element.
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def head_substitutions(meta, path, og_type="website", ld=None):
    """Return escaped HTML tokens; ld is optional page-specific Schema.org data."""
    og = meta.get("og", {})
    title = meta["title"]
    description = meta["description"]
    nodes = [BUSINESS]
    if ld:
        nodes.extend(ld if isinstance(ld, list) else [ld])
    values = {
        "TITLE": title,
        "DESCRIPTION": description,
        "CANONICAL": canonical_url(path),
        "OG_TYPE": og_type,
        "OG_TITLE": og.get("title", title),
        "OG_DESCRIPTION": og.get("description", description),
        "OG_IMAGE": SHARE_IMAGE,
        "OG_IMAGE_ALT": "Aremu Consulting logo",
    }
    substitutions = {"{{" + key + "}}": html.escape(value, quote=True) for key, value in values.items()}
    substitutions["{{JSON_LD}}"] = jsonld(nodes)
    return substitutions
