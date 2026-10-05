"""
main.py — FastAPI service wrapping the deterministic Responsible AI pipeline.

New in Phase 2: this turns the pipeline (previously only callable from scripts/
the Streamlit app) into a real, independently-testable service boundary, which
is what the latency/concurrency benchmark in scripts/benchmark_latency.py
exercises.

Run with:  uvicorn app.main:app --reload
"""
import os
import sys
from typing import Optional, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

sys.path.append(os.path.dirname(__file__))
from rules.pipeline import generate_family_communication, answer_family_question, CommunicationResult

app = FastAPI(title="Home-Care Responsible AI API", version="0.2.0")


class ConsentModel(BaseModel):
    scheduling_updates: bool = False
    delay_updates: bool = False
    general_care_updates: bool = False
    medical_information: bool = False
    location_information: bool = False
    caregiver_information: bool = False


class VisitModel(BaseModel):
    visit_status: str
    estimated_arrival: Optional[str] = None
    actual_arrival: Optional[str] = None
    traffic_level: Optional[str] = None
    travel_confidence: Optional[float] = None
    exception_code: Optional[str] = None
    data_quality: str = "good"


class CommunicationRequest(BaseModel):
    visit: VisitModel
    family_role: str
    consent: ConsentModel
    authorised: bool


class QuestionRequest(BaseModel):
    visit: VisitModel
    family_role: str
    consent: ConsentModel
    authorised: bool
    question_category: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/communicate")
def communicate(req: CommunicationRequest) -> Dict:
    result: CommunicationResult = generate_family_communication(
        req.visit.dict(), req.family_role, req.consent.dict(), req.authorised
    )
    return {
        "summary": result.summary,
        "uncertainty": result.uncertainty,
        "reason": result.reason,
        "disclosures": result.disclosures,
        "excluded_information": result.excluded_information,
        "risk_level": result.risk_level,
        "requires_human_review": result.requires_human_review,
        "explanation": result.explanation,
        "escalation_reason": result.escalation_reason,
    }


@app.post("/ask")
def ask(req: QuestionRequest) -> Dict:
    result = generate_family_communication(req.visit.dict(), req.family_role, req.consent.dict(), req.authorised)
    answer = answer_family_question(req.question_category, result)
    return {"answer": answer, "requires_human_review": result.requires_human_review}
