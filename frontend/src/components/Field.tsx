import * as React from "react"
import { cn } from "@/lib/utils"

interface FieldProps {
  /** Stable id; auto-generated when omitted. */
  id?: string
  label: string
  /** Helper text always visible under the control. */
  hint?: string
  /** Validation message; when set the control is marked invalid. */
  error?: string
  required?: boolean
  children: (props: {
    id: string
    "aria-describedby": string | undefined
    "aria-invalid": boolean | undefined
    "aria-required": boolean | undefined
  }) => React.ReactNode
}

/**
 * A labelled form field that wires up aria-describedby / aria-invalid so error
 * text is programmatically associated with its control (UI spec §5).
 */
export function Field({ id, label, hint, error, required, children }: FieldProps) {
  const generatedId = React.useId()
  const controlId = id ?? generatedId
  const hintId = `${controlId}-hint`
  const errorId = `${controlId}-error`

  const describedBy = [hint ? hintId : null, error ? errorId : null]
    .filter(Boolean)
    .join(" ")

  return (
    <div className="grid gap-1.5">
      <label htmlFor={controlId} className="text-sm font-medium">
        {label}
        {required ? (
          <span aria-hidden className="ml-1 text-destructive">
            *
          </span>
        ) : null}
      </label>
      {children({
        id: controlId,
        "aria-describedby": describedBy || undefined,
        "aria-invalid": error ? true : undefined,
        "aria-required": required || undefined,
      })}
      {hint && !error ? (
        <p id={hintId} className="text-xs text-muted-foreground">
          {hint}
        </p>
      ) : null}
      {error ? (
        <p id={errorId} role="alert" className="text-xs font-medium text-destructive">
          {error}
        </p>
      ) : null}
    </div>
  )
}

/** Two-column grid for related optional settings; collapses on narrow windows. */
export function FieldGrid({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn("grid gap-x-5 gap-y-4 sm:grid-cols-2", className)}>{children}</div>
  )
}
