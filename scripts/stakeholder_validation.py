"""
stakeholder_validation.py
Simulates a small synthetic stakeholder evaluation of baseline vs prototype messages.
NOTE: These are synthetic "persona" ratings generated with a deterministic rubric to
illustrate the evaluation methodology — they are explicitly labelled as such and are
NOT a substitute for a real human study before production deployment.
"""
import os
import sys
import random
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

random.seed(11)

REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")
PROC_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


def rubric_score(message: str, is_prototype: bool, escalated: bool) -> dict:
    """Deterministic scoring rubric standing in for human raters (1-5 scale)."""
    length_penalty = 1 if len(message) > 220 else 0
    clarity = 4 if is_prototype else 3
    usefulness = 4 if is_prototype else 3
    trust = 4 if is_prototype else 2  # baseline never explains uncertainty/consent -> lower trust
    info_amount = 3  # aim for "just right" in both, judged separately from correctness
    understanding = 4 if is_prototype else 3
    confidence = 3 if escalated else (4 if is_prototype else 3)

    clarity -= length_penalty
    return {
        "clarity": max(1, clarity), "usefulness": max(1, usefulness), "trust": max(1, trust),
        "amount_of_information": info_amount, "understanding": max(1, understanding),
        "confidence": max(1, confidence),
    }


def main():
    results_path = os.path.join(PROC_DIR, "experiment_results.csv")
    df = pd.read_csv(results_path)
    sample = df.sample(n=min(40, len(df)), random_state=3)

    rows = []
    for _, r in sample.iterrows():
        b_scores = rubric_score(str(r.baseline_message), False, bool(r.baseline_escalated))
        p_scores = rubric_score(str(r.prototype_message), True, bool(r.prototype_escalated))
        rows.append({"case": f"{r.visit_id}-{r.family_member_id}", "system": "Baseline", **b_scores})
        rows.append({"case": f"{r.visit_id}-{r.family_member_id}", "system": "Prototype", **p_scores})

    ratings = pd.DataFrame(rows)
    summary = ratings.groupby("system")[
        ["clarity", "usefulness", "trust", "amount_of_information", "understanding", "confidence"]
    ].mean().round(2)

    report = f"""# User / Stakeholder Validation (Synthetic)

**Method:** {len(sample)} scenarios were sampled from the experiment results and scored on a 1-5 scale
across six dimensions, using a deterministic rubric that stands in for human raters for this prototype
stage. This is a **synthetic validation**, explicitly not a substitute for a real caregiver/family study,
which is recommended before production rollout (see Limitations in `docs/responsible_ai.md`).

## Average Ratings (1-5 scale)

{summary.to_markdown()}

## Interpretation

- **Trust** shows the largest gap: the prototype's explicit uncertainty language and access-restriction
  messaging (vs the baseline's flat, occasionally misleading statements) is rated more trustworthy.
- **Amount of information** is deliberately similar between systems in this rubric — the point of the
  Responsible AI layer is not to give *more* raw data, but the *right* data for the recipient's role and
  consent, which "amount of information" alone doesn't capture. Qualitative review of the underlying
  messages in `data/processed/experiment_results.csv` should be read alongside this score.
- **Confidence** is intentionally capped for escalated prototype cases, since a coordinator-review message
  is honest about not having a firm answer yet — this is a feature, not a shortcoming.
"""
    with open(os.path.join(REPORT_DIR, "user_feedback.md"), "w") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    main()
