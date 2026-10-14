#!/usr/bin/env python3
"""Read-only SEO checks: render in memory; never invoke either build entry point."""
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.robotparser import RobotFileParser
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "gen"))
import build
import build_content
from seo import SITE_META, canonical_url, head_substitutions


class Document(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.tags = []
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def render_pages():
    """Exercise builder functions without main(), filesystem writes or regeneration."""
    pages = {name + ".html": build.assemble(name) for name in build.PAGES}
    blog = json.loads((ROOT / "content/blog.json").read_text())
    projects = json.loads((ROOT / "content/projects.json").read_text())
    shots = json.loads((ROOT / "content/screenshots.json").read_text())
    for name, body, ld in [
        ("blog", build_content.blog_index_body(blog), build_content.blog_listing_ld()),
        ("projects", build_content.projects_index_body(projects), build_content.project_listing_ld()),
    ]:
        meta = SITE_META[name]
        pages[name + ".html"] = build_content.page(
            meta["title"], meta["description"], name + ".html", "website", ld, body,
            active_blog=name == "blog", active_projects=name == "projects", meta=meta,
        )
    for kind, items in [("blog", blog), ("project", projects)]:
        for item in items:
            name = kind + "-" + item["slug"] + ".html"
            meta = item["seo"]
            if kind == "blog":
                body = build_content.blog_post_body(item)
                ld = build_content.blog_post_ld(item, canonical_url(name), meta["description"])
            else:
                body = build_content.project_body(item, shots.get(item["slug"], []))
                ld = build_content.project_ld(item, canonical_url(name))
            pages[name] = build_content.page(
                meta["title"], meta["description"], name, "article", ld, body,
                active_blog=kind == "blog", active_projects=kind == "project", meta=meta,
            )
    return pages


def check():
    import re
    pages = render_pages()
    titles, descriptions = set(), set()
    for name, markup in pages.items():
        assert "{{" not in markup, name + ": unresolved token"
        head = markup.split("</head>", 1)[0]
        doc = Document(markup)
        head_doc = Document(head)
        metas = {a.get("name", a.get("property")): a.get("content") for t, a in head_doc.tags if t == "meta"}
        title = re.findall(r"<title>(.*?)</title>", head)
        assert len(title) == 1 and title[0] not in titles, name + ": title"
        titles.add(title[0])
        assert metas["description"] and metas["description"] not in descriptions, name + ": description"
        descriptions.add(metas["description"])
        canonical = [a["href"] for t, a in head_doc.tags if t == "link" and a.get("rel") == "canonical"]
        assert canonical == [canonical_url(name)], name + ": canonical"
        assert metas["og:url"] == canonical[0]
        assert metas["twitter:card"] == "summary"
        for key in ["og:title", "og:description", "og:image", "og:image:alt", "twitter:title", "twitter:description", "twitter:image", "twitter:image:alt"]:
            assert metas[key], name + ": " + key
        nodes = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', head).group(1))
        business = [n for n in nodes if n.get("@type") == "LocalBusiness"]
        assert len(business) == 1 and business[0]["name"] == "Aremu Consulting Ltd"
        assert not {"telephone", "email", "openingHours", "openingHoursSpecification"} & business[0].keys()
        assert business[0]["address"]["addressLocality"] == "Manchester"
        headings = [int(t[1]) for t, _ in doc.tags if re.fullmatch("h[1-6]", t)]
        assert headings.count(1) == 1, name + ": h1 count"
        assert all(b <= a + 1 for a, b in zip([0] + headings, headings)), name + ": heading order"
        assert sum(t == "main" and a.get("id") == "main" for t, a in doc.tags) == 1, name + ": landmark"
    sitemap = ElementTree.parse(ROOT / "sitemap.xml")
    urls = [n.text for n in sitemap.findall(".//{*}loc")]
    assert len(urls) == len(set(urls)) == len(pages)
    assert set(urls) == {canonical_url(p) for p in pages}
    robots = RobotFileParser()
    robots.parse((ROOT / "robots.txt").read_text().splitlines())
    assert robots.site_maps() == [canonical_url("sitemap.xml")]
    assert all(robots.can_fetch("*", url) for url in urls)
    assert robots.can_fetch("*", canonical_url("build/assets/logo.png"))
    assert robots.can_fetch("*", canonical_url("build/assets/fonts/Atkinson_Hyperlegible-400.woff2"))
    assert not robots.can_fetch("*", canonical_url("parts/partials/head.html"))
    hostile = head_substitutions({"title": '<tag> "quote"', "description": "</script><script>alert(1)</script>"}, "index.html", ld={"text": "</script>"})
    assert "<tag>" not in hostile["{{TITLE}}"]
    assert "</script>" not in hostile["{{JSON_LD}}"]
    print(f"PASS: {len(pages)} in-memory pages; unique metadata, cards, canonicals, schema, headings, landmarks, sitemap, robots and escaping.")


if __name__ == "__main__":
    check()
