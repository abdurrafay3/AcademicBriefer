"""Benchmarks the real LLM extraction pipeline (backend.ai.briefing_graph)
against a hand-labeled synthetic dataset (accuracy_data.py) and reports
precision / recall / F1 per category, plus noise-rejection rate and latency.

Run with: uv run python -m backend.benchmarks.accuracy_benchmark
"""

import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from backend.ai.briefing_graph import generate_briefing_summary
from backend.benchmarks.accuracy_data import BATCHES
from backend.schemas.email import EmailDigest

CATEGORIES = ["deadline", "opportunity", "event", "announcement"]
DEFAULT_TRIALS = 5


def category_texts(summary: EmailDigest, category: str) -> list[str]:
    if category == "deadline":
        return [f"{d.title} {d.description}" for d in summary.deadlines]
    if category == "opportunity":
        return [f"{o.title} {o.description}" for o in summary.opportunities]
    if category == "event":
        return [f"{e.title} {e.location or ''}" for e in summary.events]
    if category == "announcement":
        return list(summary.important_announcements)
    raise ValueError(category)


def score_category(expected_phrases: list[str], extracted_texts: list[str]) -> tuple[int, int, int]:
    matched_extracted: set[int] = set()
    tp = 0
    fn = 0
    for phrase in expected_phrases:
        found = False
        for i, text in enumerate(extracted_texts):
            if phrase.lower() in text.lower():
                found = True
                matched_extracted.add(i)
                break
        if found:
            tp += 1
        else:
            fn += 1
    fp = len(extracted_texts) - len(matched_extracted)
    return tp, fp, fn


def run_trial(trial_index: int) -> dict:
    totals = {cat: {"tp": 0, "fp": 0, "fn": 0} for cat in CATEGORIES}
    noise_total = 0
    noise_leaked = 0
    batch_reports = []
    latencies = []

    for batch_index, batch in enumerate(BATCHES):
        emails = [item.email for item in batch]

        start = time.perf_counter()
        summary = generate_briefing_summary(emails, [])
        elapsed = time.perf_counter() - start
        latencies.append(elapsed)

        full_text = json.dumps(summary.model_dump()).lower()

        batch_scores = {}
        for category in CATEGORIES:
            expected = [item.expect for item in batch if item.label == category and item.expect]
            extracted = category_texts(summary, category)
            tp, fp, fn = score_category(expected, extracted)
            totals[category]["tp"] += tp
            totals[category]["fp"] += fp
            totals[category]["fn"] += fn
            batch_scores[category] = {"tp": tp, "fp": fp, "fn": fn, "expected": len(expected), "extracted": len(extracted)}

        noise_items = [item for item in batch if item.label == "noise" and item.leak_phrase]
        leaked_this_batch = 0
        for item in noise_items:
            if item.leak_phrase.lower() in full_text:
                leaked_this_batch += 1
        noise_total += len(noise_items)
        noise_leaked += leaked_this_batch

        batch_reports.append(
            {
                "batch": batch_index,
                "emails": len(emails),
                "latency_s": round(elapsed, 2),
                "scores": batch_scores,
                "noise_emails": len(noise_items),
                "noise_leaked": leaked_this_batch,
                "narrative_summary": summary.summary,
            }
        )
        print(
            f"  trial {trial_index} batch {batch_index}: {len(emails)} emails, {elapsed:.2f}s, "
            f"noise leaked {leaked_this_batch}/{len(noise_items)}"
        )

    per_category = {}
    micro_tp = micro_fp = micro_fn = 0
    for category in CATEGORIES:
        tp, fp, fn = totals[category]["tp"], totals[category]["fp"], totals[category]["fn"]
        micro_tp += tp
        micro_fp += fp
        micro_fn += fn
        precision = tp / (tp + fp) if (tp + fp) else None
        recall = tp / (tp + fn) if (tp + fn) else None
        f1 = (2 * precision * recall / (precision + recall)) if precision and recall else None
        per_category[category] = {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }

    micro_precision = micro_tp / (micro_tp + micro_fp) if (micro_tp + micro_fp) else None
    micro_recall = micro_tp / (micro_tp + micro_fn) if (micro_tp + micro_fn) else None
    micro_f1 = (
        (2 * micro_precision * micro_recall / (micro_precision + micro_recall))
        if micro_precision and micro_recall
        else None
    )

    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": "gpt-4o",
        "num_batches": len(BATCHES),
        "num_emails": sum(len(b) for b in BATCHES),
        "per_category": per_category,
        "overall": {
            "precision": micro_precision,
            "recall": micro_recall,
            "f1": micro_f1,
        },
        "noise_rejection_rate": 1 - (noise_leaked / noise_total) if noise_total else None,
        "noise_total": noise_total,
        "noise_leaked": noise_leaked,
        "latency": {
            "per_batch_s": [round(latency, 2) for latency in latencies],
            "mean_s": round(sum(latencies) / len(latencies), 2),
            "min_s": round(min(latencies), 2),
            "max_s": round(max(latencies), 2),
        },
        "batches": batch_reports,
    }
    return results


def print_trial_summary(results: dict) -> None:
    print(f"{'Category':<14}{'Precision':>11}{'Recall':>11}{'F1':>11}{'TP':>6}{'FP':>6}{'FN':>6}")
    for category, scores in results["per_category"].items():
        p = f"{scores['precision']:.0%}" if scores["precision"] is not None else "n/a"
        r = f"{scores['recall']:.0%}" if scores["recall"] is not None else "n/a"
        f1 = f"{scores['f1']:.0%}" if scores["f1"] is not None else "n/a"
        print(f"{category:<14}{p:>11}{r:>11}{f1:>11}{scores['tp']:>6}{scores['fp']:>6}{scores['fn']:>6}")
    overall = results["overall"]
    print(f"Overall: precision {overall['precision']:.1%}, recall {overall['recall']:.1%}, F1 {overall['f1']:.1%}")
    print(
        f"Noise rejection: {results['noise_rejection_rate']:.1%} "
        f"({results['noise_total'] - results['noise_leaked']}/{results['noise_total']})"
    )


def _mean_std(values: list[float]) -> dict:
    return {
        "mean": round(statistics.mean(values), 4),
        "std": round(statistics.pstdev(values), 4) if len(values) > 1 else 0.0,
        "min": round(min(values), 4),
        "max": round(max(values), 4),
    }


def aggregate(trials: list[dict]) -> dict:
    per_category_agg = {}
    for category in CATEGORIES:
        per_category_agg[category] = {
            metric: _mean_std([t["per_category"][category][metric] for t in trials])
            for metric in ("precision", "recall", "f1")
        }

    overall_agg = {
        metric: _mean_std([t["overall"][metric] for t in trials]) for metric in ("precision", "recall", "f1")
    }
    noise_agg = _mean_std([t["noise_rejection_rate"] for t in trials])
    all_latencies = [latency for t in trials for latency in t["latency"]["per_batch_s"]]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": trials[0]["model"],
        "num_trials": len(trials),
        "num_batches_per_trial": trials[0]["num_batches"],
        "num_emails_per_trial": trials[0]["num_emails"],
        "per_category": per_category_agg,
        "overall": overall_agg,
        "noise_rejection_rate": noise_agg,
        "latency_s": _mean_std(all_latencies),
        "trials": trials,
    }


def print_aggregate_summary(agg: dict) -> None:
    print("\n=== LLM Extraction Accuracy Benchmark (aggregated across trials) ===")
    print(
        f"Model: {agg['model']} | Trials: {agg['num_trials']} | "
        f"Batches/trial: {agg['num_batches_per_trial']} | Emails/trial: {agg['num_emails_per_trial']}\n"
    )
    print(f"{'Category':<14}{'Precision':>16}{'Recall':>16}{'F1':>16}")
    for category, scores in agg["per_category"].items():
        p = scores["precision"]
        r = scores["recall"]
        f1 = scores["f1"]
        print(
            f"{category:<14}"
            f"{p['mean']:.0%} (±{p['std']:.0%})".rjust(16)
            + f"{r['mean']:.0%} (±{r['std']:.0%})".rjust(16)
            + f"{f1['mean']:.0%} (±{f1['std']:.0%})".rjust(16)
        )

    overall = agg["overall"]
    print(
        f"\nOverall precision: {overall['precision']['mean']:.1%} (±{overall['precision']['std']:.1%})"
    )
    print(f"Overall recall:    {overall['recall']['mean']:.1%} (±{overall['recall']['std']:.1%})")
    print(f"Overall F1:        {overall['f1']['mean']:.1%} (±{overall['f1']['std']:.1%})")
    noise = agg["noise_rejection_rate"]
    print(f"Noise rejection:   {noise['mean']:.1%} (±{noise['std']:.1%})")
    latency = agg["latency_s"]
    print(
        f"LLM latency:       mean {latency['mean']}s (±{latency['std']}s), "
        f"min {latency['min']}s, max {latency['max']}s per batch of "
        f"~{agg['num_emails_per_trial'] // agg['num_batches_per_trial']} emails"
    )


if __name__ == "__main__":
    n_trials = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TRIALS

    trials = []
    for trial_index in range(n_trials):
        print(f"\n--- Trial {trial_index + 1}/{n_trials} ---")
        result = run_trial(trial_index)
        print_trial_summary(result)
        trials.append(result)

    agg = aggregate(trials)
    print_aggregate_summary(agg)

    out_dir = Path(__file__).parent / "results"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"accuracy_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    out_path.write_text(json.dumps(agg, indent=2))
    print(f"\nFull results written to {out_path}")
