import { Badge, type BadgeTone } from "@/components/ui/badge"
import { JOB_STATE_LABELS, JOB_STATE_TONES } from "@/lib/constants"
import type { JobState } from "@/lib/types"

/**
 * A status chip that always pairs colour with a text label — colour alone
 * never conveys state (UI spec §1.2 rule 4).
 */
export function JobStateChip({ status }: { status: JobState }) {
  const tone: BadgeTone = JOB_STATE_TONES[status]
  return <Badge tone={tone}>{JOB_STATE_LABELS[status]}</Badge>
}

export function ValidationChip({ valid }: { valid: boolean | null }) {
  if (valid === null) return <Badge tone="neutral">Not checked</Badge>
  return valid ? <Badge tone="success">Valid</Badge> : <Badge tone="destructive">Has errors</Badge>
}
