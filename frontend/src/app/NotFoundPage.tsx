import { ArrowLeft } from "lucide-react"
import { Link } from "react-router"
import { Button } from "@/components/ui/button"
import { EmptyState } from "@/components/EmptyState"
import { PageHeader } from "@/components/PageHeader"

export function NotFoundPage() {
  return (
    <div className="grid gap-6">
      <PageHeader title="Page not found" guidance="That address does not match a screen in MathMotion Studio." />
      <EmptyState
        icon={ArrowLeft}
        title="Let's head back home"
        description="The link may be out of date, or the page may have moved."
        action={
          <Button asChild>
            <Link to="/">Go to Home</Link>
          </Button>
        }
      />
    </div>
  )
}
