import { AlertTriangle, CheckCircle2, Info, X, XCircle } from "lucide-react"
import * as React from "react"
import { cn } from "@/lib/utils"

export type ToastTone = "success" | "error" | "warning" | "info"

export interface Toast {
  id: number
  tone: ToastTone
  title: string
  description?: string
  /** Errors stay until dismissed; successes auto-dismiss. */
  dismissible: boolean
}

interface ToastContextValue {
  toast: (input: { tone?: ToastTone; title: string; description?: string }) => number
  success: (title: string, description?: string) => number
  error: (title: string, description?: string) => number
  dismiss: (id: number) => void
}

const ToastContext = React.createContext<ToastContextValue | null>(null)

const TOAST_DURATION_MS = 5000

const TONE_STYLES: Record<ToastTone, { className: string; Icon: typeof Info }> = {
  success: {
    className: "border-success/30 bg-success-subtle text-success-subtle-foreground",
    Icon: CheckCircle2,
  },
  error: {
    className: "border-destructive/30 bg-destructive-subtle text-destructive-subtle-foreground",
    Icon: XCircle,
  },
  warning: {
    className: "border-warning/30 bg-warning-subtle text-warning-subtle-foreground",
    Icon: AlertTriangle,
  },
  info: {
    className: "border-border bg-surface text-foreground shadow-lg",
    Icon: Info,
  },
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<Toast[]>([])
  const nextId = React.useRef(1)
  const timers = React.useRef(new Map<number, ReturnType<typeof setTimeout>>())

  const dismiss = React.useCallback((id: number) => {
    setToasts((current) => current.filter((item) => item.id !== id))
    const timer = timers.current.get(id)
    if (timer) {
      clearTimeout(timer)
      timers.current.delete(id)
    }
  }, [])

  const toast = React.useCallback<ToastContextValue["toast"]>(
    ({ tone = "info", title, description }) => {
      const id = nextId.current++
      const dismissible = tone === "error" || tone === "warning"
      setToasts((current) => [...current.slice(-3), { id, tone, title, description, dismissible }])
      if (!dismissible) {
        timers.current.set(
          id,
          setTimeout(() => dismiss(id), TOAST_DURATION_MS),
        )
      }
      return id
    },
    [dismiss],
  )

  React.useEffect(() => {
    const pending = timers.current
    return () => {
      for (const timer of pending.values()) clearTimeout(timer)
      pending.clear()
    }
  }, [])

  const value = React.useMemo<ToastContextValue>(
    () => ({
      toast,
      success: (title, description) => toast({ tone: "success", title, description }),
      error: (title, description) => toast({ tone: "error", title, description }),
      dismiss,
    }),
    [toast, dismiss],
  )

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastViewport toasts={toasts} onDismiss={dismiss} />
    </ToastContext.Provider>
  )
}

function ToastViewport({
  toasts,
  onDismiss,
}: {
  toasts: Toast[]
  onDismiss: (id: number) => void
}) {
  return (
    <div
      aria-live="polite"
      aria-atomic="false"
      className="pointer-events-none fixed bottom-4 right-4 z-[60] flex w-full max-w-sm flex-col gap-2"
    >
      {toasts.map((item) => {
        const { className, Icon } = TONE_STYLES[item.tone]
        return (
          <div
            key={item.id}
            role={item.tone === "error" ? "alert" : "status"}
            className={cn(
              "pointer-events-auto flex items-start gap-3 rounded-[var(--radius-card)] border px-4 py-3 shadow-lg animate-fade-in-up",
              className,
            )}
          >
            <Icon className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold break-words">{item.title}</p>
              {item.description ? (
                <p className="mt-0.5 text-sm opacity-95 break-words">{item.description}</p>
              ) : null}
            </div>
            {item.dismissible ? (
              <button
                type="button"
                onClick={() => onDismiss(item.id)}
                className="-mr-1 rounded p-1 opacity-70 transition-opacity hover:opacity-100 focus-visible:outline-2 focus-visible:outline-current"
                aria-label={`Dismiss notification: ${item.title}`}
              >
                <X className="size-4" />
              </button>
            ) : null}
          </div>
        )
      })}
    </div>
  )
}

export function useToast(): ToastContextValue {
  const context = React.useContext(ToastContext)
  if (!context) throw new Error("useToast must be used inside <ToastProvider>")
  return context
}
