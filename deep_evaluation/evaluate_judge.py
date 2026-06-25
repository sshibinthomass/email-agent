"""
LLM-as-Judge evaluation module.

Runs the EmailJudgeNode on all test_gepa.csv samples (60 rows) and
evaluates the judge's accept/reject decisions using GEval and
deterministic accuracy / precision / recall / F1.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv

# Ensure project root is on sys.path for backend imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from deepeval import evaluate
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.evaluate.configs import AsyncConfig, DisplayConfig

from deep_evaluation.config import AzureGPT54Model
from deep_evaluation.data_loader import load_judge_dataset, JudgeSample
from deep_evaluation.metrics import JudgeDecisionAccuracyMetric
from backend.app.agent.nodes.email_judge_node import EmailJudgeNode


def _run_judge(sample: JudgeSample) -> Dict[str, Any]:
    """Run the judge on a single sample and return the result dict."""
    judge = EmailJudgeNode()

    state = {
        "subject": sample.subject,
        "body": sample.body,
        "category": sample.proposed_category,
        "reason": "",
        "JudgeVerted": None,
        "JudgeReasoning": None,
    }
    return judge.process(state)


def _compute_binary_metrics(results: List[Dict[str, Any]]) -> Dict[str, float]:
    """Compute precision, recall, F1 for the accept class."""
    tp = sum(1 for r in results if r["predicted_accepted"] and r["expected_accepted"])
    fp = sum(1 for r in results if r["predicted_accepted"] and not r["expected_accepted"])
    fn = sum(1 for r in results if not r["predicted_accepted"] and r["expected_accepted"])
    tn = sum(1 for r in results if not r["predicted_accepted"] and not r["expected_accepted"])

    accuracy = (tp + tn) / len(results) if results else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
    }


def run_judge_evaluation() -> List[Dict[str, Any]]:
    """
    Execute the full judge evaluation pipeline.

    Returns:
        List of per-sample result dicts with columns suitable for CSV output.
    """
    samples = load_judge_dataset()
    eval_model = AzureGPT54Model()

    # GEval metric for decision correctness
    decision_metric = GEval(
        name="Judge Decision Correctness",
        criteria=(
            "Determine whether the judge's accept/reject decision about an email "
            "category matches the expected ground-truth decision. The actual_output "
            "contains the judge's decision (accept or reject) and the expected_output "
            "contains the ground-truth decision. Rate correctness from 0 to 10, "
            "where 10 means they match perfectly (both accept or both reject), and 0 means they do not."
        ),
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        model=eval_model,
        threshold=0.5,
    )

    # GEval metric for reasoning quality
    reasoning_metric = GEval(
        name="Judge Reasoning Quality",
        criteria=(
            "Evaluate the quality of the judge's reasoning for its accept/reject "
            "decision about an email classification. The reasoning should be "
            "coherent, specific to the email content, and logically support the "
            "decision. Rate the quality from 0 to 10, where 10 is excellent and 0 is extremely poor."
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
        model=eval_model,
        threshold=0.5,
    )

    accuracy_metric = JudgeDecisionAccuracyMetric(threshold=0.5)

    # Build test cases by running the judge on each sample
    test_cases: List[LLMTestCase] = []
    raw_results: List[Dict[str, Any]] = []

    print(f"\n{'='*60}")
    print(f"  LLM-AS-JUDGE EVALUATION ({len(samples)} samples)")
    print(f"{'='*60}\n")

    for i, sample in enumerate(samples, 1):
        expected_str = "accept" if sample.expected_accepted else "reject"
        print(f"  [{i}/{len(samples)}] Judging: {sample.id} (expected: {expected_str})...", end=" ")

        result = _run_judge(sample)
        judge_decision = result.get("JudgeVerted", "reject")
        judge_reasoning = result.get("JudgeReasoning", "")
        predicted_accepted = judge_decision.strip().lower() == "accept"
        print(f"→ {judge_decision}")

        input_text = (
            f"Subject: {sample.subject}\n"
            f"Body: {sample.body}\n"
            f"Proposed Category: {sample.proposed_category}"
        )

        test_case = LLMTestCase(
            input=input_text,
            actual_output=f"Decision: {judge_decision}. Reasoning: {judge_reasoning}",
            expected_output=expected_str,
        )
        test_cases.append(test_case)

        raw_results.append({
            "id": sample.id,
            "subject": sample.subject,
            "body": sample.body,
            "proposed_category": sample.proposed_category,
            "expected_accepted": sample.expected_accepted,
            "predicted_accepted": predicted_accepted,
            "judge_decision": judge_decision,
            "judge_reasoning": judge_reasoning,
            "decision_correct": predicted_accepted == sample.expected_accepted,
        })

    # Run deepeval evaluation
    print(f"\n  Running DeepEval metrics...")
    eval_results = evaluate(
        test_cases=test_cases,
        metrics=[decision_metric, reasoning_metric, accuracy_metric],
        async_config=AsyncConfig(run_async=False),
        display_config=DisplayConfig(print_results=True),
    )

    # Enrich raw_results with metric scores
    for idx, result_row in enumerate(raw_results):
        if idx < len(test_cases):
            tc = test_cases[idx]
            # Extract metric scores from the test case
            for metric_data in tc.metrics_data if hasattr(tc, 'metrics_data') else []:
                if hasattr(metric_data, 'name') and hasattr(metric_data, 'score'):
                    result_row[f"metric_{metric_data.name}"] = metric_data.score

    # Compute binary classification metrics
    binary_metrics = _compute_binary_metrics(raw_results)

    print(f"\n  ┌─────────────────────────────────────────┐")
    print(f"  │  JUDGE RESULTS                           │")
    print(f"  │  Accuracy:  {binary_metrics['accuracy']:.2%}                       │")
    print(f"  │  Precision: {binary_metrics['precision']:.2%}                       │")
    print(f"  │  Recall:    {binary_metrics['recall']:.2%}                       │")
    print(f"  │  F1 Score:  {binary_metrics['f1']:.2%}                       │")
    print(f"  │  TP={binary_metrics['tp']} FP={binary_metrics['fp']} "
          f"FN={binary_metrics['fn']} TN={binary_metrics['tn']}                │")
    print(f"  └─────────────────────────────────────────┘\n")

    return raw_results
