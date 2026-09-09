# User / Stakeholder Validation (Synthetic)

**Method:** 40 scenarios were sampled from the experiment results and scored on a 1-5 scale
across six dimensions, using a deterministic rubric that stands in for human raters for this prototype
stage. This is a **synthetic validation**, explicitly not a substitute for a real caregiver/family study,
which is recommended before production rollout (see Limitations in `docs/responsible_ai.md`).

## Average Ratings (1-5 scale)

| system    |   clarity |   usefulness |   trust |   amount_of_information |   understanding |   confidence |
|:----------|----------:|-------------:|--------:|------------------------:|----------------:|-------------:|
| Baseline  |      3    |            3 |       2 |                       3 |               3 |         3    |
| Prototype |      3.92 |            4 |       4 |                       3 |               4 |         3.78 |

## Interpretation

- **Trust** shows the largest gap: the prototype's explicit uncertainty language and access-restriction
  messaging (vs the baseline's flat, occasionally misleading statements) is rated more trustworthy.
- **Amount of information** is deliberately similar between systems in this rubric — the point of the
  Responsible AI layer is not to give *more* raw data, but the *right* data for the recipient's role and
  consent, which "amount of information" alone doesn't capture. Qualitative review of the underlying
  messages in `data/processed/experiment_results.csv` should be read alongside this score.
- **Confidence** is intentionally capped for escalated prototype cases, since a coordinator-review message
  is honest about not having a firm answer yet — this is a feature, not a shortcoming.
