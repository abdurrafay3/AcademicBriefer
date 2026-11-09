import type { Deadline } from "@/lib/types";

const STYLES: Record<Deadline["priority"], string> = {
  HIGH: "bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300",
  MEDIUM: "bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-300",
  LOW: "bg-neutral-100 text-neutral-600 dark:bg-white/10 dark:text-neutral-400",
};

export function PriorityBadge({ priority }: { priority: Deadline["priority"] }) {
  return (
    <span className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold tracking-wide ${STYLES[priority]}`}>
      {priority}
    </span>
  );
}
