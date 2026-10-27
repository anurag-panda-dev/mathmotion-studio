import { cva, type VariantProps } from "class-variance-authority"
import * as React from "react"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 whitespace-nowrap rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset",
  {
    variants: {
      tone: {
        neutral: "bg-neutral-subtle text-neutral-subtle-foreground ring-border",
        primary: "bg-primary-subtle text-primary-subtle-foreground ring-primary/25",
        success: "bg-success-subtle text-success-subtle-foreground ring-success/25",
        warning: "bg-warning-subtle text-warning-subtle-foreground ring-warning/25",
        destructive:
          "bg-destructive-subtle text-destructive-subtle-foreground ring-destructive/25",
      },
    },
    defaultVariants: {
      tone: "neutral",
    },
  },
)

export type BadgeTone = NonNullable<VariantProps<typeof badgeVariants>["tone"]>

function Badge({
  className,
  tone,
  ...props
}: React.ComponentProps<"span"> & VariantProps<typeof badgeVariants>) {
  return <span className={cn(badgeVariants({ tone }), className)} {...props} />
}

export { Badge, badgeVariants }
