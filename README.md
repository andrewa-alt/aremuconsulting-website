# aremuconsulting-website

Static marketing site for **Aremu Consulting Ltd** (https://www.aremuconsulting.com).

A solo-builder consultancy covering three custom-scope lines: website & custom
application building, workflow & CRM automation, and custom AI agent development.

## Build

The site is assembled from `parts/` (partials, pages, tokens, styles) and content
data, producing flat HTML files at the repository root.

```bash
python3 build.py                # core pages + styles.css
python3 gen/build_content.py    # blog + project pages, sitemap, robots, vercel.json
```

## Structure

- `parts/` — shared shell (header/footer/head), page templates, tokens, stylesheet.
- `content/` — blog posts and project case studies (JSON).
- `gen/` — deterministic content/build generators.
- `build/assets/` — self-hosted fonts, logo, generated SVGs, case-study screenshots.
- Root `*.html` — the compiled, deployable site.