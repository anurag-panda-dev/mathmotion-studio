import { ClipboardPaste, Download, FileText, Upload } from "lucide-react"
import * as React from "react"
import { useNavigate } from "react-router"
import { ErrorPanel } from "@/components/ErrorPanel"
import { PageHeader } from "@/components/PageHeader"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/useToast"
import { MAX_SCENE_BYTES, describeError } from "@/lib/api"
import { useExample, useExampleList, useImportLesson } from "@/lib/queries"
import { cn, formatBytes } from "@/lib/utils"

const ACCEPTED_EXTENSIONS = [".md"]

function isAcceptedFile(file: File): boolean {
  return ACCEPTED_EXTENSIONS.some((extension) => file.name.toLowerCase().endsWith(extension))
}

export function ImportPage() {
  const navigate = useNavigate()
  const toast = useToast()
  const importLesson = useImportLesson()

  const examples = useExampleList()
  const [selectedExample, setSelectedExample] = React.useState<string | null>(null)
  const exampleContent = useExample(selectedExample)

  const [pasted, setPasted] = React.useState("")
  const [dragActive, setDragActive] = React.useState(false)
  const [localError, setLocalError] = React.useState<string | null>(null)
  const fileInputRef = React.useRef<HTMLInputElement>(null)

  const submit = (markdown: string) => {
    setLocalError(null)
    if (new Blob([markdown]).size > MAX_SCENE_BYTES) {
      setLocalError(
        `This file is ${formatBytes(new Blob([markdown]).size)}. The maximum size for a scene.md file is ${formatBytes(MAX_SCENE_BYTES)}.`,
      )
      return
    }
    importLesson.mutate(markdown, {
      onSuccess: (result) => {
        toast.success(
          "Lesson imported",
          result.report.valid ? "Validation passed." : "Check the validation results before rendering.",
        )
        void navigate(`/lessons/${result.lesson_id}`)
      },
      onError: (error) => {
        toast.error("Could not import the lesson", describeError(error))
      },
    })
  }

  const handleFile = (file: File) => {
    if (!isAcceptedFile(file)) {
      setLocalError(
        `“${file.name}” is not a .md file. Save your AI assistant's answer as a Markdown file (scene.md) and upload that.`,
      )
      return
    }
    if (file.size > MAX_SCENE_BYTES) {
      setLocalError(
        `This file is ${formatBytes(file.size)}. The maximum size for a scene.md file is ${formatBytes(MAX_SCENE_BYTES)}.`,
      )
      return
    }
    const reader = new FileReader()
    reader.onload = () => {
      const text = typeof reader.result === "string" ? reader.result : ""
      submit(text)
    }
    reader.onerror = () => setLocalError("The file could not be read. Please try again.")
    reader.readAsText(file, "utf-8")
  }

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault()
    setDragActive(false)
    const file = event.dataTransfer.files?.[0]
    if (file) handleFile(file)
  }

  const handleDownloadExample = () => {
    if (!selectedExample || !exampleContent.data) return
    const blob = new Blob([exampleContent.data.markdown], { type: "text/markdown;charset=utf-8" })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement("a")
    anchor.href = url
    anchor.download = exampleContent.data.name
    document.body.appendChild(anchor)
    anchor.click()
    anchor.remove()
    URL.revokeObjectURL(url)
    toast.success("Example downloaded", exampleContent.data.name)
  }

  return (
    <div className="grid gap-8">
      <PageHeader
        title="Import Scene"
        guidance="Bring the scene.md file your AI assistant produced into MathMotion Studio. Nothing is uploaded anywhere — the file stays on this computer."
      />

      {localError ? (
        <Alert tone="destructive">
          <AlertTitle>That file cannot be imported</AlertTitle>
          <AlertDescription>{localError}</AlertDescription>
        </Alert>
      ) : null}

      {importLesson.isError ? (
        <ErrorPanel error={importLesson.error} title="Could not import the lesson" />
      ) : null}

      <Tabs defaultValue="upload">
        <TabsList>
          <TabsTrigger value="upload">Upload a file</TabsTrigger>
          <TabsTrigger value="paste">Paste the text</TabsTrigger>
          <TabsTrigger value="examples">Try an example</TabsTrigger>
        </TabsList>

        {/* ------------------------------ Upload ------------------------------ */}
        <TabsContent value="upload" className="grid gap-4">
          <div
            onDragOver={(event) => {
              event.preventDefault()
              setDragActive(true)
            }}
            onDragLeave={() => setDragActive(false)}
            onDrop={handleDrop}
            className={cn(
              "flex flex-col items-center justify-center gap-3 rounded-[var(--radius-card)] border-2 border-dashed px-6 py-14 text-center transition-colors",
              dragActive
                ? "border-primary bg-primary-subtle/50"
                : "border-border bg-surface-alt/50 hover:border-ring/40",
            )}
          >
            <span className="flex size-12 items-center justify-center rounded-full bg-primary-subtle text-primary">
              <Upload className="size-6" aria-hidden />
            </span>
            <div>
              <p className="text-base font-semibold">Drag your scene.md file here</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Markdown files up to {formatBytes(MAX_SCENE_BYTES)}. UTF-8 encoding.
              </p>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".md,text/markdown"
              className="sr-only"
              onChange={(event) => {
                const file = event.target.files?.[0]
                if (file) handleFile(file)
                event.target.value = ""
              }}
            />
            <Button type="button" onClick={() => fileInputRef.current?.click()}>
              <FileText className="size-4" aria-hidden />
              Choose a file
            </Button>
          </div>
          <p className="text-xs text-muted-foreground">
            Your keyboard path: press <span className="font-medium">Choose a file</span> — the drop
            zone is never the only way to upload.
          </p>
        </TabsContent>

        {/* ------------------------------- Paste ------------------------------ */}
        <TabsContent value="paste" className="grid gap-3">
          <label htmlFor="paste-scene" className="text-sm font-medium">
            Paste the contents of scene.md
          </label>
          <Textarea
            id="paste-scene"
            value={pasted}
            onChange={(event) => setPasted(event.target.value)}
            rows={16}
            placeholder={"---\nschema_version: \"1.0\"\nlesson:\n  title: ...\n---\n\n```scene\n...\n```"}
            className="font-mono text-xs leading-relaxed"
          />
          <div className="flex items-center justify-between gap-3">
            <p className="text-xs text-muted-foreground">
              {pasted.length > 0
                ? `${formatBytes(new Blob([pasted]).size)} of ${formatBytes(MAX_SCENE_BYTES)}`
                : `Up to ${formatBytes(MAX_SCENE_BYTES)}`}
            </p>
            <Button
              type="button"
              disabled={pasted.trim().length === 0 || importLesson.isPending}
              onClick={() => submit(pasted)}
            >
              <ClipboardPaste className="size-4" aria-hidden />
              {importLesson.isPending ? "Importing…" : "Import pasted scene"}
            </Button>
          </div>
        </TabsContent>

        {/* ------------------------------ Examples ---------------------------- */}
        <TabsContent value="examples" className="grid gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Bundled example lessons</CardTitle>
              <CardDescription>
                Try the whole pipeline with a lesson we already validated, before involving your own
                AI assistant.
              </CardDescription>
            </CardHeader>
            <CardContent className="grid gap-4">
              {examples.isLoading ? (
                <p className="text-sm text-muted-foreground">Loading examples…</p>
              ) : examples.data?.examples.length === 0 || !examples.data ? (
                <p className="text-sm text-muted-foreground">
                  No bundled examples are available in this installation.
                </p>
              ) : (
                <div className="grid gap-2">
                  {examples.data.examples.map((example) => (
                    <label
                      key={example.name}
                      className={cn(
                        "flex cursor-pointer items-start gap-3 rounded-[var(--radius-control)] border px-3 py-2.5 transition-colors",
                        selectedExample === example.name
                          ? "border-primary bg-primary-subtle/40"
                          : "border-border hover:bg-surface-alt",
                      )}
                    >
                      <input
                        type="radio"
                        name="example"
                        value={example.name}
                        checked={selectedExample === example.name}
                        onChange={() => setSelectedExample(example.name)}
                        className="mt-1"
                      />
                      <span className="min-w-0 flex-1">
                        <span className="block truncate text-sm font-medium">{example.title}</span>
                        <span className="mt-0.5 block text-xs text-muted-foreground">
                          {example.topic} · Grade {example.grade} · {formatBytes(example.size_bytes)}
                        </span>
                      </span>
                    </label>
                  ))}
                </div>
              )}

              <div className="flex flex-wrap gap-2">
                <Button
                  type="button"
                  variant="secondary"
                  disabled={!selectedExample || exampleContent.isFetching}
                  onClick={handleDownloadExample}
                >
                  <Download className="size-4" aria-hidden />
                  Download example
                </Button>
                <Button
                  type="button"
                  disabled={!selectedExample || importLesson.isPending}
                  onClick={() => {
                    if (exampleContent.data) submit(exampleContent.data.markdown)
                  }}
                >
                  <Upload className="size-4" aria-hidden />
                  Import this example
                </Button>
              </div>

              {exampleContent.isError ? (
                <ErrorPanel error={exampleContent.error} title="Could not load that example" />
              ) : null}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
