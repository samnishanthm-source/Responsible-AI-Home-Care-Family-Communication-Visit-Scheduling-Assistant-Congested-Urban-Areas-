# Architecture

## Pipeline
```
Synthetic Data (CSV) → Data Validation → Consent Verification → Family Role Verification
→ Care Event/Visit Processing → Uncertainty Estimation → Potential Harm Assessment
→ Information Filtering → Communication Summary Generator → Explanation Layer
→ Risk Check/Fallback → Human Escalation (if required) OR Family Communication
```

## Modules
- `app/baseline.py` — deliberately simple rule-based baseline.
- `app/rules/pipeline.py` — the full deterministic Responsible AI pipeline.
- `app/rules/live_update.py` **(Phase 2)** — live traffic disruption → confidence recompute → notification cascade.
- `app/main.py` **(Phase 2)** — FastAPI service boundary wrapping the pipeline (`/communicate`, `/ask`, `/health`).
- `scripts/generate_data.py` — synthetic data generator.
- `scripts/run_experiment.py` — baseline vs prototype experiment (320 scenarios).
- `scripts/stakeholder_validation.py` — rubric + semi-structured persona validation.
- `scripts/demo_live_update.py` **(Phase 2)** — demonstrates the traffic-disruption cascade on live data.
- `scripts/benchmark_latency.py` **(Phase 2)** — latency/concurrency benchmark.
- `dashboard/streamlit_app.py` — functional application (5 screens).
- `tests/` — 21 automated tests.

## Why deterministic rules instead of an LLM in the safety path?
The consent/disclosure/uncertainty/escalation decisions must remain deterministic and auditable. An LLM
may optionally polish an already-approved, already-filtered message, but never decides what is disclosed.

## Data Model
See `data/synthetic/*.csv` for the seven core tables matching the master-prompt schemas.
