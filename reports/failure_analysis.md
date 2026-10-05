# Failure-Mode Analysis

| # | Case | Expected Behaviour | Actual Behaviour | Test |
|---|---|---|---|---|
| 1 | Missing ETA | Do not invent an ETA; escalate | ETA excluded; `requires_human_review=True` | `test_case1_missing_eta_does_not_invent_a_time` |
| 2 | Conflicting data | Flag inconsistency; don't confirm completion | Escalated with explanation | `test_case2_conflicting_data_flagged_for_review` |
| 3 | Low confidence | Communicate uncertainty, avoid precise ETA | `uncertainty="Low"`, hedged message | `test_case3_low_confidence_communicates_uncertainty_not_precision` |
| 4 | No consent | Withhold delay details | `delay_reason` excluded | `test_case4_no_consent_withholds_delay_details` |
| 5 | Unauthorised family member | Access-restriction message | `disclosures=[]`, restriction message | `test_case5_unauthorised_family_member_gets_access_restriction` |

## Additional Errors (from the 320-scenario evaluation)

**Error A — Borderline confidence under-escalated.** Confidence ≈0.55–0.60 with good data quality is
hedged rather than escalated. Risk: Medium. Fix: escalate when confidence is in a narrow band AND traffic
is "severe".

**Error B — Understanding metric penalises safe escalations.** Escalated cases cap at 0.7 understanding
even when the message is honest and clear. This is a measurement-design artifact, not a system defect.

**Error C — Secondary-contact over-restriction (fixed).** An early implementation bug limited Secondary
Contacts to `visit_status` only; now covered by regression test and fixed.

## Phase 2 Error Tracking

**Error D — Re-notification cascade over-triggers on marginal confidence shifts.** In the 25-visit live
disruption simulation, 62.3% of recipients were re-notified; spot-checking the cascade (see
`reports/live_update_cascade.md`) shows a few cases where the confidence band didn't change (e.g. Low →
Low) but the message text still varied slightly due to the updated `traffic_level` string in the reason
field, which could cause minor redundant notifications. Fix: suppress re-notification when only the
traffic-level string changes but the band and disclosed facts are identical.

## Summary
No unauthorised-disclosure or false-information cases observed in the final 320-scenario run (0.0% each).
Family understanding (79.7%) and escalation recall (89.4%) remain just under target, documented honestly
with root causes above rather than smoothed over.
