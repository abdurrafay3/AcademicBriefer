"""Times each stage of the real, live pipeline (email scrape, Canvas scrape,
calendar sync, LLM summarization) using the actual production functions
against real accounts. This is NOT a mock - it opens real browser sessions
and writes real events to Google Calendar.

Run with: uv run python -m backend.benchmarks.latency_benchmark
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

from backend.ai.briefing_graph import generate_briefing_summary
from backend.services.calendar.calendar import add_assignments_to_calendar
from backend.services.courses.canvas_scraper import get_canvas_assignments
from backend.services.email.email_scraper import get_emails


def timed(label: str, fn):
    print(f"[{label}] starting...")
    start = time.perf_counter()
    try:
        result = fn()
        elapsed = time.perf_counter() - start
        print(f"[{label}] done in {elapsed:.2f}s")
        return result, elapsed, None
    except Exception as e:
        elapsed = time.perf_counter() - start
        print(f"[{label}] FAILED after {elapsed:.2f}s: {e}")
        return None, elapsed, str(e)


def run() -> dict:
    total_start = time.perf_counter()

    emails, email_s, email_err = timed("email scrape", get_emails)
    emails = emails or []

    assignments, canvas_s, canvas_err = timed("canvas scrape", get_canvas_assignments)
    assignments = assignments or []

    if assignments:
        _, calendar_s, calendar_err = timed(
            "calendar sync", lambda: add_assignments_to_calendar(assignments)
        )
    else:
        calendar_s, calendar_err = 0.0, None
        print("[calendar sync] skipped, no assignments scraped")

    summary, llm_s, llm_err = timed(
        "llm summarization", lambda: generate_briefing_summary(emails, assignments)
    )

    total_s = time.perf_counter() - total_start

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {"emails": len(emails), "assignments": len(assignments)},
        "stages_s": {
            "email_scrape": round(email_s, 2),
            "canvas_scrape": round(canvas_s, 2),
            "calendar_sync": round(calendar_s, 2),
            "llm_summarization": round(llm_s, 2),
        },
        "errors": {
            "email_scrape": email_err,
            "canvas_scrape": canvas_err,
            "calendar_sync": calendar_err,
            "llm_summarization": llm_err,
        },
        "total_s": round(total_s, 2),
        "summary": summary.model_dump() if summary else None,
    }


def print_summary(results: dict) -> None:
    print("\n=== Live Pipeline Latency Benchmark ===")
    print(f"Emails scraped: {results['counts']['emails']} | Assignments scraped: {results['counts']['assignments']}\n")
    for stage, seconds in results["stages_s"].items():
        err = results["errors"][stage]
        status = f"FAILED: {err}" if err else "ok"
        print(f"{stage:<20}{seconds:>8.2f}s   {status}")
    print(f"\n{'TOTAL (end-to-end)':<20}{results['total_s']:>8.2f}s")


if __name__ == "__main__":
    results = run()
    print_summary(results)

    out_dir = Path(__file__).parent / "results"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"latency_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nFull results written to {out_path}")
