# Email Agent DeepEval Suite

This package provides a modular evaluation framework using **DeepEval** and **Azure OpenAI (gpt-5.4)** to test, score, and track the performance of both the **Email Classifier** and the **LLM-as-a-Judge**.

---

## 🚀 How to Run

Evaluations can be run using the standard Python module executor. Make sure you are in the project root directory and your environment variables in `.env` are set correctly.

### Run All Evaluations (Default)
Runs both the classifier and the judge evaluations:
```bash
uv run python -m deep_evaluation.run_evaluation --target all
```

### Run Classifier Only
Evaluates only the classification accuracy against ground truth:
```bash
uv run python -m deep_evaluation.run_evaluation --target classifier
```

### Run Judge Only
Evaluates only the judge decisions and reasoning quality:
```bash
uv run python -m deep_evaluation.run_evaluation --target judge
```

---

## 📂 Output Structure

All evaluation runs save detailed metrics and per-sample results into a timestamped subdirectory under `deep_evaluation/outputs/`:

```
deep_evaluation/outputs/<YYYY-MM-DD_HH-MM-SS>/
├── classifier.csv   # Per-sample classifier inputs, predictions, and correctness
├── judge.csv        # Per-sample judge decisions, reasoning, and correctness
└── overall.csv      # Unified high-level metrics for overall performance and accuracy
```

---

## 📊 What the Results Mean

### 1. `classifier.csv`
Contains the evaluation of the classification node using the 30 samples from `test_gepa.csv` where `accepted == true`.
* **exact_match**: Evaluates whether the predicted category string matches the expected category exactly (Case-insensitive).
* **metric_Classification Correctness [GEval]**: An LLM-assessed correctness score from DeepEval (normalized 0.0 - 1.0).

### 2. `judge.csv`
Contains the evaluation of the judge node using all 60 samples from `test_gepa.csv` (30 correct classifications to accept, 30 incorrect to reject).
* **expected_accepted / predicted_accepted**: Boolean indicators of whether the sample should be accepted vs. whether the LLM judge actually accepted it.
* **decision_correct**: Direct comparison of expected and predicted acceptance.
* **metric_Judge Decision Correctness [GEval]**: An LLM-assessed match score of the judge's decision against ground-truth.
* **metric_Judge Reasoning Quality [GEval]**: An LLM-evaluated score measuring the coherence and logical alignment of the judge's written explanation.

### 3. `overall.csv`
Contains the aggregate metrics for the run:
* **exact_match_accuracy**: Percentage of correct categories predicted by the classifier (Goal: >90%).
* **decision_accuracy**: Overall percentage of correct decision calls made by the judge.
* **precision**: True Positive Rate / (True Positives + False Positives) for the judge. Shows how often the judge was correct when deciding to *accept* a classification.
* **recall**: True Positive Rate / (True Positives + False Negatives) for the judge. Shows what portion of the correct classifications the judge managed to detect and *accept*.
* **f1_score**: The harmonic mean of precision and recall.
* **average_accuracy**: The average score between classification accuracy and judge decision accuracy.
