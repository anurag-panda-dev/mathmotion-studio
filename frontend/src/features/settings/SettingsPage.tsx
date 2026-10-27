import {
  CheckCircle2,
  ExternalLink,
  FolderOpen,
  HardDrive,
  RefreshCw,
  Terminal,
  Wrench,
} from "lucide-react"
import * as React from "react"
import { Link } from "react-router"
import { DependencyRow } from "@/components/DependencyStatus"
import { ErrorPanel } from "@/components/ErrorPanel"
import { Field, FieldGrid } from "@/components/Field"
import { PageHeader } from "@/components/PageHeader"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { useToast } from "@/hooks/useToast"
import { api, describeError } from "@/lib/api"
import {
  APP_THEME_LABELS,
  ASPECT_RATIO_LABELS,
  DEPENDENCY_HELP,
  QUALITY_DESCRIPTIONS,
  QUALITY_LABELS,
} from "@/lib/constants"
import { useDiagnostics, useSettings, useUpdateSettings } from "@/lib/queries"
import { APP_THEMES, ASPECT_RATIOS, QUALITIES, type AppSettingsPatch, type AppTheme, type AspectRatio, type Quality } from "@/lib/types"
import { formatBytes } from "@/lib/utils"

export function SettingsPage() {
  const toast = useToast()
  const settings = useSettings()
  const diagnostics = useDiagnostics()
  const updateSettings = useUpdateSettings()

  const [outputDir, setOutputDir] = React.useState<string | null>(null)
  const [outputDirError, setOutputDirError] = React.useState<string | null>(null)

  React.useEffect(() => {
    if (settings.data && outputDir === null) setOutputDir(settings.data.output_dir)
  }, [settings.data, outputDir])

  const effectiveOutputDir = outputDir ?? settings.data?.output_dir ?? ""
  const outputDirDirty =
    settings.data !== undefined && effectiveOutputDir !== settings.data.output_dir

  const apply = (patch: AppSettingsPatch) => {
    updateSettings.mutate(patch, {
      onSuccess: () => toast.success("Setting saved"),
      onError: (error) => toast.error("Could not save that setting", describeError(error)),
    })
  }

  const saveOutputDir = () => {
    setOutputDirError(null)
    if (!effectiveOutputDir.trim()) {
      setOutputDirError("Enter a folder path, for example D:\\MathMotion\\Videos.")
      return
    }
    updateSettings.mutate(
      { output_dir: effectiveOutputDir.trim() },
      {
        onSuccess: () => toast.success("Output folder updated", effectiveOutputDir.trim()),
        onError: (error) => {
          setOutputDirError(describeError(error))
          toast.error("Could not update the output folder", describeError(error))
        },
      },
    )
  }

  const health = diagnostics.data?.health
  const storage = diagnostics.data?.storage

  return (
    <div className="grid gap-8">
      <PageHeader
        title="Settings"
        guidance="Defaults for new renders, the appearance of this app, and the health of everything installed on this computer."
      />

      {settings.isError ? (
        <ErrorPanel error={settings.error} title="Could not load your settings" />
      ) : null}

      {/* ------------------------------- Defaults ------------------------------- */}
      <Card>
        <CardHeader>
          <CardTitle>Render defaults</CardTitle>
          <CardDescription>
            Applied to new render jobs. You can override them per lesson.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {settings.isLoading ? (
            <div className="grid gap-4 sm:grid-cols-2">
              <Skeleton className="h-9" />
              <Skeleton className="h-9" />
            </div>
          ) : (
            <FieldGrid>
              <Field label="Default quality" hint={QUALITY_DESCRIPTIONS[settings.data?.default_quality ?? "standard"]}>
                {() => (
                  <Select
                    value={settings.data?.default_quality}
                    onValueChange={(value) => apply({ default_quality: value as Quality })}
                  >
                    <SelectTrigger aria-label="Default render quality">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {QUALITIES.map((quality) => (
                        <SelectItem key={quality} value={quality}>
                          {QUALITY_LABELS[quality]}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              </Field>

              <Field label="Default aspect ratio" hint="The frame shape of new renders.">
                {() => (
                  <Select
                    value={settings.data?.default_aspect_ratio}
                    onValueChange={(value) =>
                      apply({ default_aspect_ratio: value as AspectRatio })
                    }
                  >
                    <SelectTrigger aria-label="Default aspect ratio">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {ASPECT_RATIOS.map((ratio) => (
                        <SelectItem key={ratio} value={ratio}>
                          {ASPECT_RATIO_LABELS[ratio]}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              </Field>
            </FieldGrid>
          )}
        </CardContent>
      </Card>

      {/* ------------------------------- Appearance ----------------------------- */}
      <Card>
        <CardHeader>
          <CardTitle>Appearance & language</CardTitle>
          <CardDescription>
            The app theme affects these screens only — never the colours inside a rendered lesson.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {settings.isLoading ? (
            <Skeleton className="h-9 w-56" />
          ) : (
            <FieldGrid>
              <Field label="Theme">
                {() => (
                  <Select
                    value={settings.data?.theme}
                    onValueChange={(value) => apply({ theme: value as AppTheme })}
                  >
                    <SelectTrigger aria-label="App theme">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {APP_THEMES.map((theme) => (
                        <SelectItem key={theme} value={theme}>
                          {APP_THEME_LABELS[theme]}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              </Field>
              <Field label="Preferred language" hint="Used for narration and on-screen text.">
                {(props) => (
                  <Input
                    {...props}
                    defaultValue={settings.data?.language}
                    onBlur={(event) => {
                      const value = event.target.value.trim()
                      if (value && value !== settings.data?.language) apply({ language: value })
                    }}
                  />
                )}
              </Field>
            </FieldGrid>
          )}
        </CardContent>
      </Card>

      {/* -------------------------------- Output -------------------------------- */}
      <Card>
        <CardHeader>
          <CardTitle>Output folder</CardTitle>
          <CardDescription>
            Rendered videos are written here. The path is validated before it is saved.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3">
          <div className="flex flex-wrap items-end gap-3">
            <div className="min-w-64 flex-1">
              <Field
                label="Folder path"
                error={outputDirError ?? undefined}
                hint="An existing or new folder on this computer."
              >
                {(props) => (
                  <Input
                    {...props}
                    value={effectiveOutputDir}
                    onChange={(event) => setOutputDir(event.target.value)}
                    className="font-mono text-xs"
                    spellCheck={false}
                  />
                )}
              </Field>
            </div>
            <Button onClick={saveOutputDir} disabled={!outputDirDirty || updateSettings.isPending}>
              <CheckCircle2 className="size-4" aria-hidden />
              Save folder
            </Button>
            <Button
              variant="secondary"
              onClick={() => {
                api.openOutputFolder().then(
                  (result) => {
                    if (!result.opened) {
                      toast.error("Could not open the folder", result.detail ?? "Unknown reason.")
                    }
                  },
                  (error: unknown) => toast.error("Could not open the folder", describeError(error)),
                )
              }}
            >
              <FolderOpen className="size-4" aria-hidden />
              Open folder
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* ---------------------------- Dependency health ---------------------------- */}
      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <CardTitle>Dependency health</CardTitle>
              <CardDescription>
                What is installed on this computer, and what each one is for.
              </CardDescription>
            </div>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => {
                void diagnostics.refetch()
              }}
              disabled={diagnostics.isFetching}
            >
              <RefreshCw
                className={diagnostics.isFetching ? "size-4 animate-spin" : "size-4"}
                aria-hidden
              />
              Re-check
            </Button>
          </div>
        </CardHeader>
        <CardContent className="grid gap-4">
          {diagnostics.isLoading ? (
            <div className="grid gap-2">
              <Skeleton className="h-12" />
              <Skeleton className="h-12" />
              <Skeleton className="h-12" />
            </div>
          ) : diagnostics.isError ? (
            <ErrorPanel error={diagnostics.error} title="Could not check your setup" />
          ) : health ? (
            <>
              {health.status === "degraded" ? (
                <Alert tone="warning">
                  <Wrench className="size-4" aria-hidden />
                  <AlertTitle>Rendering is currently unavailable</AlertTitle>
                  <AlertDescription>
                    Install the missing components below, then press Re-check. Prompt creation and
                    lesson import keep working in the meantime.
                  </AlertDescription>
                </Alert>
              ) : (
                <Alert tone="success">
                  <CheckCircle2 className="size-4" aria-hidden />
                  <AlertTitle>Everything required is installed</AlertTitle>
                  <AlertDescription>
                    Python {health.python} · MathMotion Studio {health.version} · Scene format{" "}
                    {health.scene_format_version}
                  </AlertDescription>
                </Alert>
              )}

              <div className="grid divide-y divide-border">
                {health.dependencies.map((dependency) => (
                  <div key={dependency.name}>
                    <DependencyRow dependency={dependency} />
                    <p className="mb-2 pl-7 text-xs text-muted-foreground">
                      {DEPENDENCY_HELP[dependency.name]}
                    </p>
                    {!dependency.available ? (
                      <a
                        href={repairUrlFor(dependency.name)}
                        target="_blank"
                        rel="noreferrer"
                        className="mb-2 ml-7 inline-flex items-center gap-1 text-xs font-medium text-primary underline underline-offset-2"
                      >
                        Installation guide
                        <ExternalLink className="size-3" aria-hidden />
                      </a>
                    ) : null}
                  </div>
                ))}
              </div>
            </>
          ) : null}
        </CardContent>
      </Card>

      {/* -------------------------------- Storage -------------------------------- */}
      <Card>
        <CardHeader>
          <CardTitle>Storage & logs</CardTitle>
          <CardDescription>How much space this application is using on disk.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
          {storage ? (
            <dl className="grid grid-cols-2 gap-4 sm:grid-cols-3">
              <Stat icon={HardDrive} label="Data" value={formatBytes(storage.data_bytes)} />
              <Stat icon={HardDrive} label="Videos" value={formatBytes(storage.output_bytes)} />
              <Stat icon={HardDrive} label="Total" value={formatBytes(storage.total_bytes)} />
            </dl>
          ) : (
            <Skeleton className="h-16" />
          )}

          <div className="flex flex-wrap gap-3">
            <Button
              variant="secondary"
              onClick={() => {
                api.openOutputFolder().then(
                  (result) => {
                    if (!result.opened) {
                      toast.error("Could not open the folder", result.detail ?? "Unknown reason.")
                    }
                  },
                  (error: unknown) =>
                    toast.error("Could not open the folder", describeError(error)),
                )
              }}
            >
              <FolderOpen className="size-4" aria-hidden />
              Open output folder
            </Button>
            <Button asChild variant="secondary">
              <Link to="/help">
                <Terminal className="size-4" aria-hidden />
                Repair & troubleshooting
              </Link>
            </Button>
          </div>

          {diagnostics.data ? (
            <p className="text-xs text-muted-foreground">
              Renders run one at a time · {diagnostics.data.rate_limit.max_requests} requests per{" "}
              {diagnostics.data.rate_limit.window_s}s allowed.
            </p>
          ) : null}
        </CardContent>
      </Card>
    </div>
  )
}

function repairUrlFor(name: string): string {
  const urls: Record<string, string> = {
    manim: "https://docs.manim.community/en/stable/installation.html",
    ffmpeg: "https://ffmpeg.org/download.html",
    latex: "https://miktex.org/download",
  }
  return urls[name] ?? "https://github.com/"
}

function Stat({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof HardDrive
  label: string
  value: string
}) {
  return (
    <div className="flex items-center gap-2.5">
      <Icon className="size-4 text-muted-foreground" aria-hidden />
      <div>
        <dt className="text-xs text-muted-foreground">{label}</dt>
        <dd className="text-sm font-medium">{value}</dd>
      </div>
    </div>
  )
}
