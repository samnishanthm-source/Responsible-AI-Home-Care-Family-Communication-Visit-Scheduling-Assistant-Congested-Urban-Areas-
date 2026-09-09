import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from app.rules.pipeline import generate_family_communication, answer_family_question

FULL_CONSENT = {
    "scheduling_updates": True, "delay_updates": True, "general_care_updates": True,
    "medical_information": False, "location_information": False, "caregiver_information": False,
}


def test_eta_question_never_fabricated_when_missing():
    visit = {
        "visit_status": "delayed", "estimated_arrival": None, "actual_arrival": None,
        "traffic_level": "heavy", "travel_confidence": 0.7, "exception_code": "traffic_delay",
        "data_quality": "poor",
    }
    result = generate_family_communication(visit, "Primary Contact", FULL_CONSENT, authorised=True)
    answer = answer_family_question("eta", result)
    assert "coordinator" in answer.lower()


def test_caregiver_info_question_not_disclosed():
    visit = {
        "visit_status": "delayed", "estimated_arrival": "2026-09-10T10:55:00", "actual_arrival": None,
        "traffic_level": "heavy", "travel_confidence": 0.8, "exception_code": "traffic_delay",
        "data_quality": "good",
    }
    result = generate_family_communication(visit, "Primary Contact", FULL_CONSENT, authorised=True)
    answer = answer_family_question("caregiver_info", result)
    assert "not shared" in answer.lower()
