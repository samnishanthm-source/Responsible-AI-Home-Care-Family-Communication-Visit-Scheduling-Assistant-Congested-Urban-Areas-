# User / Stakeholder Validation — Phase 2 (Semi-Structured)

**Method (Phase 2 upgrade):** In addition to the Phase-1 quantitative rubric (40 scenarios, 1-5 scale, six dimensions), this phase adds a semi-structured interview guide with open-ended questions, and role-specific synthetic persona transcripts illustrating the *kind* of qualitative feedback a real panel would surface. **These transcripts are still synthetic** — a live panel of care coordinators and family members was not available for this submission — but are now free-text and role-specific rather than a single opaque score, so they can be directly compared against real interview notes once a live panel is run (tracked as Phase 3 follow-up).

## Interview Guide (to be used in the real panel)

1. Walk me through what you understood from this message — what would you do next?
2. Was anything in this message confusing, alarming, or ambiguous?
3. Did the message give you enough information, too much, or too little?
4. How much would you trust this message if it came from the real app?
5. If this said 'contact the coordinator', would you actually do that, or ignore it?

## Synthetic Persona Transcripts (by role)

### Primary Contact
- **Baseline:** "Just says 'delayed, ETA: 10:55' — I don't know why, and I don't know if I should worry. Feels like I'm getting a system log, not a message meant for me."
- **Prototype:** "This one explains it's traffic and says the time might shift — that matches how I'd actually think about it. I'd still want a push notification if it changes a lot though."

### Secondary Contact
- **Baseline:** "Same raw message as a primary contact — I don't think I should be seeing caregiver-level operational detail for someone I'm not the main contact for."
- **Prototype:** "I get the basics (status + rough time) without the full detail — feels appropriately limited, though I'd like a one-line 'contact [primary contact] for more'."

### Coordinator
- **Baseline:** "No way to tell which cases are risky from this output alone — I'd have to cross-check everything manually, every time."
- **Prototype:** "The explanation + risk level + dominant harm type lets me triage the review queue fast. I'd want the risk score itself (not just High/Medium/Low) shown by default too."

## Quantitative Rubric (Phase 1, retained for comparability)

| system    |   clarity |   usefulness |   trust |   amount_of_information |   understanding |   confidence |
|:----------|----------:|-------------:|--------:|------------------------:|----------------:|-------------:|
| Baseline  |      3    |            3 |       2 |                       3 |               3 |         3    |
| Prototype |      3.92 |            4 |       4 |                       3 |               4 |         3.78 |

## Interpretation
- Across all three personas, the qualitative theme is consistent with the quantitative rubric: the prototype is seen as more trustworthy and appropriately scoped, while the baseline reads as an undifferentiated system log.
- The Coordinator persona's request to see the numeric risk score (not just Low/Medium/High) is a concrete, actionable piece of feedback — logged as a follow-up item in `docs/responsible_ai.md`.
- **Follow-up required:** replace these synthetic transcripts with a real 5-8 person semi-structured interview panel (2-3 care coordinators, 3-5 family members) before any production rollout decision.