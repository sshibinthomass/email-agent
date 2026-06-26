from pathlib import Path

PROMPTS_DIR = Path(__file__).parent


def load_prompt(filename: str) -> str:
    path = PROMPTS_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


EMAIL_CLASSIFIER_PROMPT = load_prompt("email_classifier.md")
EMAIL_JUDGE_PROMPT = load_prompt("email_judge.md")

__all__ = ["EMAIL_CLASSIFIER_PROMPT", "EMAIL_JUDGE_PROMPT"]
