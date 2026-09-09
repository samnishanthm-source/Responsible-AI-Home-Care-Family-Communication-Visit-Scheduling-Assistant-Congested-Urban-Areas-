# Architecture

## Pipeline

```
Synthetic Data (CSV)
      ↓
Data Validation           (missing/conflicting field checks)
      ↓
Consent Verification      (per-patient consent.csv)
      ↓
Family Role Verification  (family_roles.csv: role + authorisation_level)
      ↓
Care Event / Visit Processing
      ↓
Uncertainty Estimation    (confidence_band: High/Moderate/Low/Unknown)
      ↓
Potential Harm Assessment (probability x impact per risk type)
      ↓
Information Filtering     (role + consent -> allowed/excluded fields)
      ↓
Communication Summary Generator (template composition, no invented facts)
      ↓
Explanation Layer         (human-readable audit trail)
      ↓
Risk Check / Fallback     (conflicting data, missing ETA, high risk -> escalate)
      ↓
Human Escalation (if required) OR Family Communication
```

## Modules

- `app/baseline.py` — deliberately simple rule-based baseline (no role/consent/uncertainty awareness).
- `app/rules/pipeline.py` — the full deterministic Responsible AI pipeline: uncertainty banding, harm
  scoring, consent+role field filtering, message composition, explanation generation, escalation logic,
  and question answering. Everything here is pure Python/deterministic — no opaque ML in the safety path.
- `scripts/generate_data.py` — synthetic data generator (patients, family roles, consent, caregivers,
  visits, care events, family questions).
- `scripts/run_experiment.py` — builds >=300 scenarios (visit x family-member pairs), scores baseline and
  prototype, writes `data/processed/experiment_results.csv` and `reports/evaluation_report.md`.
- `scripts/stakeholder_validation.py` — synthetic stakeholder rating pass, writes `reports/user_feedback.md`.
- `dashboard/streamlit_app.py` — the functional application: Dashboard, Family Communication, Coordinator
  Review, Consent Settings, and Evaluation Dashboard screens.
- `tests/` — pytest-style test suite (consent, roles, uncertainty, disclosure, fallback, question
  answering); runnable directly with Python if `pytest` is unavailable (see README).

## Why deterministic rules instead of an LLM in the safety path?

The spec explicitly requires that "the safety, consent, disclosure, uncertainty and escalation layers
must remain deterministic and auditable." An LLM may optionally be used for *surface-level* natural
language polishing of an already-approved, already-filtered message, but it must never decide *what*
information is disclosed, to whom, or under what confidence — that decision is made by the rule engine in
`app/rules/pipeline.py`, which can be unit-tested and audited line by line.

## Data Model

See `data/synthetic/*.csv` for the seven core tables (`patients`, `family_roles`, `consent`, `caregivers`,
`visits`, `care_events`, `family_questions`), matching the schemas in the master prompt.
