"""
Data loader module for DeepEval evaluation suite.

Loads and prepares test data from test_gepa.csv for classifier
and judge evaluations.
"""

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List

from deep_evaluation.config import TEST_GEPA_CSV


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------
@dataclass
class ClassifierSample:
    """A single test sample for classifier evaluation."""
    id: str
    subject: str
    body: str
    expected_category: str


@dataclass
class JudgeSample:
    """A single test sample for judge evaluation."""
    id: str
    subject: str
    body: str
    proposed_category: str
    expected_accepted: bool
    expected_reason: str


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------
def _load_gepa_csv(csv_path: Path) -> List[dict]:
    """Read test_gepa.csv and return list of row dicts."""
    rows: List[dict] = []
    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def load_classifier_dataset(csv_path: Path = TEST_GEPA_CSV) -> List[ClassifierSample]:
    """
    Load classifier evaluation data.

    Uses test_gepa.csv rows where accepted == true (30 samples).
    These are cases where the ground-truth category IS correct,
    so the classifier should reproduce that category.
    """
    rows = _load_gepa_csv(csv_path)
    samples: List[ClassifierSample] = []

    for row in rows:
        if row.get("accepted", "").strip().lower() != "true":
            continue
        samples.append(
            ClassifierSample(
                id=row["id"],
                subject=row["subject"],
                body=row["body"],
                expected_category=row["category"],
            )
        )

    return samples


def load_judge_dataset(csv_path: Path = TEST_GEPA_CSV) -> List[JudgeSample]:
    """
    Load judge evaluation data.

    Uses all 60 rows from test_gepa.csv (30 accepted + 30 rejected).
    The judge must decide whether the proposed category is correct.
    """
    rows = _load_gepa_csv(csv_path)
    samples: List[JudgeSample] = []

    for row in rows:
        accepted_str = row.get("accepted", "").strip().lower()
        samples.append(
            JudgeSample(
                id=row["id"],
                subject=row["subject"],
                body=row["body"],
                proposed_category=row["category"],
                expected_accepted=(accepted_str == "true"),
                expected_reason=row.get("reason", ""),
            )
        )

    return samples
