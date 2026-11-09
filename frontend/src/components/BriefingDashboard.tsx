"use client";

import { useEffect, useRef, useState } from "react";
import { generateBriefing } from "@/lib/api";
import type { BriefingResponse } from "@/lib/types";
import { Card } from "@/components/ui/Card";
import { StatusPill } from "@/components/ui/StatusPill";
import { PriorityBadge } from "@/components/ui/PriorityBadge";
import { EmptyState } from "@/components/ui/EmptyState";

const LOADING_STEPS = [
  "Fetching your emails…",
  "Scraping Canvas for assignments…",
  "Syncing assignments to your calendar…",
  "Summarizing everything with AI…",
];

function formatDateTime(iso: string) {
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(iso));
  } catch {
    return iso;
  }
}

function formatDueDate(value: string | null) {
  if (!value) return "No due date";
  const formatted = formatDateTime(value);
  return formatted === value ? value : formatted;
}

export function BriefingDashboard() {
  const [data, setData] = useState<BriefingResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stepIndex, setStepIndex] = useState(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!loading) {
      if (intervalRef.current) clearInterval(intervalRef.current);
      return;
    }
    intervalRef.current = setInterval(() => {
      setStepIndex((i) => Math.min(i + 1, LOADING_STEPS.length - 1));
    }, 6000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [loading]);

  async function handleGenerate() {
    setStepIndex(0);
    setLoading(true);
    setError(null);
    try {
      const result = await generateBriefing();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  const summary = data?.summary ?? null;

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-6 px-6 py-10">
      <header className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-4">
          <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-neutral-900 text-sm font-bold text-white dark:bg-white dark:text-neutral-900">
            AB
          </span>
          <div>
            <h1 className="text-xl font-semibold text-neutral-900 dark:text-neutral-50">AcademicBriefer</h1>
            <p className="text-sm text-neutral-500 dark:text-neutral-400">
              Your emails and Canvas, distilled into one morning briefing.
            </p>
          </div>
        </div>

        <div className="flex flex-col items-start gap-3 sm:items-end">
          {data && (
            <div className="flex flex-wrap gap-2">
              <StatusPill label="Email" status={data.email_status} />
              <StatusPill label="Canvas" status={data.canvas_status} />
              <StatusPill label="Calendar" status={data.calendar_status} />
            </div>
          )}
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-xl bg-neutral-900 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-neutral-700 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-white dark:text-neutral-900 dark:hover:bg-neutral-200"
          >
            {loading && (
              <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/40 border-t-white dark:border-neutral-900/30 dark:border-t-neutral-900" />
            )}
            {loading ? "Generating…" : "Generate Briefing"}
          </button>
        </div>
      </header>

      {data && !loading && (
        <p className="-mt-2 text-xs text-neutral-400 dark:text-neutral-500">
          Last generated {formatDateTime(data.generated_at)} · {data.emails_scraped} emails ·{" "}
          {data.assignments.length} Canvas assignments
        </p>
      )}

      {loading && (
        <p className="-mt-2 flex items-center gap-2 text-sm text-neutral-500 dark:text-neutral-400">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-neutral-400" />
          {LOADING_STEPS[stepIndex]}
        </p>
      )}

      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-300">
          Couldn&apos;t generate a briefing: {error}
        </div>
      )}

      <main className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <Card title="Announcements" icon="📢" accent="blue">
          {summary && summary.important_announcements.length > 0 ? (
            <ul className="space-y-3">
              {summary.important_announcements.map((item, i) => (
                <li key={i} className="flex gap-2 text-sm text-neutral-700 dark:text-neutral-300">
                  <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-sky-400" />
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState>
              {summary ? "No important announcements right now." : "Generate a briefing to see important announcements from your emails."}
            </EmptyState>
          )}
        </Card>

        <Card title="Opportunities" icon="🎯" accent="amber">
          {summary && summary.opportunities.length > 0 ? (
            <ul className="space-y-4">
              {summary.opportunities.map((item, i) => (
                <li key={i} className="text-sm">
                  <p className="font-medium text-neutral-800 dark:text-neutral-100">{item.title}</p>
                  {item.deadline && (
                    <p className="mt-0.5 text-xs font-medium text-amber-600 dark:text-amber-400">
                      Due {item.deadline}
                    </p>
                  )}
                  <p className="mt-1 text-neutral-500 dark:text-neutral-400">{item.description}</p>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState>
              {summary ? "No new opportunities right now." : "Scholarships, internships, and career opportunities will show up here."}
            </EmptyState>
          )}
        </Card>

        <Card title="Assignments" icon="📝" accent="rose">
          <div className="space-y-4">
            {data && data.assignments.length > 0 ? (
              <ul className="space-y-3">
                {data.assignments.map((item, i) => (
                  <li key={i} className="text-sm">
                    <p className="font-medium text-neutral-800 dark:text-neutral-100">{item.title}</p>
                    <p className="mt-0.5 text-xs font-medium text-rose-600 dark:text-rose-400">
                      {formatDueDate(item.due_date)}
                      {item.max_points != null ? ` · ${item.max_points} pts` : ""}
                    </p>
                  </li>
                ))}
              </ul>
            ) : (
              <EmptyState>
                {data ? "No Canvas assignments found." : "Canvas assignments (already synced to your calendar) will appear here."}
              </EmptyState>
            )}

            {summary && summary.deadlines.length > 0 && (
              <div className="border-t border-neutral-100 pt-3 dark:border-white/10">
                <p className="mb-2 text-[11px] font-semibold tracking-wide text-neutral-400 uppercase dark:text-neutral-500">
                  From your emails
                </p>
                <ul className="space-y-2">
                  {summary.deadlines.map((item, i) => (
                    <li key={i} className="flex items-start justify-between gap-2 text-sm">
                      <div>
                        <p className="font-medium text-neutral-800 dark:text-neutral-100">{item.title}</p>
                        <p className="text-xs text-neutral-500 dark:text-neutral-400">{item.due_date}</p>
                      </div>
                      <PriorityBadge priority={item.priority} />
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </Card>

        <Card title="Events & Workshops" icon="🎉" accent="violet">
          {summary && summary.events.length > 0 ? (
            <ul className="space-y-4">
              {summary.events.map((item, i) => (
                <li key={i} className="text-sm">
                  <p className="font-medium text-neutral-800 dark:text-neutral-100">{item.title}</p>
                  <p className="mt-0.5 text-xs font-medium text-violet-600 dark:text-violet-400">
                    {item.date}
                    {item.location ? ` · ${item.location}` : ""}
                  </p>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState>
              {summary ? "No upcoming events or workshops." : "Upcoming events and workshops worth attending will show up here."}
            </EmptyState>
          )}
        </Card>

        <Card title="Summary / Briefing" icon="🗞️" accent="emerald" className="sm:col-span-2 lg:col-span-4">
          {summary ? (
            <p className="text-sm leading-relaxed text-neutral-700 dark:text-neutral-300">{summary.summary}</p>
          ) : (
            <EmptyState>
              Click &quot;Generate Briefing&quot; to fetch your emails and Canvas, sync your calendar, and get a
              plain-English summary.
            </EmptyState>
          )}
        </Card>
      </main>
    </div>
  );
}
