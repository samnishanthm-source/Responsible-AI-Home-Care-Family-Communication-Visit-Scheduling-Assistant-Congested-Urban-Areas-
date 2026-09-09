import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from app.rules.pipeline import generate_family_communication

BASE_VISIT = {
    "visit_status": "delayed",
    "estimated_arrival": "2026-09-10T10:55:00",
    "actual_arrival": None,
    "traffic_level": "heavy",
    "travel_confidence": 0.75,
    "exception_code": "traffic_delay",
    "data_quality": "good",
}


def test_no_consent_blocks_delay_details():
    consent = {
        "scheduling_updates": True,
        "delay_updates": False,   # NO CONSENT for delay info
        "general_care_updates": True,
        "medical_information": False,
        "location_information": False,
        "caregiver_information": False,
    }
    result = generate_family_communication(BASE_VISIT, "Primary Contact", consent, authorised=True)
    assert "delay_reason" not in result.disclosures
    assert "Reason:" not in result.summary


def test_full_consent_allows_delay_details():
    consent = {
        "scheduling_updates": True,
        "delay_updates": True,
        "general_care_updates": True,
        "medical_information": False,
        "location_information": False,
        "caregiver_information": False,
    }
    result = generate_family_communication(BASE_VISIT, "Primary Contact", consent, authorised=True)
    assert "delay_reason" in result.disclosures


def test_caregiver_identity_never_auto_disclosed():
    consent = {
        "scheduling_updates": True, "delay_updates": True, "general_care_updates": True,
        "medical_information": False, "location_information": False, "caregiver_information": True,
    }
    result = generate_family_communication(BASE_VISIT, "Primary Contact", consent, authorised=True)
    assert "caregiver_identifier" in result.excluded_information
