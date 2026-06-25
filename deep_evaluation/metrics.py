"""
Custom deterministic metrics for DeepEval evaluation suite.

These complement the LLM-based GEval metrics with hard,
non-LLM accuracy / precision / recall / F1 scores.
"""

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class ClassificationAccuracyMetric(BaseMetric):
    """
    Deterministic exact-match metric for email classification.

    Compares the classifier's predicted category against the
    ground-truth expected_output. Score is 1.0 on match, 0.0 otherwise.
    """

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.score: float = 0.0
        self.reason: str = ""

    @property
    def __name__(self):
        return "Classification Accuracy"

    def measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:
        predicted = (test_case.actual_output or "").strip().lower()
        expected = (test_case.expected_output or "").strip().lower()

        if predicted == expected:
            self.score = 1.0
            self.reason = f"Correct: predicted '{predicted}' matches expected '{expected}'."
        else:
            self.score = 0.0
            self.reason = (
                f"Incorrect: predicted '{predicted}' but expected '{expected}'."
            )
        self.success = self.score >= self.threshold
        return self.score

    async def a_measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.score >= self.threshold


class JudgeDecisionAccuracyMetric(BaseMetric):
    """
    Deterministic metric for judge accept/reject decisions.

    Compares the judge's actual accept/reject decision against the
    ground-truth expected_output. Score is 1.0 on match, 0.0 otherwise.
    """

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.score: float = 0.0
        self.reason: str = ""

    @property
    def __name__(self):
        return "Judge Decision Accuracy"

    @staticmethod
    def _extract_decision(text: str) -> bool:
        """Extract accept/reject from text like 'Decision: accept. Reasoning: ...'"""
        lower = text.strip().lower()
        # Handle structured format: "Decision: accept. Reasoning: ..."
        if lower.startswith("decision:"):
            decision_part = lower.split(".")[0]  # "decision: accept"
            return "accept" in decision_part
        # Handle plain values
        return lower in ("accept", "true", "yes")

    def measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:
        actual = test_case.actual_output or ""
        expected = test_case.expected_output or ""

        actual_bool = self._extract_decision(actual)
        expected_bool = self._extract_decision(expected)

        if actual_bool == expected_bool:
            self.score = 1.0
            decision_str = "accept" if actual_bool else "reject"
            self.reason = f"Correct: judge decided '{decision_str}' matching expected."
        else:
            self.score = 0.0
            actual_str = "accept" if actual_bool else "reject"
            expected_str = "accept" if expected_bool else "reject"
            self.reason = (
                f"Incorrect: judge decided '{actual_str}' but expected '{expected_str}'."
            )
        self.success = self.score >= self.threshold
        return self.score

    async def a_measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.score >= self.threshold
