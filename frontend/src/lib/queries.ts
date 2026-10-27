/**
 * TanStack Query hooks wrapping the local API.
 *
 * Server state (lessons, jobs, settings, health) lives here so screens stay
 * declarative and job polling is centralised rather than scattered.
 */

import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseMutationResult,
  type UseQueryResult,
} from "@tanstack/react-query"
import { api, describeError, type ApiError } from "./api"
import type {
  AppSettingsModel,
  AppSettingsPatch,
  CreateJobRequest,
  DiagnosticsResponse,
  ExampleContentResponse,
  ExampleListResponse,
  HealthResponse,
  ImportResponse,
  JobStatusModel,
  LessonDetail,
  LessonListItem,
  LogsResponse,
  PromptRequest,
  PromptResponse,
  ValidationReportResponse,
} from "./types"
import { isActiveJobState } from "./types"

export const queryKeys = {
  health: ["health"] as const,
  diagnostics: ["diagnostics"] as const,
  settings: ["settings"] as const,
  schemaReference: ["reference", "schema"] as const,
  examples: ["reference", "examples"] as const,
  example: (name: string) => ["reference", "examples", name] as const,
  lessons: (params: Record<string, string>) => ["lessons", params] as const,
  lesson: (lessonId: string) => ["lessons", "detail", lessonId] as const,
  jobs: (params: Record<string, string>) => ["jobs", params] as const,
  job: (jobId: string) => ["jobs", "detail", jobId] as const,
  jobLogs: (jobId: string) => ["jobs", "logs", jobId] as const,
}

/** How often an in-flight render job is polled. */
export const JOB_POLL_MS = 1500

/* ------------------------------------------------------------------ */
/* Health, diagnostics, settings                                       */
/* ------------------------------------------------------------------ */

export function useHealth(): UseQueryResult<HealthResponse> {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: ({ signal }) => api.health(signal),
    staleTime: 30_000,
    refetchOnWindowFocus: true,
  })
}

export function useDiagnostics(enabled = true): UseQueryResult<DiagnosticsResponse> {
  return useQuery({
    queryKey: queryKeys.diagnostics,
    queryFn: ({ signal }) => api.diagnostics(signal),
    enabled,
    staleTime: 15_000,
  })
}

export function useSettings(): UseQueryResult<AppSettingsModel> {
  return useQuery({
    queryKey: queryKeys.settings,
    queryFn: ({ signal }) => api.getSettings(signal),
    staleTime: 60_000,
  })
}

export function useUpdateSettings(): UseMutationResult<
  AppSettingsModel,
  ApiError,
  AppSettingsPatch
> {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (patch: AppSettingsPatch) => api.updateSettings(patch),
    onSuccess: (settings) => {
      queryClient.setQueryData(queryKeys.settings, settings)
      void queryClient.invalidateQueries({ queryKey: queryKeys.diagnostics })
    },
  })
}

/* ------------------------------------------------------------------ */
/* Prompt generation                                                   */
/* ------------------------------------------------------------------ */

export function useGeneratePrompt(): UseMutationResult<PromptResponse, ApiError, PromptRequest> {
  return useMutation({
    mutationFn: (body: PromptRequest) => api.generatePrompt(body),
  })
}

/* ------------------------------------------------------------------ */
/* Reference (schema + examples)                                       */
/* ------------------------------------------------------------------ */

export function useExampleList(enabled = true): UseQueryResult<ExampleListResponse> {
  return useQuery({
    queryKey: queryKeys.examples,
    queryFn: ({ signal }) => api.listExamples(signal),
    enabled,
    staleTime: 5 * 60_000,
  })
}

export function useExample(
  name: string | null,
): UseQueryResult<ExampleContentResponse, ApiError> {
  return useQuery({
    queryKey: queryKeys.example(name ?? ""),
    queryFn: ({ signal }) => api.getExample(name as string, signal),
    enabled: Boolean(name),
    staleTime: 5 * 60_000,
  })
}

/* ------------------------------------------------------------------ */
/* Lessons                                                             */
/* ------------------------------------------------------------------ */

export interface LessonQueryParams {
  search?: string
  sort?: string
  topic?: string
  grade?: string
}

export function useLessons(params: LessonQueryParams): UseQueryResult<LessonListItem[]> {
  const serialised = {
    search: params.search ?? "",
    sort: params.sort ?? "created_desc",
    topic: params.topic ?? "",
    grade: params.grade ?? "",
  }
  return useQuery({
    queryKey: queryKeys.lessons(serialised),
    queryFn: ({ signal }) => api.listLessons(serialised, signal),
    staleTime: 5_000,
  })
}

export function useLesson(
  lessonId: string | undefined,
): UseQueryResult<LessonDetail, ApiError> {
  return useQuery({
    queryKey: queryKeys.lesson(lessonId ?? ""),
    queryFn: ({ signal }) => api.getLesson(lessonId as string, signal),
    enabled: Boolean(lessonId),
  })
}

export function useImportLesson(): UseMutationResult<ImportResponse, ApiError, string> {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (markdown: string) =>
      api.importLesson({ markdown, filename: "scene.md", verify: true }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["lessons"] })
      void queryClient.invalidateQueries({ queryKey: ["jobs"] })
    },
  })
}

export function useValidateScene(): UseMutationResult<ValidationReportResponse, ApiError, string> {
  return useMutation({
    mutationFn: (markdown: string) =>
      api.validateScene({ markdown, filename: "scene.md", verify: true }),
  })
}

export function useUpdateLessonSource(
  lessonId: string,
): UseMutationResult<ImportResponse, ApiError, string> {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (markdown: string) => api.updateLessonSource(lessonId, markdown),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["lessons"] })
    },
  })
}

export function useDeleteLesson(): UseMutationResult<void, ApiError, string> {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (lessonId: string) => api.deleteLesson(lessonId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["lessons"] })
      void queryClient.invalidateQueries({ queryKey: ["jobs"] })
    },
  })
}

/* ------------------------------------------------------------------ */
/* Render jobs                                                         */
/* ------------------------------------------------------------------ */

export function useJobs(lessonId?: string): UseQueryResult<{ jobs: JobStatusModel[] }> {
  const params: Record<string, string> = lessonId ? { lesson_id: lessonId } : {}
  return useQuery({
    queryKey: queryKeys.jobs(params),
    queryFn: ({ signal }) => api.listJobs(params, signal),
    refetchInterval: (query) => {
      const jobs = query.state.data?.jobs ?? []
      return jobs.some((job) => isActiveJobState(job.status)) ? JOB_POLL_MS : false
    },
  })
}

/**
 * A single render job. Polls while the job is in flight so the preview page
 * and the jobs list stay live without a websocket.
 */
export function useJob(jobId: string | undefined): UseQueryResult<JobStatusModel, ApiError> {
  return useQuery({
    queryKey: queryKeys.job(jobId ?? ""),
    queryFn: ({ signal }) => api.getJob(jobId as string, signal),
    enabled: Boolean(jobId),
    refetchInterval: (query) =>
      query.state.data && isActiveJobState(query.state.data.status) ? JOB_POLL_MS : false,
  })
}

export function useJobLogs(
  jobId: string | undefined,
  enabled: boolean,
): UseQueryResult<LogsResponse, ApiError> {
  return useQuery({
    queryKey: queryKeys.jobLogs(jobId ?? ""),
    queryFn: ({ signal }) => api.getJobLogs(jobId as string, signal),
    enabled: Boolean(jobId) && enabled,
    refetchInterval: (query) =>
      query.state.data !== undefined && enabled ? 3000 : false,
  })
}

export function useCreateJob(): UseMutationResult<
  JobStatusModel,
  ApiError,
  { lessonId: string; request: CreateJobRequest }
> {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ lessonId, request }: { lessonId: string; request: CreateJobRequest }) =>
      api.createJob(lessonId, request),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["jobs"] })
      void queryClient.invalidateQueries({ queryKey: ["lessons"] })
    },
  })
}

export function useCancelJob(): UseMutationResult<unknown, ApiError, string> {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (jobId: string) => api.cancelJob(jobId),
    onSuccess: (_data, jobId) => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.job(jobId) })
      void queryClient.invalidateQueries({ queryKey: ["jobs"] })
    },
  })
}

export function useRetryJob(): UseMutationResult<JobStatusModel, ApiError, string> {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (jobId: string) => api.retryJob(jobId),
    onSuccess: (job) => {
      void queryClient.invalidateQueries({ queryKey: ["jobs"] })
      void queryClient.invalidateQueries({ queryKey: ["lessons"] })
      void queryClient.invalidateQueries({ queryKey: queryKeys.job(job.job_id) })
    },
  })
}

export { describeError }
