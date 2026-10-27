import {
  Film,
  Home,
  Import,
  LayoutList,
  LifeBuoy,
  Moon,
  PlusCircle,
  Settings,
  Sun,
  SunMoon,
} from "lucide-react"
import * as React from "react"
import { NavLink, Outlet, useLocation } from "react-router"
import { PageLoading } from "@/app/PageLoading"
import { DependencySummary } from "@/components/DependencyStatus"
import { Button } from "@/components/ui/button"
import { useTheme } from "@/hooks/useTheme"
import { useHealth, useJobs } from "@/lib/queries"
import { cn } from "@/lib/utils"

interface NavItem {
  to: string
  label: string
  icon: React.ComponentType<{ className?: string; "aria-hidden"?: boolean }>
  /** Count badge for live render jobs. */
  badge?: number
}

function useNavItems(): NavItem[] {
  const { data: jobs } = useJobs()
  const activeCount = React.useMemo(
    () =>
      (jobs?.jobs ?? []).filter((job) =>
        ["queued", "validating", "preparing", "rendering", "postprocessing"].includes(job.status),
      ).length,
    [jobs],
  )

  return [
    { to: "/", label: "Home", icon: Home },
    { to: "/create", label: "Create Animation", icon: PlusCircle },
    { to: "/import", label: "Import Scene", icon: Import },
    { to: "/animations", label: "My Animations", icon: Film },
    { to: "/jobs", label: "Rendering Jobs", icon: LayoutList, badge: activeCount },
    { to: "/settings", label: "Settings", icon: Settings },
    { to: "/help", label: "Help & Getting Started", icon: LifeBuoy },
  ]
}

function ThemeToggleButton() {
  const { preference, resolved, setPreference } = useTheme()
  const Icon = preference === "system" ? SunMoon : resolved === "dark" ? Moon : Sun
  const next = preference === "light" ? "dark" : preference === "dark" ? "system" : "light"
  const label =
    preference === "system"
      ? "Theme: match system. Switch to light."
      : preference === "light"
        ? "Theme: light. Switch to dark."
        : "Theme: dark. Switch to match system."

  return (
    <Button variant="ghost" size="iconSm" aria-label={label} title={label} onClick={() => setPreference(next)}>
      <Icon aria-hidden />
    </Button>
  )
}

/**
 * The application shell: persistent left sidebar navigation plus the routed
 * main workspace (docs/UI_UX_SPEC.md §2).
 */
export function AppShell() {
  const navItems = useNavItems()
  const location = useLocation()
  const { data: health } = useHealth()
  const { resolved } = useTheme()

  return (
    <div className="flex min-h-svh w-full bg-background">
      <aside className="flex w-60 shrink-0 flex-col border-r border-border bg-surface-alt">
        <div className="flex items-center gap-2.5 px-4 py-4">
          <img
            src={resolved === "dark" ? "/logo-dark.svg" : "/logo-primary.svg"}
            alt=""
            className="h-7 w-auto"
          />
          <span className="sr-only">MathMotion Studio</span>
        </div>

        <nav aria-label="Main navigation" className="flex-1 overflow-y-auto px-2.5 py-2">
          <ul className="grid gap-0.5">
            {navItems.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  end={item.to === "/"}
                  className={({ isActive }) =>
                    cn(
                      "flex items-center gap-2.5 rounded-[var(--radius-control)] px-2.5 py-2 text-sm font-medium transition-colors",
                      "focus-visible:outline-2 focus-visible:outline-ring focus-visible:outline-offset-1",
                      isActive
                        ? "bg-primary-subtle text-primary-subtle-foreground"
                        : "text-muted-foreground hover:bg-surface hover:text-foreground",
                    )
                  }
                >
                  {({ isActive }) => (
                    <>
                      <item.icon
                        className={cn("size-4 shrink-0", isActive ? "text-primary" : "")}
                        aria-hidden
                      />
                      <span className="min-w-0 flex-1 truncate">{item.label}</span>
                      {item.badge ? (
                        <span
                          className="inline-flex min-w-5 items-center justify-center rounded-full bg-primary px-1.5 py-0.5 text-[11px] font-semibold text-primary-foreground"
                          aria-label={`${item.badge} render jobs in progress`}
                        >
                          {item.badge}
                        </span>
                      ) : null}
                    </>
                  )}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <div className="border-t border-border px-4 py-3">
          <div className="flex items-center justify-between gap-2">
            <div className="min-w-0">
              <p className="truncate text-xs text-muted-foreground">
                {health ? `v${health.version} · Scene ${health.scene_format_version}` : "Loading…"}
              </p>
            </div>
            <ThemeToggleButton />
          </div>
        </div>
      </aside>

      <main key={location.pathname} className="min-w-0 flex-1 overflow-x-hidden">
        <div className="mx-auto w-full max-w-6xl px-6 py-8 lg:px-10 lg:py-10">
          <React.Suspense fallback={<PageLoading />}>
            <Outlet />
          </React.Suspense>
        </div>
      </main>
    </div>
  )
}

export { DependencySummary }
