import { Copy, Download, Eye, EyeOff, RotateCcw, Sparkles } from "lucide-react"
import * as React from "react"
import { z } from "zod"
import { ErrorPanel } from "@/components/ErrorPanel"
import { Field, FieldGrid } from "@/components/Field"
import { PageHeader } from "@/components/PageHeader"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/useToast"
import {
  ASPECT_RATIO_DESCRIPTIONS,
  ASPECT_RATIO_LABELS,
  DIFFICULTY_LABELS,
  SCENE_COLORS,
  SCENE_COLOR_SWATCHES,
  STYLE_LABELS,
} from "@/lib/constants"
import { useGeneratePrompt } from "@/lib/queries"
import {
  ASPECT_RATIOS,
  DIFFICULTIES,
  PROMPT_STYLES,
  type AspectRatio,
  type Difficulty,
  type PromptStyle,
} from "@/lib/types"
import { copyToClipboard, downloadTextFile } from "@/lib/utils"

/* ------------------------------------------------------------------ */
/* Form model + validation                                             */
/* ------------------------------------------------------------------ */

const formSchema = z.object({
  topic: z
    .string()
    .trim()
    .min(3, "Enter a topic of at least 3 characters, for example “the Pythagorean theorem”."),
  grade: z
    .string()
    .trim()
    .min(1, "Enter the class or grade level, for example “8” or “Year 9”.")
    .max(24, "Grade level must be 24 characters or fewer."),
  branch: z
    .string()
    .trim()
    .max(60, "Subject name must be 60 characters or fewer.")
    .optional(),
  language: z
    .string()
    .trim()
    .min(2, "Language must be at least 2 characters.")
    .max(40, "Language must be 40 characters or fewer."),
  style: z.enum(PROMPT_STYLES),
  duration: z.coerce
    .number()
    .int("Duration must be a whole number of minutes.")
    .min(1, "Duration must be at least 1 minute.")
    .max(60, "Duration must be 60 minutes or fewer."),
  aspectRatio: z.enum(ASPECT_RATIOS),
  difficulty: z.enum(DIFFICULTIES),
  colors: z.string().trim().max(200, "Describe colours in 200 characters or fewer."),
  includePractice: z.boolean(),
  includeRecap: z.boolean(),
  includeVoiceover: z.boolean(),
  additional: z.string().trim().max(1000, "Additional instructions must be 1000 characters or fewer."),
})

type FormState = z.infer<typeof formSchema>

const DEFAULTS: FormState = {
  topic: "",
  grade: "",
  branch: "",
  language: "English",
  style: "intuitive",
  duration: 5,
  aspectRatio: "16:9",
  difficulty: "standard",
  colors: "navy, violet, ivory",
  includePractice: true,
  includeRecap: true,
  includeVoiceover: true,
  additional: "",
}

type FieldErrors = Partial<Record<keyof FormState, string>>

function validate(form: FormState): FieldErrors {
  const result = formSchema.safeParse(form)
  if (result.success) return {}
  const errors: FieldErrors = {}
  for (const issue of result.error.issues) {
    const key = issue.path[0] as keyof FormState
    if (!errors[key]) errors[key] = issue.message
  }
  return errors
}

/* ------------------------------------------------------------------ */
/* Page                                                                */
/* ------------------------------------------------------------------ */

export function CreatePage() {
  const [form, setForm] = React.useState<FormState>(DEFAULTS)
  const [showCompact, setShowCompact] = React.useState(false)
  const [touched, setTouched] = React.useState(false)
  const [clipboardFailed, setClipboardFailed] = React.useState(false)

  const generate = useGeneratePrompt()
  const toast = useToast()

  const errors = React.useMemo(() => validate(form), [form])
  const isValid = Object.keys(errors).length === 0
  const isDirty = JSON.stringify(form) !== JSON.stringify(DEFAULTS)

  const set = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    setForm((current) => ({ ...current, [key]: value }))
  }

  const handleGenerate = () => {
    setTouched(true)
    if (!isValid) return
    setClipboardFailed(false)
    generate.mutate({
      topic: form.topic,
      grade: form.grade,
      branch: form.branch || null,
      language: form.language,
      style: form.style,
      duration: form.duration,
      aspect_ratio: form.aspectRatio,
      difficulty: form.difficulty,
      colors: form.colors || null,
      include_recap: form.includeRecap,
      include_practice: form.includePractice,
      include_voiceover: form.includeVoiceover,
      additional: form.additional || null,
    })
  }

  const handleReset = () => {
    setForm(DEFAULTS)
    setTouched(false)
    setClipboardFailed(false)
    generate.reset()
  }

  const handleCopy = async () => {
    if (!generate.data) return
    const text = showCompact ? generate.data.compact_prompt : generate.data.prompt
    const ok = await copyToClipboard(text)
    if (ok) {
      setClipboardFailed(false)
      toast.success("Prompt copied", "Paste it into any AI assistant to get your scene.md file.")
    } else {
      setClipboardFailed(true)
      toast.error(
        "Could not copy automatically",
        "Select the text in the preview and press Ctrl+C to copy it manually.",
      )
    }
  }

  const handleDownload = () => {
    if (!generate.data) return
    const text = showCompact ? generate.data.compact_prompt : generate.data.prompt
    downloadTextFile(generate.data.filename, text)
    toast.success("Prompt downloaded", generate.data.filename)
  }

  const errorList = touched ? Object.entries(errors) : []

  return (
    <div className="grid gap-8">
      <PageHeader
        title="Create Animation"
        guidance="Tell MathMotion Studio what to teach. It writes a complete prompt you can paste into any AI assistant — this app never contacts an AI service itself."
      />

      {errorList.length > 0 ? (
        <Alert tone="destructive">
          <AlertTitle>
            Please fix {errorList.length} problem{errorList.length === 1 ? "" : "s"} before
            generating
          </AlertTitle>
          <AlertDescription>
            <ul className="mt-1 list-disc space-y-0.5 pl-5">
              {errorList.map(([key, message]) => (
                <li key={key}>{message}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      ) : null}

      <form
        className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]"
        onSubmit={(event) => {
          event.preventDefault()
          handleGenerate()
        }}
      >
        {/* ------------------------------ Inputs ------------------------------ */}
        <div className="grid content-start gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Lesson</CardTitle>
              <CardDescription>The topic and who you are teaching.</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-4">
              <Field
                label="Topic"
                required
                hint="The mathematical idea to teach, in your own words."
                error={touched ? errors.topic : undefined}
              >
                {(props) => (
                  <Input
                    {...props}
                    value={form.topic}
                    onChange={(event) => set("topic", event.target.value)}
                    placeholder="e.g. the Pythagorean theorem"
                    autoComplete="off"
                  />
                )}
              </Field>

              <Field
                label="Class / grade level"
                required
                hint="How old or experienced are your students?"
                error={touched ? errors.grade : undefined}
              >
                {(props) => (
                  <Input
                    {...props}
                    value={form.grade}
                    onChange={(event) => set("grade", event.target.value)}
                    placeholder="e.g. 8, or Year 9"
                    autoComplete="off"
                  />
                )}
              </Field>

              <FieldGrid>
                <Field
                  label="Subject / branch"
                  hint="Optional."
                  error={touched ? errors.branch : undefined}
                >
                  {(props) => (
                    <Input
                      {...props}
                      value={form.branch}
                      onChange={(event) => set("branch", event.target.value)}
                      placeholder="e.g. Geometry"
                      autoComplete="off"
                    />
                  )}
                </Field>

                <Field
                  label="Language"
                  hint="Narration and on-screen text."
                  error={touched ? errors.language : undefined}
                >
                  {(props) => (
                    <Input
                      {...props}
                      value={form.language}
                      onChange={(event) => set("language", event.target.value)}
                      autoComplete="off"
                    />
                  )}
                </Field>

                <Field label="Explanation style" hint="How the idea is introduced.">
                  {(props) => (
                    <select
                      {...props}
                      value={form.style}
                      onChange={(event) => set("style", event.target.value as PromptStyle)}
                      className="h-9 w-full rounded-[var(--radius-control)] border border-input bg-surface px-3 text-sm shadow-sm"
                    >
                      {PROMPT_STYLES.map((style) => (
                        <option key={style} value={style}>
                          {STYLE_LABELS[style]}
                        </option>
                      ))}
                    </select>
                  )}
                </Field>

                <Field
                  label="Target duration (minutes)"
                  error={touched ? errors.duration : undefined}
                >
                  {(props) => (
                    <Input
                      {...props}
                      type="number"
                      min={1}
                      max={60}
                      value={form.duration}
                      onChange={(event) => set("duration", Number(event.target.value))}
                    />
                  )}
                </Field>

                <Field label="Output aspect ratio" hint={ASPECT_RATIO_DESCRIPTIONS[form.aspectRatio]}>
                  {(props) => (
                    <select
                      {...props}
                      value={form.aspectRatio}
                      onChange={(event) => set("aspectRatio", event.target.value as AspectRatio)}
                      className="h-9 w-full rounded-[var(--radius-control)] border border-input bg-surface px-3 text-sm shadow-sm"
                    >
                      {ASPECT_RATIOS.map((ratio) => (
                        <option key={ratio} value={ratio}>
                          {ASPECT_RATIO_LABELS[ratio]}
                        </option>
                      ))}
                    </select>
                  )}
                </Field>

                <Field label="Difficulty" hint="How much prior knowledge to assume.">
                  {(props) => (
                    <select
                      {...props}
                      value={form.difficulty}
                      onChange={(event) => set("difficulty", event.target.value as Difficulty)}
                      className="h-9 w-full rounded-[var(--radius-control)] border border-input bg-surface px-3 text-sm shadow-sm"
                    >
                      {DIFFICULTIES.map((difficulty) => (
                        <option key={difficulty} value={difficulty}>
                          {DIFFICULTY_LABELS[difficulty]}
                        </option>
                      ))}
                    </select>
                  )}
                </Field>
              </FieldGrid>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Style & content</CardTitle>
              <CardDescription>Colours and what to include at the end of the lesson.</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-4">
              <Field
                label="Preferred colours"
                hint="Colour names the animation may use, or your own hex values."
                error={touched ? errors.colors : undefined}
              >
                {(props) => (
                  <Input
                    {...props}
                    value={form.colors}
                    onChange={(event) => set("colors", event.target.value)}
                    placeholder="e.g. navy, violet, ivory"
                    autoComplete="off"
                  />
                )}
              </Field>

              <div>
                <p className="text-xs font-medium text-muted-foreground">Scene format colour names</p>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {SCENE_COLORS.map((color) => (
                    <button
                      key={color}
                      type="button"
                      onClick={() => {
                        const current = form.colors
                          .split(",")
                          .map((entry) => entry.trim())
                          .filter(Boolean)
                        if (!current.includes(color)) {
                          set("colors", [...current, color].join(", "))
                        }
                      }}
                      className="inline-flex items-center gap-1.5 rounded-full border border-border bg-surface px-2 py-0.5 text-xs transition-colors hover:bg-surface-alt focus-visible:outline-2 focus-visible:outline-ring"
                      title={`Add “${color}” to preferred colours`}
                    >
                      <span
                        aria-hidden
                        className="size-2.5 rounded-full ring-1 ring-inset ring-black/10"
                        style={{ backgroundColor: SCENE_COLOR_SWATCHES[color] }}
                      />
                      {color}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid gap-3">
                <ToggleRow
                  id="include-recap"
                  checked={form.includeRecap}
                  onChange={(value) => set("includeRecap", value)}
                  label="Include a recap"
                  description="A short summary of the key ideas at the end."
                />
                <ToggleRow
                  id="include-practice"
                  checked={form.includePractice}
                  onChange={(value) => set("includePractice", value)}
                  label="Include practice questions"
                  description="Questions students can try after watching."
                />
                <ToggleRow
                  id="include-voiceover"
                  checked={form.includeVoiceover}
                  onChange={(value) => set("includeVoiceover", value)}
                  label="Include a voiceover script"
                  description="Suggested narration text for each scene."
                />
              </div>

              <Field
                label="Additional instructions"
                hint="Anything else the AI should know. Optional."
                error={touched ? errors.additional : undefined}
              >
                {(props) => (
                  <Textarea
                    {...props}
                    value={form.additional}
                    onChange={(event) => set("additional", event.target.value)}
                    rows={3}
                    maxLength={1000}
                    placeholder="e.g. Use examples from carpentry. Avoid negative numbers."
                  />
                )}
              </Field>
              <p className="-mt-2 text-right text-xs text-muted-foreground">
                {form.additional.length}/1000
              </p>
            </CardContent>
          </Card>

          <div className="flex flex-wrap gap-3">
            <Button type="submit" size="lg" disabled={generate.isPending}>
              <Sparkles className="size-4" aria-hidden />
              {generate.isPending ? "Generating…" : "Generate Prompt"}
            </Button>
            <Button
              type="button"
              variant="secondary"
              size="lg"
              onClick={handleReset}
              disabled={!isDirty && !generate.data}
            >
              <RotateCcw className="size-4" aria-hidden />
              Reset Form
            </Button>
          </div>
        </div>

        {/* ---------------------------- Preview ---------------------------- */}
        <div className="lg:sticky lg:top-8 lg:self-start">
          <Card className="overflow-hidden">
            <CardHeader className="flex-row items-start justify-between gap-3 space-y-0">
              <div>
                <CardTitle>Generated prompt</CardTitle>
                <CardDescription>
                  {generate.data
                    ? showCompact
                      ? `Compact version — ${generate.data.compact_char_count.toLocaleString()} characters (${generate.data.compact_reduced_percent}% shorter).`
                      : `Full version — ${generate.data.char_count.toLocaleString()} characters.`
                    : "Fill in a topic and grade, then press Generate Prompt."}
                </CardDescription>
              </div>
              {generate.data ? (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowCompact((current) => !current)}
                  aria-pressed={showCompact}
                >
                  {showCompact ? (
                    <Eye className="size-4" aria-hidden />
                  ) : (
                    <EyeOff className="size-4" aria-hidden />
                  )}
                  {showCompact ? "Full" : "Compact"}
                </Button>
              ) : null}
            </CardHeader>

            <CardContent className="grid gap-4">
              {generate.isError ? (
                <ErrorPanel error={generate.error} title="Could not generate the prompt" />
              ) : null}

              {clipboardFailed && generate.data ? (
                <Alert tone="warning">
                  <AlertTitle>Copy it manually</AlertTitle>
                  <AlertDescription>
                    Your browser blocked automatic clipboard access. Click inside the preview below,
                    press <kbd className="rounded border border-current px-1 font-mono text-xs">Ctrl</kbd>+<kbd className="rounded border border-current px-1 font-mono text-xs">C</kbd>, then paste into your AI assistant.
                  </AlertDescription>
                </Alert>
              ) : null}

              {generate.data ? (
                <div className="grid gap-3">
                  <pre
                    tabIndex={0}
                    aria-label="Generated AI prompt"
                    className="scrollbar-slim max-h-[32rem] overflow-auto rounded-[var(--radius-control)] border border-border bg-surface-sunken p-4 font-mono text-xs leading-relaxed whitespace-pre-wrap text-foreground"
                  >
                    {showCompact ? generate.data.compact_prompt : generate.data.prompt}
                  </pre>
                  <div className="flex flex-wrap gap-2">
                    <Button type="button" onClick={() => void handleCopy()}>
                      <Copy className="size-4" aria-hidden />
                      Copy Prompt
                    </Button>
                    <Button type="button" variant="secondary" onClick={handleDownload}>
                      <Download className="size-4" aria-hidden />
                      Download as TXT
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="rounded-[var(--radius-control)] border border-dashed border-border bg-surface-alt/50 p-8 text-center">
                  <p className="text-sm text-muted-foreground">
                    Your prompt will appear here, ready to copy into any AI assistant.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          <p className="mt-3 text-xs text-muted-foreground">
            MathMotion Studio never contacts an AI service. You copy this prompt into the assistant
            you already use, and paste its answer back on the{" "}
            <span className="font-medium">Import Scene</span> page.
          </p>
        </div>
      </form>
    </div>
  )
}

function ToggleRow({
  id,
  checked,
  onChange,
  label,
  description,
}: {
  id: string
  checked: boolean
  onChange: (value: boolean) => void
  label: string
  description: string
}) {
  return (
    <div className="flex items-start justify-between gap-4 rounded-[var(--radius-control)] border border-border bg-surface-alt/40 px-3 py-2.5">
      <div className="min-w-0">
        <Label htmlFor={id}>{label}</Label>
        <p className="mt-0.5 text-xs text-muted-foreground">{description}</p>
      </div>
      <Switch id={id} checked={checked} onCheckedChange={onChange} />
    </div>
  )
}
