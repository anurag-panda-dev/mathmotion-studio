import * as React from "react"
import { cn } from "@/lib/utils"

interface PageHeaderProps {
  title: string
  /** One sentence of contextual guidance shown under the title. */
  guidance?: string
  /** Status indicators and actions, right-aligned. */
  actions?: React.ReactNode
  className?: string
}

/**
 * The standard page header: title, contextual guidance, and status/action area.
 * Focus moves to the heading on route change (UI spec §5).
 */
export function PageHeader({ title, guidance, actions, className }: PageHeaderProps) {
  const headingRef = React.useRef<HTMLHeadingElement>(null)

  React.useEffect(() => {
    headingRef.current?.focus()
  }, [title])

  return (
    <header
      className={cn(
        "flex flex-col gap-3 border-b border-border pb-5 sm:flex-row sm:items-start sm:justify-between",
        className,
      )}
    >
      <div className="min-w-0">
        <h1
          ref={headingRef}
          tabIndex={-1}
          className="text-2xl font-semibold tracking-tight outline-none"
        >
          {title}
        </h1>
        {guidance ? (
          <p className="mt-1.5 max-w-2xl text-sm text-muted-foreground">{guidance}</p>
        ) : null}
      </div>
      {actions ? <div className="flex shrink-0 flex-wrap items-center gap-2">{actions}</div> : null}
    </header>
  )
}
