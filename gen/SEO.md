# SEO generation contract

Both builders use `parts/partials/head.html` and `gen/seo.py`. Core and index
metadata lives in `content/site.json`; each blog post and project has a `seo`
object with `title`, `description`, and optional `og.title` / `og.description`.
The content refresh scripts preserve reviewed `seo` objects by slug.

Canonical URLs use `https://www.aremuconsulting.com/`, without `.html` or a
trailing slash on named pages, matching Vercel's `cleanUrls: true` and
`trailingSlash: false`. `/case-studies` is a redirect to `/projects`, and legacy
nested case-study routes redirect to flat project routes. Sitemap entries use
the same canonical function; aliases are not additional pages. The content
builder emits redirects with clean destinations, avoiding an extra `.html`
redirect. PI must regenerate `vercel.json` along with HTML during integration.

The shared JSON-LD business node is a `LocalBusiness` with a stable `@id`.
It includes the supplied name, solo-builder description, founder, and
Manchester/GB locality. No phone, email, hours, street address, coordinates,
ratings or customer results are invented. Article schemas reference the same
business node as publisher.

Share cards use the existing 160 × 160 PNG logo, absolute image URLs and a
Twitter `summary` card. No new network dependency or executable metadata
script is added. Editorial values are HTML-escaped; JSON-LD escapes `<` so
content cannot terminate its script element. The inline JSON-LD script is data.

Robots rules allow public fonts, screenshots and the share image under
`build/assets/`, and disallow source directories. Robots rules are crawl
instructions, not access control.

Legacy blog extraction left unfinished section wrappers and empty headings.
Those remnants are removed from the content and from future extraction.
Generated articles retain one main landmark and one h1. The screenshot dialog
contains Tab focus while open, closes with Escape, and restores launcher focus.

## Verification without regeneration

Run `python3 gen/check_seo.py`. It imports guarded builder modules and calls
rendering functions in memory. It never invokes either `main()` or writes root
HTML, styles, sitemap, robots or hosting configuration. It checks all 29 current
pages, metadata uniqueness, canonical/schema/card consistency, heading order,
main landmarks, sitemap coverage, crawl rules and escaping. No extra package
is required.

For integration, PI runs the normal two build scripts after both agents finish,
then verifies rendered pages and hosting redirects. Root HTML was deliberately
left for that integration step. HTML parser checks passed on all 29 in-memory pages. Chrome DevTools MCP was
not available, and local Chromium could not launch because the execution sandbox
denied its process operation. Browser DOM, modal keyboard behavior, performance,
deployed redirects and social-platform previews remain integration checks.

## Sources

- [Google canonical guidance](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls): absolute self-canonicals and sitemap consistency.
- [Vercel cleanUrls](https://vercel.com/docs/project-configuration/vercel-json#cleanurls): public paths omit `.html`.
- [Open Graph](https://ogp.me/): `property` attributes, absolute URLs, image metadata.
- [Schema.org LocalBusiness](https://schema.org/LocalBusiness): business identity and locality.
- [Google robots guidance](https://developers.google.com/search/docs/crawling-indexing/robots/intro): allow assets needed to understand public pages.
