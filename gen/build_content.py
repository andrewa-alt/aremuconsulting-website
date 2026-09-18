#!/usr/bin/env python3
"""Generate Aremu's Blog + Projects (case studies) content pages.

Reuses the notebook design shell (tokens.json, self-hosted fonts, styles.css,
shared header/footer) and writes flat files to the project root so every
relative link + font URL resolves identically to the 4 core pages:

    blog.html              blog index
    blog-<slug>.html       14 blog posts
    projects.html          5 real projects (index)
    project-<slug>.html    project detail + gallery

Also emits sitemap.xml, robots.txt, and vercel.json (cleanUrls + redirects
from the old Next.js /blog, /case-studies, /lab, /consultation routes).

Run after:  python3 gen/extract_content.py   (blog.json)
           python3 gen/build_projects.py     (projects.json)
           python3 gen/copy_screenshots.py   (images + logo + screenshots.json)
Run:        python3 gen/build_content.py
"""
import json
import os
import re
import html as H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = os.path.join(ROOT, "parts")
CONTENT = os.path.join(ROOT, "content")
PARTIAL_DIR = os.path.join(PARTS, "partials")
FONTS = os.path.join(ROOT, "build", "assets", "fonts")

SITE_URL = "https://www.aremuconsulting.com"


def read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return fh.read()


def load_tokens():
    data = json.loads(read(os.path.join(PARTS, "tokens.json")))
    lines = [":root {"]
    for k, v in data["colors"].items():
        lines.append(f"  --{k}: {v};")
    lines.append("  --measure: " + data.get("measure", "68ch") + ";")
    lines.append("  --font-display: " + data["fonts"]["display"] + ";")
    lines.append("  --font-body: " + data["fonts"]["body"] + ";")
    lines.append("  --font-mono: " + data["fonts"]["mono"] + ";")
    lines.append("}")
    return "\n".join(lines)


def font_faces():
    families = {
        "Atkinson Hyperlegible": ["Atkinson_Hyperlegible-400.woff2", "Atkinson_Hyperlegible-700.woff2"],
        "Martian Mono": ["Martian_Mono-400.woff2", "Martian_Mono-500.woff2", "Martian_Mono-700.woff2"],
    }
    out = []
    if not os.path.isdir(FONTS):
        return ""
    for family, files in families.items():
        for fname in files:
            weight = fname.split("-")[-1][:-6]
            out.append(
                f"@font-face {{ font-family: '{family}'; font-style: normal; "
                f"font-weight: {weight}; font-display: swap; "
                f"src: url('build/assets/fonts/{fname}') format('woff2'); }}"
            )
    return "\n".join(out)


def full_css():
    return load_tokens() + "\n" + font_faces() + "\n" + read(os.path.join(PARTS, "styles.css"))


def plain_text(fragment):
    t = re.sub(r"<[^>]+>", " ", fragment or "")
    t = H.unescape(t)
    return re.sub(r"\s+", " ", t).strip()


def excerpt(fragment, limit=160):
    t = plain_text(fragment)
    if len(t) <= limit:
        return t
    return t[: limit].rsplit(" ", 1)[0].rstrip(".,;:") + "…"


def jsonld(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def build_head(title, description, canonical_path, og_type, ld):
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{H.escape(title)}</title>\n"
        f"<meta name=\"description\" content=\"{H.escape(description, quote=True)}\">\n"
        f"<link rel=\"canonical\" href=\"{SITE_URL}/{canonical_path}\">\n"
        f"<meta property=\"og:type\" content=\"{og_type}\">\n"
        f"<meta property=\"og:title\" content=\"{H.escape(title, quote=True)}\">\n"
        f"<meta property=\"og:description\" content=\"{H.escape(description, quote=True)}\">\n"
        f"<meta property=\"og:url\" content=\"{SITE_URL}/{canonical_path}\">\n"
        "<meta name=\"og:site_name\" content=\"Aremu Consulting\">\n"
        f"<script type=\"application/ld+json\">{ld}</script>\n"
        "<style>\n" + full_css() + "\n</style>\n</head>\n<body>\n"
        "<a class=\"skip-link\" href=\"#main\">Skip to content</a>\n"
    )


def build_header(active_blog=False, active_projects=False):
    h = read(os.path.join(PARTIAL_DIR, "header.html"))
    subs = {
        "{{ACTIVE_INDEX}}": "",
        "{{ACTIVE_SERVICES}}": "",
        "{{ACTIVE_APPROACH}}": "",
        "{{ACTIVE_PROJECTS}}": ' class="active"' if active_projects else "",
        "{{ACTIVE_BLOG}}": ' class="active"' if active_blog else "",
        "{{ACTIVE_CONTACT}}": "",
    }
    for k, v in subs.items():
        h = h.replace(k, v)
    return h


def build_footer():
    f = read(os.path.join(PARTIAL_DIR, "footer.html"))
    return f.replace("{{YEAR}}", "2026")


ORG = {
    "@type": "Organization",
    "name": "Aremu Consulting Ltd",
    "url": SITE_URL,
    "founder": {"@type": "Person", "name": "Andrew Aremu"},
    "address": {"@type": "PostalAddress", "addressLocality": "Manchester", "addressCountry": "GB"},
}


def person():
    return {"@type": "Person", "name": "Andrew Aremu"}


def blog_listing_ld():
    return jsonld([{
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Field notes — Aremu Consulting",
        "description": "Automation, AI agents, and workflows for operators.",
        "url": f"{SITE_URL}/blog.html",
        "isPartOf": ORG,
    }])


def blog_post_ld(post, url, description):
    return jsonld([{
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post["title"],
        "description": description,
        "datePublished": post["date"],
        "author": person(),
        "publisher": ORG,
        "mainEntityOfPage": url,
        "articleSection": post["category"],
    }])


def project_listing_ld():
    return jsonld([{
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Selected work — Aremu Consulting",
        "description": "Systems built for real operations — projects and the tools behind them.",
        "url": f"{SITE_URL}/projects.html",
        "isPartOf": ORG,
    }])


def project_ld(proj, url):
    return jsonld([{
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": proj["title"],
        "description": proj["description"],
        "author": person(),
        "publisher": ORG,
        "mainEntityOfPage": url,
        "articleSection": "Project",
    }])


def page(title, description, canonical, og_type, ld, body, active_blog=False, active_projects=False):
    return build_head(title, description, canonical, og_type, ld) + \
        build_header(active_blog=active_blog, active_projects=active_projects) + body + build_footer()


# ---------------------------------------------------------------------------
# Bodies
# ---------------------------------------------------------------------------
def format_date(d):
    if not d:
        return ""
    try:
        y, m, dd = d.split("-")
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return f"{int(dd)} {months[int(m)-1]} {y}"
    except Exception:
        return d


def blog_index_body(posts):
    rows = []
    for p in sorted(posts, key=lambda x: x["date"], reverse=True):
        ext = excerpt(p["body"]) if excerpt(p["body"]) else p["description"]
        rows.append(
            '<li class="entry">'
            f'<p class="post-meta"><span class="cat">{H.escape(p["category"])}</span>'
            f'<span>{format_date(p["date"])}</span></p>'
            f'<h2 class="entry-title"><a href="blog-{H.escape(p["slug"])}.html">{H.escape(p["title"])}</a></h2>'
            f'<p class="entry-excerpt">{H.escape(ext)}</p>'
            "</li>"
        )
    return (
        '<main id="main" class="page">'
        '<div class="hero"><div class="hero-inner">'
        "<h1>Field notes</h1>"
        '<p class="lede">Automation, AI agents, and the workflows that give you your week back — written for operators, not tool vendors.</p>'
        "</div></div>"
        '<div class="page-inner"><ol class="post-list">'
        + "".join(rows)
        + "</ol>"
        '<p class="disclosure">Figures referenced across these notes are illustrative estimates for a typical business — not audited client results.</p>'
        "</div></main>"
    )


def blog_post_body(p):
    return (
        '<main id="main" class="page"><div class="page-inner"><article>'
        '<header class="post-head">'
        f'<p class="post-meta"><span class="cat">{H.escape(p["category"])}</span><span>{format_date(p["date"])}</span><span>By Andrew Aremu</span></p>'
        f'<h1>{H.escape(p["title"])}</h1>'
        f'<p class="lede">{H.escape(excerpt(p["body"], 200))}</p>'
        "</header>"
        f'<div class="prose">{p["body"]}</div>'
        '<p class="disclosure">This article references illustrative cost figures — estimates for a typical business, not audited client results.</p>'
        '<div class="post-cta"><a class="btn btn-primary" href="contact.html">Schedule Your Project Consultation</a></div>'
        "</article></div></main>"
    )


def projects_index_body(projects):
    rows = []
    for p in projects:
        rows.append(
            '<li class="entry">'
            f'<span class="case-label">{H.escape(p["kind"])}</span>'
            f'<h2 class="entry-title"><a href="project-{H.escape(p["slug"])}.html">{H.escape(p["title"])}</a></h2>'
            f'<p class="entry-excerpt">{H.escape(excerpt(p["body"], 180))}</p>'
            "</li>"
        )
    return (
        '<main id="main" class="page">'
        '<div class="hero"><div class="hero-inner">'
        "<h1>Selected work</h1>"
        '<p class="lede">Systems built for real operations, described in full and shown with their actual screens and product graphics.</p>'
        "</div></div>"
        '<div class="page-inner"><ol class="post-list">'
        + "".join(rows)
        + "</ol></div></main>"
    )


LIGHTBOX_HTML = (
    '<div class="lightbox" role="dialog" aria-modal="true" aria-label="Screenshot viewer" hidden>'
    '<div class="lightbox-backdrop"></div>'
    '<div class="lightbox-panel" role="document">'
    '<div class="lightbox-top">'
    '<span class="lightbox-status" aria-live="polite"></span>'
    '<button type="button" class="lightbox-close" aria-label="Close viewer">Close \u2715</button>'
    '</div>'
    '<div class="lightbox-stage"><img class="lightbox-img" alt=""></div>'
    '<div class="lightbox-nav">'
    '<button type="button" class="gallery-btn lightbox-prev" aria-label="Previous screenshot">\u2190</button>'
    '<span class="lightbox-counter" aria-live="polite"></span>'
    '<button type="button" class="gallery-btn lightbox-next" aria-label="Next screenshot">\u2192</button>'
    '</div>'
    '</div>'
    '</div>'
)


SLIDE_JS = """<script>(function () {
  var g = document.querySelector('.gallery');
  if (!g || !document.querySelector('.lightbox')) return;
  var frame = g.querySelector('.gallery-frame');
  var imgs = Array.prototype.slice.call(frame.querySelectorAll('img'));
  var cap = g.querySelector('.gallery-caption');
  var counter = g.querySelector('.gallery-counter');
  var prev = g.querySelector('.gallery-btn.prev');
  var next = g.querySelector('.gallery-btn.next');
  var n = imgs.length, i = 0;

  var lb = document.querySelector('.lightbox');
  var lbImg = lb.querySelector('.lightbox-img');
  var lbStatus = lb.querySelector('.lightbox-status');
  var lbCounter = lb.querySelector('.lightbox-counter');
  var lbPrev = lb.querySelector('.lightbox-prev');
  var lbNext = lb.querySelector('.lightbox-next');
  var lbClose = lb.querySelector('.lightbox-close');
  var backdrop = lb.querySelector('.lightbox-backdrop');
  var lastFocus = null;

  function render() {
    imgs.forEach(function (img, k) { img.hidden = k !== i; });
    if (cap) cap.textContent = imgs[i].dataset.caption || '';
    if (counter) counter.textContent = (i + 1) + ' / ' + n;
  }
  function renderLightbox() {
    lbImg.src = imgs[i].getAttribute('src');
    lbImg.alt = imgs[i].getAttribute('alt') || '';
    if (lbStatus) lbStatus.textContent = (i + 1) + ' / ' + n + ' · ' + (imgs[i].dataset.caption || '');
    if (lbCounter) lbCounter.textContent = (i + 1) + ' / ' + n;
  }
  function step(d) {
    if (n <= 1) return;
    i = (i + d + n) % n;
    render();
    if (!lb.hidden) renderLightbox();
  }
  function openLightbox() {
    renderLightbox();
    lb.hidden = false;
    lastFocus = document.activeElement;
    if (lbClose) lbClose.focus();
    document.body.style.overflow = 'hidden';
  }
  function closeLightbox() {
    lb.hidden = true;
    document.body.style.overflow = '';
    if (lastFocus) lastFocus.focus();
  }

  if (prev) prev.addEventListener('click', function () { step(-1); });
  if (next) next.addEventListener('click', function () { step(1); });
  if (frame) frame.addEventListener('click', openLightbox);
  if (lbPrev) lbPrev.addEventListener('click', function () { step(-1); });
  if (lbNext) lbNext.addEventListener('click', function () { step(1); });
  if (lbClose) lbClose.addEventListener('click', closeLightbox);
  if (backdrop) backdrop.addEventListener('click', closeLightbox);

  g.addEventListener('keydown', function (e) {
    if (lb.hidden && (e.key === 'ArrowLeft' || e.key === 'ArrowRight')) { step(e.key === 'ArrowLeft' ? -1 : 1); e.preventDefault(); }
  });
  document.addEventListener('keydown', function (e) {
    if (lb.hidden) return;
    if (e.key === 'Escape') { closeLightbox(); }
    else if (e.key === 'ArrowLeft') { step(-1); }
    else if (e.key === 'ArrowRight') { step(1); }
  });

  render();
})();</script>"""


def gallery_html(shots, slug):
    if not shots:
        return ""
    imgs = []
    for i, s in enumerate(shots):
        hidden = "" if i == 0 else " hidden"
        loading = "eager" if i == 0 else "lazy"
        imgs.append(
            f'<img src="build/assets/screenshots/{slug}/{s["file"]}" '
            f'alt="{H.escape(s["alt"], quote=True)}" data-caption="{H.escape(s["caption"], quote=True)}" '
            f'loading="{loading}"{hidden}>'
        )
    controls = ""
    if len(shots) > 1:
        controls = (
            '<div class="gallery-controls">'
            '<button type="button" class="gallery-btn prev" aria-label="Previous screenshot">\u2190</button>'
            f'<span class="gallery-counter" aria-live="polite">1 / {len(shots)}</span>'
            '<button type="button" class="gallery-btn next" aria-label="Next screenshot">\u2192</button>'
            '</div>'
        )
    return (
        '<aside class="project-gallery" aria-label="Project screenshots">'
        '<h2 class="gallery-head">Screenshots</h2>'
        '<figure class="gallery" aria-label="Screenshots">'
        f'<button type="button" class="gallery-frame" aria-label="Open full-size screenshot viewer" aria-haspopup="dialog">{"".join(imgs)}<span class="gallery-zoom" aria-hidden="true">\u2197 Enlarge</span></button>'
        f'<figcaption class="gallery-caption">{H.escape(shots[0]["caption"])}</figcaption>'
        + controls
        + '</figure></aside>'
    )


def project_body(p, shots):
    stats = "".join(
        f'<div class="stat"><div class="stat-v">{H.escape(s["value"])}</div><div class="stat-l">{H.escape(s["label"])}</div></div>'
        for s in p.get("stats", [])
    )
    quote = ""
    if p.get("quote"):
        quote = (
            '<blockquote class="quote"><p>“' + H.escape(p["quote"].strip()) + '”</p>'
            '<p class="quote-footer">— anonymised client</p></blockquote>'
        )
    gallery = gallery_html(shots, p["slug"])
    end = '<div class="post-cta"><a class="btn btn-primary" href="contact.html">Schedule Your Project Consultation</a></div>'
    if gallery:
        content = (
            '<div class="project-layout">'
            '<div class="project-main">'
            f'<div class="prose">{p["body"]}</div>'
            f'<div class="stat-grid">{stats}</div>'
            + quote + end
            + '</div>'
            + gallery
            + '</div>'
            + LIGHTBOX_HTML
            + SLIDE_JS
        )
    else:
        content = f'<div class="prose">{p["body"]}</div><div class="stat-grid">{stats}</div>' + quote + end
    return (
        '<main id="main" class="page"><div class="page-inner"><article>'
        '<header class="post-head">'
        f'<span class="case-label">{H.escape(p["kind"])}</span>'
        f'<h1>{H.escape(p["title"])}</h1>'
        f'<p class="lede">{H.escape(p["description"])}</p>'
        "</header>"
        + content
        + "</article></div></main>"
    )


# ---------------------------------------------------------------------------
# Sitemap / robots / vercel
# ---------------------------------------------------------------------------
def write_sitemap(blog, projects):
    urls = [
        ("", "1.0"),
        ("services.html", "0.9"),
        ("approach.html", "0.8"),
        ("projects.html", "0.9"),
        ("blog.html", "0.9"),
        ("contact.html", "0.8"),
        ("privacy.html", "0.3"),
        ("terms.html", "0.3"),
        ("cookies.html", "0.3"),
        ("refund.html", "0.3"),
    ]
    for p in blog:
        urls.append((f"blog-{p['slug']}.html", "0.7"))
    for c in projects:
        urls.append((f"project-{c['slug']}.html", "0.7"))
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, prio in urls:
        out.append("  <url>")
        out.append(f"    <loc>{SITE_URL}/{path if path else ''}</loc>")
        out.append(f"    <priority>{prio}</priority>")
        out.append("  </url>")
    out.append("</urlset>")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))


def write_robots():
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write(
            "User-agent: *\n"
            "Allow: /\n"
            "Disallow: /build/\n"
            "Disallow: /parts/\n"
            f"Sitemap: {SITE_URL}/sitemap.xml\n"
        )


def write_vercel(blog, projects):
    redirects = [
        {"source": "/blog/:slug((?!\\.html$).*)", "destination": "/blog-:slug.html", "statusCode": 308},
        {"source": "/case-studies/:slug((?!\\.html$).*)", "destination": "/project-:slug.html", "statusCode": 308},
        {"source": "/lab/:path*", "destination": "/blog.html", "statusCode": 308},
        {"source": "/case-studies", "destination": "/projects.html", "statusCode": 308},
        {"source": "/lab", "destination": "/blog.html", "statusCode": 308},
        {"source": "/consultation", "destination": "/contact.html", "statusCode": 308},
        {"source": "/services", "destination": "/services.html", "statusCode": 308},
        {"source": "/approach", "destination": "/approach.html", "statusCode": 308},
    ]
    cfg = {"cleanUrls": True, "trailingSlash": False, "redirects": redirects}
    with open(os.path.join(ROOT, "vercel.json"), "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2)


# ---------------------------------------------------------------------------
def main():
    blog = json.loads(read(os.path.join(CONTENT, "blog.json")))
    projects = json.loads(read(os.path.join(CONTENT, "projects.json")))
    shots_path = os.path.join(CONTENT, "screenshots.json")
    screenshots = json.loads(read(shots_path)) if os.path.exists(shots_path) else {}

    # blog index
    bi_title = "Field notes — Aremu Consulting"
    bi_desc = "Automation, AI agents, and workflows that give you your week back — written for operators."
    bi_body = blog_index_body(blog)
    write(os.path.join(ROOT, "blog.html"),
          page(bi_title, bi_desc, "blog.html", "website", blog_listing_ld(), bi_body, active_blog=True))

    # posts
    for p in blog:
        desc = excerpt(p["body"], 160) or p["description"]
        url = f"{SITE_URL}/blog-{p['slug']}.html"
        write(os.path.join(ROOT, f"blog-{p['slug']}.html"),
              page(p["title"], desc, f"blog-{p['slug']}.html", "article",
                   blog_post_ld(p, url, desc), blog_post_body(p), active_blog=True))

    # projects index
    pi_title = "Selected work — Aremu Consulting"
    pi_desc = "Systems built for real operations — projects and the tools behind them."
    write(os.path.join(ROOT, "projects.html"),
          page(pi_title, pi_desc, "projects.html", "website", project_listing_ld(),
               projects_index_body(projects), active_projects=True))

    # project pages
    for c in projects:
        url = f"{SITE_URL}/project-{c['slug']}.html"
        write(os.path.join(ROOT, f"project-{c['slug']}.html"),
              page(c["title"], c["description"], f"project-{c['slug']}.html", "article",
                   project_ld(c, url), project_body(c, screenshots.get(c["slug"], [])), active_projects=True))

    write_sitemap(blog, projects)
    write_robots()
    write_vercel(blog, projects)

    print(f"blog: index + {len(blog)} posts")
    print(f"projects: index + {len(projects)} case studies")
    print("sitemap.xml, robots.txt, vercel.json written")


def write(path, content):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print("built", os.path.relpath(path, ROOT), f"({len(content)} bytes)")


if __name__ == "__main__":
    main()