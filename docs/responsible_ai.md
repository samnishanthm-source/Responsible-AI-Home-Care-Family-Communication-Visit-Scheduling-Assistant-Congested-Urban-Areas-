# Responsible AI Design

## Privacy & Consent
Every disclosure is checked against `consent.csv` per patient, per field (`FIELD_CONSENT_MAP` in
`app/rules/pipeline.py`). No field is ever sent without an explicit "true" in the corresponding consent
column, and caregiver identity is excluded by default regardless of consent unless explicitly requested
through an authorised channel.

## Role-Based Access
- **Primary Contact** — full role-appropriate scheduling/delay information (still filtered by consent).
- **Secondary Contact** — a least-privilege subset (`visit_status`, `estimated_arrival`, `delay_reason`)
  even when consent would technically allow more.
- **Unauthorised** — receives zero disclosures and an explicit access-restriction message.
- **Care Coordinator** — sees full operational data, risk scores, and explanations via the Coordinator
  Review screen.
- **Caregiver** — scoped to their own assigned visits (not implemented as a full screen in this prototype
  demo, but the data model and role list support it — see Limitations).

## Transparency
Every generated message carries a parallel `explanation` list (see `CommunicationResult.explanation`)
describing exactly which rules fired: confidence classification, dominant risk, which fields were
allowed/excluded and why, and whether escalation was triggered. This is visible to coordinators via the
"Explanation" expander in the Family Communication screen.

## Uncertainty
Confidence is always classified into High / Moderate / Low / Unknown bands before it reaches the message
composer. Low/Unknown confidence *never* produces a precise ETA — the family is told the estimate is
uncertain, matching Section 12 of the spec.

## Harm Awareness
`assess_harm()` scores multiple candidate risks (incorrect ETA, unauthorised disclosure, incorrect status,
missing exception, overconfident recommendation) as `probability x impact`, classifies each into
Low/Medium/High/Critical, and the dominant (highest-scoring) risk drives the escalation decision.

## Human Oversight
High-risk, conflicting, or low-quality/low-confidence cases are never auto-communicated with specifics —
they are routed to the Coordinator Review queue with the full risk breakdown and a suggested action.

## Security
This prototype uses local CSV/SQLite-style flat files for a synthetic demo. A production deployment would
require: encrypted storage of consent and family-role records, authenticated API access (per-role tokens),
audit logging of every disclosure decision, and role-based access control at the database layer — the
consent/role checks implemented here would move from application logic to enforced database-level policies
as a defense-in-depth measure.

## Limitations
- All data is synthetic; no real patient data was used or is required for this prototype.
- The "understanding" and "stakeholder rating" scores are rubric-based proxies, not a real user study —
  labelled explicitly as synthetic throughout the reports.
- ETA/ traffic modelling uses simple randomised confidence bands rather than a real routing/traffic API.
- The Caregiver role and its screen are defined in the data model but not built out as a full UI in this
  prototype iteration.
- Escalation-recall and family-understanding metrics are reported honestly at their measured (sub-target)
  values along with root-cause analysis in `reports/failure_analysis.md`, rather than adjusted to hit targets.

## Testing
See `tests/` for consent, role, uncertainty, disclosure, fallback (5 required edge cases), and
question-answering tests — 19/19 passing at time of writing (see README for how to run them).

## Deployment
For a real deployment: wrap `app/rules/pipeline.py` behind a FastAPI service (`app/main.py` /
`app/api/`), replace CSV loading with SQLAlchemy models against SQLite/Postgres, add authentication per
role, and keep the Streamlit dashboard (or a React frontend) as a thin client calling the API.
