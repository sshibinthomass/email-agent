"""
Email Classifier evaluation module.

Runs the EmailClassifierNode on test_gepa.csv (accepted==true) samples
and evaluates predictions using both GEval and deterministic accuracy.
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
from deep_evaluation.data_loader import load_classifier_dataset, ClassifierSample
from deep_evaluation.metrics import ClassificationAccuracyMetric
from backend.app.agent.nodes.email_classifier_node import EmailClassifierNode
from backend.app.agent.llms.azure_llm import AzureLLM
from deep_evaluation.config import (
    AZURE_API_KEY,
    AZURE_ENDPOINT,
    AZURE_API_VERSION,
    AZURE_DEPLOYMENT,
)


def _build_classifier_llm():
    """Build the Azure LLM used by the classifier under test."""
    controls = {
        "AZURE_OPENAI_API_KEY": AZURE_API_KEY,
        "AZURE_OPENAI_ENDPOINT": AZURE_ENDPOINT,
        "AZURE_OPENAI_API_VERSION": AZURE_API_VERSION,
        "selected_llm": AZURE_DEPLOYMENT,
    }
    return AzureLLM(controls).get_base_llm()


def _run_classifier(sample: ClassifierSample) -> Dict[str, Any]:
    """Run the classifier on a single sample and return the result dict."""
    llm = _build_classifier_llm()
    classifier = EmailClassifierNode(llm)

    state = {
        "subject": sample.subject,
        "body": sample.body,
        "category": None,
        "reason": None,
    }
    return classifier.process(state)


def run_classifier_evaluation() -> List[Dict[str, Any]]:
    """
    Execute the full classifier evaluation pipeline.

    Returns:
        List of per-sample result dicts with columns suitable for CSV output.
    """
    samples = load_classifier_dataset()
    eval_model = AzureGPT54Model()

    # Define GEval metric for classification correctness
    correctness_metric = GEval(
        name="Classification Correctness",
        criteria=(
            "Determine whether the actual email classification output matches "
            "the expected category. The output should be one of: forum, verify_code, "
            "promotions, social_media, spam, updates. Rate correctness from 0 to 10, "
            "where 10 means the actual output matches the expected category exactly "
            "(ignoring case/whitespace), and 0 means they do not match."
        ),
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        model=eval_model,
        threshold=0.5,
    )

    accuracy_metric = ClassificationAccuracyMetric(threshold=0.5)

    # Build test cases by running the classifier on each sample
    test_cases: List[LLMTestCase] = []
    raw_results: List[Dict[str, Any]] = []

    print(f"\n{'='*60}")
    print(f"  EMAIL CLASSIFIER EVALUATION ({len(samples)} samples)")
    print(f"{'='*60}\n")

    for i, sample in enumerate(samples, 1):
        print(f"  [{i}/{len(samples)}] Classifying: {sample.id}...", end=" ")
        result = _run_classifier(sample)
        predicted = result.get("category", "Unknown")
        reason = result.get("reason", "")
        print(f"→ {predicted}")

        input_text = f"Subject: {sample.subject}\nBody: {sample.body}"

        test_case = LLMTestCase(
            input=input_text,
            actual_output=predicted,
            expected_output=sample.expected_category,
        )
        test_cases.append(test_case)

        raw_results.append({
            "id": sample.id,
            "subject": sample.subject,
            "body": sample.body,
            "expected_category": sample.expected_category,
            "predicted_category": predicted,
            "classifier_reason": reason,
            "exact_match": predicted.strip().lower() == sample.expected_category.strip().lower(),
        })

    # Run deepeval evaluation
    print(f"\n  Running DeepEval metrics...")
    eval_results = evaluate(
        test_cases=test_cases,
        metrics=[correctness_metric, accuracy_metric],
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

    # Compute aggregate accuracy
    correct = sum(1 for r in raw_results if r["exact_match"])
    total = len(raw_results)
    accuracy = correct / total if total > 0 else 0.0

    print(f"\n  ┌─────────────────────────────────────┐")
    print(f"  │  CLASSIFIER RESULTS                  │")
    print(f"  │  Accuracy: {correct}/{total} = {accuracy:.2%}           │")
    print(f"  └─────────────────────────────────────┘\n")

    return raw_results
