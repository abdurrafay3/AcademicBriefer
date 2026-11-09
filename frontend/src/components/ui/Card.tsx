import type { ReactNode } from "react";

export type Accent = "blue" | "amber" | "rose" | "violet" | "emerald";

const ACCENT_STYLES: Record<Accent, { border: string; iconBg: string }> = {
  blue: {
    border: "before:bg-sky-400",
    iconBg: "bg-sky-100 dark:bg-sky-500/15",
  },
  amber: {
    border: "before:bg-amber-400",
    iconBg: "bg-amber-100 dark:bg-amber-500/15",
  },
  rose: {
    border: "before:bg-rose-400",
    iconBg: "bg-rose-100 dark:bg-rose-500/15",
  },
  violet: {
    border: "before:bg-violet-400",
    iconBg: "bg-violet-100 dark:bg-violet-500/15",
  },
  emerald: {
    border: "before:bg-emerald-400",
    iconBg: "bg-emerald-100 dark:bg-emerald-500/15",
  },
};

interface CardProps {
  title: string;
  icon: ReactNode;
  accent: Accent;
  className?: string;
  children: ReactNode;
}

export function Card({ title, icon, accent, className = "", children }: CardProps) {
  const styles = ACCENT_STYLES[accent];

  return (
    <section
      className={`relative flex flex-col overflow-hidden rounded-2xl border border-black/5 bg-white shadow-sm shadow-black/[0.03] before:absolute before:inset-x-0 before:top-0 before:h-1 dark:border-white/10 dark:bg-neutral-900 ${styles.border} ${className}`}
    >
      <header className="flex items-center gap-3 px-5 pt-5 pb-3">
        <span className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-lg ${styles.iconBg}`}>
          {icon}
        </span>
        <h2 className="text-sm font-semibold tracking-wide text-neutral-800 uppercase dark:text-neutral-100">
          {title}
        </h2>
      </header>
      <div className="flex-1 px-5 pb-5">{children}</div>
    </section>
  );
}
