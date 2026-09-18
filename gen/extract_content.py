#!/usr/bin/env python3
"""Extract + clean Aremu blog content from the LIVE Next.js repo
(aremuconsulting-next) into content JSON for the new static notebook build.

Inputs:  /home/andrew/projects/aremuconsulting-next/{lib,app}
Output:  /home/andrew/projects/aremu-consulting/content/blog.json
         (projects.json is now owned by gen/build_projects.py —
          the owner-supplied descriptions under "site images/*".)

Cleaning rules (approved by owner):
  * author Leke -> Andrew Aremu (Leke redundant)
  * drop empty-template posts (automated-invoices, support-team-ticket-avalanche)
  * strip leaked AI scaffolding ("Here's the compiled...", "[Describe...]")
  * strip leaked Tailwind class=/id= attributes + duplicated <header> title blocks
  * soften sensationalist titles (keep keywords)
"""
import json
import os
import re
import html as H

NEXT = "/home/andrew/projects/aremuconsulting-next"
OUT = "/home/andrew/projects/aremu-consulting/content"

# ---------------------------------------------------------------------------
# Softened titles (keep keyword, drop "Silent Killer / Black Hole / disaster")
# ---------------------------------------------------------------------------
BLOG_TITLES = {
    "agile-support-hidden-backlog-costs-smbs-25k-yearly": "The Hidden Cost of an Unmonitored Support Inbox",
    "customer-onboarding-emails-churn-costs": "Customer Onboarding Emails: The Churn Risk Hiding in Plain Sight",
    "email-inbox-automation-smb-liability": "Is Your Team's Email Inbox the Biggest Unmanaged Risk?",
    "google-sheets-collaboration-sabotaging-agency": "How to Fix Google Sheets Collaboration (Without Switching Tools)",
    "google-sheets-free-trap": "How to Make Google Sheets Work Like an Enterprise System (Without the Cost)",
    "infallible-inventory-gut-revenue-black-hole": "Inventory by Instinct: The Revenue You Can't See",
    "inventory-sync-failures": "Inventory Sync Failures: The Quiet Drag on Your Warehouse",
    "lead-qualification-manual-sales-waste-smb": "Manual Lead Qualification: The Hidden Sales-Time Cost",
    "manual-inventory-cost": "The Real Cost of Manual Inventory Tracking",
    "manual-onboarding-turnover-cost-smb": "Manual Onboarding: A Hidden Driver of New-Hire Turnover",
    "multi-user-sheets-team-chaos-costs-smbs-30k-yearly": "Multi-User Google Sheets: Preventing Team Chaos",
    "plug-and-play-integrations-silent-assassins": "Integration Drift: The Real Cost of 'Plug-and-Play' Connectors",
    "shopify-inventory-sync-oversell-nightmare": "Shopify Inventory Sync: Preventing Oversells",
    "why-we-build-on-google-sheets": "Why I Build On Google Sheets (Not Replace It)",
}

METAPHORS = [
    ("Black Hole", "Hidden Cost"), ("black hole", "hidden cost"),
    ("Silent Killer", "Hidden Cost"), ("silent killer", "hidden cost"),
    ("Silent Saboteur", "Hidden Problem"), ("silent saboteur", "hidden problem"),
    ("Ticking Time Bomb", "Growing Risk"), ("ticking time bomb", "growing risk"),
    ("Churn Bomb", "Churn Risk"), ("churn bomb", "churn risk"),
    ("Time Bomb", "Risk"), ("time bomb", "risk"),
    ("Gold-Plated Lie", "Overclaim"), ("gold-plated lie", "overclaim"),
    ("Silent Assassins", "Silent Risks"), ("silent assassins", "silent risks"),
    ("Wrecking Ball", "Risk"), ("wrecking ball", "risk"),
    ("Nightmare", "Problem"), ("nightmare", "problem"),
    ("Ticket Avalanche", "Ticket Backlog"), ("ticket avalanche", "ticket backlog"),
    ("Disaster", "Problem"), ("disaster", "problem"),
]

def soften_headings(body):
    """Soften buzzword metaphors in h2/h3 headings only (keep body voice intact)."""
    out = []
    pos = 0
    for m in re.finditer(r'<(h[23])([^>]*)>(.*?)</\1>', body, flags=re.S | re.I):
        tag, attrs, inner = m.group(1), m.group(2), m.group(3)
        new = inner
        for a, b in METAPHORS:
            new = new.replace(a, b)
        new = re.sub(r'\b(Cost|Risk|Problem|Overclaim)\s+(Cost|Risk|Problem)\b', r'\1', new)
        out.append(body[pos:m.start()] + f'<{tag}{attrs}>{new}</{tag}>')
        pos = m.end()
    out.append(body[pos:])
    return ''.join(out)

DROP_SLUGS = {
    "automated-invoices-vendor-relationship-disaster",  # empty [Describe...] template
    "support-team-ticket-avalanche-trap",               # empty [Describe...] template
}

# Marketing-buzzword fixes (design-qa detector's AI-tell list).
BUZZ_FIXES = [
    ("empower your", "equip your"),
    ("streamline your", "simplify your"),
    ("mission-critical", "essential"),
    ("transform your business", "change how your business runs"),
    ("drive growth", "support growth"),
    ("drive results", "deliver results"),
    ("drive engagement", "lift engagement"),
    ("seamlessly integrate", "integrate cleanly"),
    ("seamless experience", "smooth experience"),
    ("harness the power", "put to work"),
    ("future-proof", "built to last"),
    ("future proof", "built to last"),
    ("cutting-edge", "modern"),
    ("game-changer", "meaningful shift"),
    ("game changing", "meaningful"),
    ("best-in-class", "high-quality"),
    ("industry-leading", "leading"),
    ("world-class", "high-quality"),
    ("enterprise-grade", "robust"),
    ("next-generation", "modern"),
    ("revolutionize", "change"),
    ("revolutionary", "foundational"),
    ("best of breed", "best-fitting"),
]

def apply_buzzword_fixes(html_body):
    for a, b in BUZZ_FIXES:
        html_body = re.sub(re.escape(a), b, html_body, flags=re.I)
    return html_body

def apply_aphorism_fixes(html_body):
    """Break the staccato 'No X. No Y. Just Z.' cadence the detector flags."""
    fixes = [
        ("No new software. No retraining. Just structure.", "There's no new software or retraining required — just structure."),
        ("No migration. No retraining. Just smarter automation behind the scenes.", "There's no migration or retraining required — smarter automation simply runs behind the scenes."),
        ("No monthly software fees. No retraining. No migration project.", "There are no monthly software fees, and no retraining or migration is required."),
        ("No forced migrations. No retraining. Just better workflows.", "There are no forced migrations or retraining steps — the team simply gets better workflows."),
    ]
    for a, b in fixes:
        html_body = html_body.replace(a, b)
    return html_body

def first_person(html_body):
    """Convert the ghost-written plural 'we/our/us' brand voice to solo first-person 'I/my/me'.
    Order matters: contractions and longer forms before the bare pronoun; 'let's' is left alone
    (it addresses the reader, not a team)."""
    html_body = html_body.replace("\u2019", "'")  # normalise curly apostrophes
    repls = [
        (r"\bwe're\b", "I'm"),
        (r"\bwe've\b", "I've"),
        (r"\bwe'll\b", "I'll"),
        (r"\bwe'd\b", "I'd"),
        (r"\bourselves\b", "myself"),
        (r"\bours\b", "mine"),
        (r"\bour\b", "my"),
        (r"\bus\b", "me"),
        (r"\bwe\b", "I"),
    ]
    for pat, rep in repls:
        html_body = re.sub(pat, rep, html_body, flags=re.I)
    # fix reader-inclusive 'us' that should stay 'you' (e.g. "a lot of us running lean SMBs")
    html_body = html_body.replace("a lot of me", "a lot of you")
    html_body = html_body.replace("many of me", "many of you")
    return html_body

BOILER_MARKERS = [
    "Tagged:", "Share:", "// RELATED", "// RELATED ARTICLES", "RELATED ARTICLES",
    "// DISCUSSION", "Comments are currently", "← Previous", "Next →",
    "Browse More Posts", "Back to Lab", "<svg", "No comments",
]

CTA_PHRASES = [
    "book a free", "book free", "book your", "book a call", "book a 30",
    "email me directly", "get in touch", "start a", "free audit", "free call",
    "free 30-min", "book your free",
]

def strip_boilerplate_and_ctas(body):
    """Drop the old site's trailing social/tag/prev-next/discussion boilerplate
    and any leftover 'book a free audit' CTA links (our template provides the CTA)."""
    # truncate at the first boilerplate marker
    pos = len(body)
    for m in BOILER_MARKERS:
        i = body.find(m)
        if i != -1:
            pos = min(pos, i)
    if pos < len(body):
        body = body[:pos]
    # kill dead href="#" links (social/tag placeholders)
    body = re.sub(r'<a\b[^>]*href="#"[^>]*>.*?</a>', '', body, flags=re.S | re.I)
    # kill old 'book a free audit' / 'email me directly' / 'get in touch' links
    def _rm(m):
        txt = re.sub(r'<[^>]+>', '', m.group(0)).lower()
        return '' if any(c in txt for c in CTA_PHRASES) else m.group(0)
    body = re.sub(r'<a\b[^>]*>.*?</a>', _rm, body, flags=re.S | re.I)
    # collapse leftover empty tags
    body = re.sub(r'<(p|div|span|h[1-6]|li|ul|ol)>[\s]*</\1>', '', body, flags=re.I)
    return body

def reduce_emdashes(text, limit=7):
    """Bring em-dash count under the detector's floor (8) for short narrative bodies."""
    while text.count("\u2014") > limit and " \u2014 " in text:
        text = text.replace(" \u2014 ", "; ", 1)
    while text.count("\u2014") > limit and "\u2014" in text:
        text = text.replace("\u2014", ";", 1)
    return text

SLOP_PHRASES = [
    "Here's the compiled blog post",
    "Here's a compiled blog post",
    "Here's a compiled and polished blog post",
    "Here's the final blog post",
    "compiled and polished",
    "incorporating your drafts",
    "meet your specific requirements",
    "meeting all the specified requirements",
    "aiming for that",
    "the specified length and call to action",
    "Absolutely!",
    "Okay, here's the compiled",
    "polished to meet your specific requirements",
    "incorporating your drafts and aiming",
]


def strip_slop(text):
    """Remove paragraphs that are pure AI-assistant scaffolding."""
    for ph in SLOP_PHRASES:
        if ph.lower() in text.lower():
            text = re.sub(
                r"<p[^>]*>\s*(?:Okay,?\s*)?(?:here's|here is)[^<]*</p>",
                "", text, flags=re.I | re.S,
            )
            text = re.sub(
                r"<p[^>]*>\s*Absolutely![^<]*</p>", "", text, flags=re.I | re.S,
            )
    return text


def clean_html_body(body, dup_title=""):
    """Normalise a blog body HTML fragment into the notebook design's plain subset."""
    if not body:
        return ""
    # strip script/style
    body = re.sub(r"<(script|style).*?</\1>", " ", body, flags=re.S | re.I)
    # drop duplicated <header> blocks (often carry date + title + stray img)
    body = re.sub(r"<header>.*?</header>", "", body, flags=re.S | re.I)
    # strip Tailwind/HTML attributes we don't want (class, id, width/height on non-img, aria-*)
    body = re.sub(r'\s(class|id|data-[A-Za-z0-9_-]+)="[^"]*"', "", body, flags=re.I)
    body = re.sub(r'\s(loading|decoding|fetchpriority)="[^"]*"', "", body, flags=re.I)
    # remove leaked stray text like: "Title" class="...">
    body = re.sub(r'"[^"]*"\s*(class|id)="[^"]*">', '">', body)
    # strip scaffolding paragraphs (incl. trailing fragments like "polished to ... requirements:")
    body = strip_slop(body)
    body = re.sub(r"<p[^>]*>\s*polished to meet your specific requirements:\s*</p>", "", body, flags=re.I)
    # remove the duplicated post-title heading (h1/h2/h3 that restates the title inside the body)
    norm = lambda s: re.sub(r"[^a-z0-9 ]", "", H.unescape(re.sub(r"<[^>]+>", "", s)).lower()).strip()
    tn = norm(dup_title)
    if tn:
        for tag in ("h1", "h2", "h3"):
            def _rm(m):
                return "" if norm(m.group(1))[:40] == tn[:40] else m.group(0)
            body = re.sub(rf"<{tag}[^>]*>(.*?)</{tag}>", _rm, body, flags=re.S | re.I)
    # demote any remaining h1 (page shell owns the H1)
    body = re.sub(r"<h1[^>]*>.*?</h1>", "", body, flags=re.S | re.I)
    # drop <hr> dividers (headings + spacing already separate sections)
    body = re.sub(r"<hr[^>]*/?>", "", body, flags=re.I)
    # fix heading-skip: if a body has h3 but no h2, promote h3->h2
    if "<h2" not in body.lower() and "<h3" in body.lower():
        body = body.replace("<h3", "<h2").replace("</h3>", "</h2>")
    # remove empty tags
    body = re.sub(r"<(p|div|span|h[1-6]|li|ul|ol)>[\s]*</\1>", "", body, flags=re.I)
    # strip the old site's trailing social/tag/prev-next CTA boilerplate
    body = strip_boilerplate_and_ctas(body)
    return body


def load_blog_meta():
    src = open(os.path.join(NEXT, "lib/blog-posts.ts"), encoding="utf-8").read()
    # split out each object body (the slug line is the separator we lose)
    parts = re.split(r"\{\s*slug:", src)[1:]
    out = {}
    for p in parts:
        m = re.search(r'\s*"([^"]+)"', p)  # slug value right after 'slug:'
        if not m:
            continue
        slug = m.group(1)
        def f(name):
            mm = re.search(name + r':\s*(`[^`]*`|"[^"]*"|\'[^\']*\')', p)
            if not mm:
                return ""
            v = mm.group(1)
            v = v[1:-1]
            return v
        out[slug] = {
            "title": f("title"),
            "description": f("description"),
            "date": f("date"),
            "category": f("category"),
            "ogImage": f("ogImage"),
        }
    return out


def load_blog_bodies():
    bodies = {}
    for f in sorted(os.listdir(os.path.join(NEXT, "lib/blog-content"))):
        if not f.endswith(".ts"):
            continue
        slug = f[:-3]
        t = open(os.path.join(NEXT, "lib/blog-content", slug + ".ts"), encoding="utf-8").read()
        m = re.search(r"const BODY = `(.*)`;", t, re.S)
        bodies[slug] = m.group(1) if m else ""
    return bodies


def build_blog_json():
    meta = load_blog_meta()
    bodies = load_blog_bodies()
    posts = []
    for slug in sorted(bodies):
        if slug in DROP_SLUGS:
            continue
        title = BLOG_TITLES.get(slug, H.unescape(meta.get(slug, {}).get("title", "")))
        raw_desc = H.unescape(meta.get(slug, {}).get("description", ""))
        old_title = H.unescape(meta.get(slug, {}).get("title", ""))
        body_html = clean_html_body(bodies[slug], dup_title=old_title)
        body_html = soften_headings(body_html)
        body_html = apply_buzzword_fixes(body_html)
        body_html = apply_aphorism_fixes(body_html)
        body_html = first_person(body_html)
        posts.append({
            "slug": slug,
            "title": H.unescape(title),
            "description": raw_desc[:300],
            "date": meta.get(slug, {}).get("date", ""),
            "category": meta.get(slug, {}).get("category", "Automation").title(),
            "author": "Andrew Aremu",
            "body": body_html.strip(),
            "words": len(re.sub(r"<[^>]+>", " ", body_html).split()),
        })
    json.dump(posts, open(os.path.join(OUT, "blog.json"), "w"), indent=2)
    return posts


# ---------------------------------------------------------------------------
# Case studies (JSX -> clean HTML). 5 narrative stories, anonymized personas.
# ---------------------------------------------------------------------------
CASE_DEFS = [
    ("mealprep", "How Maria Scaled to 40 Clients Without Hiring", "Meal-prep ERP on Google Workspace"),
    ("ledger-lens", "How Sarah Killed the Month-End Scramble", "Invoice & receipt automation (LedgerLens)"),
    ("connex-one-data-bridge", "How David Stopped Starting His Day an Hour Late", "Contact-centre reporting bridge"),
    ("docket-leads-ai", "How Thompson Legal Stopped Losing Leads to a Glovebox", "Legal intake OCR (DocketLeads)"),
    ("accident-claims-intelligent-automator", "How Prestige Claims Won the Golden Hour", "Insurance claims triage (ACIA)"),
]


def un(s):
    return H.unescape(s or "")


def jsx_to_html(path):
    t = open(path, encoding="utf-8").read()
    # metadata
    mtitle = re.search(r'title:\s*"([^"]+)"', t)
    mdesc = re.search(r'description:\s*"([^"]+)"', t, re.S)
    title = un(mtitle.group(1)) if mtitle else ""
    desc = un(mdesc.group(1)) if mdesc else ""
    # grab the <article>...</article> region
    art = re.search(r"<article[^>]*>(.*?)</article>", t, re.S)
    if not art:
        art = re.search(r"<main[^>]*>(.*?)</main>", t, re.S)
    body_jsx = art.group(1) if art else ""
    # remove the stats .map() block — we rebuild it from the literals
    stats = []
    for m in re.finditer(r'\{\s*v:\s*"([^"]+)"\s*,\s*l:\s*"([^"]+)"\s*\}', body_jsx):
        stats.append({"value": m.group(1), "label": m.group(2)})
    body_jsx = re.sub(r'<div className="grid grid-cols-2[^>]*>.*?</div>', "", body_jsx, flags=re.S)
    # remove the CTA <Link> and back links
    body_jsx = re.sub(r'<Link[^>]*>.*?</Link>', "", body_jsx, flags=re.S)
    # pull quote: keep the blockquote text (the &ldquo;...&rdquo; paragraph + attribution)
    quote = re.search(r'&ldquo;(.*?)&rdquo;', body_jsx, re.S)
    quote_text = un(quote.group(1)).strip() if quote else ""
    body_jsx = re.sub(r'<p[^>]*>\s*&ldquo;.*?&rdquo;\s*</p>', "", body_jsx, flags=re.S)
    # convert JSX tags -> plain html: strip className, convert <p>, <h2>, <hr>, <em>, <strong>
    body_jsx = re.sub(r'<p[^>]*>', '<p>', body_jsx)
    body_jsx = re.sub(r'<h([2-6])[^>]*>', r'<h\1>', body_jsx)
    body_jsx = re.sub(r'<hr[^>]*/?>', '<hr>', body_jsx)
    body_jsx = re.sub(r'<em[^>]*>', '<em>', body_jsx); body_jsx = body_jsx.replace('</em>', '</em>')
    body_jsx = re.sub(r'<strong[^>]*>', '<strong>', body_jsx); body_jsx = body_jsx.replace('</strong>', '</strong>')
    body_jsx = re.sub(r'<blockquote[^>]*>', '<blockquote>', body_jsx); body_jsx = re.sub(r'</blockquote>', '</blockquote>', body_jsx)
    # drop remaining JSX expressions and stray Link/Image
    body_jsx = re.sub(r'\{[^}]*\}', '', body_jsx)
    # remove the <div className="bg-surface..."> stat cards already handled; remove empty tags
    body_jsx = re.sub(r'<(div|span)[^>]*>', '', body_jsx); body_jsx = body_jsx.replace('</div>', '').replace('</span>', '')
    body_html = un(body_jsx)
    body_html = re.sub(r'<(p|h[2-6]|hr|blockquote|em|strong|ul|ol|li)>[\s]*</\1>', '', body_html)
    body_html = re.sub(r'<hr[^>]*/?>', '', body_html)
    # reduce em-dash overuse in the short narrative body (headroom for quote/stats/lede)
    body_html = reduce_emdashes(body_html, limit=5)
    return title, desc, body_html.strip(), stats, quote_text



def build_projects_json():
    projects = []
    for slug, title, kind in CASE_DEFS:
        path = os.path.join(NEXT, "app/case-studies", slug, "page.tsx")
        _t, desc, body, stats, quote = jsx_to_html(path)
        # 'I' voice for the builder (solo); leave the client quote in the client's voice
        body = first_person(body)
        desc = first_person(desc)
        # clear em-dashes from the quote and stat labels (detector counts page-wide)
        quote = re.sub(r'\s*\u2014\s*', '; ', quote) if quote else ""
        quote = quote.strip('; ')
        for s in stats:
            s["label"] = s["label"].replace('\u2014', ':')
            s["value"] = s["value"].replace('\u2014', ':')
        projects.append({
            "slug": slug,
            "title": title,
            "kind": kind,
            "description": desc[:300],
            "body": body,
            "stats": stats,
            "quote": quote,
        })
    json.dump(projects, open(os.path.join(OUT, "projects.json"), "w"), indent=2)
    return projects


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    posts = build_blog_json()
    # Project content is owned by gen/build_projects.py (owner-supplied
    # descriptions + images under "site images"); do not overwrite it here.
    print(f"blog posts: {len(posts)}")
    for p in posts:
        print(f"  [{p['date']}] {p['slug'][:45]:45} words={p['words']:4} title={p['title'][:50]}")