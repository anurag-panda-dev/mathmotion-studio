import { AlertTriangle, Film, Import, LayoutList, PlusCircle, Sparkles } from "lucide-react"
import { Link } from "react-router"
import { DependencySummary } from "@/components/DependencyStatus"
import { EmptyState } from "@/components/EmptyState"
import { ErrorPanel } from "@/components/ErrorPanel"
import { PageHeader } from "@/components/PageHeader"
import { JobStateChip } from "@/components/StatusChip"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { useHealth, useJobs, useLessons } from "@/lib/queries"
import { formatRelativeTime, truncate } from "@/lib/utils"

const QUICK_START_STEPS = [
  {
    step: 1,
    title: "Describe your lesson",
    body: "Enter a topic and grade level. MathMotion Studio writes a complete prompt for you.",
    to: "/create",
    cta: "Create Animation",
  },
  {
    step: 2,
    title: "Use any AI assistant",
    body: "Paste the prompt into the AI you already use. It replies with a scene.md lesson file — no API key or account needed.",
  },
  {
    step: 3,
    title: "Import and render",
    body: "Upload the scene.md, check the scene plan, then render the animation locally with Manim.",
    to: "/import",
    cta: "Import Scene",
  },
]

export function DashboardPage() {
  const health = useHealth()
  const lessons = useLessons({})
  const jobs = useJobs()

  const recentLessons = (lessons.data ?? []).slice(0, 5)
  const recentJobs = (jobs.data?.jobs ?? []).slice(0, 4)

  const degraded = health.data?.status === "degraded"

  return (
    <div className="grid gap-8">
      <PageHeader
        title="Welcome to MathMotion Studio"
        guidance="Turn a maths topic into a short animated lesson — write a prompt, use any AI assistant, then render the result here on your own computer."
      />

      {health.isError ? <ErrorPanel error={health.error} title="Could not check your setup" /> : null}

      {degraded ? (
        <Alert tone="warning">
          <AlertTriangle className="size-4" aria-hidden />
          <AlertTitle>Some components are missing</AlertTitle>
          <AlertDescription>
            You can still build prompts and import lessons, but rendering needs every required
            component.{" "}
            <Link to="/settings" className="font-medium underline underline-offset-2">
              See repair steps in Settings
            </Link>
            .
          </AlertDescription>
        </Alert>
      ) : null}

      {/* Primary actions */}
      <div className="grid gap-4 sm:grid-cols-2">
        <Card className="relative overflow-hidden">
          <CardHeader>
            <span className="mb-1 flex size-9 items-center justify-center rounded-[var(--radius-control)] bg-primary-subtle text-primary">
              <PlusCircle className="size-5" aria-hidden />
            </span>
            <CardTitle className="text-lg">Create New Animation</CardTitle>
            <CardDescription>
              Describe the lesson you need and get a complete prompt ready for your AI assistant.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild size="lg" className="w-full sm:w-auto">
              <Link to="/create">Start a new lesson</Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <span className="mb-1 flex size-9 items-center justify-center rounded-[var(--radius-control)] bg-primary-subtle text-primary">
              <Import className="size-5" aria-hidden />
            </span>
            <CardTitle className="text-lg">Import scene.md</CardTitle>
            <CardDescription>
              Already have a lesson file from an AI assistant? Upload or paste it to validate and
              render.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant="secondary" size="lg" className="w-full sm:w-auto">
              <Link to="/import">Import a lesson file</Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Render job status */}
      <section aria-labelledby="jobs-heading">
        <div className="mb-3 flex items-center justify-between">
          <h2 id="jobs-heading" className="text-base font-semibold">
            Render jobs
          </h2>
          <Button asChild variant="link" size="sm">
            <Link to="/jobs">View all</Link>
          </Button>
        </div>

        {jobs.isLoading ? (
          <div className="grid gap-2">
            <Skeleton className="h-16" />
            <Skeleton className="h-16" />
          </div>
        ) : jobs.isError ? (
          <ErrorPanel error={jobs.error} title="Could not load render jobs" />
        ) : recentJobs.length === 0 ? (
          <EmptyState
            icon={LayoutList}
            title="No render jobs yet"
            description="Once you import a lesson and press Render Animation, its progress will appear here."
          />
        ) : (
          <Card>
            <ul className="divide-y divide-border">
              {recentJobs.map((job) => (
                <li key={job.job_id}>
                  <Link
                    to={`/jobs/${job.job_id}`}
                    className="flex items-center gap-3 px-5 py-3 transition-colors hover:bg-surface-alt focus-visible:outline-2 focus-visible:outline-ring"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium">
                        {job.lesson_title ?? "Untitled lesson"}
                      </p>
                      <p className="mt-0.5 text-xs text-muted-foreground">
                        {job.phase} · started {formatRelativeTime(job.created_at)}
                      </p>
                    </div>
                    <JobStateChip status={job.status} />
                  </Link>
                </li>
              ))}
            </ul>
          </Card>
        )}
      </section>

      {/* Recent lessons */}
      <section aria-labelledby="lessons-heading">
        <div className="mb-3 flex items-center justify-between">
          <h2 id="lessons-heading" className="text-base font-semibold">
            Recent lessons
          </h2>
          <Button asChild variant="link" size="sm">
            <Link to="/animations">View all</Link>
          </Button>
        </div>

        {lessons.isLoading ? (
          <div className="grid gap-2">
            <Skeleton className="h-16" />
            <Skeleton className="h-16" />
          </div>
        ) : lessons.isError ? (
          <ErrorPanel error={lessons.error} title="Could not load your recent lessons" />
        ) : recentLessons.length === 0 ? (
          <EmptyState
            icon={Film}
            title="No lessons yet"
            description="Create your first animation prompt, or import a scene.md you already have."
            action={
              <>
                <Button asChild>
                  <Link to="/create">
                    <Sparkles className="size-4" aria-hidden />
                    Create New Animation
                  </Link>
                </Button>
                <Button asChild variant="secondary">
                  <Link to="/import">Import scene.md</Link>
                </Button>
              </>
            }
          />
        ) : (
          <Card>
            <ul className="divide-y divide-border">
              {recentLessons.map((lesson) => (
                <li key={lesson.lesson_id}>
                  <Link
                    to={`/lessons/${lesson.lesson_id}`}
                    className="flex items-center gap-3 px-5 py-3 transition-colors hover:bg-surface-alt focus-visible:outline-2 focus-visible:outline-ring"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium">{truncate(lesson.title, 80)}</p>
                      <p className="mt-0.5 truncate text-xs text-muted-foreground">
                        {truncate(lesson.topic, 60)} · Grade {lesson.grade} · imported{" "}
                        {formatRelativeTime(lesson.created_at)}
                      </p>
                    </div>
                    {lesson.valid === true ? (
                      <span className="text-xs font-medium text-success">Valid</span>
                    ) : lesson.valid === false ? (
                      <span className="text-xs font-medium text-destructive">
                        {lesson.error_count} error{lesson.error_count === 1 ? "" : "s"}
                      </span>
                    ) : (
                      <span className="text-xs text-muted-foreground">Not checked</span>
                    )}
                  </Link>
                </li>
              ))}
            </ul>
          </Card>
        )}
      </section>

      {/* Quick start + setup status */}
      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <Card>
          <CardHeader>
            <CardTitle>How it works</CardTitle>
            <CardDescription>Three steps from a topic to a finished animation.</CardDescription>
          </CardHeader>
          <CardContent>
            <ol className="grid gap-4">
              {QUICK_START_STEPS.map((item) => (
                <li key={item.step} className="flex gap-3">
                  <span className="flex size-6 shrink-0 items-center justify-center rounded-full bg-primary-subtle text-xs font-semibold text-primary-subtle-foreground">
                    {item.step}
                  </span>
                  <div className="min-w-0">
                    <p className="text-sm font-medium">{item.title}</p>
                    <p className="mt-0.5 text-sm text-muted-foreground">{item.body}</p>
                    {item.to ? (
                      <Button asChild variant="link" size="sm" className="mt-1 h-auto p-0">
                        <Link to={item.to}>{item.cta}</Link>
                      </Button>
                    ) : null}
                  </div>
                </li>
              ))}
            </ol>
            <p className="mt-4 text-xs text-muted-foreground">
              Need more detail?{" "}
              <Link to="/help" className="underline underline-offset-2">
                Read the getting started guide
              </Link>
              .
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Setup status</CardTitle>
            <CardDescription>Everything needed to render on this computer.</CardDescription>
          </CardHeader>
          <CardContent>
            {health.isLoading ? (
              <div className="grid gap-2">
                <Skeleton className="h-5" />
                <Skeleton className="h-5" />
                <Skeleton className="h-5" />
              </div>
            ) : health.data ? (
              <div className="grid divide-y divide-border">
                <DependencySummary dependencies={health.data.dependencies} />
              </div>
            ) : null}
            <Button asChild variant="secondary" size="sm" className="mt-4">
              <Link to="/settings">Open Settings</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
