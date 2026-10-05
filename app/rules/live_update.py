"""
live_update.py — Phase 2 addition.

Addresses reviewer feedback: "Further articulate how dynamic urban traffic
disruptions (e.g., sudden transit delays) update live visit confidence scores
and cascade down to family notification batches."

Model: each visit carries a traffic_level and travel_confidence. A live
traffic disruption event (e.g. a sudden jam reported mid-route) revises both,
and `recompute_and_cascade()` re-runs the full Responsible AI pipeline for
every active family recipient of that visit, re-triggering escalation if the
new state crosses a risk threshold it previously didn't. Only recipients
whose *outward message actually changes* are re-notified, to avoid alert
fatigue.
"""
from dataclasses import dataclass
from typing import Dict, List, Any
from .pipeline import generate_family_communication, confidence_band

TRAFFIC_CONFIDENCE_PRIORS = {
    "light": (0.85, 0.98),
    "moderate": (0.65, 0.85),
    "heavy": (0.45, 0.70),
    "severe": (0.20, 0.50),
}


@dataclass
class TrafficDisruptionEvent:
    visit_id: str
    new_traffic_level: str
    delay_minutes_added: int
    source: str = "live_traffic_feed"


def apply_disruption(visit: Dict[str, Any], event: TrafficDisruptionEvent) -> Dict[str, Any]:
    """Revises a visit's traffic_level and travel_confidence in response to a live
    disruption event. Confidence is pulled toward the low end of the new traffic
    band's prior range, reflecting the fresh uncertainty of an unplanned event."""
    updated = dict(visit)
    lo, hi = TRAFFIC_CONFIDENCE_PRIORS.get(event.new_traffic_level, (0.5, 0.7))
    # A *new* disruption is treated as less certain than a steady-state reading of
    # the same traffic level, so we bias toward the lower bound of the prior.
    updated["travel_confidence"] = round(lo + 0.25 * (hi - lo), 2)
    updated["traffic_level"] = event.new_traffic_level
    if updated.get("visit_status") in ("scheduled", "in_progress"):
        updated["visit_status"] = "delayed"
    updated["exception_code"] = updated.get("exception_code") or "traffic_delay"
    return updated


def recompute_and_cascade(visit: Dict[str, Any], event: TrafficDisruptionEvent,
                           recipients: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    recipients: list of {"family_role": str, "consent": dict, "authorised": bool, "family_member_id": str}
    Returns before/after communication per recipient, and which ones require re-notification.
    """
    before_band = confidence_band(visit.get("travel_confidence"))
    updated_visit = apply_disruption(visit, event)
    after_band = confidence_band(updated_visit.get("travel_confidence"))

    cascade = []
    for r in recipients:
        before = generate_family_communication(visit, r["family_role"], r["consent"], r["authorised"])
        after = generate_family_communication(updated_visit, r["family_role"], r["consent"], r["authorised"])
        message_changed = (before.summary != after.summary) or (before.requires_human_review != after.requires_human_review)
        cascade.append({
            "family_member_id": r["family_member_id"],
            "before_summary": before.summary,
            "after_summary": after.summary,
            "before_requires_review": before.requires_human_review,
            "after_requires_review": after.requires_human_review,
            "renotify": message_changed,
        })

    return {
        "visit_id": event.visit_id,
        "confidence_band_before": before_band,
        "confidence_band_after": after_band,
        "updated_visit": updated_visit,
        "recipients_renotified": sum(1 for c in cascade if c["renotify"]),
        "recipients_total": len(cascade),
        "cascade": cascade,
    }
