import {
  AlertTriangle,
  CheckCircle2,
  Eye,
  FileText,
  Pencil,
  RefreshCw,
  ShieldAlert,
  Upload,
} from "lucide-react"
import * as React from "react"
import { Link, useNavigate, useParams } from "react-router"
import { ConfirmDialog } from "@/components/ConfirmDialog"
import { ErrorPanel } from "@/components/ErrorPanel"
import { PageHeader } from "@/components/PageHeader"
import { ValidationChip } from "@/components/StatusChip"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/useToast"
import { describeError } from "@/lib/api"
import { SCENE_TYPE_LABELS } from "@/lib/constants"
import { useCreateJob, useLesson, useUpdateLessonSource } from "@/lib/queries"
import type { ValidationIssueModel } from "@/lib/types"
import { formatDuration } from "@/lib/utils"

export function ReviewPage() {
  const { lessonId } = useParams<{ lessonId: string }>()
  const navigate = useNavigate()
  const toast = useToast()

  const lesson = useLesson(lessonId)
  const updateSource = useUpdateLessonSource(lessonId ?? "")
  const createJob = useCreateJob()

  const [editing, setEditing] = React.useState(false)
  const [draft, setDraft] = React.useState("")
  const [confirmRender, setConfirmRender] = React.useState(false)

  // Keep the editor draft in sync once the source has loaded.
  React.useEffect(() => {
    if (!editing && lesson.data?.markdown) setDraft(lesson.data.markdown)
  }, [editing, lesson.data?.markdown])

  const summary = lesson.data?.summary
  const report = lesson.data?.report
  const isValid = lesson.data?.valid === true

  // Re-validating an existing lesson re-submits its stored source, which the
  // backend re-parses, re-validates and re-associates with the same lesson id.
  const handleValidate = () => {
    if (!lesson.data?.markdown) return
    updateSource.mutate(lesson.data.markdown, {
      onSuccess: (result) => {
        toast.success(
          "Validation complete",
          result.report.valid
            ? "No errors found."
            : `${result.report.errors.length} error${result.report.errors.length === 1 ? "" : "s"} need attention.`,
        )
        void lesson.refetch()
      },
      onError: (error) => toast.error("Validation failed", describeError(error)),
    })
  }

  const handleSaveSource = () => {
    if (!draft.trim()) return
    updateSource.mutate(draft, {
      onSuccess: (result) => {
        setEditing(false)
        toast.success(
          "Source saved",
          result.report.valid ? "Validation passed." : "Validation found errors — see the report.",
        )
        void lesson.refetch()
      },
      onError: (error) => toast.error("Could not save the source", describeError(error)),
    })
  }

  const handleRender = () => {
    if (!lessonId) return
    createJob.mutate(
      { lessonId, request: {} },
      {
        onSuccess: (job) => {
          setConfirmRender(false)
          toast.success("Render started", "Follow its progress on the Rendering Jobs page.")
          void navigate(`/jobs/${job.job_id}`)
        },
        onError: (error) => {
          setConfirmRender(false)
          toast.error("Could not start the render", describeError(error))
        },
      },
    )
  }

  if (lesson.isLoading) {
    return (
      <div className="grid gap-6">
        <Skeleton className="h-9 w-72" />
        <Skeleton className="h-40" />
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (lesson.isError || !lesson.data) {
    return (
      <div className="grid gap-6">
        <PageHeader title="Lesson not found" />
        <ErrorPanel
          error={lesson.error ?? new Error("This lesson does not exist on this computer.")}
          title="Could not load this lesson"
        />
        <div>
          <Button asChild variant="secondary">
            <Link to="/animations">Back to My Animations</Link>
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="grid gap-8">
      <PageHeader
        title={summary?.title ?? (lesson.data.title || "Untitled lesson")}
        guidance={
          summary
            ? `${summary.topic} · Grade ${summary.grade} · ${summary.language}`
            : `Imported file: ${lesson.data.filename}`
        }
        actions={
          <>
            <Button
              variant="secondary"
              onClick={() => {
                setDraft(lesson.data.markdown)
                setEditing((current) => !current)
              }}
            >
              <Pencil className="size-4" aria-hidden />
              {editing ? "Close editor" : "Edit Source"}
            </Button>
            <Button asChild variant="secondary">
              <Link to="/import">
                <Upload className="size-4" aria-hidden />
                Re-upload
              </Link>
            </Button>
          </>
        }
      />

      {/* --------------------------- Validation gate --------------------------- */}
      {isValid ? (
        <Alert tone="success">
          <CheckCircle2 className="size-4" aria-hidden />
          <AlertTitle>This lesson is ready to render</AlertTitle>
          <AlertDescription>
            Validation passed{report ? ` with ${report.warnings.length} warning${report.warnings.length === 1 ? "" : "s"}` : ""}. Rendering stays off until you press the button yourself.
          </AlertDescription>
        </Alert>
      ) : (
        <Alert tone="destructive">
          <ShieldAlert className="size-4" aria-hidden />
          <AlertTitle>Fix these problems before rendering</AlertTitle>
          <AlertDescription>
            {lesson.data.valid === null
              ? "This lesson has not been validated yet. Press Validate Scene to check it."
              : `${lesson.data.error_count} error${lesson.data.error_count === 1 ? "" : "s"} must be resolved. Rendering is blocked until validation passes.`}
          </AlertDescription>
        </Alert>
      )}

      {editing ? (
        <Card>
          <CardHeader>
            <CardTitle>Edit scene.md source</CardTitle>
            <CardDescription>
              Make small corrections directly. For larger changes, paste them back to your AI
              assistant and re-upload the result.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3">
            <Textarea
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              rows={20}
              className="font-mono text-xs leading-relaxed"
              aria-label="scene.md source"
            />
            <div className="flex gap-2">
              <Button onClick={handleSaveSource} disabled={updateSource.isPending || !draft.trim()}>
                <CheckCircle2 className="size-4" aria-hidden />
                {updateSource.isPending ? "Saving…" : "Save and re-validate"}
              </Button>
              <Button variant="secondary" onClick={() => setEditing(false)}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : null}

      {/* ------------------------------ Summary ------------------------------ */}
      {summary ? (
        <div className="grid gap-6 lg:grid-cols-3">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Lesson overview</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-5">
              <dl className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                <Meta label="Target duration" value={`${summary.duration_minutes} min`} />
                <Meta
                  label="Estimated length"
                  value={formatDuration(summary.total_duration_s)}
                />
                <Meta label="Aspect ratio" value={summary.aspect_ratio} />
                <Meta label="Render theme" value={summary.theme} capitalize />
              </dl>

              {summary.objectives.length > 0 ? (
                <div>
                  <h3 className="text-sm font-semibold">Learning objectives</h3>
                  <ul className="mt-2 grid list-disc gap-1 pl-5 text-sm text-muted-foreground">
                    {summary.objectives.map((objective) => (
                      <li key={objective}>{objective}</li>
                    ))}
                  </ul>
                </div>
              ) : null}

              {summary.prerequisites.length > 0 ? (
                <div>
                  <h3 className="text-sm font-semibold">Prerequisites</h3>
                  <ul className="mt-2 grid list-disc gap-1 pl-5 text-sm text-muted-foreground">
                    {summary.prerequisites.map((prerequisite) => (
                      <li key={prerequisite}>{prerequisite}</li>
                    ))}
                  </ul>
                </div>
              ) : null}

              {summary.recap ? (
                <div>
                  <h3 className="text-sm font-semibold">Recap</h3>
                  <p className="mt-1.5 text-sm text-muted-foreground">{summary.recap}</p>
                </div>
              ) : null}

              {summary.practice_questions.length > 0 ? (
                <div>
                  <h3 className="text-sm font-semibold">Practice questions</h3>
                  <ol className="mt-1.5 grid list-decimal gap-1 pl-5 text-sm text-muted-foreground">
                    {summary.practice_questions.map((question) => (
                      <li key={question}>{question}</li>
                    ))}
                  </ol>
                </div>
              ) : null}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Scene timeline</CardTitle>
              <CardDescription>
                {summary.scenes.length} scene{summary.scenes.length === 1 ? "" : "s"},{" "}
                {summary.object_count} objects, {summary.action_count} actions.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ol className="grid gap-3">
                {summary.scenes.map((scene) => (
                  <li key={scene.id} className="flex gap-3">
                    <span
                      aria-hidden
                      className="mt-1.5 size-2 shrink-0 rounded-full bg-primary"
                    />
                    <div className="min-w-0 flex-1 border-l border-border pl-3">
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="text-sm font-medium">{scene.title}</p>
                        <Badge tone="primary">
                          {SCENE_TYPE_LABELS[scene.type] ?? scene.type}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {formatDuration(scene.duration_s)}
                        </span>
                      </div>
                      <p className="mt-0.5 text-xs text-muted-foreground">
                        {scene.object_count} objects · {scene.action_count} actions
                      </p>
                      {scene.narration ? (
                        <p className="mt-1 text-xs text-muted-foreground italic">
                          “{scene.narration}”
                        </p>
                      ) : null}
                      {scene.formulas.length > 0 ? (
                        <p className="mt-1 font-mono text-xs text-primary">
                          {scene.formulas.join("   ")}
                        </p>
                      ) : null}
                    </div>
                  </li>
                ))}
              </ol>
            </CardContent>
          </Card>
        </div>
      ) : (
        <Card>
          <CardContent className="py-8 text-center text-sm text-muted-foreground">
            No lesson summary is available yet. Run Validate Scene to build the scene timeline.
          </CardContent>
        </Card>
      )}

      {/* ---------------------------- Validation report ---------------------------- */}
      {report ? (
        <Card>
          <CardHeader>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <CardTitle>Validation report</CardTitle>
                <CardDescription>
                  {report.valid ? "No blocking problems found." : `${report.errors.length} error(s) and ${report.warnings.length} warning(s).`}
                </CardDescription>
              </div>
              <ValidationChip valid={report.valid} />
            </div>
          </CardHeader>
          <CardContent className="grid gap-5">
            <IssueList title="Errors" issues={report.errors} tone="destructive" />
            <IssueList title="Warnings" issues={report.warnings} tone="warning" />

            {report.verification.length > 0 ? (
              <div>
                <h3 className="text-sm font-semibold">Mathematical verification</h3>
                <ul className="mt-2 grid gap-2">
                  {report.verification.map((check) => (
                    <li
                      key={check.id}
                      className="rounded-[var(--radius-control)] border border-border bg-surface-alt/40 px-3 py-2"
                    >
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-sm font-medium">{check.description}</span>
                        <Badge
                          tone={
                            check.status === "passed"
                              ? "success"
                              : check.status === "failed"
                                ? "destructive"
                                : "neutral"
                          }
                        >
                          {check.status}
                        </Badge>
                        <span className="text-xs text-muted-foreground">{check.kind}</span>
                      </div>
                      <p className="mt-1 text-xs text-muted-foreground">{check.message}</p>
                    </li>
                  ))}
                </ul>
                <p className="mt-2 text-xs text-muted-foreground">
                  A successful render means the animation compiled — it does not by itself prove the
                  mathematics. Checks above ran separately.
                </p>
              </div>
            ) : null}
          </CardContent>
        </Card>
      ) : null}

      {/* -------------------------------- Actions -------------------------------- */}
      <Card>
        <CardContent className="flex flex-wrap items-center gap-3 py-5">
          <Button
            variant="secondary"
            onClick={handleValidate}
            disabled={updateSource.isPending || !lesson.data?.markdown}
          >
            <RefreshCw
              className={updateSource.isPending ? "size-4 animate-spin" : "size-4"}
              aria-hidden
            />
            {updateSource.isPending ? "Validating…" : "Validate Scene"}
          </Button>

          <Button variant="secondary" onClick={() => setEditing((current) => !current)}>
            <Pencil className="size-4" aria-hidden />
            Edit Source
          </Button>

          <Button asChild variant="secondary">
            <Link to="/import">
              <Upload className="size-4" aria-hidden />
              Re-upload
            </Link>
          </Button>

          <Button
            onClick={() => setConfirmRender(true)}
            disabled={!isValid || createJob.isPending}
            aria-describedby="render-hint"
          >
            <Eye className="size-4" aria-hidden />
            Render Animation
          </Button>

          <p id="render-hint" className="basis-full text-xs text-muted-foreground sm:basis-auto">
            {isValid
              ? "Renders locally at your default quality."
              : "Run Validate Scene first — rendering is blocked until validation passes."}
          </p>
        </CardContent>
      </Card>

      <ConfirmDialog
        open={confirmRender}
        onOpenChange={setConfirmRender}
        title="Render this animation?"
        description={`“${summary?.title ?? (lesson.data.title || "This lesson")}” will be rendered on this computer using your default quality settings. You can follow its progress and cancel at any time.`}
        confirmLabel="Start render"
        busy={createJob.isPending}
        onConfirm={handleRender}
      />
    </div>
  )
}

function Meta({
  label,
  value,
  capitalize = false,
}: {
  label: string
  value: string
  capitalize?: boolean
}) {
  return (
    <div>
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className={`mt-0.5 text-sm font-medium ${capitalize ? "capitalize" : ""}`}>{value}</dd>
    </div>
  )
}

function IssueList({
  title,
  issues,
  tone,
}: {
  title: string
  issues: ValidationIssueModel[]
  tone: "destructive" | "warning"
}) {
  if (issues.length === 0) return null
  return (
    <div>
      <h3 className="flex items-center gap-2 text-sm font-semibold">
        {tone === "destructive" ? (
          <ShieldAlert className="size-4 text-destructive" aria-hidden />
        ) : (
          <AlertTriangle className="size-4 text-warning" aria-hidden />
        )}
        {title} ({issues.length})
      </h3>
      <ul className="mt-2 grid gap-2">
        {issues.map((issue, index) => (
          <li
            key={`${issue.category}-${issue.path ?? ""}-${index}`}
            className={`rounded-[var(--radius-control)] border px-3 py-2 ${
              tone === "destructive"
                ? "border-destructive/25 bg-destructive-subtle/40"
                : "border-warning/25 bg-warning-subtle/40"
            }`}
          >
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone={tone}>{issue.category.replace(/_/g, " ")}</Badge>
              {issue.scene ? <span className="text-xs text-muted-foreground">scene {issue.scene}</span> : null}
              {issue.line !== null ? (
                <span className="text-xs text-muted-foreground">line {issue.line}</span>
              ) : null}
              {issue.path ? (
                <code className="font-mono text-xs text-muted-foreground">{issue.path}</code>
              ) : null}
            </div>
            <p className="mt-1 text-sm">{issue.message}</p>
            {issue.suggestion ? (
              <p className="mt-1 text-xs text-muted-foreground">
                <FileText className="mr-1 inline size-3" aria-hidden />
                {issue.suggestion}
              </p>
            ) : null}
          </li>
        ))}
      </ul>
    </div>
  )
}
