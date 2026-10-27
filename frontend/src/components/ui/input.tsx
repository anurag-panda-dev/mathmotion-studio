import * as React from "react"
import { cn } from "@/lib/utils"

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      className={cn(
        "flex h-9 w-full min-w-0 rounded-[var(--radius-control)] border border-input bg-surface px-3 py-1 text-sm shadow-sm transition-colors",
        "placeholder:text-muted-foreground/70",
        "selection:bg-primary-subtle selection:text-primary-subtle-foreground",
        "hover:border-ring/50",
        "focus-visible:border-ring focus-visible:outline-2 focus-visible:outline-ring focus-visible:outline-offset-1",
        "disabled:cursor-not-allowed disabled:bg-surface-alt disabled:opacity-70",
        className,
      )}
      {...props}
    />
  )
}

export { Input }
