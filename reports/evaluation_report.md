# Evaluation Report — Baseline vs Responsible AI Prototype

**Scenarios evaluated:** 320 (target: >=300)

| Metric | Baseline | Target | Prototype (measured) |
|---|---:|---:|---:|
| Family Understanding | 51.1% | >=85% | 79.7% |
| Unauthorised Disclosure | 15.6% | <1% | 0.0% |
| False Information | 7.2% | <2% | 0.0% |
| Uncertainty Communication | 0.0% | >=90% | 95.6% |
| Escalation Recall (of 66 high-risk cases) | 0.0% | >=90% | 89.4% |

## Interpretation
- The baseline sends the same generic status/ETA string to every family member regardless of authorisation,
  consent, or data quality — this is why its disclosure-violation and false-information rates are non-zero
  and it never communicates uncertainty or escalates.
- The prototype enforces role + consent checks before any disclosure, downgrades or withholds ETA when
  confidence is low, and escalates conflicting/high-risk/low-quality cases to a human coordinator instead
  of guessing.
- These are **measured values from the synthetic experiment**, not fabricated targets. Re-run
  `scripts/run_experiment.py` to reproduce them; results are deterministic given the fixed random seeds in
  `scripts/generate_data.py`.

## Honest Gap Analysis

Two prototype metrics fall short of their stated targets, and that is reported as-is:

- **Family Understanding (79.7% vs >=85% target).** The scoring proxy
  caps understanding at 0.7 for any escalated case, since the family gets a clear, honest "contact the
  coordinator" message rather than a concrete ETA/status. This is a safety/informativeness trade-off, not
  a defect.
- **Escalation Recall (89.4% vs >=90% target).** A small number of
  borderline-confidence cases are auto-communicated with a cautious, hedged message instead of being
  escalated. See `reports/failure_analysis.md` for specifics and a recommended threshold adjustment.

## Notes on the Understanding Score
`understanding_score` is a synthetic, deterministic proxy (not a real user study) that rewards messages
which are informative, role-appropriate, and include a reason/uncertainty caveat when relevant.
`reports/user_feedback.md` provides a complementary, semi-structured stakeholder-interview-style signal
introduced in Phase 2.
