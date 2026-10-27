/**
 * Display labels and reference data shared across screens.
 *
 * Labels are teacher-facing plain language; enum values themselves stay in
 * types.ts so the wire format is never confused with presentation.
 */

import type {
  AppTheme,
  AspectRatio,
  Difficulty,
  JobState,
  PromptStyle,
  Quality,
} from "./types"

export const QUALITY_LABELS: Record<Quality, string> = {
  preview: "Preview",
  standard: "Standard",
  high: "High",
}

export const QUALITY_DESCRIPTIONS: Record<Quality, string> = {
  preview: "Fastest — small resolution, for checking a lesson quickly.",
  standard: "Balanced quality and speed. Good for classroom use.",
  high: "Slowest — largest resolution, for final export.",
}

export const ASPECT_RATIO_LABELS: Record<AspectRatio, string> = {
  "16:9": "16:9 — Widescreen",
  "9:16": "9:16 — Vertical",
  "1:1": "1:1 — Square",
}

export const ASPECT_RATIO_DESCRIPTIONS: Record<AspectRatio, string> = {
  "16:9": "Standard classroom projector and monitor shape.",
  "9:16": "Vertical video for phones.",
  "1:1": "Square format for embedding in documents.",
}

export const STYLE_LABELS: Record<PromptStyle, string> = {
  intuitive: "Intuitive — build the idea from everyday intuition",
  "step-by-step": "Step-by-step — work through each stage explicitly",
  "visual proof": "Visual proof — show why the result must hold",
  "worked example": "Worked example — one problem solved completely",
  revision: "Revision — a fast recap for students who have seen it",
}

export const DIFFICULTY_LABELS: Record<Difficulty, string> = {
  basic: "Basic",
  standard: "Standard",
  advanced: "Advanced",
}

export const APP_THEME_LABELS: Record<AppTheme, string> = {
  light: "Light",
  dark: "Dark",
  system: "Match system",
}

export const JOB_STATE_LABELS: Record<JobState, string> = {
  queued: "Queued",
  validating: "Validating",
  preparing: "Preparing",
  rendering: "Rendering",
  postprocessing: "Finishing up",
  completed: "Completed",
  failed: "Failed",
  cancelling: "Cancelling…",
  cancelled: "Cancelled",
}

/** Tone used for status chips; paired with a text label, never colour alone. */
export type Tone = "neutral" | "primary" | "success" | "warning" | "destructive"

export const JOB_STATE_TONES: Record<JobState, Tone> = {
  queued: "neutral",
  validating: "primary",
  preparing: "primary",
  rendering: "primary",
  postprocessing: "primary",
  completed: "success",
  failed: "destructive",
  cancelling: "warning",
  cancelled: "neutral",
}

/* ------------------------------------------------------------------ */
/* Scene format reference (v1.0)                                       */
/* ------------------------------------------------------------------ */

/** The 12 colour names a scene.md may use (not the app chrome palette). */
export const SCENE_COLORS = [
  "amber",
  "black",
  "blue",
  "gray",
  "green",
  "ivory",
  "navy",
  "pink",
  "red",
  "teal",
  "violet",
  "white",
] as const

/** Approximate swatches for the Scene format palette, for the colour picker. */
export const SCENE_COLOR_SWATCHES: Record<(typeof SCENE_COLORS)[number], string> = {
  amber: "#E0A126",
  black: "#000000",
  blue: "#3B7DD8",
  gray: "#8A93A5",
  green: "#2E9E6B",
  ivory: "#F1F3EA",
  navy: "#061830",
  pink: "#D96BA0",
  red: "#D0402E",
  teal: "#2AA79B",
  violet: "#6A4AEE",
  white: "#FFFFFF",
}

export const SCENE_TYPES = [
  "intro",
  "explanation",
  "worked_example",
  "proof",
  "recap",
  "practice",
] as const

export const SCENE_TYPE_LABELS: Record<string, string> = {
  intro: "Introduction",
  explanation: "Explanation",
  worked_example: "Worked example",
  proof: "Proof",
  recap: "Recap",
  practice: "Practice",
}

export const SCENE_RENDER_THEMES = ["midnight", "ivory"] as const

export const KNOWN_DEPENDENCY_REPAIR_URLS: Record<string, string> = {
  manim: "https://docs.manim.community/en/stable/installation.html",
  ffmpeg: "https://ffmpeg.org/download.html",
  latex: "https://miktex.org/download",
}

/** Plain-language meaning of each optional dependency, shown in Settings. */
export const DEPENDENCY_HELP: Record<string, string> = {
  manim: "Manim is the animation engine. Without it, lessons cannot be rendered.",
  ffmpeg: "FFmpeg encodes the rendered frames into an MP4 video file.",
  latex:
    "LaTeX typesets advanced formulas. Simple lessons still work without it — the app falls back to Manim's built-in text renderer.",
}
