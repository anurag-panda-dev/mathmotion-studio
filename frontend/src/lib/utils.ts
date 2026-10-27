import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

/** Merge conditional class names, resolving Tailwind conflicts. */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs))
}

/** Format a byte count for human reading (binary units, as reported by the OS). */
export function formatBytes(bytes: number | null | undefined): string {
  if (bytes === null || bytes === undefined || Number.isNaN(bytes)) return "—"
  if (bytes === 0) return "0 B"
  const units = ["B", "KB", "MB", "GB", "TB"]
  const exponent = Math.min(Math.floor(Math.log(Math.abs(bytes)) / Math.log(1024)), units.length - 1)
  const value = bytes / 1024 ** exponent
  const digits = exponent === 0 || value >= 100 ? 0 : value >= 10 ? 1 : 2
  return `${value.toFixed(digits)} ${units[exponent]}`
}

/** Parse an ISO-8601 timestamp; returns null when unparseable. */
export function parseTimestamp(iso: string | null | undefined): Date | null {
  if (!iso) return null
  const date = new Date(iso)
  return Number.isNaN(date.getTime()) ? null : date
}

/** Format a timestamp for display, e.g. "27 Oct 2026, 09:00". Local time. */
export function formatDateTime(iso: string | null | undefined): string {
  const date = parseTimestamp(iso)
  if (!date) return "—"
  return new Intl.DateTimeFormat(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date)
}

/** Relative time ("just now", "4 min ago", "yesterday"), falling back to a date. */
export function formatRelativeTime(iso: string | null | undefined): string {
  const date = parseTimestamp(iso)
  if (!date) return "—"
  const deltaMs = date.getTime() - Date.now()
  const absMs = Math.abs(deltaMs)
  const rtf = new Intl.RelativeTimeFormat(undefined, { numeric: "auto" })

  const units: Array<[Intl.RelativeTimeFormatUnit, number]> = [
    ["year", 365 * 24 * 60 * 60 * 1000],
    ["month", 30 * 24 * 60 * 60 * 1000],
    ["week", 7 * 24 * 60 * 60 * 1000],
    ["day", 24 * 60 * 60 * 1000],
    ["hour", 60 * 60 * 1000],
    ["minute", 60 * 1000],
  ]

  for (const [unit, ms] of units) {
    if (absMs >= ms) return rtf.format(Math.round(deltaMs / ms), unit)
  }
  return rtf.format(Math.round(deltaMs / 1000), "second")
}

/** Format a duration in seconds as "12s" or "3m 40s". */
export function formatDuration(seconds: number | null | undefined): string {
  if (seconds === null || seconds === undefined || Number.isNaN(seconds)) return "—"
  const total = Math.max(0, Math.round(seconds))
  if (total < 60) return `${total}s`
  const minutes = Math.floor(total / 60)
  const rest = total % 60
  return rest === 0 ? `${minutes}m` : `${minutes}m ${rest}s`
}

/** Truncate text for compact displays, appending an ellipsis. */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return `${text.slice(0, Math.max(0, maxLength - 1)).trimEnd()}…`
}

/** Trigger a client-side file download from an in-memory string. */
export function downloadTextFile(filename: string, content: string): void {
  const blob = new Blob([content], { type: "text/plain;charset=utf-8" })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement("a")
  anchor.href = url
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  URL.revokeObjectURL(url)
}

/**
 * Copy text to the clipboard, reporting failure instead of throwing.
 * Returns false when clipboard access is unavailable (denied permission,
 * insecure context, or a browser without the async clipboard API).
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text)
      return true
    }
  } catch {
    // fall through to the legacy path below
  }
  try {
    // Legacy fallback: a temporary, off-screen, selectable textarea.
    const textarea = document.createElement("textarea")
    textarea.value = text
    textarea.setAttribute("readonly", "")
    textarea.style.position = "fixed"
    textarea.style.top = "-1000px"
    textarea.style.opacity = "0"
    document.body.appendChild(textarea)
    textarea.select()
    const succeeded = document.execCommand("copy")
    textarea.remove()
    return succeeded
  } catch {
    return false
  }
}

/** Build a query string from an object, dropping null/undefined/empty values. */
export function toQueryString(params: Record<string, string | null | undefined>): string {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== null && value !== undefined && value !== "") search.set(key, value)
  }
  const query = search.toString()
  return query ? `?${query}` : ""
}
