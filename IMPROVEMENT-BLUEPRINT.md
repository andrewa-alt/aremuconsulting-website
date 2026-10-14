# IMPROVEMENT-BLUEPRINT.md
## Full-site Audit + Implementable Design Spec
**Author:** claude · **Date:** 2026-10-14  
**Inputs read:** DESIGN-DIRECTION-V2.md, DESIGN.md, parts/styles.css, parts/tokens.json, parts/pages/index.html, index.html (root), approach.html (root), gen/gen_method.py  
**Constraint:** Blueprint only — no HTML/CSS/JS/Python edits in this document.

---

## Deliverables

- file: ~/projects/aremu-consulting/IMPROVEMENT-BLUEPRINT.md
- grep: ~/projects/aremu-consulting/IMPROVEMENT-BLUEPRINT.md: F1-CRITICAL
- grep: ~/projects/aremu-consulting/IMPROVEMENT-BLUEPRINT.md: pipeline diagram
- grep: ~/projects/aremu-consulting/IMPROVEMENT-BLUEPRINT.md: terminal demo
- grep: ~/projects/aremu-consulting/IMPROVEMENT-BLUEPRINT.md: Syne

---

## 1 · Executive Summary

The `parts/` directory is the canonical V2 source and **already fully implements** all three
DESIGN-DIRECTION-V2.md "WOW" moments (pipeline hero diagram, terminal micro-demo, Syne display
typeface). The root HTML pages (`index.html`, `services.html`, `approach.html`, `contact.html`)
are **V1 builds that have not been regenerated** from the updated parts. Visitors currently see
the old text-forward hero with no diagram and no display face.

**The single critical action is: run `python3 build.py` from the project root.** Everything
else in this blueprint is verification criteria and minor outstanding gaps that remain after the
rebuild.

---

## 2 · Audit Findings

### F1-CRITICAL — Root pages not rebuilt from V2 parts

**Severity:** Critical — all three V2 "WOW" features are invisible to visitors.

| Deployed root page | Canonical template |
|---|---|
| `index.html` — V1 text hero | `parts/pages/index.html` — V2 pipeline + display H1 + terminal |
| `services.html` — unknown V1 state | `parts/pages/services.html` — needs verification |
| `approach.html` — unknown V1 state | `parts/pages/approach.html` — needs verification |
| `contact.html` — unknown V1 state | `parts/pages/contact.html` — needs verification |

**Root cause:** `build.py` assembles root pages from `parts/` but was not re-run after the V2
changes landed in `parts/`.

**Fix:** `python3 build.py` (no code changes required — assembly only).

---

### F2 — Display typeface: Syne Bold

**Status:** Fully implemented in `parts/`, not deployed.

**Evidence in parts/:**
- `parts/tokens.json` line `"display": "'Syne', 'Atkinson Hyperlegible', 'Segoe UI', system-ui, sans-serif"`
- `parts/styles.css` line 2: `@font-face { font-family: 'Syne'; font-style: normal; font-weight: 700; ... }`
- `parts/styles.css` lines 153–163: `.h1-display { font-family: var(--font-display); font-size: clamp(2.6rem, 5.2vw, 4rem); font-weight: 700; line-height: 1.06; letter-spacing: -0.025em; max-width: 16ch; }`
- `build/assets/fonts/Syne-700.woff2` — file exists on disk ✓
- `parts/pages/index.html` line 5: `<h1 class="h1-display">Ship the thing that runs the thing.</h1>`

**Evidence of gap in deployed root:**
- `index.html` `:root` block: `--font-display: 'Atkinson Hyperlegible', 'Segoe UI', system-ui, sans-serif` — points to body font, NOT Syne
- `index.html` hero H1: no `h1-display` class, old copy, old font-size

**Post-build check:** After running build.py, verify `grep "h1-display" index.html` returns the V2 H1.

---

### F3 — Living hero pipeline diagram

**Status:** Fully implemented in `parts/`, not deployed.

**Evidence in parts/:**
- `parts/pages/index.html` lines 9–118: full inline SVG pipeline diagram (`.pipeline-diagram`, viewBox 860×185)
- Four stage boxes (DISCOVER / SCOPE / MILESTONES / HANDOVER) with mono stage numbers and names
- Artifact labels between connectors: "scope brief", "written scope", "milestone plan"
- Blueprint grid background + registration marks (drafting convention)
- Green animated overlays: `.pd-green-conn`, `.pd-green-arrow`, `.pd-green-node`, `.pd-green-box`
- `parts/styles.css` lines 222–263: `@keyframes pd-s1` through `pd-s4` and `pd-c1` through `pd-c3`, 6-second loop
- Animation sequence: S1 active (8–26%) → C1 connector (25–33%) → S2 active (30–47%) → C2 (46–54%) → S3 (51–68%) → C3 (67–75%) → S4 (72–89%) → reset — correct sequential "job running" feel

**Reduced-motion:** Handled correctly. `parts/styles.css` line 531: `.pd-green-conn, .pd-green-arrow, .pd-green-node { opacity: 1 !important; }` — shows completed green state (static, still-beautiful) when motion is off. `.pd-green-box { opacity: 0 !important; }` — suppresses the pulsing box highlight only, keeping the diagram legible. ✓

**Evidence of gap in deployed root:**
- `index.html`: no pipeline SVG, no `.pd-*` classes, no pipeline `@keyframes`

---

### F4 — Terminal micro-demo

**Status:** Fully implemented in `parts/`, not deployed.

**Evidence in parts/:**
- `parts/pages/index.html` lines 132–146: `.terminal-demo` with `.td-header` ("agent-log / scope-analysis") and `.td-badge` "(demo)"
- Seven lines: `$ aremu-scope --analyze "claims intake workflow"` + 4 output lines + 2 `✓` lines
- `parts/styles.css` lines 265–304: full terminal component styles + sequential reveal animation (`.td-l1` delay 0.3s → `.td-l7` delay 4.0s, one-shot on load)
- `(demo)` label present and visible in header — honest, per V2 spec ✓
- Reduced-motion: `html.js .td-line { opacity: 1 !important; }` — all lines immediately visible ✓

**Evidence of gap in deployed root:**
- `index.html`: has old `.offer-chips` / `.pf-rise` / `.pf-type` animation instead (kept as "legacy" in `parts/styles.css` line 307 — safe to leave)

---

### F5 — Hero H1 copy and layout

**Status:** Fully implemented in `parts/`, not deployed.

| | V1 (deployed root) | V2 (parts canonical) |
|---|---|---|
| H1 copy | "Tools, systems, and processes that help small businesses improve, scale, and stay efficient." | "Ship the thing that runs the thing." |
| H1 class | none | `h1-display` |
| H1 font | Atkinson Hyperlegible body | Syne Bold display |
| H1 size | `clamp(2.1rem, 4.4vw, 3.3rem)` | `clamp(2.6rem, 5.2vw, 4rem)` |
| Hero layout | single-column (H1 + lede + actions + chips) | H1 + lede → pipeline SVG → hero-bottom (CTAs + terminal) |

---

### F6 — Hero layout `.hero-inner` structure

**Status:** Updated in parts/, not deployed.

`parts/styles.css` `.hero-inner` is `display: grid; gap: 30px` (single stacking grid) — the pipeline SVG and hero-bottom row sit inside it. `parts/pages/index.html` uses `.hero-text` wrapper for H1 + lede, then `.pipeline-wrap` > SVG, then `.hero-bottom` grid (CTAs left / terminal right).

The deployed root `index.html` `.hero-inner` has the same base grid rule but lacks all the pipeline and terminal children — it won't visually break after rebuild, but verifying the assembly output is required.

---

### F7 — `@font-face` for Syne not in deployed CSS

**Status:** Will be fixed by build.py rebuild.

`parts/styles.css` line 2 declares Syne's `@font-face`. `build.py` inlines the full `parts/styles.css` content into every page. After rebuild, `grep "Syne" index.html` should return the `@font-face` block and the `--font-display` token.

**Font file:** `build/assets/fonts/Syne-700.woff2` exists. The `font_faces()` function in `build.py` generates `@font-face` blocks for Syne from the font file list. Verify the list includes `Syne-700.woff2`.

---

### F8 — Approach page: optional system view (second layer)

**Status:** Not yet implemented in parts/.

DESIGN-DIRECTION-V2.md §4.3 describes an optional second layer for `approach.html`:
```
[INTAKE AGENT]->[SCOPING ENGINE]->[MILESTONE PLANNER]->[HANDOVER AUDITOR]
edges labeled with stage artifacts; honest mapping, no fabricated "live AI" claims.
```

`parts/pages/approach.html` was not read in detail but this second-layer diagram was marked
"optional" in DESIGN.md §5. It is a post-rebuild enhancement, not a rebuild blocker.

**Spec when implemented:**
- Same drafting-sheet block language as the main method SVG
- Horizontal layout: 4 agent nodes, labeled `->` edges
- Edge labels: "scope brief" / "written scope" / "milestone plan" / "handover pack"
- No claim of "live AI" — label as system diagram honestly
- Generate via `gen/gen_method.py` as a second output, not hand-authored SVG

---

### F9 — Blog and project pages (out of scope for V2)

`blog-*.html` and `project-*.html` are built by `gen/build_content.py` from `content/` data. These pages inherit the shared CSS (inlined at build time) but their HTML structure is separate. They are not affected by the V2 hero/display changes. No action needed.

---

### F10 — Scroll-reveal on method SVG (Approach page)

**Status:** Implemented correctly in parts/, pending rebuild to deploy.

`parts/styles.css` lines 517–523: `html.js .js-reveal g.sheet` settle animation (translateY 12px → 0, 450ms, exponential ease-out, 90ms stagger per V2 spec). Reduced-motion override at line 528 resets transform and forces opacity:1. ✓

The stagger delays in `parts/styles.css` are 0/800ms/1600ms/2400ms (not 90ms as DESIGN.md §6 specifies). This is a **minor gap**: the spec says 90ms stagger; the implementation uses 800ms. The 800ms stagger reads as more deliberate/dramatic on a tall vertical diagram and is visually defensible, but pi should confirm whether the 90ms vs 800ms delta is intentional.

---

## 3 · Design Token Verification

After rebuild, each page's inlined `:root` block must contain:

```css
--paper: #F5F6F6;
--sheet: #FFFFFF;
--ink: #16181A;
--ink-soft: #3F4448;
--muted: #5C6266;
--rule: #D9DDDC;
--grid: #E7EAE9;
--accent: #1D6A4F;
--accent-strong: #14532D;
--accent-soft: #E6F0EA;
--font-display: 'Syne', 'Atkinson Hyperlegible', 'Segoe UI', system-ui, sans-serif;
--font-body: 'Atkinson Hyperlegible', 'Segoe UI', system-ui, sans-serif;
--font-mono: 'Martian Mono', 'Cascadia Code', 'SF Mono', Menlo, Consolas, monospace;
```

Warm-cream `#FBF7EF` and terracotta `#A85C2B` (from old `tokens.json` per DESIGN.md §8.1) must NOT appear. Verify with `grep -r "FBF7EF\|A85C2B" index.html services.html approach.html contact.html`.

---

## 4 · Anti-regression Checklist (per DESIGN-DIRECTION-V2.md §"Keep")

These must hold on every deployed page after rebuild:

| Constraint | Check |
|---|---|
| No gradient-on-text | `grep -n "gradient" index.html \| grep -v "linear-gradient(var(--grid"` → empty |
| No glass / glow / drop-shadow | `grep -n "blur\|box-shadow\|text-shadow\|backdrop" index.html` → empty |
| No dark-indigo hero | `grep -n "#3B1F7" index.html` → empty |
| No beige/cream ground | `grep -n "FBF7EF\|F5F0E8\|FAF7F0" index.html` → empty |
| One `<h1>` per page | `grep -c "<h1" index.html` → 1 |
| Self-hosted fonts only | No `fonts.googleapis.com` or `fonts.gstatic.com` in any page |
| Reduced-motion honored | `.pd-green-*` and `.td-line` get `opacity: 1 !important` in reduced-motion block |
| WCAG AA contrast | All new classes use tokens from DESIGN.md §2 (pre-verified) |

---

## 5 · Implementation Sequence

### Step 1 — Run gen scripts (if outputs are stale)
```
python3 gen/gen_method.py
```
Writes `build/assets/method.svg`. Check mtime vs `gen/gen_method.py`; skip if fresh.

### Step 2 — Run build.py
```
python3 build.py
```
Assembles `index.html`, `services.html`, `approach.html`, `contact.html` from `parts/`.
This is the only step needed to deploy all three V2 "WOW" features.

### Step 3 — QA: verify F1 through F7 are resolved
```bash
# Display font deployed
grep "Syne" index.html | grep "@font-face"

# Display H1 present
grep "h1-display" index.html

# Pipeline SVG present
grep "pipeline-diagram" index.html

# Terminal demo present
grep "terminal-demo" index.html

# Token integrity
grep -c "#F5F6F6" index.html    # --paper
grep -c "#1D6A4F" index.html    # --accent
grep "FBF7EF\|A85C2B" index.html  # must return empty

# No external font requests
grep "googleapis\|gstatic" index.html  # must return empty

# One H1 per page (repeat for all 4 core pages)
grep -c "<h1" index.html
```

### Step 4 — Run existing QA tools (per DESIGN.md §10)
```
python3 /home/andrew/execution/design_detector.py scan index.html --json
python3 /home/andrew/execution/verify_page.py index.html --viewport 1440x900 --viewport 390x844
```
Both must pass. Repeat for services.html, approach.html, contact.html.

### Step 5 — Post-rebuild enhancement: approach page system view (F8)
Only after Steps 1–4 pass. Implement the optional second layer as a new `gen_method.py` output
(not a code change in this blueprint — describe it to the implementer as:
- New function `render_system_view()` in `gen/gen_method.py`
- 4 rectangular agent nodes in horizontal layout (~860px wide), same `.sheet` class for CSS hooks
- Labeled arrows using same `arr` marker
- Labels: "scope brief" / "written scope" / "milestone plan" / "handover pack"
- Output to `build/assets/system-view.svg`
- `parts/pages/approach.html` inlines it below the main method blocks)

---

## 6 · Division of Labour (post-blueprint)

Per DESIGN-DIRECTION-V2.md §"Division of labour":

| Owner | Scope |
|---|---|
| **claude** | Run build.py + gen scripts, QA Steps 3–4, any visual/CSS fixes in `parts/` |
| **codex** | SEO meta, JSON-LD, canonical, heading fixes — scoped to `gen/` and content layer; hold until blueprint verified |
| **pi** | Integration, git commit, final verify, release downstream tasks |

**Downstream task gate:** Tasks `947a3661` (visual rebuild) and `16b4f248` (SEO) should remain
held until this blueprint is verified present and pi confirms the build pipeline is clean. The
visual rebuild task is now largely superseded by the existing `parts/` implementation — the main
action is running `build.py`, not re-authoring design.

---

## 7 · Summary of V2 Gaps vs Parts Implementation

| V2 requirement | Status in parts/ | Deployed in root? |
|---|---|---|
| Living hero pipeline diagram | ✅ Complete | ❌ Not yet |
| Terminal micro-demo (labeled demo) | ✅ Complete | ❌ Not yet |
| Syne display face for hero H1 | ✅ Complete (font on disk) | ❌ Not yet |
| "Ship the thing that runs the thing." H1 copy | ✅ Complete | ❌ Not yet |
| Approach system view (optional) | ❌ Not yet in parts/ | ❌ Not yet |
| All other V1 design tokens + layout | ✅ Unchanged / correct | ✅ Yes |
| Reduced-motion handling | ✅ Complete | ❌ Not yet |
| Syne @font-face self-hosted | ✅ Complete | ❌ Not yet |

**Bottom line:** One `python3 build.py` converts a V1 site into the V2 design. No new design
work is needed for the hero, display face, or terminal demo — they are already authored.
