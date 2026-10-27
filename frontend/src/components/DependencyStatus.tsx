import { CheckCircle2, CircleDashed, TriangleAlert } from "lucide-react"
import type { DependencyStatus } from "@/lib/types"
import { cn } from "@/lib/utils"

/**
 * Dependency health rendered as a labelled state, never an unexplained dot
 * (UI spec §2.3).
 */
export function DependencyRow({ dependency }: { dependency: DependencyStatus }) {
  const Icon = dependency.available ? CheckCircle2 : TriangleAlert
  const tone = dependency.available ? "text-success" : "text-warning"

  return (
    <div className="flex items-start gap-3 py-2">
      <Icon className={cn("mt-0.5 size-4 shrink-0", tone)} aria-hidden />
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-x-2">
          <span className="text-sm font-medium capitalize">{dependency.name}</span>
          <span className={cn("text-xs font-medium", tone)}>
            {dependency.available ? "Available" : "Missing"}
          </span>
          {dependency.version ? (
            <span className="font-mono text-xs text-muted-foreground">{dependency.version}</span>
          ) : null}
        </div>
        <p className="mt-0.5 text-xs text-muted-foreground">{dependency.detail ?? dependency.required_for}</p>
      </div>
    </div>
  )
}

/** Compact summary strip for the dashboard. */
export function DependencySummary({
  dependencies,
}: {
  dependencies: DependencyStatus[]
}) {
  const missing = dependencies.filter((dep) => !dep.available)
  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm">
      {dependencies.map((dep) => (
        <span key={dep.name} className="inline-flex items-center gap-1.5">
          {dep.available ? (
            <CheckCircle2 className="size-3.5 text-success" aria-hidden />
          ) : (
            <TriangleAlert className="size-3.5 text-warning" aria-hidden />
          )}
          <span className="text-muted-foreground">
            {dep.name[0]?.toUpperCase()}
            {dep.name.slice(1)}
          </span>
          <span className="font-medium">{dep.available ? "ready" : "missing"}</span>
        </span>
      ))}
      {missing.length === 0 ? (
        <span className="inline-flex items-center gap-1.5 text-muted-foreground">
          <CircleDashed className="size-3.5" aria-hidden />
          <span className="text-xs">LaTeX optional</span>
        </span>
      ) : null}
    </div>
  )
}
