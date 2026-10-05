# Responsible AI Home-Care Family Communication & Visit Scheduling System

An end-to-end **synthetic-data** prototype converting raw home-care scheduling/visit data into
role-appropriate, consent-aware, uncertainty-aware family communication — with explanation, potential-harm
detection, fallback/escalation, a FastAPI service, and a measured baseline-vs-prototype evaluation.

⚠️ No real patient data is used anywhere. All data comes from `scripts/generate_data.py`.

## Quick Start
```bash
pip install -r requirements.txt

python scripts/generate_data.py          # 1. synthetic data
python scripts/run_experiment.py         # 2. baseline vs prototype (320 scenarios)
python scripts/stakeholder_validation.py # 3. semi-structured stakeholder validation
python scripts/benchmark_latency.py      # 4. latency/concurrency benchmark (Phase 2)
python scripts/demo_live_update.py       # 5. live traffic-disruption cascade (Phase 2)

streamlit run dashboard/streamlit_app.py # 6. launch the application
uvicorn app.main:app --reload            # 7. (optional) launch the API
```

## Running Tests
```bash
pytest tests/ -v
```

## Project Layout
```
homecare-responsible-ai/
├── app/
│   ├── baseline.py
│   ├── main.py                 # FastAPI service (Phase 2)
│   └── rules/
│       ├── pipeline.py         # core Responsible AI engine
│       └── live_update.py      # live traffic cascade (Phase 2)
├── dashboard/streamlit_app.py
├── data/synthetic/ data/processed/
├── scripts/
├── reports/
├── docs/
├── tests/
└── requirements.txt
```

## What's New in Phase 2 (addressing Review 1 feedback)
1. **Semi-structured stakeholder validation** — interview guide + role-specific synthetic persona
   transcripts, alongside the Phase-1 quantitative rubric (`reports/user_feedback.md`).
2. **Latency & concurrency benchmark** — p50/p95/p99 latency and throughput at 1/8/32/64 concurrent
   workers (`reports/latency_benchmark.md`).
3. **Dynamic traffic disruption → notification cascade** — live confidence recompute and selective
   re-notification, measured on 25 simulated disruptions (`reports/live_update_cascade.md`).
4. **FastAPI service layer** (`app/main.py`) exposing the pipeline as `/communicate` and `/ask`.
5. **21/21 tests passing**, including 2 new tests for the live-update cascade.

See `docs/responsible_ai.md` for the full design writeup and limitations.
