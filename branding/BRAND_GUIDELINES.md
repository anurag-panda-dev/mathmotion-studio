# MathMotion Studio — Brand Guidelines

> **Status:** v1.1 draft, derived from the three raster references in [`../assets/`](../assets/), the provided potrace outlines, plus the brand direction in the project prompts. The application is not yet implemented ([`docs/ROADMAP.md`](../docs/ROADMAP.md)), so these guidelines currently govern documentation, generated assets, and the planned UI. The logo wordmark is now outlined vector path data (traced from the rasters), so the unknown brand typeface only affects future typeset use (§12).

---

## 1. Brand overview and personality

**MATHMOTION STUDIO** turns mathematical concepts into clear, beautiful animated lessons. The identity must communicate:

| Pillar | How it shows up |
|---|---|
| Mathematical precision | Exact geometry: true ellipses, deliberate points, measured proportions. |
| Motion and transformation | The violet trajectory sweeping through the orbit — the brand's core metaphor: an idea moving along a curve. |
| Educational clarity | High contrast, generous negative space, no decorative noise. |
| Creative visualization | The interlocked orbits suggest a graph, an atom, a system in motion. |
| Modern craftsmanship | Minimal, Swiss-inspired restraint; typography does the talking. |

Voice in wording: calm, precise, teacher-friendly. The exact brand wording is **MATHMOTION STUDIO** (two words, `STUDIO` set in wide tracking beneath `MATHMOTION`). Never abbreviate to "MMS", never re-case ("Mathmotion", "MATHMOTION STUDIO APP").

## 2. Logo variants and intended use

| File | Variant | Use it on | Never use it on |
|---|---|---|---|
| [`logo-primary.svg`](logo-primary.svg) | Full color, horizontal lockup | White or very light surfaces — the canonical logo. | Dark or colored surfaces (use `logo-dark`). |
| [`logo-dark.svg`](logo-dark.svg) | Full color for dark contexts | Solid navy `#061830` or other dark surfaces (the file has no background — pair it with the surface). | Light surfaces. |
| [`logo-symbol.svg`](logo-symbol.svg) | Mark alone, full color | Light surfaces where the wordmark is unnecessary (app chrome, favicons at ≥32px, social avatars on light). | Dark surfaces (use the inverted mark inside `app-icon.svg` or set colors per §7). |
| [`logo-monochrome.svg`](logo-monochrome.svg) | One color, `currentColor` | One-color printing, embossing, engraving, partner sheets. | Anywhere full color is available. |
| [`app-icon.svg`](app-icon.svg) / [`app-icon.png`](app-icon.png) / [`app-icon.ico`](app-icon.ico) | Application icon | Desktop icon, window chrome, tile. Works fully without the wordmark. | As a document logo (it is an icon, not a lockup). |
| [`favicon.svg`](favicon.svg) | Full mark on navy plate, 256×256 | Browser tab, bookmark bar. | Sizes above 64px (use the symbol instead). |

**There is no separate `logo-light.svg`:** `logo-primary.svg` *is* the light-background variant. Duplicating it would create two sources of truth (deliberate deviation from the proposed structure).

**Lockup structure:** symbol (left) + two-line wordmark (`MATHMOTION` heavy above `STUDIO` tracked out). The symbol may stand alone; the wordmark may never appear without the symbol, and the two-line arrangement is fixed — do not re-stack, re-space, or inline them.

## 3. Color palette

Source of truth: [`palette.json`](palette.json) (measured by pixel sampling the rasters).

### Brand colors (measured)

| Name | Hex | Role | Observed range in rasters |
|---|---|---|---|
| Navy | `#061830` | Primary ink, dark surface | `#061830`–`#071A32` |
| Violet | `#6A4AEE` | Accent: trajectory, emphasis | `#5946E4`–`#6B4BEC` |
| Ivory | `#F1F3EA` | Light ink on dark | `#E9EADC`–`#F3F6EF` |

Single violet rule: **one canonical violet `#6A4AEE`** everywhere, even though the dark-context rasters render slightly deeper. Do not introduce a second violet.

### Supporting scene colors

`white #FFFFFF`, `black #000000`, `gray #8A93A6`, `red #D0402E`, `green #2E9E6B`, `blue #2E6FD0`, `amber #E0A126`, `teal #1F9E9E`, `pink #D0509E` — for diagrams and multi-series graphs inside rendered lessons; normative for `scene.md` ([`SCENE_FORMAT_SPEC.md` §7.2](../prompts/SCENE_FORMAT_SPEC.md)).

### Themes

| Theme | Surface | Ink | Accent |
|---|---|---|---|
| `midnight` (default) | `#061830` | `#F1F3EA` | `#6A4AEE` |
| `ivory` (light) | `#FFFFFF` | `#061830` | `#6A4AEE` |

## 4. Typography

### Wordmark (as rendered in the rasters)

Heavy geometric sans, all caps: `MATHMOTION` with tight-to-normal tracking; `STUDIO` in a lighter weight with very wide tracking beneath it. **The exact typeface is unknown** — see §12 — but since v1.1 it no longer matters for the logo files: the SVG wordmark is *outlined path data* (traced from the raster masters and the provided potrace sample), so the logo renders identically everywhere without the font installed. For **typeset** uses (documents, future UI headings) fall back to `Montserrat, Poppins, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif` at weight 800/600, and keep the PNG rasters as the pixel-exact letterform reference. Do not typeset the wordmark in an arbitrary font and present it as the logo.

### Planned UI hierarchy (application not yet implemented)

| Level | Treatment |
|---|---|
| Page titles | Geometric sans, 600–700, sentence case. |
| Body | 400, 15–16px, 1.5 line height. |
| Technical/diagnostic (expandable panels) | Monospace stack (`'Cascadia Code', Consolas, monospace`). |
| Math in UI chrome | Never render raw LaTeX strings to teachers; the renderer owns math typography. |

Documentation (this repository) uses the same neutral sans stack and renders consistently in GitHub/VS Code.

## 5. Clear space and minimum sizes

- **Clear space:** on all four sides, at least the height of the `M` in `MATHMOTION` (≈ 0.75 × cap height; ≈ 54px in the 885×225 raster). Nothing enters that zone — no text, no edge, no other logo.
- **Minimum sizes (lockup):** 160px wide on screen, 35mm in print. Below that, switch to the symbol alone.
- **Minimum sizes (symbol):** 24px on screen; use [`favicon.svg`](favicon.svg) below 32px (navy plate keeps the mark legible at tab size).
- **Minimum sizes (app icon):** do not scale below 16px; the `.ico` ships pre-rendered sizes 16–256.

## 6. Light and dark background usage

- **Light surfaces:** `logo-primary.svg` (navy ink reads at 17.7:1 on white).
- **Dark surfaces:** `logo-dark.svg` on solid navy `#061830` (ivory reads at 15.8:1). On non-navy dark surfaces, verify ivory still reaches 4.5:1 against the actual background before shipping.
- **Photographic/busy surfaces:** place the logo inside a solid navy or white plate with clear space — never drop the raw lockup onto an image.
- **Borders and hairlines:** if a container edge sits near the logo, keep it outside the clear-space zone.

## 7. Monochrome usage

- `logo-monochrome.svg` inherits `currentColor` — set the color at the usage site (`#061830` on light, `#F1F3EA` on dark).
- Because the mark is line art, monochrome loses the violet trajectory's distinction: acceptable and intentional (single-color media), but do not use monochrome in brand-primary contexts.
- Never place monochrome navy on navy, or ivory on white.

## 8. App icon and favicon

- The app icon is **navy rounded square + violet border + ivory orbits + violet trajectory**; the center dot is ivory, end dots violet. It reads independently of the wordmark at every size.
- Rounded-corner radius scales with the platform: the `.svg`/`.png` are platform-neutral; the `.ico` carries pre-rendered sizes (16/24/32/48/64/128/256) derived from the original raster.
- The favicon is the **full mark** (inner loop included) on the navy plate, identical to the app icon at 256×256; legibility at tab size comes from the silhouette. A legacy 16/32/48 `.ico` remains a listed missing deliverable — export from `favicon.svg`/`app-icon.ico` when needed.
- Never re-create the icon by screenshotting the logo; use these files.

## 9. Correct and incorrect treatments

**Do:** use the provided files as-is; scale proportionally; use the correct variant for the surface; keep the two-line wordmark; give clear space.

**Don't:**
1. Recolor outside the palette (no gradients, no neon, no second violet).
2. Stretch, skew, rotate, or crop the lockup; or re-position `STUDIO`.
3. Add effects: shadows, outlines, glows, bevels, transparency fades.
4. Place the light logo on dark, or the dark logo on light.
5. Set the wordmark in a different font "just for this size".
6. Rebuild the mark from components (e.g. swap ellipses for a literal atom glyph, a graduation cap, or a calculator).
7. Pair the logo with taglines inside the clear-space zone.
8. Use the app icon where a document logo belongs (or vice versa).

## 10. Accessibility and contrast

Computed WCAG 2.1 ratios (in [`palette.json`](palette.json)):

| Pair | Ratio | Verdict |
|---|---|---|
| Navy on white | 17.7:1 | AAA |
| Ivory on navy | 15.8:1 | AAA |
| Violet on white | 5.5:1 | AA body, AAA large |
| Violet on navy | 3.2:1 | **Large text / UI components only — never body text on navy** |

Rules: text on navy is ivory (never violet); body text on light surfaces is navy; violet is for accents, headings ≥24px, and non-text UI. The logo itself is exempt from contrast requirements as a graphic, but the variants above already exceed them. All interactive UI (planned) must be keyboard-navigable with visible focus — see [`docs/UI_UX_SPEC.md`](../docs/UI_UX_SPEC.md).

## 11. Export formats and asset naming

| Asset | Format | Naming | Notes |
|---|---|---|---|
| Logo lockups, symbol | `.svg` (source of truth for vector) | `logo-<variant>.svg` | Self-contained, no external refs, valid XML (verified). |
| App icon | `.svg` (vector) + `.png` (256², raster export) + `.ico` (16–256, multi-size) | `app-icon.<ext>` | PNG/ICO derived from `assets/mathmotion_app_icon.png` with Pillow. |
| Favicon | `.svg` | `favicon.svg` | Browsers accepting SVG use this; for legacy `.ico` favicons, export from `favicon.svg` or `app-icon.ico` at implementation time. |
| Palette | `.json` | `palette.json` | Machine-readable; syncs with scene format §7.2. |
| Original rasters | `.png` | `assets/*.png` | **Do not modify** — they are the reference masters until a vector original exists. |
