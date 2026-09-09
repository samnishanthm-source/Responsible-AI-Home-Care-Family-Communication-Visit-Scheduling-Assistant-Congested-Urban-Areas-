# Field-Workflow Map

```
Care Event
    ↓
Scheduling System
    ↓
Data Quality Check  ───────────────► (poor quality / missing fields flagged)
    ↓
Consent + Role Check ──────────────► (Unauthorised → hard stop, restriction message)
    ↓
AI Summary Engine (deterministic rules)
    ↓
Uncertainty Check ─────────────────► (Low confidence → hedge or withhold precise ETA)
    ↓
Harm/Risk Check ───────────────────► (conflicting data / high risk → force escalation)
    ↓
 ┌───────────────┐
 │ Safe to Send? │
 └───────┬───────┘
       YES│       │NO
          ↓       ↓
      Family    Coordinator
      Message     Review Queue
          ↓       ↓
       Feedback  Human Decision
      (question    (Approve / Reject /
       answering)   Edit / Escalate)
```

## Human escalation points

1. **Conflicting data** (e.g. `visit_status = completed` but `actual_arrival` missing).
2. **Missing ETA** for a visit that is not yet completed.
3. **Dominant potential-harm risk level is High or Critical.**
4. **Poor data quality combined with low/unknown confidence.**

In all four cases, the family receives an honest "please contact the coordinator" message rather than a
guess, and the coordinator sees the full explanation, risk breakdown, and suggested action in the
Coordinator Review screen.
