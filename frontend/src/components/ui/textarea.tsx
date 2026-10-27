import * as React from "react"
import { cn } from "@/lib/utils"

function Textarea({ className, ...props }: React.ComponentProps<"textarea">) {
  return (
    <textarea
      className={cn(
        "flex min-h-20 w-full rounded-[var(--radius-control)] border border-input bg-surface px-3 py-2 text-sm shadow-sm transition-colors",
        "placeholder:text-muted-foreground/70",
        "hover:border-ring/50",
        "focus-visible:border-ring focus-visible:outline-2 focus-visible:outline-ring focus-visible:outline-offset-1",
        "disabled:cursor-not-allowed disabled:bg-surface-alt disabled:opacity-70",
        className,
      )}
      {...props}
    />
  )
}

export { Textarea }
