# Responsible AI Design

## Privacy & Consent
Every disclosure is checked against `consent.csv` per patient, per field. Caregiver identity is excluded
by default regardless of consent unless explicitly requested through an authorised channel.

## Role-Based Access
- **Primary Contact** — full role-appropriate info (filtered by consent).
- **Secondary Contact** — least-privilege subset even with full consent.
- **Unauthorised** — zero disclosures, explicit restriction message.
- **Care Coordinator** — full operational data, risk scores, explanations.
- **Caregiver** — scoped to own assigned visits (data model supports it; dedicated UI is future work).

## Transparency
Every message carries a parallel `explanation` list describing which rules fired.

## Uncertainty
Confidence always classified High/Moderate/Low/Unknown before reaching the composer. Low/Unknown
confidence never produces a precise ETA.

## Harm Awareness
`assess_harm()` scores multiple risks as `probability x impact`, classified Low–Critical; the dominant
risk drives escalation.

## Human Oversight
High-risk, conflicting, or low-quality/low-confidence cases are routed to Coordinator Review rather than
auto-communicated with specifics.

## Phase 2 Updates (in response to Review 1 feedback)

**1. Stakeholder validation methodology upgraded.** `scripts/stakeholder_validation.py` now produces a
semi-structured interview guide plus role-specific synthetic persona transcripts (Primary Contact,
Secondary Contact, Coordinator) in addition to the Phase-1 numeric rubric — see `reports/user_feedback.md`.
This is still synthetic (no live panel was available for this submission) but is now free-text and
directly comparable to real interview notes once a live 5-8 person panel is run. **Open action item from
the Coordinator persona:** surface the numeric risk score (not just Low/Medium/High) in the Coordinator
Review screen by default.

**2. Latency & concurrency now tracked.** `scripts/benchmark_latency.py` measures p50/p95/p99 latency
(sub-millisecond; see `reports/latency_benchmark.md`) and throughput at 1/8/32/64 concurrent workers. The
rule engine itself is not the bottleneck at scale — the report documents that DB I/O and notification
dispatch are the real constraints and recommends batched reads + an async notification queue for the
FastAPI service (`app/main.py`, added this phase).

**3. Dynamic traffic disruption cascade implemented.** `app/rules/live_update.py` models a live disruption
event revising a visit's `traffic_level`/`travel_confidence`, then re-runs the pipeline for every active
family recipient and flags only those whose outward message actually changed for re-notification (avoiding
alert fatigue). Measured on 25 simulated disruptions / 53 recipients: 62.3% required re-notification — see
`reports/live_update_cascade.md`.

## Security
Production deployment would require encrypted consent/role storage, authenticated per-role API tokens via
the new `app/main.py` FastAPI layer, audit logging of every disclosure decision, and DB-level RBAC as
defense-in-depth beyond the application-logic checks implemented here.

## Limitations
- All data is synthetic; no real patient data used.
- "Understanding" and stakeholder-persona scores are proxies, explicitly labelled as such.
- Escalation-recall (89.4%) and family-understanding (79.7%) are reported honestly at their measured,
  sub-target values with root-cause analysis in `reports/failure_analysis.md`.
- The latency benchmark measures the pure rule engine only, not the full deployed service under network
  load — a real load test against `app/main.py` + a database is the next step.
- The live-update cascade currently assumes a single disruption event per visit; batching multiple
  simultaneous disruptions across a zone is future work.

## Testing
21/21 tests passing across consent, roles, uncertainty, disclosure, fallback (5 required edge cases),
question answering, and the new live-update cascade (Phase 2).

## Deployment
`app/main.py` (FastAPI, added Phase 2) exposes `/communicate` and `/ask`; pair with SQLAlchemy models
against SQLite/Postgres and per-role authentication for a production deployment, with the Streamlit
dashboard (or a React frontend) as a thin client.
