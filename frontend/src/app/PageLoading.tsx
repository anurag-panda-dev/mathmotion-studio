/** Full-page fallback shown while a lazily-loaded route downloads. */
export function PageLoading() {
  return (
    <div
      role="status"
      aria-live="polite"
      className="flex min-h-svh w-full items-center justify-center bg-background"
    >
      <div className="flex flex-col items-center gap-3">
        <div
          className="size-8 animate-spin rounded-full border-2 border-border border-t-primary motion-reduce:animate-none"
          aria-hidden
        />
        <p className="text-sm text-muted-foreground">Loading…</p>
      </div>
    </div>
  )
}
