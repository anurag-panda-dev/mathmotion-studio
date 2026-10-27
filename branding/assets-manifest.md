# Assets manifest

Every brand asset in this repository: what it is, where it came from, and what is still missing.

> Verification for the 2026-10-27 rebuild: SVG well-formedness via `xml.etree`, JSON parse of `palette.json`, pixel-sampled color values (recorded in [`palette.json`](palette.json)), headless-browser renders of all six SVGs, and pixel diffs against the raster masters (numbers below).

## Original references (do not modify)

| Path | Type | Dimensions | Origin | Status |
|---|---|---|---|---|
| `assets/mathmotion_logo_light.png` | Raster logo (light) | 885 × 225 RGB | Provided project asset | **Authoritative master** for the light lockup |
| `assets/mathmotion_logo_dark.png` | Raster logo (dark) | 500 × 155 RGB | Provided project asset | **Authoritative master** for the dark lockup (different layout/margins than the light one) |
| `assets/mathmotion_app_icon.png` | Raster app icon | 310 × 290 RGB | Provided project asset | **Authoritative master** for the icon |

## Tool-generated vector references (provided 2026-10-27, do not modify)

| Path | Produced by | Used for |
|---|---|---|
| `assets/cleanvector-sample.svg` | potrace 1.16 (vectorization tool used by the project owner) | **Ink layer of the branding SVGs**: the mark silhouette and the outlined MATHMOTION/STUDIO letterforms, embedded verbatim by the builder |
| `assets/mathmotion_logo_light.svg` | 4-color vectorization tool (same owner) | **Reference only — not used in any output.** Its geometry is correct (its violet path matches our own mask segmentation exactly: bbox 58,33–300,185) but the trace carries edge artifacts: furry outlines and a `#8f93a6` path of 41 anti-aliasing halo fragments; its quantized colors (`#0b1a2f`, `#6649da`) are also off-palette. Superseded by the potrace outlines + fresh mask traces. |

## Generated brand files

All six SVGs are **generated** — not hand-drawn — by [`tools/build_brand_svgs.py`](../tools/build_brand_svgs.py). Do not edit them by hand; change the inputs or the script and regenerate.

| File | Built from | Notes |
|---|---|---|
| `branding/logo-primary.svg` | potrace ink layer (light) + violet mask traced from the light master | viewBox 885×225, matching the raster grid |
| `branding/logo-dark.svg` | violet mark + ivory letters traced from the **dark** master | viewBox 500×155 — the dark master has different margins and a different mark/letter scale (0.511 vs 0.575), so this is not a recolor of the light file |
| `branding/logo-monochrome.svg` | potrace ink layer, `currentColor` | |
| `branding/logo-symbol.svg` | potrace ink layer + violet mask, cropped viewBox (32,22)–(305,215) | |
| `branding/app-icon.svg` | ivory + violet masks traced from the icon master on a navy plate | viewBox 512×512; icon content mapped from the 310×290 raster grid |
| `branding/favicon.svg` | same composition as the app icon at 256×256 | full mark incl. inner loop; legibility comes from size, not simplification |

**How the builder works:** the potrace sample's mark silhouette merges rings, dots and trajectory into one contour, so it cannot be color-split. The builder keeps that sample for the ink layer and re-traces *color masks* (violet/ivory, pixel-classified from the raster masters) with the potrace algorithm (pure-Python `potracer`) to produce the separate violet-trajectory and icon layers. Trace parameters (`alphamax=1.33`, `opttolerance=0.4`, no mask dilation) were chosen by measured pixel-diff against the masters — the potrace defaults mangled the dark master's small letterforms.

**Measured fidelity (headless-browser render vs. raster master, mean absolute pixel difference / share of pixels >40):**

| Output | mean | px > 40 |
|---|---|---|
| `logo-primary.svg` vs light master | 3.84 | 2.30% |
| `logo-dark.svg` vs dark master | 7.68 | 4.89% |
| `app-icon.svg` vs icon master | 8.82 | 4.97% |

Remaining differences are anti-aliasing and edge-fit noise (visually verified with 4× zoom crops of letterforms, ring/trajectory crossings and the icon frame; no seam artifacts at color boundaries).

Requirements to regenerate: `numpy`, `Pillow`, `potracer` (`pip install potracer`).

## Derived exports (generated, not hand-drawn)

| Path | Type | How it was made | Verification |
|---|---|---|---|
| `branding/app-icon.png` | 256 × 256 RGB PNG | Pillow: icon master padded to a 310 × 310 square (navy `#061830` fill), downscaled with LANCZOS | `Image.open(…).size == (256, 256)` |
| `branding/app-icon.ico` | Multi-size ICO | Pillow from the same square canvas; embedded sizes: 16, 24, 32, 48, 64, 128, 256 | `info['sizes']` read back: all 7 present |

No upscaled or placeholder images were created; the 256px export is a downscale of the 310px original. (These raster exports derive from the icon PNG directly, so they are unaffected by SVG rebuilds.)

## Machine-readable palette

| Path | Contents | Sync obligations |
|---|---|---|
| [`branding/palette.json`](palette.json) | 3 measured brand colors (+ observed ranges), 12 scene-format colors, 2 themes, planned UI neutrals, computed WCAG ratios | Must match [`prompts/SCENE_FORMAT_SPEC.md` §7.2](../prompts/SCENE_FORMAT_SPEC.md) and the validator palette in `tools/validate_scene.py` |

The SVG outputs use these canonical palette values (`#061830`, `#6A4AEE`, `#F1F3EA`), **not** the color-trace tool's quantized hexes.

## Missing deliverables (explicit, not forgotten)

| Deliverable | Why missing | What would satisfy it |
|---|---|---|
| Original designer vector (`.ai`/`.svg` source) | Never supplied — repository started from PNGs; current vectors are *traces* of those PNGs | The designer's source file; outputs would then be rebuilt or verified against it |
| Brand typeface + license | Wordmark font still unidentified — but **logo rendering no longer depends on it** (the wordmark is outlined path data traced from the rasters) | Font name/license only matters for future *typeset* uses (documents, UI headings), not for the logo files |
| `favicon.ico` (legacy 16/32/48 bundle) | Not required for modern browsers; no HTML app exists yet | Export from `branding/favicon.svg`/`app-icon.ico` when the web frontend exists |
| Official 512/1024 marketing PNGs | No store/listing exists | Downscale exports from `app-icon.svg` at implementation time |

## Documentation references

All brand file references in this repository point at paths that exist in this manifest. Cross-checking those references is part of the consistency routine in [`docs/TESTING.md`](../docs/TESTING.md).
