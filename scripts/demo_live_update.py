"""
demo_live_update.py
Demonstrates a live traffic disruption cascading to family notifications,
across every active visit + its family recipients in the synthetic dataset.
Writes reports/live_update_cascade.md with measured, non-fabricated results.
"""
import os, sys, random
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from app.rules.live_update import TrafficDisruptionEvent, recompute_and_cascade

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")
random.seed(5)


def main():
    visits = pd.read_csv(os.path.join(DATA_DIR, "visits.csv"))
    family_roles = pd.read_csv(os.path.join(DATA_DIR, "family_roles.csv"))
    consent = pd.read_csv(os.path.join(DATA_DIR, "consent.csv")).set_index("patient_id")

    active = visits[visits.visit_status.isin(["scheduled", "in_progress", "delayed"])].sample(
        n=min(25, len(visits)), random_state=5
    )

    total_renotified, total_recipients, examples = 0, 0, []
    for _, v in active.iterrows():
        recipients_df = family_roles[family_roles.patient_id == v.patient_id]
        if recipients_df.empty or v.patient_id not in consent.index:
            continue
        crow = consent.loc[v.patient_id]
        recipients = [{
            "family_member_id": r.family_member_id, "family_role": r.role,
            "authorised": r.role != "Unauthorised" and bool(r.active_status),
            "consent": {
                "scheduling_updates": bool(crow.scheduling_updates), "delay_updates": bool(crow.delay_updates),
                "general_care_updates": bool(crow.general_care_updates), "medical_information": bool(crow.medical_information),
                "location_information": bool(crow.location_information), "caregiver_information": bool(crow.caregiver_information),
            },
        } for _, r in recipients_df.iterrows()]

        event = TrafficDisruptionEvent(visit_id=v.visit_id, new_traffic_level="severe",
                                        delay_minutes_added=random.randint(15, 45))
        result = recompute_and_cascade(v.to_dict(), event, recipients)
        total_renotified += result["recipients_renotified"]
        total_recipients += result["recipients_total"]
        if len(examples) < 3:
            examples.append((v.visit_id, result))

    pct = round(100 * total_renotified / total_recipients, 1) if total_recipients else 0.0

    lines = [
        "# Live Traffic Disruption → Notification Cascade (Phase 2)",
        "",
        f"Simulated a sudden 'severe traffic' disruption event on {len(active)} active visits "
        f"and recomputed the Responsible AI pipeline for every active family recipient.",
        "",
        f"- Total recipients evaluated: {total_recipients}",
        f"- Recipients whose message actually changed (re-notified): {total_renotified} ({pct}%)",
        f"- Recipients NOT re-notified (message unchanged — avoids alert fatigue): {total_recipients - total_renotified}",
        "",
        "## Example Cascades",
    ]
    for visit_id, result in examples:
        lines.append(f"\n### Visit {visit_id}")
        lines.append(f"Confidence band: {result['confidence_band_before']} → {result['confidence_band_after']}")
        for c in result["cascade"]:
            lines.append(f"- **{c['family_member_id']}** (renotify={c['renotify']}): "
                         f"\"{c['before_summary']}\" → \"{c['after_summary']}\"")

    with open(os.path.join(REPORT_DIR, "live_update_cascade.md"), "w") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
