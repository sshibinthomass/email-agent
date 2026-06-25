"""
Main runner for DeepEval evaluation suite.

Orchestrates classifier and judge evaluations, writes results to CSV files
inside a datetime-stamped folder under deep_evaluation/outputs/.

Output structure:
    deep_evaluation/outputs/<YYYY-MM-DD_HH-MM-SS>/
        classifier.csv   — per-sample classifier results
        judge.csv         — per-sample judge results
        overall.csv       — aggregate summary of both evaluations
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from deep_evaluation.evaluate_classifier import run_classifier_evaluation
from deep_evaluation.evaluate_judge import run_judge_evaluation


# ---------------------------------------------------------------------------
# CSV output helpers
# ---------------------------------------------------------------------------
OUTPUTS_DIR = Path(__file__).resolve().parent / "outputs"


def _create_run_directory() -> Path:
    """Create a timestamped output directory and return its path."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = OUTPUTS_DIR / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def _write_csv(filepath: Path, rows: List[Dict[str, Any]]) -> None:
    """Write a list of dicts to a CSV file."""
    if not rows:
        print(f"  ⚠ No data to write to {filepath.name}")
        return

    fieldnames = list(rows[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  ✓ Saved {filepath.name} ({len(rows)} rows)")


def _build_overall_summary(
    classifier_results: List[Dict[str, Any]],
    judge_results: List[Dict[str, Any]],
    run_timestamp: str,
) -> List[Dict[str, Any]]:
    """Build the overall summary rows combining both evaluations."""
    rows: List[Dict[str, Any]] = []

    # --- Classifier summary ---
    if classifier_results:
        total = len(classifier_results)
        correct = sum(1 for r in classifier_results if r.get("exact_match"))
        accuracy = correct / total if total > 0 else 0.0
        rows.append({
            "evaluation": "classifier",
            "metric": "exact_match_accuracy",
            "value": f"{accuracy:.4f}",
            "correct": correct,
            "total": total,
            "datetime": run_timestamp,
        })

    # --- Judge summary ---
    if judge_results:
        total = len(judge_results)
        correct = sum(1 for r in judge_results if r.get("decision_correct"))
        accuracy = correct / total if total > 0 else 0.0

        tp = sum(1 for r in judge_results if r["predicted_accepted"] and r["expected_accepted"])
        fp = sum(1 for r in judge_results if r["predicted_accepted"] and not r["expected_accepted"])
        fn = sum(1 for r in judge_results if not r["predicted_accepted"] and r["expected_accepted"])
        tn = sum(1 for r in judge_results if not r["predicted_accepted"] and not r["expected_accepted"])

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        rows.append({
            "evaluation": "judge",
            "metric": "decision_accuracy",
            "value": f"{accuracy:.4f}",
            "correct": correct,
            "total": total,
            "datetime": run_timestamp,
        })
        rows.append({
            "evaluation": "judge",
            "metric": "precision",
            "value": f"{precision:.4f}",
            "correct": tp,
            "total": tp + fp,
            "datetime": run_timestamp,
        })
        rows.append({
            "evaluation": "judge",
            "metric": "recall",
            "value": f"{recall:.4f}",
            "correct": tp,
            "total": tp + fn,
            "datetime": run_timestamp,
        })
        rows.append({
            "evaluation": "judge",
            "metric": "f1_score",
            "value": f"{f1:.4f}",
            "correct": "",
            "total": "",
            "datetime": run_timestamp,
        })

    # --- Overall summary ---
    if classifier_results and judge_results:
        cls_acc = sum(1 for r in classifier_results if r.get("exact_match")) / len(classifier_results)
        jdg_acc = sum(1 for r in judge_results if r.get("decision_correct")) / len(judge_results)
        overall = (cls_acc + jdg_acc) / 2.0
        rows.append({
            "evaluation": "overall",
            "metric": "average_accuracy",
            "value": f"{overall:.4f}",
            "correct": "",
            "total": "",
            "datetime": run_timestamp,
        })

    return rows


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Run DeepEval evaluation for Email Classifier and/or LLM Judge."
    )
    parser.add_argument(
        "--target",
        choices=["classifier", "judge", "all"],
        default="all",
        help="Which evaluation to run (default: all).",
    )
    args = parser.parse_args()

    run_dir = _create_run_directory()
    run_timestamp = run_dir.name  # e.g. "2026-06-25_21-13-30"

    print(f"\n{'#'*60}")
    print(f"  DeepEval Evaluation Suite")
    print(f"  Target: {args.target}")
    print(f"  Output: {run_dir}")
    print(f"{'#'*60}")

    classifier_results: List[Dict[str, Any]] = []
    judge_results: List[Dict[str, Any]] = []

    # --- Run classifier evaluation ---
    if args.target in ("classifier", "all"):
        classifier_results = run_classifier_evaluation()
        _write_csv(run_dir / "classifier.csv", classifier_results)

    # --- Run judge evaluation ---
    if args.target in ("judge", "all"):
        judge_results = run_judge_evaluation()
        _write_csv(run_dir / "judge.csv", judge_results)

    # --- Write overall summary ---
    overall_rows = _build_overall_summary(
        classifier_results, judge_results, run_timestamp
    )
    _write_csv(run_dir / "overall.csv", overall_rows)

    print(f"\n{'#'*60}")
    print(f"  Evaluation complete!")
    print(f"  Results saved to: {run_dir}")
    print(f"{'#'*60}\n")


if __name__ == "__main__":
    main()
