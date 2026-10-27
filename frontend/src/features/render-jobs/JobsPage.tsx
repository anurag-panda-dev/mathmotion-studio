import { LayoutList, RotateCcw, XCircle } from "lucide-react"
import * as React from "react"
import { Link } from "react-router"
import { ConfirmDialog } from "@/components/ConfirmDialog"
import { EmptyState } from "@/components/EmptyState"
import { ErrorPanel } from "@/components/ErrorPanel"
import { PageHeader } from "@/components/PageHeader"
import { JobStateChip } from "@/components/StatusChip"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Skeleton } from "@/components/ui/skeleton"
import { useToast } from "@/hooks/useToast"
import { describeError } from "@/lib/api"
import { useCancelJob, useJobs, useRetryJob } from "@/lib/queries"
import { isActiveJobState, type JobStatusModel } from "@/lib/types"
import { cn, formatDateTime, formatDuration } from "@/lib/utils"

export function JobsPage() {
  const jobs = useJobs()
  const toast = useToast()
  const cancelJob = useCancelJob()
  const retryJob = useRetryJob()
  const [pendingCancel, setPendingCancel] = React.useState<JobStatusModel | null>(null)

  const list = jobs.data?.jobs ?? []
  const activeCount = list.filter((job) => isActiveJobState(job.status)).length

  const handleCancel = () => {
    if (!pendingCancel) return
    cancelJob.mutate(pendingCancel.job_id, {
      onSuccess: () => {
        toast.success("Cancelling render", "The job will stop shortly.")
        setPendingCancel(null)
      },
      onError: (error) => toast.error("Could not cancel the render", describeError(error)),
    })
  }

  const handleRetry = (job: JobStatusModel) => {
    retryJob.mutate(job.job_id, {
      onSuccess: (newJob) => {
        toast.success("Render restarted", `Attempt ${newJob.attempt} is now queued.`)
      },
      onError: (error) => toast.error("Could not restart the render", describeError(error)),
    })
  }

  return (
    <div className="grid gap-6">
      <PageHeader
        title="Rendering Jobs"
        guidance={
          activeCount > 0
            ? `${activeCount} job${activeCount === 1 ? "" : "s"} in progress. Renders run one at a time; queued jobs start automatically.`
            : "Every render started on this computer, newest first."
        }
      />

      {jobs.isLoading ? (
        <div className="grid gap-3">
          <Skeleton className="h-20" />
          <Skeleton className="h-20" />
        </div>
      ) : jobs.isError ? (
        <ErrorPanel error={jobs.error} title="Could not load render jobs" />
      ) : list.length === 0 ? (
        <EmptyState
          icon={LayoutList}
          title="No render jobs yet"
          description="Import a lesson and press Render Animation — its progress will appear here in real time."
          action={
            <>
              <Button asChild>
                <Link to="/import">Import a lesson</Link>
              </Button>
              <Button asChild variant="secondary">
                <Link to="/animations">Open My Animations</Link>
              </Button>
            </>
          }
        />
      ) : (
        <ul className="grid gap-3">
          {list.map((job) => (
            <li key={job.job_id}>
              <Card>
                <div className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center">
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <Link
                        to={`/jobs/${job.job_id}`}
                        className="truncate text-base font-semibold underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-ring"
                      >
                        {job.lesson_title ?? "Untitled lesson"}
                      </Link>
                      <JobStateChip status={job.status} />
                      {job.attempt > 1 ? (
                        <span className="text-xs text-muted-foreground">attempt {job.attempt}</span>
                      ) : null}
                    </div>

                    <p className="mt-1 text-sm text-muted-foreground">
                      {job.phase} · {job.settings.quality} · {job.settings.aspect_ratio} ·{" "}
                      {job.settings.frame_rate} fps
                    </p>
                    <p className="mt-0.5 text-xs text-muted-foreground">
                      Started {formatDateTime(job.created_at)}
                      {job.finished_at
                        ? ` · took ${formatDuration(
                            (new Date(job.finished_at).getTime() -
                              new Date(job.started_at ?? job.created_at).getTime()) /
                              1000,
                          )}`
                        : ""}
                    </p>

                    {job.error_summary ? (
                      <p className="mt-1.5 text-sm font-medium text-destructive">
                        {job.error_summary}
                      </p>
                    ) : null}

                    {isActiveJobState(job.status) ? (
                      <div className="mt-2 max-w-md">
                        <Progress
                          value={job.progress ?? undefined}
                          indeterminate={!job.determinate}
                          aria-label={
                            job.determinate && job.progress !== null
                              ? `Render progress ${Math.round(job.progress * 100)} percent`
                              : "Render in progress"
                          }
                        />
                      </div>
                    ) : null}
                  </div>

                  <div className="flex shrink-0 flex-wrap gap-2">
                    {isActiveJobState(job.status) && job.status !== "cancelling" ? (
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => setPendingCancel(job)}
                        aria-label={`Cancel render for ${job.lesson_title ?? "untitled lesson"}`}
                      >
                        <XCircle className="size-4" aria-hidden />
                        Cancel
                      </Button>
                    ) : null}

                    {job.status === "failed" || job.status === "cancelled" ? (
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleRetry(job)}
                        disabled={retryJob.isPending}
                        aria-label={`Retry render for ${job.lesson_title ?? "untitled lesson"}`}
                      >
                        <RotateCcw className="size-4" aria-hidden />
                        Retry
                      </Button>
                    ) : null}

                    <Button asChild variant="secondary" size="sm">
                      <Link to={`/jobs/${job.job_id}`}>Open</Link>
                    </Button>
                  </div>
                </div>
              </Card>
            </li>
          ))}
        </ul>
      )}

      <p className={cn("text-xs text-muted-foreground")}>
        Jobs survive a restart of the application: anything that was interrupted is shown as failed
        with a reason, never silently marked successful.
      </p>

      <ConfirmDialog
        open={pendingCancel !== null}
        onOpenChange={(open) => {
          if (!open) setPendingCancel(null)
        }}
        title="Cancel this render?"
        description={
          pendingCancel
            ? `The render for “${pendingCancel.lesson_title ?? "this lesson"}” will stop. You can start it again at any time.`
            : ""
        }
        confirmLabel="Cancel render"
        destructive
        busy={cancelJob.isPending}
        onConfirm={handleCancel}
      />
    </div>
  )
}
