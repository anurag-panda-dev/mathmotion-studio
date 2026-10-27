import type { LucideIcon } from "lucide-react"
import * as React from "react"
import { cn } from "@/lib/utils"

interface EmptyStateProps {
  icon?: LucideIcon
  title: string
  description?: React.ReactNode
  /** Primary call-to-action, e.g. "Create New Animation". */
  action?: React.ReactNode
  className?: string
}

/**
 * A contextual empty state: explains the situation and points at the next
 * action instead of showing a bare zero or an empty list.
 */
export function EmptyState({ icon: Icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 rounded-[var(--radius-card)] border border-dashed border-border bg-surface-alt/50 px-6 py-12 text-center",
        className,
      )}
    >
      {Icon ? (
        <span className="flex size-11 items-center justify-center rounded-full bg-primary-subtle text-primary">
          <Icon className="size-5" aria-hidden />
        </span>
      ) : null}
      <div className="max-w-md">
        <p className="text-base font-semibold">{title}</p>
        {description ? (
          <div className="mt-1.5 text-sm text-muted-foreground">{description}</div>
        ) : null}
      </div>
      {action ? <div className="mt-1 flex flex-wrap justify-center gap-2">{action}</div> : null}
    </div>
  )
}
