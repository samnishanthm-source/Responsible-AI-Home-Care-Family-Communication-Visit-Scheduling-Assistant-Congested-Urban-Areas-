import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from app.rules.pipeline import generate_family_communication

FULL_CONSENT = {"scheduling_updates": True, "delay_updates": True, "general_care_updates": True,
                 "medical_information": False, "location_information": False, "caregiver_information": False}

def test_case1_missing_eta_does_not_invent_a_time():
    visit = {"visit_status": "delayed", "estimated_arrival": None, "actual_arrival": None,
              "traffic_level": "heavy", "travel_confidence": 0.7, "exception_code": "traffic_delay", "data_quality": "poor"}
    result = generate_family_communication(visit, "Primary Contact", FULL_CONSENT, True)
    assert "estimated_arrival" not in result.disclosures
    assert result.requires_human_review is True

def test_case2_conflicting_data_flagged_for_review():
    visit = {"visit_status": "completed", "estimated_arrival": "2026-09-10T09:00:00", "actual_arrival": None,
              "traffic_level": "light", "travel_confidence": 0.9, "exception_code": None, "data_quality": "good"}
    result = generate_family_communication(visit, "Primary Contact", FULL_CONSENT, True)
    assert result.requires_human_review is True
    assert "coordinator" in result.summary.lower()

def test_case3_low_confidence_communicates_uncertainty_not_precision():
    visit = {"visit_status": "delayed", "estimated_arrival": "2026-09-10T11:40:00", "actual_arrival": None,
              "traffic_level": "severe", "travel_confidence": 0.32, "exception_code": "traffic_delay", "data_quality": "good"}
    result = generate_family_communication(visit, "Primary Contact", FULL_CONSENT, True)
    assert result.uncertainty == "Low"

def test_case4_no_consent_withholds_delay_details():
    visit = {"visit_status": "delayed", "estimated_arrival": "2026-09-10T10:55:00", "actual_arrival": None,
              "traffic_level": "heavy", "travel_confidence": 0.8, "exception_code": "traffic_delay", "data_quality": "good"}
    no_consent = dict(FULL_CONSENT, delay_updates=False)
    result = generate_family_communication(visit, "Primary Contact", no_consent, True)
    assert "delay_reason" not in result.disclosures

def test_case5_unauthorised_family_member_gets_access_restriction():
    visit = {"visit_status": "delayed", "estimated_arrival": "2026-09-10T10:55:00", "actual_arrival": None,
              "traffic_level": "heavy", "travel_confidence": 0.8, "exception_code": "traffic_delay", "data_quality": "good"}
    result = generate_family_communication(visit, "Unauthorised", FULL_CONSENT, False)
    assert result.disclosures == []
    assert "not authorised" in result.summary.lower()
