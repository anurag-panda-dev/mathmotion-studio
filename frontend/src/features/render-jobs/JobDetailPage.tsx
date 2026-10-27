import {
  ChevronDown,
  Download,
  FileText,
  FolderOpen,
  Play,
  RefreshCw,
  Trash2,
  XCircle,
} from "lucide-react"
import * as React from "react"
import { Link, useNavigate, useParams } from "react-router"
import { ConfirmDialog } from "@/components/ConfirmDialog"
import { ErrorPanel } from "@/components/ErrorPanel"
import { PageHeader } from "@/components/PageHeader"
import { JobStateChip } from "@/components/StatusChip"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Progress } from "@/components/ui/progress"
import { Skeleton } from "@/components/ui/skeleton"
import { useToast } from "@/hooks/useToast"
import { api, describeError, jobDownloadUrl, jobVideoUrl } from "@/lib/api"
import { QUALITY_LABELS } from "@/lib/constants"
import {
  useCancelJob,
  useCreateJob,
  useDeleteLesson,
  useJob,
  useJobLogs,
  useRetryJob,
} from "@/lib/queries"
import { isActiveJobState } from "@/lib/types"
import { formatDateTime } from "@/lib/utils"

export function JobDetailPage() {
  const { jobId } = useParams<{ jobId: string }>()
  const navigate = useNavigate()
  const toast = useToast()

  const job = useJob(jobId)
  const cancelJob = useCancelJob()
  const retryJob = useRetryJob()
  const createJob = useCreateJob()
  const deleteLesson = useDeleteLesson()

  const [logsOpen, setLogsOpen] = React.useState(false)
  const [confirmCancel, setConfirmCancel] = React.useState(false)
  const [confirmDelete, setConfirmDelete] = React.useState(false)

  const status = job.data?.status
  const running = status !== undefined && isActiveJobState(status)
  const completed = status === "completed"

  const logs = useJobLogs(jobId, logsOpen)

  const handleCancel = () => {
    if (!jobId) return
    cancelJob.mutate(jobId, {
      onSuccess: () => {
        setConfirmCancel(false)
        toast.success("Cancelling render", "The job will stop shortly.")
      },
      onError: (error) => {
        setConfirmCancel(false)
        toast.error("Could not cancel the render", describeError(error))
      },
    })
  }

  const handleRetry = () => {
    if (!jobId) return
    retryJob.mutate(jobId, {
      onSuccess: (newJob) => {
        toast.success("Render restarted", `Attempt ${newJob.attempt} is now queued.`)
        void navigate(`/jobs/${newJob.job_id}`)
      },
      onError: (error) => toast.error("Could not restart the render", describeError(error)),
    })
  }

  const handleRenderAgain = () => {
    if (!job.data) return
    createJob.mutate(
      { lessonId: job.data.lesson_id, request: { quality: job.data.settings.quality } },
      {
        onSuccess: (newJob) => {
          toast.success("New render started", "Follow it here or on the jobs page.")
          void navigate(`/jobs/${newJob.job_id}`)
        },
        onError: (error) => toast.error("Could not start the render", describeError(error)),
      },
    )
  }

  const handleDelete = () => {
    if (!job.data) return
    deleteLesson.mutate(job.data.lesson_id, {
      onSuccess: () => {
        setConfirmDelete(false)
        toast.success("Lesson deleted", "The lesson and its renders were removed.")
        void navigate("/animations")
      },
      onError: (error) => {
        setConfirmDelete(false)
        toast.error("Could not delete the lesson", describeError(error))
      },
    })
  }

  if (job.isLoading) {
    return (
      <div className="grid gap-6">
        <Skeleton className="h-9 w-72" />
        <Skeleton className="aspect-video w-full max-w-3xl" />
        <Skeleton className="h-32" />
      </div>
    )
  }

  if (job.isError || !job.data) {
    return (
      <div className="grid gap-6">
        <PageHeader title="Render job not found" />
        <ErrorPanel
          error={job.error ?? new Error("This render job does not exist on this computer.")}
          title="Could not load this render"
        />
        <div>
          <Button asChild variant="secondary">
            <Link to="/jobs">Back to Rendering Jobs</Link>
          </Button>
        </div>
      </div>
    )
  }

  const detail = job.data

  return (
    <div className="grid gap-8">
      <PageHeader
        title={detail.lesson_title ?? "Render job"}
        guidance={`Started ${formatDateTime(detail.created_at)}${
          detail.started_at ? ` · ${detail.settings.quality} · ${detail.settings.aspect_ratio}` : ""
        }`}
        actions={
          <>
            {running && detail.status !== "cancelling" ? (
              <Button variant="secondary" onClick={() => setConfirmCancel(true)}>
                <XCircle className="size-4" aria-hidden />
                Cancel render
              </Button>
            ) : null}
            {detail.status === "failed" || detail.status === "cancelled" ? (
              <Button variant="secondary" onClick={handleRetry} disabled={retryJob.isPending}>
                <RefreshCw className="size-4" aria-hidden />
                Retry
              </Button>
            ) : null}
            {completed ? (
              <Button variant="secondary" onClick={handleRenderAgain} disabled={createJob.isPending}>
                <Play className="size-4" aria-hidden />
                Render again
              </Button>
            ) : null}
          </>
        }
      />

      {/* -------------------------------- Status -------------------------------- */}
      <div className="flex flex-wrap items-center gap-3">
        <JobStateChip status={detail.status} />
        <span className="text-sm text-muted-foreground">{detail.phase}</span>
        <Badge tone="neutral">Attempt {detail.attempt}</Badge>
        {detail.output_path ? (
          <span className="font-mono text-xs text-muted-foreground">{detail.output_path}</span>
        ) : null}
      </div>

      {running ? (
        <Card>
          <CardContent className="grid gap-3 py-5">
            <Progress
              value={detail.progress ?? undefined}
              indeterminate={!detail.determinate}
              aria-label={
                detail.determinate && detail.progress !== null
                  ? `Render progress ${Math.round(detail.progress * 100)} percent`
                  : "Render in progress"
              }
            />
            <p className="text-sm text-muted-foreground">
              {detail.determinate && detail.progress !== null
                ? `${Math.round(detail.progress * 100)}% — ${detail.phase}`
                : `${detail.phase} — Manim does not report exact progress here, so no percentage is shown.`}
            </p>
          </CardContent>
        </Card>
      ) : null}

      {detail.status === "failed" ? (
        <Alert tone="destructive">
          <AlertTitle>The animation could not be rendered</AlertTitle>
          <AlertDescription>
            <p>{detail.error_summary ?? "The render failed for an unknown reason."}</p>
            <p className="mt-2 text-xs opacity-90">
              Your lesson is untouched — fix the problem and press Retry.
            </p>
            <details className="mt-2 rounded-[var(--radius-control)] border border-destructive/20 bg-background/40 p-3">
              <summary className="flex cursor-pointer list-none items-center gap-1.5 text-xs font-medium">
                <ChevronDown className="size-3.5" aria-hidden />
                Technical details
              </summary>
              <dl className="mt-2 space-y-1 font-mono text-xs">
                <div>
                  <dt className="font-sans font-semibold">Job ID</dt>
                  <dd className="break-all">{detail.job_id}</dd>
                </div>
                {detail.technical_detail ? (
                  <div>
                    <dt className="font-sans font-semibold">Detail</dt>
                    <dd className="whitespace-pre-wrap break-all">{detail.technical_detail}</dd>
                  </div>
                ) : null}
              </dl>
            </details>
          </AlertDescription>
        </Alert>
      ) : null}

      {/* -------------------------------- Player -------------------------------- */}
      <div className="grid gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
        <Card className="overflow-hidden">
          <CardContent className="p-0">
            {completed ? (
              <video
                controls
                className="aspect-video w-full bg-black"
                src={jobVideoUrl(detail.job_id)}
                preload="metadata"
              >
                <track kind="captions" />
              </video>
            ) : (
              <div className="flex aspect-video w-full flex-col items-center justify-center gap-2 bg-surface-sunken p-6 text-center">
                <p className="text-sm font-medium">
                  {running ? "The video will appear here when the render finishes." : "No video yet."}
                </p>
                <p className="text-xs text-muted-foreground">
                  {running
                    ? "This page updates automatically."
                    : detail.status === "failed"
                      ? "Retry the render to produce a video."
                      : "Start a render from the lesson page."}
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Export & details</CardTitle>
            <CardDescription>Download the finished files or open the folder.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-5">
            <dl className="grid gap-2 text-sm">
              <Row label="Quality" value={QUALITY_LABELS[detail.settings.quality]} />
              <Row label="Aspect ratio" value={detail.settings.aspect_ratio} />
              <Row label="Frame rate" value={`${detail.settings.frame_rate} fps`} />
              <Row
                label="Finished"
                value={detail.finished_at ? formatDateTime(detail.finished_at) : "—"}
              />
            </dl>

            <div className="grid gap-2">
              <Button disabled={!completed} asChild={completed}>
                <a href={jobDownloadUrl(detail.job_id)} download>
                  <Download className="size-4" aria-hidden />
                  Download video
                </a>
              </Button>
              <Button variant="secondary" onClick={() => setLogsOpen(true)}>
                <ChevronDown className="size-4" aria-hidden />
                View render log
              </Button>
              <Button
                variant="secondary"
                onClick={() => {
                  api.openOutputFolder().then(
                    (result) => {
                      if (!result.opened) {
                        toast.error("Could not open the folder", result.detail ?? "Unknown reason.")
                      }
                    },
                    (error: unknown) => toast.error("Could not open the folder", describeError(error)),
                  )
                }}
              >
                <FolderOpen className="size-4" aria-hidden />
                Open output folder
              </Button>
              <Button variant="secondary" asChild>
                <Link to={`/lessons/${detail.lesson_id}`}>
                  <FileText className="size-4" aria-hidden />
                  Open lesson source
                </Link>
              </Button>
            </div>

            <div className="border-t border-border pt-4">
              <Button variant="destructiveOutline" size="sm" onClick={() => setConfirmDelete(true)}>
                <Trash2 className="size-4" aria-hidden />
                Delete lesson and output
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* -------------------------------- Logs -------------------------------- */}
      <Dialog open={logsOpen} onOpenChange={setLogsOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Render log</DialogTitle>
            <DialogDescription>
              Technical output from the render worker. Newest lines are kept (up to 256 KB).
              {logs.data?.truncated ? " This log has been truncated." : ""}
            </DialogDescription>
          </DialogHeader>
          {logs.isLoading ? (
            <Skeleton className="h-64" />
          ) : logs.isError ? (
            <ErrorPanel error={logs.error} title="Could not load the log" />
          ) : (
            <pre
              tabIndex={0}
              aria-label="Render log"
              className="scrollbar-slim max-h-80 overflow-auto rounded-[var(--radius-control)] border border-border bg-surface-sunken p-4 font-mono text-xs leading-relaxed whitespace-pre-wrap text-foreground"
            >
              {logs.data?.logs || "(The log is empty.)"}
            </pre>
          )}
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={confirmCancel}
        onOpenChange={setConfirmCancel}
        title="Cancel this render?"
        description="The render will stop. You can start it again at any time — your lesson is unchanged."
        confirmLabel="Cancel render"
        destructive
        busy={cancelJob.isPending}
        onConfirm={handleCancel}
      />

      <ConfirmDialog
        open={confirmDelete}
        onOpenChange={setConfirmDelete}
        title="Delete this lesson?"
        description={`“${detail.lesson_title ?? "This lesson"}”, its source file and all of its rendered videos will be permanently removed from this computer. This cannot be undone.`}
        confirmLabel="Delete everything"
        destructive
        busy={deleteLesson.isPending}
        onConfirm={handleDelete}
      />
    </div>
  )
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-3">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="text-right font-medium">{value}</dd>
    </div>
  )
}
