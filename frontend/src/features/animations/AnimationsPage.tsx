import { Film, FolderOpen, Play, Search, Trash2 } from "lucide-react"
import * as React from "react"
import { Link } from "react-router"
import { ConfirmDialog } from "@/components/ConfirmDialog"
import { EmptyState } from "@/components/EmptyState"
import { ErrorPanel } from "@/components/ErrorPanel"
import { PageHeader } from "@/components/PageHeader"
import { ValidationChip } from "@/components/StatusChip"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { useToast } from "@/hooks/useToast"
import { describeError } from "@/lib/api"
import { useDeleteLesson, useLessons } from "@/lib/queries"
import type { LessonListItem } from "@/lib/types"
import { formatDateTime, formatRelativeTime, truncate } from "@/lib/utils"

const SORT_OPTIONS = [
  { value: "created_desc", label: "Newest first" },
  { value: "created_asc", label: "Oldest first" },
  { value: "title_asc", label: "Title A–Z" },
  { value: "title_desc", label: "Title Z–A" },
] as const

export function AnimationsPage() {
  const toast = useToast()
  const deleteLesson = useDeleteLesson()

  const [search, setSearch] = React.useState("")
  const [sort, setSort] = React.useState("created_desc")
  const [pendingDelete, setPendingDelete] = React.useState<LessonListItem | null>(null)

  // Debounce so typing does not hammer the local API.
  const [debouncedSearch, setDebouncedSearch] = React.useState("")
  React.useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search), 300)
    return () => clearTimeout(timer)
  }, [search])

  const lessons = useLessons({ search: debouncedSearch, sort })

  const handleDelete = () => {
    if (!pendingDelete) return
    deleteLesson.mutate(pendingDelete.lesson_id, {
      onSuccess: () => {
        toast.success("Lesson deleted", `“${pendingDelete.title || "Untitled lesson"}” was removed.`)
        setPendingDelete(null)
      },
      onError: (error) => toast.error("Could not delete the lesson", describeError(error)),
    })
  }

  return (
    <div className="grid gap-6">
      <PageHeader
        title="My Animations"
        guidance="Everything you have imported, stored on this computer. Reopen a lesson to review it, render it again, or delete it."
      />

      <div className="flex flex-wrap items-center gap-3">
        <div className="relative min-w-64 flex-1">
          <Search
            className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
            aria-hidden
          />
          <Input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search by title or topic…"
            aria-label="Search lessons"
            className="pl-9"
          />
        </div>
        <Select value={sort} onValueChange={setSort}>
          <SelectTrigger className="w-48" aria-label="Sort lessons">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {SORT_OPTIONS.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <p aria-live="polite" className="sr-only">
        {lessons.isLoading
          ? "Loading lessons"
          : `${lessons.data?.length ?? 0} lesson${(lessons.data?.length ?? 0) === 1 ? "" : "s"} found`}
      </p>

      {lessons.isLoading ? (
        <div className="grid gap-3">
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
        </div>
      ) : lessons.isError ? (
        <ErrorPanel error={lessons.error} title="Could not load your lessons" />
      ) : (lessons.data ?? []).length === 0 ? (
        <EmptyState
          icon={Film}
          title={debouncedSearch ? "No lessons match your search" : "No lessons yet"}
          description={
            debouncedSearch
              ? "Try a different search term, or clear the search to see everything."
              : "Create your first animation prompt, or import a scene.md you already have."
          }
          action={
            debouncedSearch ? (
              <Button variant="secondary" onClick={() => setSearch("")}>
                Clear search
              </Button>
            ) : (
              <>
                <Button asChild>
                  <Link to="/create">Create New Animation</Link>
                </Button>
                <Button asChild variant="secondary">
                  <Link to="/import">Import scene.md</Link>
                </Button>
              </>
            )
          }
        />
      ) : (
        <ul className="grid gap-3">
          {(lessons.data ?? []).map((lesson) => (
            <li key={lesson.lesson_id}>
              <Card className="transition-colors hover:border-ring/40">
                <div className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center">
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <Link
                        to={`/lessons/${lesson.lesson_id}`}
                        className="truncate text-base font-semibold underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-ring"
                      >
                        {truncate(lesson.title || "Untitled lesson", 90)}
                      </Link>
                      <ValidationChip valid={lesson.valid} />
                      {lesson.job_count > 0 ? (
                        <span className="text-xs text-muted-foreground">
                          {lesson.job_count} render{lesson.job_count === 1 ? "" : "s"}
                        </span>
                      ) : null}
                    </div>
                    <p className="mt-1 truncate text-sm text-muted-foreground">
                      {truncate(lesson.topic, 90)} · Grade {lesson.grade} · {lesson.language}
                    </p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      Imported {formatDateTime(lesson.created_at)}
                      {lesson.last_render_at
                        ? ` · last rendered ${formatRelativeTime(lesson.last_render_at)}`
                        : " · never rendered"}
                    </p>
                  </div>

                  <div className="flex shrink-0 flex-wrap gap-2">
                    <Button asChild variant="secondary" size="sm">
                      <Link to={`/lessons/${lesson.lesson_id}`}>
                        <FolderOpen className="size-4" aria-hidden />
                        Open
                      </Link>
                    </Button>
                    <Button asChild variant="secondary" size="sm">
                      <Link to={`/lessons/${lesson.lesson_id}`} state={{ render: true }}>
                        <Play className="size-4" aria-hidden />
                        Render
                      </Link>
                    </Button>
                    <Button
                      variant="destructiveOutline"
                      size="sm"
                      onClick={() => setPendingDelete(lesson)}
                      aria-label={`Delete ${lesson.title || "untitled lesson"}`}
                    >
                      <Trash2 className="size-4" aria-hidden />
                      Delete
                    </Button>
                  </div>
                </div>
              </Card>
            </li>
          ))}
        </ul>
      )}

      <ConfirmDialog
        open={pendingDelete !== null}
        onOpenChange={(open) => {
          if (!open) setPendingDelete(null)
        }}
        title="Delete this lesson?"
        description={
          pendingDelete
            ? `“${pendingDelete.title || "Untitled lesson"}” and its saved source will be permanently removed from this computer, along with its render history. This cannot be undone.`
            : ""
        }
        confirmLabel="Delete lesson"
        destructive
        busy={deleteLesson.isPending}
        onConfirm={handleDelete}
      />
    </div>
  )
}
