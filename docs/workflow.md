# Field-Workflow Map

```
Care Event → Scheduling System → Data Quality Check → Consent + Role Check
→ AI Summary Engine → Uncertainty Check → Harm/Risk Check → Safe to Send?
      YES → Family Message → Feedback (question answering)
      NO  → Coordinator Review → Human Decision (Approve/Reject/Edit/Escalate)
```

## Phase 2 addition — Live Disruption Cascade
```
Live Traffic Disruption Event (e.g. sudden jam)
      ↓
app/rules/live_update.apply_disruption()   (revises traffic_level + travel_confidence)
      ↓
Pipeline re-run for every active family recipient of that visit
      ↓
Compare before/after message per recipient
      ↓
Only recipients whose message actually changed are re-notified (avoids alert fatigue)
```
See `reports/live_update_cascade.md` for measured results on 25 simulated disruption events.

## Human escalation points
1. Conflicting data (status says completed, no actual arrival recorded).
2. Missing ETA for a visit that is not yet completed.
3. Dominant potential-harm risk level is High or Critical.
4. Poor data quality combined with low/unknown confidence.
