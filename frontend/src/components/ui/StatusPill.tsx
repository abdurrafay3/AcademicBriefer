import type { StepStatus } from "@/lib/types";

const STYLES: Record<StepStatus, string> = {
  success: "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300",
  failed: "bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300",
  skipped: "bg-neutral-100 text-neutral-500 dark:bg-white/10 dark:text-neutral-400",
};

const DOT_STYLES: Record<StepStatus, string> = {
  success: "bg-emerald-500",
  failed: "bg-rose-500",
  skipped: "bg-neutral-400",
};

export function StatusPill({ label, status }: { label: string; status: StepStatus }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${STYLES[status]}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${DOT_STYLES[status]}`} />
      {label}
    </span>
  );
}
