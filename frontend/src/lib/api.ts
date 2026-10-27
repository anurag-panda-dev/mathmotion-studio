/**
 * Minimal typed fetch client for the local MathMotion Studio API.
 *
 * The backend answers errors in one of two shapes:
 *   1. Its own envelope  { error: { code, message, request_id, detail? } }
 *   2. FastAPI's built-in request-schema shape  { detail: [...] } on 422
 * Both are normalised into a single ApiError so UI code never has to branch.
 */

import type {
  AppSettingsModel,
  AppSettingsPatch,
  CancelResponse,
  CreateJobRequest,
  DiagnosticsResponse,
  ExampleContentResponse,
  ExampleListResponse,
  HealthResponse,
  ImportResponse,
  JobListResponse,
  JobStatusModel,
  LessonDetail,
  LessonListItem,
  LogsResponse,
  OpenOutputResponse,
  PromptRequest,
  PromptResponse,
  SchemaReferenceResponse,
  ValidateRequest,
  ValidationReportResponse,
} from "./types"
import { toQueryString } from "./utils"

export const API_BASE = "/api/v1"

/** Maximum scene.md size accepted by the backend (Scene format v1.0, 512 KiB). */
export const MAX_SCENE_BYTES = 512 * 1024

export interface FieldIssue {
  path: string
  message: string
}

export class ApiError extends Error {
  readonly status: number
  readonly code: string
  readonly requestId: string | null
  readonly detail: unknown
  readonly fieldIssues: FieldIssue[]

  constructor(init: {
    status: number
    code: string
    message: string
    requestId?: string | null
    detail?: unknown
    fieldIssues?: FieldIssue[]
  }) {
    super(init.message)
    this.name = "ApiError"
    this.status = init.status
    this.code = init.code
    this.requestId = init.requestId ?? null
    this.detail = init.detail
    this.fieldIssues = init.fieldIssues ?? []
  }
}

interface EnvelopeError {
  code?: unknown
  message?: unknown
  request_id?: unknown
  detail?: unknown
}

interface FastApiDetailItem {
  loc?: unknown
  msg?: unknown
}

function normaliseFastApiDetail(detail: unknown): { message: string; fieldIssues: FieldIssue[] } {
  if (!Array.isArray(detail)) {
    return { message: "The request was rejected by the server.", fieldIssues: [] }
  }
  const fieldIssues: FieldIssue[] = []
  for (const raw of detail as FastApiDetailItem[]) {
    if (!raw || typeof raw !== "object") continue
    const path = Array.isArray(raw.loc) ? raw.loc.map(String).join(".") : ""
    const message = typeof raw.msg === "string" ? raw.msg : "Invalid value"
    fieldIssues.push({ path, message })
  }
  const message =
    fieldIssues.length > 0
      ? fieldIssues.map((issue) => issue.message).join(" ")
      : "The request was rejected by the server."
  return { message, fieldIssues }
}

function parseBody(payload: unknown): { body: unknown; raw: string | null } {
  if (typeof payload === "string") {
    return { body: payload, raw: payload.length > 0 ? payload : null }
  }
  return { body: payload, raw: null }
}

async function toApiError(response: Response): Promise<ApiError> {
  const requestId = response.headers.get("X-Request-ID")
  const contentType = response.headers.get("Content-Type") ?? ""
  let payload: unknown = null

  if (contentType.includes("application/json")) {
    try {
      payload = await response.json()
    } catch {
      payload = null
    }
  } else {
    const { body } = parseBody(await response.text().catch(() => ""))
    payload = body
  }

  // Shape 1: the application's { error: {...} } envelope.
  if (payload && typeof payload === "object" && "error" in payload) {
    const envelope = (payload as { error: EnvelopeError }).error ?? {}
    const message =
      typeof envelope.message === "string" && envelope.message.trim().length > 0
        ? envelope.message
        : `The request failed (HTTP ${response.status}).`
    return new ApiError({
      status: response.status,
      code: typeof envelope.code === "string" ? envelope.code : "unknown",
      message,
      requestId:
        typeof envelope.request_id === "string" && envelope.request_id !== "-"
          ? envelope.request_id
          : requestId,
      detail: envelope.detail ?? null,
    })
  }

  // Shape 2: FastAPI's request-validation payload.
  if (payload && typeof payload === "object" && "detail" in payload) {
    const { detail } = payload
    const { message, fieldIssues } = normaliseFastApiDetail(detail)
    return new ApiError({
      status: response.status,
      code: "validation_failed",
      message,
      requestId,
      detail,
      fieldIssues,
    })
  }

  return new ApiError({
    status: response.status,
    code: "unknown",
    message: `The request failed (HTTP ${response.status}).`,
    requestId,
    detail: typeof payload === "string" && payload ? payload : null,
  })
}

interface RequestOptions {
  method?: "GET" | "POST" | "PATCH" | "DELETE"
  body?: unknown
  signal?: AbortSignal
  /** Suppress the error entirely and return null (used for optional probes). */
  tolerateFailure?: boolean
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, signal } = options

  let response: Response
  try {
    response = await fetch(`${API_BASE}${path}`, {
      method,
      headers: body !== undefined ? { "Content-Type": "application/json" } : undefined,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal,
    })
  } catch (cause) {
    if (cause instanceof DOMException && cause.name === "AbortError") throw cause
    throw new ApiError({
      status: 0,
      code: "network_error",
      message:
        "Could not reach the MathMotion Studio service. Check that the application is still running, then try again.",
      detail: cause instanceof Error ? cause.message : String(cause),
    })
  }

  if (!response.ok) {
    const error = await toApiError(response)
    if (options.tolerateFailure) return null as T
    throw error
  }

  if (response.status === 204) return undefined as T

  const text = await response.text()
  if (!text) return undefined as T
  try {
    return JSON.parse(text) as T
  } catch {
    throw new ApiError({
      status: response.status,
      code: "invalid_response",
      message: "The application received an unexpected response from its local service.",
      detail: text.slice(0, 500),
    })
  }
}

/* ------------------------------------------------------------------ */
/* Endpoint-specific helpers                                           */
/* ------------------------------------------------------------------ */

export const api = {
  health: (signal?: AbortSignal) => apiRequest<HealthResponse>("/health", { signal }),

  diagnostics: (signal?: AbortSignal) => apiRequest<DiagnosticsResponse>("/diagnostics", { signal }),

  generatePrompt: (body: PromptRequest) =>
    apiRequest<PromptResponse>("/prompt", { method: "POST", body }),

  schemaReference: (signal?: AbortSignal) =>
    apiRequest<SchemaReferenceResponse>("/reference/schema", { signal }),

  listExamples: (signal?: AbortSignal) =>
    apiRequest<ExampleListResponse>("/reference/examples", { signal }),

  getExample: (name: string, signal?: AbortSignal) =>
    apiRequest<ExampleContentResponse>(`/reference/examples/${encodeURIComponent(name)}`, { signal }),

  validateScene: (body: ValidateRequest) =>
    apiRequest<ValidationReportResponse>("/scenes/validate", { method: "POST", body }),

  importLesson: (body: ValidateRequest) =>
    apiRequest<ImportResponse>("/lessons", { method: "POST", body }),

  listLessons: (
    params: { search?: string; sort?: string; topic?: string; grade?: string } = {},
    signal?: AbortSignal,
  ) => apiRequest<LessonListItem[]>(`/lessons${toQueryString(params)}`, { signal }),

  getLesson: (lessonId: string, signal?: AbortSignal) =>
    apiRequest<LessonDetail>(`/lessons/${encodeURIComponent(lessonId)}`, { signal }),

  updateLessonSource: (lessonId: string, markdown: string) =>
    apiRequest<ImportResponse>(`/lessons/${encodeURIComponent(lessonId)}/source`, {
      method: "PATCH",
      body: { markdown },
    }),

  deleteLesson: (lessonId: string) =>
    apiRequest<void>(`/lessons/${encodeURIComponent(lessonId)}`, { method: "DELETE" }),

  createJob: (lessonId: string, body: CreateJobRequest) =>
    apiRequest<JobStatusModel>(`/lessons/${encodeURIComponent(lessonId)}/jobs`, {
      method: "POST",
      body,
    }),

  listJobs: (params: { lesson_id?: string } = {}, signal?: AbortSignal) =>
    apiRequest<JobListResponse>(`/jobs${toQueryString(params)}`, { signal }),

  getJob: (jobId: string, signal?: AbortSignal) =>
    apiRequest<JobStatusModel>(`/jobs/${encodeURIComponent(jobId)}`, { signal }),

  getJobLogs: (jobId: string, signal?: AbortSignal) =>
    apiRequest<LogsResponse>(`/jobs/${encodeURIComponent(jobId)}/logs`, { signal }),

  cancelJob: (jobId: string) =>
    apiRequest<CancelResponse>(`/jobs/${encodeURIComponent(jobId)}/cancel`, { method: "POST" }),

  retryJob: (jobId: string) =>
    apiRequest<JobStatusModel>(`/jobs/${encodeURIComponent(jobId)}/retry`, { method: "POST" }),

  getSettings: (signal?: AbortSignal) => apiRequest<AppSettingsModel>("/settings", { signal }),

  updateSettings: (patch: AppSettingsPatch) =>
    apiRequest<AppSettingsModel>("/settings", { method: "PATCH", body: patch }),

  openOutputFolder: () =>
    apiRequest<OpenOutputResponse>("/settings/open-output", { method: "POST" }),
}

/** Absolute-in-app URL for streaming a rendered video. */
export function jobVideoUrl(jobId: string): string {
  return `${API_BASE}/media/${encodeURIComponent(jobId)}/video`
}

/** Absolute-in-app URL for downloading a rendered video as an attachment. */
export function jobDownloadUrl(jobId: string): string {
  return `${API_BASE}/media/${encodeURIComponent(jobId)}/download`
}

/** Human-facing explanation for an unknown failure. */
export function describeError(error: unknown): string {
  if (error instanceof ApiError) return error.message
  if (error instanceof Error) return error.message
  return "Something went wrong. Please try again."
}
