import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { Suspense, lazy, useState } from "react"
import { BrowserRouter, Route, Routes } from "react-router"
import { PageLoading } from "@/app/PageLoading"
import { ThemeProvider } from "@/hooks/useTheme"
import { ToastProvider } from "@/hooks/useToast"
import { ApiError } from "@/lib/api"

// Route-level code splitting keeps the first paint small; each screen loads
// only when the teacher navigates to it.
const AppShell = lazy(() => import("@/app/AppShell").then((m) => ({ default: m.AppShell })))
const NotFoundPage = lazy(() =>
  import("@/app/NotFoundPage").then((m) => ({ default: m.NotFoundPage })),
)
const AnimationsPage = lazy(() =>
  import("@/features/animations/AnimationsPage").then((m) => ({ default: m.AnimationsPage })),
)
const CreatePage = lazy(() =>
  import("@/features/prompt-builder/CreatePage").then((m) => ({ default: m.CreatePage })),
)
const DashboardPage = lazy(() =>
  import("@/features/dashboard/DashboardPage").then((m) => ({ default: m.DashboardPage })),
)
const HelpPage = lazy(() =>
  import("@/features/help/HelpPage").then((m) => ({ default: m.HelpPage })),
)
const ImportPage = lazy(() =>
  import("@/features/scene-import/ImportPage").then((m) => ({ default: m.ImportPage })),
)
const JobDetailPage = lazy(() =>
  import("@/features/render-jobs/JobDetailPage").then((m) => ({ default: m.JobDetailPage })),
)
const JobsPage = lazy(() =>
  import("@/features/render-jobs/JobsPage").then((m) => ({ default: m.JobsPage })),
)
const ReviewPage = lazy(() =>
  import("@/features/scene-review/ReviewPage").then((m) => ({ default: m.ReviewPage })),
)
const SettingsPage = lazy(() =>
  import("@/features/settings/SettingsPage").then((m) => ({ default: m.SettingsPage })),
)

function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // The backend is a local service; failures are usually transient
        // (app restarting) so a short retry ladder is worthwhile, but a 4xx
        // will never become valid on retry.
        retry: (failureCount, error) => {
          if (error instanceof ApiError && error.status >= 400 && error.status < 500) return false
          return failureCount < 2
        },
        refetchOnWindowFocus: false,
        staleTime: 10_000,
      },
      mutations: {
        retry: false,
      },
    },
  })
}

export function App() {
  const [queryClient] = useState(createQueryClient)

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <ToastProvider>
          <BrowserRouter>
            <Suspense fallback={<PageLoading />}>
              <Routes>
                <Route element={<AppShell />}>
                  <Route index element={<DashboardPage />} />
                  <Route path="create" element={<CreatePage />} />
                  <Route path="import" element={<ImportPage />} />
                  <Route path="lessons/:lessonId" element={<ReviewPage />} />
                  <Route path="animations" element={<AnimationsPage />} />
                  <Route path="jobs" element={<JobsPage />} />
                  <Route path="jobs/:jobId" element={<JobDetailPage />} />
                  <Route path="settings" element={<SettingsPage />} />
                  <Route path="help" element={<HelpPage />} />
                  <Route path="*" element={<NotFoundPage />} />
                </Route>
              </Routes>
            </Suspense>
          </BrowserRouter>
        </ToastProvider>
      </ThemeProvider>
    </QueryClientProvider>
  )
}
