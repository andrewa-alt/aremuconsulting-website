#!/usr/bin/env python3
"""Assemble the Aremu Consulting 4-page static site (DESIGN.md contract).

Reads parts/ (tokens.json, styles.css, partials, pages) plus generated
build/assets/*.svg and self-hosted woff2 in build/assets/fonts/, and writes
fully self-contained pages to the project root (index.html, services.html,
approach.html, contact.html) with zero external requests: every page inlines
the full shared CSS (including @font-face) in a <style> tag and generated
SVGs as inline markup.

Layout of each output page:
    head.html (doctype, <head>, skip-link, <body>)
    header.html (mono wordmark + nav + CTA)
    parts/pages/<page>.html  (main content)
    footer.html (footer + close)

Usage: python3 build.py
"""

import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
PARTS = os.path.join(ROOT, "parts")
PAGE_DIR = os.path.join(PARTS, "pages")
PARTIAL_DIR = os.path.join(PARTS, "partials")
ASSETS = os.path.join(ROOT, "build", "assets")
FONTS = os.path.join(ASSETS, "fonts")

PAGES = ["index", "services", "approach", "contact", "privacy", "terms", "cookies", "refund"]

PAGE_META = {
    "index": (
        "Aremu Consulting — bespoke web builds, workflow + CRM automation, custom AI agents (Manchester)",
        "A solo builder in Manchester, UK, building tools, systems, and processes for "
        "small-to-medium businesses: web and app builds, workflow and CRM automation, "
        "and custom AI agents. Named method, written scope, and every project ships with code, docs, and tests.",
    ),
    "services": (
        "Services — Aremu Consulting",
        "Three custom-scope lines: website and app building, workflow and CRM automation "
        "(n8n + your existing tools), and custom AI agent development. Three fixed-price tiers per line.",
    ),
    "approach": (
        "Approach — Discover → Scope → Milestones → Handover",
        "A named delivery method, published: scope frozen in writing before a line of code, "
        "changes priced before they are done, and every project ships with code, docs, tests, "
        "and a handover session.",
    ),
    "contact": (
        "Contact — Book a Free Fit Call",
        "Book a free 15-minute fit call, then a paid discovery/audit credited against any build. "
        "You leave with a written scope, a milestone map, and a pricing shape. Reply within one working day.",
    ),
    "privacy": (
        "Privacy Policy — Aremu Consulting",
        "How Aremu Consulting Ltd collects, uses and protects your personal data, and the rights "
        "you hold under UK data-protection law.",
    ),
    "terms": (
        "Terms and Conditions — Aremu Consulting",
        "The terms that govern use of this website and the engagement of Aremu Consulting Ltd "
        "services.",
    ),
    "cookies": (
        "Cookie Policy — Aremu Consulting",
        "Which cookies and browser storage this site uses — and that it currently sets no "
        "non-essential or advertising cookies.",
    ),
    "refund": (
        "Refund Policy — Aremu Consulting",
        "How refunds and cancellations work for scoping consultations and milestone-based project work.",
    ),
}


def read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def load_tokens():
    """Render tokens.json into a :root CSS block (single source of truth)."""
    with open(os.path.join(PARTS, "tokens.json"), "r", encoding="utf-8") as fh:
        data = json.load(fh)
    lines = [":root {"]
    for key, value in data["colors"].items():
        lines.append(f"  --{key}: {value};")
    lines.append("  --measure: " + data.get("measure", "68ch") + ";")
    lines.append("  --radius: " + data.get("radius", "0") + ";")
    lines.append("  --radius-control: " + data.get("radius-control", "2px") + ";")
    lines.append("  --font-display: " + data["fonts"]["display"] + ";")
    lines.append("  --font-body: " + data["fonts"]["body"] + ";")
    lines.append("  --font-mono: " + data["fonts"]["mono"] + ";")
    lines.append("}")
    return "\n".join(lines)


def font_faces():
    """Generate @font-face for the self-hosted woff2 (zero external requests)."""
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


def svg_assets():
    """Map placeholder name -> inline SVG markup. Read from files, never pasted."""
    found = {}
    if os.path.isdir(ASSETS):
        for fname in sorted(os.listdir(ASSETS)):
            if fname.endswith(".svg"):
                stem = fname[:-4].upper().replace("-", "_")
                found["{{" + stem + "}}"] = read(os.path.join(ASSETS, fname)).strip()
    return found


def assemble(page_name):
    tokens_root = load_tokens()
    full_css = tokens_root + "\n" + font_faces() + "\n" + read(os.path.join(PARTS, "styles.css"))

    head = read(os.path.join(PARTIAL_DIR, "head.html"))
    header = read(os.path.join(PARTIAL_DIR, "header.html"))
    footer = read(os.path.join(PARTIAL_DIR, "footer.html"))
    page = read(os.path.join(PAGE_DIR, page_name + ".html"))

    title, description = PAGE_META[page_name]
    nav_classes = {p: "" for p in PAGES}
    nav_classes[page_name] = ' class="active"'

    substitutions = {
        "{{TITLE}}": title,
        "{{DESCRIPTION}}": description,
        "{{CSS}}": full_css,
        "{{ACTIVE_INDEX}}": nav_classes["index"],
        "{{ACTIVE_SERVICES}}": nav_classes["services"],
        "{{ACTIVE_APPROACH}}": nav_classes["approach"],
        "{{ACTIVE_PROJECTS}}": "",
        "{{ACTIVE_BLOG}}": "",
        "{{ACTIVE_CONTACT}}": nav_classes["contact"],
        "{{YEAR}}": "2026",
    }
    # Inject generated SVGs (inline by file read).
    for key, value in svg_assets().items():
        substitutions.setdefault(key, value)

    def fill(template):
        out = template
        for key, value in substitutions.items():
            out = out.replace(key, value)
        return out

    html = fill(head) + fill(header) + fill(page) + fill(footer)
    return html


def main():
    os.makedirs(ROOT, exist_ok=True)
    # Emit the shared stylesheet too (identical to what's inlined in each page)
    tokens_root = load_tokens()
    full_css = tokens_root + "\n" + font_faces() + "\n" + read(os.path.join(PARTS, "styles.css"))
    with open(os.path.join(ROOT, "styles.css"), "w", encoding="utf-8") as fh:
        fh.write(full_css)
    print("built", os.path.join(ROOT, "styles.css"))
    for page in PAGES:
        html = assemble(page)
        out = os.path.join(ROOT, page + ".html")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(html)
        print("built", out, f"({len(html)} bytes)")
    print("done")


if __name__ == "__main__":
    main()