import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from app.rules.pipeline import generate_family_communication, confidence_band

CONSENT = {"scheduling_updates": True, "delay_updates": True, "general_care_updates": True,
           "medical_information": False, "location_information": False, "caregiver_information": False}

def test_confidence_bands():
    assert confidence_band(0.95) == "High"
    assert confidence_band(0.70) == "Moderate"
    assert confidence_band(0.30) == "Low"
    assert confidence_band(None) == "Unknown"

def test_low_confidence_never_states_precise_eta_as_fact():
    visit = {"visit_status": "delayed", "estimated_arrival": "2026-09-10T11:20:00", "actual_arrival": None,
              "traffic_level": "severe", "travel_confidence": 0.32, "exception_code": "traffic_delay", "data_quality": "good"}
    result = generate_family_communication(visit, "Primary Contact", CONSENT, True)
    assert "uncertain" in result.summary.lower() or result.uncertainty == "Low"

def test_high_confidence_states_eta_directly():
    visit = {"visit_status": "scheduled", "estimated_arrival": "2026-09-10T09:00:00", "actual_arrival": None,
              "traffic_level": "light", "travel_confidence": 0.93, "exception_code": None, "data_quality": "good"}
    result = generate_family_communication(visit, "Primary Contact", CONSENT, True)
    assert result.uncertainty == "High"
    assert "may change" not in result.summary.lower()
