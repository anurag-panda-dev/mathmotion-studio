import { ChevronDown, ShieldAlert } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { ApiError } from "@/lib/api"
import { cn } from "@/lib/utils"

interface ErrorPanelProps {
  error: unknown
  /** Fallback heading when the error carries no message. */
  title?: string
  className?: string
}

function describe(error: unknown): string {
  if (error instanceof Error) return error.message
  if (typeof error === "string") return error
  if (error === null || error === undefined) return "Unknown error"
  try {
    return JSON.stringify(error)
  } catch {
    return "Unknown error"
  }
}

/**
 * Teacher-facing error display: a plain-language message, plus a collapsed
 * technical disclosure for developers (UI spec §3.5, MASTER-PROMPT §8 —
 * stack traces never appear in the normal interface).
 */
export function ErrorPanel({ error, title = "Something went wrong", className }: ErrorPanelProps) {
  const message = describe(error)

  const technical: Array<{ label: string; value: string }> = []
  if (error instanceof ApiError) {
    technical.push({ label: "Error code", value: error.code })
    technical.push({ label: "HTTP status", value: String(error.status) })
    if (error.requestId) technical.push({ label: "Request ID", value: error.requestId })
    if (error.detail !== null && error.detail !== undefined) {
      technical.push({
        label: "Server detail",
        value:
          typeof error.detail === "string" ? error.detail : JSON.stringify(error.detail, null, 2),
      })
    }
  } else if (error instanceof Error && error.stack) {
    technical.push({ label: "Stack trace", value: error.stack })
  }

  return (
    <Alert tone="destructive" className={cn("grid-cols-1", className)}>
      <ShieldAlert className="size-4" aria-hidden />
      <AlertTitle>{error ? title : title}</AlertTitle>
      <AlertDescription>{message}</AlertDescription>
      {technical.length > 0 ? (
        <details className="mt-2 rounded-[var(--radius-control)] border border-destructive/20 bg-background/40 p-3">
          <summary className="flex cursor-pointer list-none items-center gap-1.5 text-xs font-medium opacity-80 hover:opacity-100">
            <ChevronDown className="size-3.5" aria-hidden />
            Technical details
          </summary>
          <dl className="mt-2 space-y-1.5 font-mono text-xs">
            {technical.map((item) => (
              <div key={item.label}>
                <dt className="font-sans font-semibold">{item.label}</dt>
                <dd className="whitespace-pre-wrap break-all opacity-90">{item.value}</dd>
              </div>
            ))}
          </dl>
        </details>
      ) : null}
    </Alert>
  )
}
