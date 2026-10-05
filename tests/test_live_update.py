import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from app.rules.live_update import TrafficDisruptionEvent, apply_disruption, recompute_and_cascade

FULL_CONSENT = {"scheduling_updates": True, "delay_updates": True, "general_care_updates": True,
                 "medical_information": False, "location_information": False, "caregiver_information": False}


def test_disruption_lowers_confidence_and_marks_delayed():
    visit = {"visit_status": "scheduled", "estimated_arrival": "2026-09-10T09:00:00", "actual_arrival": None,
              "traffic_level": "light", "travel_confidence": 0.9, "exception_code": None, "data_quality": "good"}
    event = TrafficDisruptionEvent(visit_id="V1", new_traffic_level="severe", delay_minutes_added=30)
    updated = apply_disruption(visit, event)
    assert updated["travel_confidence"] < visit["travel_confidence"]
    assert updated["visit_status"] == "delayed"
    assert updated["traffic_level"] == "severe"


def test_cascade_only_renotifies_changed_recipients():
    visit = {"visit_status": "scheduled", "estimated_arrival": "2026-09-10T09:00:00", "actual_arrival": None,
              "traffic_level": "light", "travel_confidence": 0.95, "exception_code": None, "data_quality": "good"}
    recipients = [
        {"family_member_id": "F1", "family_role": "Primary Contact", "authorised": True, "consent": FULL_CONSENT},
        {"family_member_id": "F2", "family_role": "Unauthorised", "authorised": False, "consent": FULL_CONSENT},
    ]
    event = TrafficDisruptionEvent(visit_id="V1", new_traffic_level="severe", delay_minutes_added=40)
    result = recompute_and_cascade(visit, event, recipients)
    # Unauthorised recipient's message never changes (still restricted) -> not renotified
    unauth = [c for c in result["cascade"] if c["family_member_id"] == "F2"][0]
    assert unauth["renotify"] is False
    # Authorised recipient's message should change given the confidence drop
    auth = [c for c in result["cascade"] if c["family_member_id"] == "F1"][0]
    assert auth["renotify"] is True
