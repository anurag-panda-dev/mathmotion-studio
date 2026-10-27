import * as React from "react"
import { useSettings, useUpdateSettings } from "@/lib/queries"
import type { AppTheme } from "@/lib/types"

interface ThemeContextValue {
  /** The persisted preference: "light" | "dark" | "system". */
  preference: AppTheme
  /** What is actually applied right now, after resolving "system". */
  resolved: "light" | "dark"
  /** Persist the preference to the local database and apply it. */
  setPreference: (theme: AppTheme) => void
  saving: boolean
}

const ThemeContext = React.createContext<ThemeContextValue | null>(null)

const STORAGE_KEY = "mathmotion-theme-preference"

function readStoredPreference(): AppTheme {
  try {
    const value = window.localStorage.getItem(STORAGE_KEY)
    if (value === "light" || value === "dark" || value === "system") return value
  } catch {
    // localStorage may be unavailable; fall back to the system theme.
  }
  return "system"
}

function systemPrefersDark(): boolean {
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ?? false
}

function applyTheme(resolved: "light" | "dark"): void {
  const root = document.documentElement
  root.classList.toggle("dark", resolved === "dark")
}

/**
 * UI theme controller.
 *
 * The preference is persisted server-side (PATCH /api/v1/settings) per the
 * Settings spec, and mirrored into localStorage so a reload paints the right
 * theme before the first API response arrives.
 */
export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const { data: settings } = useSettings()
  const updateSettings = useUpdateSettings()
  const [preference, setPreferenceState] = React.useState<AppTheme>(readStoredPreference)
  const [systemDark, setSystemDark] = React.useState<boolean>(systemPrefersDark)
  const [saving, setSaving] = React.useState(false)

  // Adopt the server-stored preference once it loads (source of truth).
  React.useEffect(() => {
    if (!settings) return
    setPreferenceState((current) => {
      if (settings.theme === current) return current
      try {
        window.localStorage.setItem(STORAGE_KEY, settings.theme)
      } catch {
        // ignore
      }
      return settings.theme
    })
  }, [settings])

  // Track OS-level changes while "system" is selected.
  React.useEffect(() => {
    const media = window.matchMedia?.("(prefers-color-scheme: dark)")
    if (!media) return
    const listener = (event: MediaQueryListEvent) => setSystemDark(event.matches)
    media.addEventListener("change", listener)
    return () => media.removeEventListener("change", listener)
  }, [])

  const resolved: "light" | "dark" =
    preference === "system" ? (systemDark ? "dark" : "light") : preference

  React.useEffect(() => {
    applyTheme(resolved)
  }, [resolved])

  const setPreference = React.useCallback(
    (theme: AppTheme) => {
      setPreferenceState(theme)
      try {
        window.localStorage.setItem(STORAGE_KEY, theme)
      } catch {
        // ignore
      }
      setSaving(true)
      updateSettings.mutate(
        { theme },
        {
          onSettled: () => setSaving(false),
        },
      )
    },
    [updateSettings],
  )

  const value = React.useMemo<ThemeContextValue>(
    () => ({ preference, resolved, setPreference, saving }),
    [preference, resolved, setPreference, saving],
  )

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

export function useTheme(): ThemeContextValue {
  const context = React.useContext(ThemeContext)
  if (!context) throw new Error("useTheme must be used inside <ThemeProvider>")
  return context
}
