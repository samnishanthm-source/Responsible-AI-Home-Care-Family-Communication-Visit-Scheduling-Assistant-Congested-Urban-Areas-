import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from app.rules.pipeline import generate_family_communication

FULL_CONSENT = {"scheduling_updates": True, "delay_updates": True, "general_care_updates": True,
                "medical_information": True, "location_information": True, "caregiver_information": True}
VISIT = {"visit_status": "delayed", "estimated_arrival": "2026-09-10T10:55:00", "actual_arrival": None,
         "traffic_level": "heavy", "travel_confidence": 0.75, "exception_code": "traffic_delay", "data_quality": "good"}

def test_unauthorised_person_receives_nothing():
    result = generate_family_communication(VISIT, "Unauthorised", FULL_CONSENT, False)
    assert result.disclosures == []
    assert "not authorised" in result.summary.lower()

def test_secondary_contact_gets_limited_fields_even_with_full_consent():
    result = generate_family_communication(VISIT, "Secondary Contact", FULL_CONSENT, True)
    assert "medical_detail" not in result.disclosures
    assert set(result.disclosures).issubset({"visit_status", "estimated_arrival", "delay_reason"})

def test_primary_contact_gets_more_detail_than_secondary():
    primary = generate_family_communication(VISIT, "Primary Contact", FULL_CONSENT, True)
    secondary = generate_family_communication(VISIT, "Secondary Contact", FULL_CONSENT, True)
    assert len(primary.disclosures) >= len(secondary.disclosures)
