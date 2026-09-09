"""
generate_data.py
Generates synthetic (NOT real) home-care data:
patients, family_roles, consent, caregivers, visits, care_events, family_questions.
"""
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

random.seed(42)
np.random.seed(42)

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic")
os.makedirs(OUT_DIR, exist_ok=True)

N_PATIENTS = 120
N_CAREGIVERS = 55
N_VISITS = 500
N_FAMILY_LINKS = 220
N_QUESTIONS = 400

ZONES = ["North Zone", "South Zone", "East Zone", "West Zone", "Central Zone"]
LANGS = ["English", "Tamil", "Hindi", "Telugu", "Malayalam"]
CARE_LEVELS = ["low", "medium", "high"]
AGE_GROUPS = ["60-70", "71-80", "81-90", "90+"]
COMM_PREF = ["SMS", "App Notification", "Phone Call", "Email"]

ROLES = ["Primary Contact", "Secondary Contact", "Unauthorised"]
RELATIONSHIPS = ["Child", "Spouse", "Sibling", "Friend", "Grandchild", "Neighbour"]
AUTH_LEVELS = {"Primary Contact": "high", "Secondary Contact": "medium", "Unauthorised": "none"}

TRAFFIC_LEVELS = ["light", "moderate", "heavy", "severe"]
VISIT_STATUSES = ["scheduled", "in_progress", "delayed", "completed", "cancelled"]
EXCEPTION_CODES = [None, "traffic_delay", "caregiver_unavailable", "patient_unavailable",
                    "medical_emergency", "route_blocked", "vehicle_issue"]

EVENT_TYPES = ["visit_scheduled", "visit_started", "visit_delayed", "visit_completed",
               "visit_cancelled", "care_exception", "follow_up_required"]

QUESTION_TEMPLATES = [
    ("When will the caregiver arrive?", "eta"),
    ("Is the visit delayed?", "status"),
    ("Why was the visit changed?", "exception"),
    ("Has the visit been completed?", "status"),
    ("Who is the assigned caregiver?", "caregiver_info"),
    ("Is everything okay with the patient?", "medical"),
    ("Can the visit be rescheduled?", "scheduling"),
    ("Why hasn't anyone arrived yet?", "eta"),
]


def gen_patients():
    rows = []
    for i in range(1, N_PATIENTS + 1):
        rows.append({
            "patient_id": f"P{i:03d}",
            "age_group": random.choice(AGE_GROUPS),
            "care_level": random.choice(CARE_LEVELS),
            "location_zone": random.choice(ZONES),
            "preferred_language": random.choice(LANGS),
            "communication_preference": random.choice(COMM_PREF),
        })
    return pd.DataFrame(rows)


def gen_family_roles(patients):
    rows = []
    fid = 1
    patient_ids = patients["patient_id"].tolist()
    for pid in patient_ids:
        n_family = random.randint(1, 3)
        # ensure at least one primary contact
        roles_for_patient = ["Primary Contact"] + [
            random.choice(ROLES) for _ in range(n_family - 1)
        ]
        for role in roles_for_patient:
            rows.append({
                "family_member_id": f"F{fid:03d}",
                "patient_id": pid,
                "role": role,
                "relationship": random.choice(RELATIONSHIPS),
                "authorisation_level": AUTH_LEVELS[role],
                "active_status": True,
            })
            fid += 1
    df = pd.DataFrame(rows)
    # pad to reach N_FAMILY_LINKS by duplicating extra secondary/unauthorised links
    while len(df) < N_FAMILY_LINKS:
        pid = random.choice(patient_ids)
        role = random.choice(ROLES)
        df.loc[len(df)] = {
            "family_member_id": f"F{fid:03d}",
            "patient_id": pid,
            "role": role,
            "relationship": random.choice(RELATIONSHIPS),
            "authorisation_level": AUTH_LEVELS[role],
            "active_status": True,
        }
        fid += 1
    return df


def gen_consent(patients):
    rows = []
    for pid in patients["patient_id"]:
        rows.append({
            "patient_id": pid,
            "scheduling_updates": random.random() > 0.05,
            "delay_updates": random.random() > 0.10,
            "general_care_updates": random.random() > 0.20,
            "medical_information": random.random() > 0.85,  # rarely allowed
            "location_information": random.random() > 0.30,
            "caregiver_information": random.random() > 0.60,
            "consent_status": "active",
            "updated_at": (datetime.now() - timedelta(days=random.randint(1, 200))).isoformat(),
        })
    return pd.DataFrame(rows)


def gen_caregivers():
    return pd.DataFrame([{"caregiver_id": f"C{i:02d}", "zone": random.choice(ZONES)}
                         for i in range(1, N_CAREGIVERS + 1)])


def gen_visits(patients, caregivers):
    rows = []
    base_time = datetime(2026, 9, 1, 8, 0)
    patient_ids = patients["patient_id"].tolist()
    caregiver_ids = caregivers["caregiver_id"].tolist()
    for i in range(1, N_VISITS + 1):
        scheduled = base_time + timedelta(
            days=random.randint(0, 30), hours=random.randint(0, 9), minutes=random.choice([0, 15, 30, 45])
        )
        traffic = random.choices(TRAFFIC_LEVELS, weights=[0.35, 0.30, 0.25, 0.10])[0]
        delay_minutes = {"light": (0, 5), "moderate": (5, 15), "heavy": (15, 35), "severe": (30, 70)}[traffic]
        delay = random.randint(*delay_minutes)
        estimated_arrival = scheduled + timedelta(minutes=delay)

        confidence = {
            "light": random.uniform(0.85, 0.98),
            "moderate": random.uniform(0.65, 0.85),
            "heavy": random.uniform(0.45, 0.70),
            "severe": random.uniform(0.20, 0.50),
        }[traffic]

        status = random.choices(
            VISIT_STATUSES, weights=[0.15, 0.10, 0.30, 0.35, 0.10]
        )[0]

        actual_arrival = None
        if status == "completed":
            actual_arrival = estimated_arrival + timedelta(minutes=random.randint(-5, 10))
        exception_code = None
        if status in ("delayed", "cancelled") or random.random() < 0.1:
            exception_code = random.choice(EXCEPTION_CODES[1:])

        # Inject some missing-data / low-quality rows deliberately (edge cases)
        data_quality = "good"
        if random.random() < 0.06:
            estimated_arrival = None
            data_quality = "poor"
        if random.random() < 0.04:
            confidence = None
            data_quality = "poor"

        rows.append({
            "visit_id": f"V{1000+i}",
            "patient_id": random.choice(patient_ids),
            "caregiver_id": random.choice(caregiver_ids),
            "scheduled_time": scheduled.isoformat(),
            "estimated_arrival": estimated_arrival.isoformat() if estimated_arrival else None,
            "actual_arrival": actual_arrival.isoformat() if actual_arrival else None,
            "traffic_level": traffic,
            "travel_confidence": round(confidence, 2) if confidence is not None else None,
            "visit_status": status,
            "exception_code": exception_code,
            "data_quality": data_quality,
        })
    return pd.DataFrame(rows)


def gen_care_events(visits):
    rows = []
    eid = 1
    for _, v in visits.iterrows():
        n_events = random.randint(1, 3)
        for _ in range(n_events):
            etype = random.choice(EVENT_TYPES)
            rows.append({
                "event_id": f"E{eid:05d}",
                "patient_id": v["patient_id"],
                "visit_id": v["visit_id"],
                "event_type": etype,
                "event_time": v["scheduled_time"],
                "severity": random.choice(["info", "low", "medium", "high"]),
                "description": f"Auto-generated synthetic event: {etype.replace('_', ' ')}",
                "source": random.choice(["scheduling_system", "caregiver_app", "coordinator"]),
                "data_quality": random.choice(["good", "good", "good", "poor"]),
            })
            eid += 1
        if len(rows) >= 500:
            pass
    return pd.DataFrame(rows)


def gen_family_questions(family_roles):
    rows = []
    authorised = family_roles[family_roles["role"] != "Unauthorised"]
    for i in range(1, N_QUESTIONS + 1):
        fam = authorised.sample(1).iloc[0]
        q, cat = random.choice(QUESTION_TEMPLATES)
        rows.append({
            "question_id": f"Q{i:04d}",
            "family_member_id": fam["family_member_id"],
            "patient_id": fam["patient_id"],
            "question": q,
            "question_category": cat,
            "timestamp": (datetime.now() - timedelta(hours=random.randint(0, 500))).isoformat(),
        })
    return pd.DataFrame(rows)


def main():
    patients = gen_patients()
    family_roles = gen_family_roles(patients)
    consent = gen_consent(patients)
    caregivers = gen_caregivers()
    visits = gen_visits(patients, caregivers)
    care_events = gen_care_events(visits)
    family_questions = gen_family_questions(family_roles)

    patients.to_csv(os.path.join(OUT_DIR, "patients.csv"), index=False)
    family_roles.to_csv(os.path.join(OUT_DIR, "family_roles.csv"), index=False)
    consent.to_csv(os.path.join(OUT_DIR, "consent.csv"), index=False)
    caregivers.to_csv(os.path.join(OUT_DIR, "caregivers.csv"), index=False)
    visits.to_csv(os.path.join(OUT_DIR, "visits.csv"), index=False)
    care_events.to_csv(os.path.join(OUT_DIR, "care_events.csv"), index=False)
    family_questions.to_csv(os.path.join(OUT_DIR, "family_questions.csv"), index=False)

    print("Synthetic data generated:")
    for name, df in [
        ("patients", patients), ("family_roles", family_roles), ("consent", consent),
        ("caregivers", caregivers), ("visits", visits), ("care_events", care_events),
        ("family_questions", family_questions),
    ]:
        print(f"  {name}: {len(df)} rows")


if __name__ == "__main__":
    main()
