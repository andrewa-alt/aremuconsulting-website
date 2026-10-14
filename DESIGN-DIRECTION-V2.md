# DESIGN-DIRECTION-V2 — "Showcase, not document"

**Problem:** v1 reads like a well-typeset document — restrained to the point of flat.
**Goal:** WOW on first paint, then let the craft reveal itself as the visitor browses.
**North star:** "The site IS the product." Aremu builds workflow/CRM automation and AI-agent
systems — so the hero should *show* one working, not describe it in a paragraph.

## Keep — the anti-slop identity (do not regress)

- Light cool-neutral ground (`--paper #F5F6F6`, `--sheet #FFFFFF`), ink `#16181A`, ONE
  ink-green accent `#1D6A4F` (+ `--accent-strong #14532D`, `--accent-soft #E6F0EA`).
- **No** gradient-on-text, glass, glow, drop-shadow card grids, dark-indigo hero, beige/cream
  default, stock illustration, "trusted by" wall, or rounded-card monotony.
- Self-hosted fonts only (NO Inter / Poppins / Open Sans). Mono-forward labels stay.
- WCAG AA everywhere · one `<h1>` per page · reduced-motion fully honoured.

## Add the WOW (one signature moment, not decoration)

1. **Hero = a living system diagram.** Replace the text-forward hero with a crafted technical
   visual of Aremu's named method — *Discover → Scope → Milestones → Handover* — drawn as a
   monochrome schematic (hairline strokes, small mono labels) with a single green "progress"
   line/nodes that *animate as if a job is running*. Reduced-motion → a static, still-beautiful
   diagram. It must read as "this is the machine we build", not a clip-art infographic.
2. **A "watch it work" micro-demo.** A small terminal/agent-log snippet (mono, green-on-paper)
   that types a real-looking task in, labelled honestly `(demo)` — proof by demonstration, not
   a bullet list.
3. **One display moment.** A distinct self-hosted display face for the single hero H1 phrase
   (e.g. "Ship the thing that runs the thing"), set large; everything else stays Atkinson
   Hyperlegible (body) + Martian Mono (labels).

## Then reveal it subtly (as you browse)

Precise measure/rhythm, hairline rules, tiny mono captions, focus/hover states that feel
engineered, scroll-reveal on one or two elements only (not everything), consistent
case/terminology. The polish should be a quiet "oh, this is well built", not effects.

## Uniqueness test (must pass)

Change the logo + colours and it's unrecognisable as a template. It must look authored by a
builder who ships automation — not by a "website designer".

## Division of labour (no file collisions)

- **claude** owns the visual/design layer: `parts/` (tokens, styles.css, header/footer/head,
  page templates), plus `index.html`, `services.html`, `approach.html`, `contact.html`.
- **codex** owns the SEO/content/structural layer + tooling: `gen/`, `build.py`, `content/`,
  `robots.txt`, `sitemap.xml`, and meta/OG/JSON-LD/canonical/headings fixes across all pages.
- **agy** owns the audit + this spec; **pi** integrates, verifies, commits.