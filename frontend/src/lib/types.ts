/**
 * TypeScript mirrors of the FastAPI backend's Pydantic response/request models
 * (backend/app/schemas/api.py and backend/app/schemas/scene.py).
 *
 * Field names here must match the JSON the backend actually emits — they are
 * snake_case, exactly as in the Pydantic models.
 */

/* ------------------------------------------------------------------ */
/* Shared enums                                                        */
/* ------------------------------------------------------------------ */

export const QUALITIES = ["preview", "standard", "high"] as const
export type Quality = (typeof QUALITIES)[number]

export const ASPECT_RATIOS = ["16:9", "9:16", "1:1"] as const
export type AspectRatio = (typeof ASPECT_RATIOS)[number]

export const APP_THEMES = ["light", "dark", "system"] as const
export type AppTheme = (typeof APP_THEMES)[number]

export const PROMPT_STYLES = [
  "intuitive",
  "step-by-step",
  "visual proof",
  "worked example",
  "revision",
] as const
export type PromptStyle = (typeof PROMPT_STYLES)[number]

export const DIFFICULTIES = ["basic", "standard", "advanced"] as const
export type Difficulty = (typeof DIFFICULTIES)[number]

export const JOB_STATES = [
  "queued",
  "validating",
  "preparing",
  "rendering",
  "postprocessing",
  "completed",
  "failed",
  "cancelling",
  "cancelled",
] as const
export type JobState = (typeof JOB_STATES)[number]

/** States in which a job is still in flight (matches backend ACTIVE_STATES). */
export const ACTIVE_JOB_STATES: readonly JobState[] = [
  "queued",
  "validating",
  "preparing",
  "rendering",
  "postprocessing",
  "cancelling",
]

export function isActiveJobState(status: JobState): boolean {
  return ACTIVE_JOB_STATES.includes(status)
}

/* ------------------------------------------------------------------ */
/* Health & diagnostics                                                */
/* ------------------------------------------------------------------ */

export interface DependencyStatus {
  name: string
  available: boolean
  version: string | null
  detail: string | null
  required_for: string
}

export interface HealthResponse {
  status: "ok" | "degraded"
  version: string
  scene_format_version: string
  python: string
  dependencies: DependencyStatus[]
  frontend_built: boolean
  directories: { data: string; output: string; logs: string; repo: string }
}

export interface DiagnosticsResponse {
  health: HealthResponse
  storage: { data_bytes: number; output_bytes: number; total_bytes: number }
  render_concurrency: number
  rate_limit: { window_s: number; max_requests: number }
  job_counts: Partial<Record<JobState, number>>
}

/* ------------------------------------------------------------------ */
/* Prompt generation                                                   */
/* ------------------------------------------------------------------ */

export interface PromptRequest {
  topic: string
  grade: string
  branch?: string | null
  language?: string
  style?: PromptStyle
  duration?: number
  aspect_ratio?: AspectRatio
  difficulty?: Difficulty
  colors?: string | null
  include_recap?: boolean
  include_practice?: boolean
  include_voiceover?: boolean
  additional?: string | null
}

export interface PromptResponse {
  prompt: string
  compact_prompt: string
  filename: string
  char_count: number
  compact_char_count: number
  compact_reduced_percent: number
}

/* ------------------------------------------------------------------ */
/* Scene reference                                                     */
/* ------------------------------------------------------------------ */

export interface ExampleListItem {
  name: string
  title: string
  topic: string
  grade: string
  size_bytes: number
}

export interface ExampleListResponse {
  examples: ExampleListItem[]
}

export interface ExampleContentResponse {
  name: string
  markdown: string
}

export interface SchemaReferenceResponse {
  scene_format_version: string
  specification: string
  object_kinds: string[]
  actions: string[]
  colors: string[]
  frames: Record<AspectRatio, [number, number, number, number]>
  lesson_schema: Record<string, unknown>
  scene_schema: Record<string, unknown>
}

/* ------------------------------------------------------------------ */
/* Validation                                                          */
/* ------------------------------------------------------------------ */

export type IssueSeverity = "error" | "warning"

export interface ValidationIssueModel {
  severity: IssueSeverity
  category: string
  message: string
  scene: string | null
  path: string | null
  line: number | null
  suggestion: string | null
}

export interface VerificationResultModel {
  id: string
  kind: "numeric" | "symbolic"
  description: string
  status: "passed" | "failed" | "unavailable"
  message: string
  expected: number
  actual: number | null
}

export interface SceneTimelineEntry {
  id: string
  title: string
  type: string
  duration_s: number
  narration: string | null
  object_count: number
  action_count: number
  formulas: string[]
}

export interface SceneSummary {
  title: string
  topic: string
  grade: string
  language: string
  duration_minutes: number
  aspect_ratio: AspectRatio
  theme: string
  objectives: string[]
  prerequisites: string[]
  recap: string | null
  practice_questions: string[]
  scenes: SceneTimelineEntry[]
  total_duration_s: number
  object_count: number
  action_count: number
}

export interface ValidationReportResponse {
  valid: boolean
  schema_version: string | null
  errors: ValidationIssueModel[]
  warnings: ValidationIssueModel[]
  verification: VerificationResultModel[]
  summary: SceneSummary | null
}

export interface ValidateRequest {
  markdown: string
  filename?: string | null
  verify?: boolean
}

/* ------------------------------------------------------------------ */
/* Lessons                                                             */
/* ------------------------------------------------------------------ */

export interface ImportResponse {
  lesson_id: string
  filename: string
  report: ValidationReportResponse
}

export interface LessonListItem {
  lesson_id: string
  title: string
  topic: string
  grade: string
  language: string
  schema_version: string | null
  filename: string
  valid: boolean | null
  error_count: number
  warning_count: number
  duration_minutes: number | null
  aspect_ratio: string | null
  created_at: string
  updated_at: string
  last_render_at: string | null
  job_count: number
}

export interface LessonDetail extends LessonListItem {
  markdown: string
  report: ValidationReportResponse | null
  summary: SceneSummary | null
  jobs: JobStatusModel[]
}

export interface SourceUpdateRequest {
  markdown: string
}

/* ------------------------------------------------------------------ */
/* Render jobs                                                         */
/* ------------------------------------------------------------------ */

export interface RenderSettingsModel {
  quality: Quality
  aspect_ratio: AspectRatio
  frame_rate: number
}

export interface JobStatusModel {
  job_id: string
  lesson_id: string
  lesson_title: string | null
  status: JobState
  progress: number | null
  determinate: boolean
  phase: string
  settings: RenderSettingsModel
  output_path: string | null
  output_url: string | null
  error_summary: string | null
  technical_detail: string | null
  attempt: number
  created_at: string
  started_at: string | null
  finished_at: string | null
}

export interface JobListResponse {
  jobs: JobStatusModel[]
}

export interface CreateJobRequest {
  quality?: Quality | null
  aspect_ratio?: AspectRatio | null
}

export interface LogsResponse {
  job_id: string
  logs: string
  truncated: boolean
}

export interface CancelResponse {
  job_id: string
  status: JobState
}

/* ------------------------------------------------------------------ */
/* Settings                                                            */
/* ------------------------------------------------------------------ */

export interface AppSettingsModel {
  output_dir: string
  default_quality: Quality
  default_aspect_ratio: AspectRatio
  theme: AppTheme
  language: string
}

export interface AppSettingsPatch {
  output_dir?: string | null
  default_quality?: Quality | null
  default_aspect_ratio?: AspectRatio | null
  theme?: AppTheme | null
  language?: string | null
}

export interface OpenOutputResponse {
  opened: boolean
  path: string
  detail: string | null
}
