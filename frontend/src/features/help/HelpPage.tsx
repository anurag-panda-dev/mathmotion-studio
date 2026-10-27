import {
  BookOpen,
  ExternalLink,
  HelpCircle,
  Lock,
  Sparkles,
  Upload,
  Wand2,
} from "lucide-react"
import { Link } from "react-router"
import { DependencyRow } from "@/components/DependencyStatus"
import { PageHeader } from "@/components/PageHeader"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useHealth } from "@/lib/queries"

const WORKFLOW = [
  {
    icon: Wand2,
    title: "1. Describe the lesson you want",
    body: "Open Create Animation, enter a topic and a grade level, and adjust anything else you care about. MathMotion Studio writes a complete, topic-specific prompt on your computer — no AI service is contacted.",
    to: "/create",
    cta: "Open Create Animation",
  },
  {
    icon: Sparkles,
    title: "2. Paste the prompt into any AI assistant",
    body: "Use whichever assistant you already know — ChatGPT, Claude, Gemini, a local model, anything capable. Paste the prompt and ask for the answer as a scene.md file. You need no API key, account, or subscription for MathMotion Studio.",
  },
  {
    icon: Upload,
    title: "3. Import the scene.md file",
    body: "Save the assistant's reply as a plain .md file, then drop it on the Import Scene page. MathMotion Studio parses and validates it, and shows you exactly what will be animated — scene by scene.",
    to: "/import",
    cta: "Open Import Scene",
  },
  {
    icon: BookOpen,
    title: "4. Review, then render",
    body: "Check the scene timeline, fix any validation errors with Edit Source, and press Render Animation. Rendering happens locally with Manim; you can watch progress, read the log, and cancel at any time.",
    to: "/jobs",
    cta: "Open Rendering Jobs",
  },
]

const TROUBLESHOOTING = [
  {
    question: "Validation reports errors — what do I do?",
    body: "Each error names the scene, the field, and a suggested correction. Use Edit Source on the lesson page for small fixes. For larger problems, copy the error text back to your AI assistant and ask it to correct the file, then re-upload.",
  },
  {
    question: "Rendering is disabled",
    body: "The Render Animation button unlocks only after validation passes. Fix every error listed in the validation report, press Validate Scene again, then render.",
  },
  {
    question: "A dependency is reported missing",
    body: "Settings → Dependency health shows exactly what is missing and links to its installation guide. Manim and FFmpeg are required to render; LaTeX is optional and only affects advanced formula typesetting.",
  },
  {
    question: "The render failed partway through",
    body: "Open the render job, expand Technical details, and read the log. The most common causes are a formula the typesetter could not build, or an unsupported instruction in the scene file. Your lesson is never modified by a failed render — press Retry once fixed.",
  },
  {
    question: "The clipboard will not copy the prompt",
    body: "Some browsers block clipboard access for local pages. The prompt stays visible and selectable in the preview — click it and press Ctrl+C, or use Download as TXT.",
  },
]

export function HelpPage() {
  const health = useHealth()

  return (
    <div className="grid gap-8">
      <PageHeader
        title="Help & Getting Started"
        guidance="MathMotion Studio turns a maths topic into a short animated lesson. It runs entirely on this computer — nothing about your lessons is sent anywhere."
      />

      <Alert tone="primary">
        <Lock className="size-4" aria-hidden />
        <AlertTitle>Your lessons never leave this computer</AlertTitle>
        <AlertDescription>
          This application contains no AI integration, requires no API key, no account, and no
          subscription. It writes a prompt locally; you paste that prompt into the AI assistant you
          already use, and paste the answer back here.
        </AlertDescription>
      </Alert>

      <section aria-labelledby="workflow-heading">
        <h2 id="workflow-heading" className="text-lg font-semibold">
          The four steps
        </h2>
        <ol className="mt-4 grid gap-4 lg:grid-cols-2">
          {WORKFLOW.map((step) => (
            <li key={step.title}>
              <Card className="h-full">
                <CardHeader>
                  <span className="mb-1 flex size-8 items-center justify-center rounded-[var(--radius-control)] bg-primary-subtle text-primary">
                    <step.icon className="size-4" aria-hidden />
                  </span>
                  <CardTitle>{step.title}</CardTitle>
                  <CardDescription>{step.body}</CardDescription>
                </CardHeader>
                {step.to ? (
                  <CardContent>
                    <Button asChild variant="secondary" size="sm">
                      <Link to={step.to}>{step.cta}</Link>
                    </Button>
                  </CardContent>
                ) : null}
              </Card>
            </li>
          ))}
        </ol>
      </section>

      <section aria-labelledby="setup-heading">
        <h2 id="setup-heading" className="text-lg font-semibold">
          Your setup
        </h2>
        <Card className="mt-4">
          <CardContent className="py-5">
            {health.isLoading ? (
              <p className="text-sm text-muted-foreground">Checking your installation…</p>
            ) : health.data ? (
              <div className="grid divide-y divide-border">
                {health.data.dependencies.map((dependency) => (
                  <DependencyRow key={dependency.name} dependency={dependency} />
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                Could not check your setup. See{" "}
                <Link to="/settings" className="underline underline-offset-2">
                  Settings
                </Link>{" "}
                for details.
              </p>
            )}
          </CardContent>
        </Card>
      </section>

      <section aria-labelledby="troubleshooting-heading">
        <h2 id="troubleshooting-heading" className="text-lg font-semibold">
          Common problems
        </h2>
        <Card className="mt-4">
          <CardContent className="divide-y divide-border py-2">
            {TROUBLESHOOTING.map((item) => (
              <details key={item.question} className="group py-3">
                <summary className="flex cursor-pointer list-none items-center justify-between gap-3 text-sm font-medium">
                  <span className="flex items-center gap-2">
                    <HelpCircle className="size-4 shrink-0 text-muted-foreground" aria-hidden />
                    {item.question}
                  </span>
                  <span
                    aria-hidden
                    className="text-muted-foreground transition-transform group-open:rotate-90"
                  >
                    ›
                  </span>
                </summary>
                <p className="mt-2 pl-6 text-sm text-muted-foreground">{item.body}</p>
              </details>
            ))}
          </CardContent>
        </Card>
      </section>

      <section aria-labelledby="docs-heading" className="grid gap-4">
        <h2 id="docs-heading" className="text-lg font-semibold">
          Where your data lives
        </h2>
        <Card>
          <CardContent className="grid gap-3 py-5 text-sm">
            {health.data ? (
              <dl className="grid gap-2">
                <Row label="Lesson database & metadata" value={health.data.directories.data} />
                <Row label="Rendered videos" value={health.data.directories.output} />
                <Row label="Render logs" value={health.data.directories.logs} />
              </dl>
            ) : (
              <p className="text-muted-foreground">Start the application to see these paths.</p>
            )}
            <p className="text-xs text-muted-foreground">
              Back up your work by copying the data and output folders. Deleting a lesson inside the
              app removes its source file permanently.
            </p>
          </CardContent>
        </Card>

        <div className="flex flex-wrap gap-3">
          <Button asChild variant="secondary">
            <a
              href="https://docs.manim.community/en/stable/installation.html"
              target="_blank"
              rel="noreferrer"
            >
              Manim installation guide
              <ExternalLink className="size-4" aria-hidden />
            </a>
          </Button>
          <Button asChild variant="secondary">
            <a href="https://ffmpeg.org/download.html" target="_blank" rel="noreferrer">
              FFmpeg download
              <ExternalLink className="size-4" aria-hidden />
            </a>
          </Button>
        </div>
      </section>
    </div>
  )
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-0.5 sm:flex-row sm:items-baseline sm:justify-between sm:gap-4">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="break-all font-mono text-xs">{value}</dd>
    </div>
  )
}
