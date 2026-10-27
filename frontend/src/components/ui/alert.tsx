import { cva, type VariantProps } from "class-variance-authority"
import * as React from "react"
import { cn } from "@/lib/utils"

const alertVariants = cva(
  "relative grid w-full grid-cols-[0fr_1fr] gap-y-0.5 rounded-[var(--radius-card)] border px-4 py-3 text-sm [&>svg]:mt-0.5 [&>svg]:shrink-0",
  {
    variants: {
      tone: {
        neutral: "border-border bg-surface-alt text-foreground",
        primary: "border-primary/25 bg-primary-subtle text-primary-subtle-foreground",
        success: "border-success/25 bg-success-subtle text-success-subtle-foreground",
        warning: "border-warning/30 bg-warning-subtle text-warning-subtle-foreground",
        destructive:
          "border-destructive/30 bg-destructive-subtle text-destructive-subtle-foreground",
      },
    },
    defaultVariants: {
      tone: "neutral",
    },
  },
)

type AlertProps = React.ComponentProps<"div"> & VariantProps<typeof alertVariants>

function Alert({ className, tone, ...props }: AlertProps) {
  return <div role="alert" className={cn(alertVariants({ tone }), className)} {...props} />
}

function AlertTitle({ className, ...props }: React.ComponentProps<"div">) {
  return <div className={cn("text-sm font-semibold", className)} {...props} />
}

function AlertDescription({ className, ...props }: React.ComponentProps<"div">) {
  return <div className={cn("text-sm opacity-95", className)} {...props} />
}

export { Alert, AlertTitle, AlertDescription }
