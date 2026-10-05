from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import math


def is_missing(value) -> bool:
    if value is None:
        return True
    try:
        return isinstance(value, float) and math.isnan(value)
    except TypeError:
        return False


def confidence_band(confidence: Optional[float]) -> str:
    if confidence is None:
        return "Unknown"
    if confidence > 0.80:
        return "High"
    if confidence >= 0.60:
        return "Moderate"
    return "Low"


HARM_LIBRARY = {
    "incorrect_eta": {"description": "Incorrect ETA could cause the family to believe the caregiver will arrive earlier/later than they actually will.", "base_probability": 0.5, "impact": 0.6},
    "unauthorised_disclosure": {"description": "Sharing information the recipient is not authorised or consented to receive.", "base_probability": 0.05, "impact": 0.9},
    "incorrect_status": {"description": "Communicating a visit status that conflicts with underlying data.", "base_probability": 0.3, "impact": 0.7},
    "missing_exception": {"description": "Failing to communicate an important exception (e.g. medical emergency) that the family should know about.", "base_probability": 0.2, "impact": 0.8},
    "overconfident_recommendation": {"description": "Presenting a low-confidence estimate as though it were certain.", "base_probability": 0.3, "impact": 0.5},
}


def classify_risk(score: float) -> str:
    if score >= 0.6:
        return "Critical"
    if score >= 0.35:
        return "High"
    if score >= 0.15:
        return "Medium"
    return "Low"


def assess_harm(visit: Dict[str, Any], confidence: Optional[float], conflicting: bool) -> Dict[str, Any]:
    risks = []
    conf = confidence if confidence is not None else 0.0
    eta_prob = min(HARM_LIBRARY["incorrect_eta"]["base_probability"] * (1 - conf) + (0.3 if confidence is None else 0), 0.95)
    eta_score = round(eta_prob * HARM_LIBRARY["incorrect_eta"]["impact"], 2)
    risks.append({"type": "incorrect_eta", "probability": round(eta_prob, 2), "impact": HARM_LIBRARY["incorrect_eta"]["impact"],
                   "score": eta_score, "level": classify_risk(eta_score), "description": HARM_LIBRARY["incorrect_eta"]["description"]})
    if conflicting:
        prob = 0.7
        score = round(prob * HARM_LIBRARY["incorrect_status"]["impact"], 2)
        risks.append({"type": "incorrect_status", "probability": prob, "impact": HARM_LIBRARY["incorrect_status"]["impact"],
                       "score": score, "level": classify_risk(score), "description": HARM_LIBRARY["incorrect_status"]["description"]})
    if visit.get("exception_code") == "medical_emergency":
        prob = 0.6
        score = round(prob * HARM_LIBRARY["missing_exception"]["impact"], 2)
        risks.append({"type": "missing_exception", "probability": prob, "impact": HARM_LIBRARY["missing_exception"]["impact"],
                       "score": score, "level": classify_risk(score), "description": HARM_LIBRARY["missing_exception"]["description"]})
    if confidence is not None and confidence < 0.6:
        prob = 0.4
        score = round(prob * HARM_LIBRARY["overconfident_recommendation"]["impact"], 2)
        risks.append({"type": "overconfident_recommendation", "probability": prob, "impact": HARM_LIBRARY["overconfident_recommendation"]["impact"],
                       "score": score, "level": classify_risk(score), "description": HARM_LIBRARY["overconfident_recommendation"]["description"]})
    dominant = max(risks, key=lambda r: r["score"])
    return {"dominant_risk": dominant, "all_risks": risks}


FIELD_CONSENT_MAP = {
    "visit_status": "scheduling_updates", "estimated_arrival": "scheduling_updates",
    "delay_reason": "delay_updates", "general_care_note": "general_care_updates",
    "medical_detail": "medical_information", "location": "location_information",
    "caregiver_identifier": "caregiver_information",
}


def role_allows_disclosure(role: str) -> bool:
    return role in ("Primary Contact", "Secondary Contact")


def filter_fields(candidate_fields: List[str], role: str, consent: Dict[str, bool]) -> Dict[str, List[str]]:
    allowed, excluded = [], []
    if not role_allows_disclosure(role):
        return {"allowed": [], "excluded": candidate_fields}
    for f in candidate_fields:
        key = FIELD_CONSENT_MAP.get(f)
        if key is None:
            allowed.append(f)
            continue
        (allowed if consent.get(key, False) else excluded).append(f)
    if role == "Secondary Contact":
        limited = {"visit_status", "estimated_arrival", "delay_reason"}
        excluded += [f for f in allowed if f not in limited]
        allowed = [f for f in allowed if f in limited]
    return {"allowed": allowed, "excluded": excluded}


@dataclass
class CommunicationResult:
    summary: str
    uncertainty: str
    reason: Optional[str]
    disclosures: List[str]
    excluded_information: List[str]
    risk_level: str
    requires_human_review: bool
    explanation: List[str] = field(default_factory=list)
    escalation_reason: Optional[str] = None
    harm_assessment: Optional[Dict[str, Any]] = None


def generate_family_communication(visit: Dict[str, Any], family_role: str, consent: Dict[str, bool], authorised: bool) -> CommunicationResult:
    explanation = []
    if not authorised or family_role == "Unauthorised":
        explanation.append("Recipient is not an authorised family contact for this patient.")
        return CommunicationResult(
            summary="You are not authorised to receive information about this visit. Please contact the care coordinator if you believe this is in error.",
            uncertainty="N/A", reason=None, disclosures=[], excluded_information=["all_visit_information"],
            risk_level="Low", requires_human_review=False, explanation=explanation)

    status = visit.get("visit_status")
    eta = visit.get("estimated_arrival")
    actual_arrival = visit.get("actual_arrival")
    confidence = visit.get("travel_confidence")
    if is_missing(confidence):
        confidence = None
    traffic = visit.get("traffic_level")
    exception_code = visit.get("exception_code")
    if is_missing(exception_code):
        exception_code = None
    data_quality = visit.get("data_quality", "good")

    conflicting = (status == "completed" and is_missing(actual_arrival)) or \
                  (status == "cancelled" and exception_code is None and data_quality == "poor")
    if conflicting:
        explanation.append("Visit data is internally inconsistent (e.g. status says completed but no actual arrival time is recorded). Confident communication is unsafe.")

    missing_eta = status in ("scheduled", "delayed", "in_progress") and is_missing(eta)
    band = confidence_band(confidence)
    explanation.append(f"Travel/ETA confidence classified as '{band}' (raw confidence: {confidence if confidence is not None else 'not available'}).")

    harm = assess_harm(visit, confidence, conflicting)
    dominant = harm["dominant_risk"]
    explanation.append(f"Dominant potential harm: {dominant['type']} (probability {dominant['probability']}, impact {dominant['impact']}, risk score {dominant['score']} -> {dominant['level']}).")

    candidate_fields = ["visit_status"]
    if status in ("scheduled", "delayed", "in_progress"):
        candidate_fields.append("estimated_arrival")
    if status == "delayed" or exception_code:
        candidate_fields.append("delay_reason")
    if exception_code == "medical_emergency":
        candidate_fields.append("medical_detail")

    filtered = filter_fields(candidate_fields, family_role, consent)
    explanation.append(f"Role '{family_role}' with active consent settings permits disclosure of: {filtered['allowed'] or 'none'}.")
    if filtered["excluded"]:
        explanation.append(f"Excluded due to role/consent restrictions: {filtered['excluded']}.")
    explanation.append("Caregiver identity is excluded by default unless explicitly consented and requested.")

    requires_review, escalation_reason = False, None
    if conflicting:
        requires_review, escalation_reason = True, "Conflicting or inconsistent visit data."
    elif missing_eta:
        requires_review, escalation_reason = True, "ETA information is missing for a visit that is not yet completed."
    elif dominant["level"] in ("High", "Critical"):
        requires_review, escalation_reason = True, f"Dominant risk level is {dominant['level']}."
    elif data_quality == "poor" and band == "Low":
        requires_review, escalation_reason = True, "Low data quality combined with low confidence."

    if requires_review:
        explanation.append(f"Escalation triggered: {escalation_reason}")
        return CommunicationResult(
            summary="The latest visit information could not be confirmed with confidence. Please contact the care coordinator for the most accurate update.",
            uncertainty=band, reason=escalation_reason, disclosures=[], excluded_information=filtered["excluded"] + ["caregiver_identifier"],
            risk_level=dominant["level"], requires_human_review=True, explanation=explanation,
            escalation_reason=escalation_reason, harm_assessment=harm)

    parts = []
    if "visit_status" in filtered["allowed"]:
        status_phrases = {"scheduled": "Your scheduled care visit is on track.", "delayed": "Your scheduled care visit is delayed.",
                           "in_progress": "Your care visit is currently in progress.", "completed": "Your care visit has been completed.",
                           "cancelled": "Your care visit has been cancelled."}
        parts.append(status_phrases.get(status, "There is an update on your care visit."))

    if "estimated_arrival" in filtered["allowed"] and not is_missing(eta):
        if band == "High":
            parts.append(f"Expected arrival: {eta}.")
        elif band == "Moderate":
            parts.append(f"Expected arrival is approximately {eta}. This may change due to traffic conditions.")
        else:
            parts.append("The arrival time is currently uncertain due to traffic conditions. Please contact the care coordinator for the latest update.")

    reason_text = None
    if "delay_reason" in filtered["allowed"]:
        reason_text = f"{traffic.capitalize()} traffic is affecting travel time." if traffic else \
            (exception_code.replace("_", " ").capitalize() if exception_code else None)
        if reason_text:
            parts.append(f"Reason: {reason_text}")

    if consent.get("medical_information") is False:
        parts.append("No medical information is included in this update.")

    summary = " ".join(parts) if parts else "No update is currently available for this visit."

    return CommunicationResult(summary=summary, uncertainty=band, reason=reason_text, disclosures=filtered["allowed"],
        excluded_information=filtered["excluded"] + ["caregiver_identifier"], risk_level=dominant["level"],
        requires_human_review=False, explanation=explanation, harm_assessment=harm)


def answer_family_question(question_category: str, comm_result: CommunicationResult) -> str:
    if comm_result.requires_human_review:
        return "I cannot reliably determine the current status of this visit. Please contact the care coordinator for confirmation."
    if question_category == "eta":
        if "estimated_arrival" in comm_result.disclosures:
            return comm_result.summary
        return "I don't have an authorised, confirmed arrival time to share with you. Please contact the care coordinator for the latest update."
    if question_category in ("status", "scheduling"):
        return comm_result.summary
    if question_category == "exception":
        return comm_result.reason or "No specific exception reason is available for this visit."
    if question_category == "caregiver_info":
        return "Caregiver identity details are not shared through this channel. Please contact the care coordinator."
    if question_category == "medical":
        return "Medical information is not shared through this family communication channel by default."
    return "I don't have enough authorised information to answer that. Please contact the care coordinator."
