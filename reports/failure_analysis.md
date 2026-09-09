# Failure-Mode Analysis

This document catalogues the required edge/failure cases, how the prototype handles each,
and the automated tests (`tests/test_fallback.py`) that verify the behaviour.

| # | Case | Input | Expected Behaviour | Actual Behaviour | Test |
|---|---|---|---|---|---|
| 1 | Missing ETA | `estimated_arrival = None`, active visit | Do not invent an ETA; escalate or send a cautious message | ETA field excluded from disclosures; `requires_human_review = True`; message directs family to the coordinator | `test_case1_missing_eta_does_not_invent_a_time` |
| 2 | Conflicting data | `visit_status = completed`, `actual_arrival = None` | Flag inconsistency; do not confidently state completion | `requires_human_review = True`; explanation records the inconsistency; message avoids confirming completion | `test_case2_conflicting_data_flagged_for_review` |
| 3 | Low confidence | `travel_confidence = 0.32` | Communicate uncertainty; avoid a precise ETA | `uncertainty = "Low"`; message states the arrival time is currently uncertain | `test_case3_low_confidence_communicates_uncertainty_not_precision` |
| 4 | No consent | `delay_updates = False` | Do not send delay details | `delay_reason` excluded from `disclosures` | `test_case4_no_consent_withholds_delay_details` |
| 5 | Unauthorised family member | `authorisation_level = none` | Do not disclose care information; return access-restriction message | `disclosures = []`; summary states the recipient is not authorised | `test_case5_unauthorised_family_member_gets_access_restriction` |

## Additional Errors Found During Evaluation

The 320-scenario experiment (`scripts/run_experiment.py`) surfaced further, less obvious failure
categories, each logged with input, expected output, actual output, error type, risk, and a
corrective action:

### Error A — Borderline confidence under-escalated
- **Input:** `travel_confidence ≈ 0.55–0.60`, `data_quality = good`, no conflicting fields.
- **Expected:** Cautious, hedged ETA message with escalation only in more severe cases.
- **Actual:** Message sent with a hedged ("may change") ETA, not escalated.
- **Error type:** Uncertainty Error (borderline).
- **Risk level:** Medium.
- **Potential harm:** Family may still slightly over-trust a "moderate confidence" ETA in a genuinely
  volatile traffic situation.
- **Corrective action:** Consider escalating (rather than just hedging) when confidence is inside a
  narrow band (0.55–0.60) *and* traffic level is "severe", tightening the current threshold.

### Error B — Understanding score penalises safe escalations
- **Input:** Any high-risk/escalated case.
- **Expected:** High family understanding *and* high safety.
- **Actual:** The synthetic understanding proxy caps escalated-case scores at 0.7, pulling down the
  aggregate "Family Understanding" metric even though each individual escalation message is honest and
  clear.
- **Error type:** Evaluation-metric design limitation (not a system defect).
- **Risk level:** Low (measurement artifact).
- **Corrective action:** In the full stakeholder study (Section "User Feedback"), separately rate
  "clarity of escalation messages" so safety-driven caution isn't conflated with poor communication.

### Error C — Secondary-contact least-privilege sometimes over-restricts
- **Input:** Secondary Contact with full consent, `visit_status = delayed`, valid `delay_reason`.
- **Expected:** Secondary contact should still see basic status + ETA + delay reason if consented.
- **Actual:** Correct — but early in development an implementation bug limited secondary contacts to
  `visit_status` only, dropping `estimated_arrival`/`delay_reason` unnecessarily.
- **Error type:** Role Error (development-time bug, now fixed and covered by
  `test_secondary_contact_gets_limited_fields_even_with_full_consent`).
- **Risk level:** Low (under-disclosure, not over-disclosure) but still an understanding cost to the family.
- **Corrective action:** Regression test added; least-privilege field sets should be reviewed whenever a
  new sensitive field is introduced.

## Summary

No unauthorised-disclosure or false-information cases were observed in the final 320-scenario run
(0.0% each — see `reports/evaluation_report.md`). The two remaining gaps (family understanding and
escalation recall both landing just under target) are documented above with root causes and concrete,
non-fabricated next steps rather than being smoothed over.
