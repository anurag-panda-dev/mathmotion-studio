import * as ProgressPrimitive from "@radix-ui/react-progress"
import * as React from "react"
import { cn } from "@/lib/utils"

interface ProgressProps extends React.ComponentProps<typeof ProgressPrimitive.Root> {
  /** Renders an animated, honest indeterminate bar when true. */
  indeterminate?: boolean
}

function Progress({ className, value, indeterminate = false, ...props }: ProgressProps) {
  const percent = indeterminate ? null : Math.min(100, Math.max(0, (value ?? 0) * 100))
  return (
    <ProgressPrimitive.Root
      className={cn(
        "relative h-2 w-full overflow-hidden rounded-full bg-surface-alt ring-1 ring-inset ring-border",
        className,
      )}
      value={percent === null ? undefined : percent}
      {...props}
    >
      {indeterminate ? (
        <div
          className="absolute inset-y-0 w-1/3 animate-indeterminate rounded-full bg-primary"
          aria-hidden="true"
        />
      ) : (
        <ProgressPrimitive.Indicator
          className="h-full rounded-full bg-primary transition-[width] duration-500 ease-out"
          style={{ width: `${percent ?? 0}%` }}
        />
      )}
    </ProgressPrimitive.Root>
  )
}

export { Progress }
