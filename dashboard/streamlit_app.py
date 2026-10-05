import os
import sys
import pandas as pd
import streamlit as st
import plotly.express as px

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from app.baseline import baseline_message
from app.rules.pipeline import generate_family_communication, answer_family_question

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic")
PROC_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

st.set_page_config(page_title="Home-Care Responsible AI", layout="wide")


@st.cache_data
def load_data():
    patients = pd.read_csv(os.path.join(DATA_DIR, "patients.csv"))
    family_roles = pd.read_csv(os.path.join(DATA_DIR, "family_roles.csv"))
    consent = pd.read_csv(os.path.join(DATA_DIR, "consent.csv"))
    visits = pd.read_csv(os.path.join(DATA_DIR, "visits.csv"))
    care_events = pd.read_csv(os.path.join(DATA_DIR, "care_events.csv"))
    questions = pd.read_csv(os.path.join(DATA_DIR, "family_questions.csv"))
    return patients, family_roles, consent, visits, care_events, questions


patients, family_roles, consent, visits, care_events, questions = load_data()

st.sidebar.title("🏥 Home-Care Responsible AI")
screen = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Family Communication", "Coordinator Review", "Consent Settings", "Evaluation Dashboard"],
)

if screen == "Dashboard":
    st.title("Operational Dashboard")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Visits", len(visits))
    c2.metric("Scheduled", (visits.visit_status == "scheduled").sum())
    c3.metric("Delayed", (visits.visit_status == "delayed").sum())
    c4.metric("Completed", (visits.visit_status == "completed").sum())

    c5, c6, c7 = st.columns(3)
    conflicting = ((visits.visit_status == "completed") & (visits.actual_arrival.isna())).sum()
    poor_quality = (visits.data_quality == "poor").sum()
    c5.metric("High-Risk Cases (data conflicts)", int(conflicting))
    c6.metric("Low Data-Quality Visits", int(poor_quality))
    c7.metric("Cancelled Visits", (visits.visit_status == "cancelled").sum())

    fig = px.histogram(visits, x="visit_status", color="traffic_level", title="Visit Status by Traffic Level")
    st.plotly_chart(fig, use_container_width=True)
    fig2 = px.histogram(visits, x="travel_confidence", nbins=20, title="Distribution of Travel Confidence")
    st.plotly_chart(fig2, use_container_width=True)

elif screen == "Family Communication":
    st.title("Family Communication")
    fam_options = family_roles.merge(patients, on="patient_id")
    fam_id = st.selectbox("Select family member", fam_options["family_member_id"],
        format_func=lambda fid: f"{fid} ({fam_options.loc[fam_options.family_member_id==fid,'role'].values[0]})")
    fam_row = family_roles[family_roles.family_member_id == fam_id].iloc[0]
    patient_id = fam_row["patient_id"]
    patient_visits = visits[visits.patient_id == patient_id]

    if patient_visits.empty:
        st.warning("No visits found for this patient.")
    else:
        visit_id = st.selectbox("Select visit", patient_visits["visit_id"])
        visit_row = patient_visits[patient_visits.visit_id == visit_id].iloc[0].to_dict()
        consent_row = consent[consent.patient_id == patient_id].iloc[0]
        consent_dict = {k: bool(consent_row[k]) for k in ["scheduling_updates", "delay_updates",
            "general_care_updates", "medical_information", "location_information", "caregiver_information"]}
        authorised = fam_row["role"] != "Unauthorised" and bool(fam_row["active_status"])

        colA, colB = st.columns(2)
        with colA:
            st.subheader("Family Member")
            st.write(f"**Role:** {fam_row['role']}")
            st.write(f"**Relationship:** {fam_row['relationship']}")
            st.write(f"**Authorisation level:** {fam_row['authorisation_level']}")
        with colB:
            st.subheader("Consent Status")
            st.json(consent_dict)

        result = generate_family_communication(visit_row, fam_row["role"], consent_dict, authorised)

        st.subheader("📨 Communication Summary")
        st.info(result.summary)

        c1, c2, c3 = st.columns(3)
        c1.metric("Uncertainty", result.uncertainty)
        c2.metric("Risk Level", result.risk_level)
        c3.metric("Needs Human Review", "Yes" if result.requires_human_review else "No")

        with st.expander("🔍 Explanation (why was this message generated?)"):
            for line in result.explanation:
                st.write(f"• {line}")
        with st.expander("🚫 Excluded Information"):
            st.write(result.excluded_information or "None")

        st.subheader("💬 Ask a Question")
        q_text = st.text_input("Type a question (e.g. 'When will the caregiver arrive?')")
        q_cat = st.selectbox("Question category (for demo routing)",
                              ["eta", "status", "exception", "caregiver_info", "medical", "scheduling"])
        if st.button("Ask"):
            st.success(answer_family_question(q_cat, result))

        st.divider()
        st.subheader("Baseline vs Prototype (this visit)")
        c1, c2 = st.columns(2)
        c1.markdown("**Baseline (rule-based)**")
        c1.write(baseline_message(visit_row))
        c2.markdown("**Responsible AI Prototype**")
        c2.write(result.summary)

elif screen == "Coordinator Review":
    st.title("Coordinator Review Queue")
    st.caption("Cases the Responsible AI pipeline has escalated for human review.")
    rows = []
    merged = family_roles.merge(visits, on="patient_id")
    for _, r in merged.iterrows():
        crow = consent[consent.patient_id == r.patient_id]
        if crow.empty:
            continue
        crow = crow.iloc[0]
        consent_dict = {k: bool(crow[k]) for k in ["scheduling_updates", "delay_updates", "general_care_updates",
            "medical_information", "location_information", "caregiver_information"]}
        authorised = r["role"] != "Unauthorised" and bool(r["active_status"])
        result = generate_family_communication(r.to_dict(), r["role"], consent_dict, authorised)
        if result.requires_human_review:
            rows.append({"Case ID": f"{r.visit_id}-{r.family_member_id}", "Patient": r.patient_id, "Visit": r.visit_id,
                "Issue": result.escalation_reason, "Data Quality": r.data_quality, "Confidence": r.travel_confidence,
                "Risk Level": result.risk_level, "Suggested Action": "Verify visit status manually and confirm ETA before contacting family."})
    review_df = pd.DataFrame(rows).drop_duplicates(subset=["Case ID"])
    st.dataframe(review_df, use_container_width=True, height=400)
    if not review_df.empty:
        case = st.selectbox("Select a case to action", review_df["Case ID"])
        c1, c2, c3, c4 = st.columns(4)
        c1.button("✅ Approve"); c2.button("❌ Reject"); c3.button("✏️ Edit"); c4.button("⬆️ Escalate Further")
        st.caption("(Demo buttons — wire to a case-management backend for production use.)")

elif screen == "Consent Settings":
    st.title("Consent Settings")
    patient_id = st.selectbox("Select patient", patients["patient_id"])
    crow = consent[consent.patient_id == patient_id].iloc[0]
    st.toggle("Scheduling Updates", value=bool(crow.scheduling_updates), key="c1")
    st.toggle("Delay Updates", value=bool(crow.delay_updates), key="c2")
    st.toggle("Care Updates", value=bool(crow.general_care_updates), key="c3")
    st.toggle("Medical Information", value=bool(crow.medical_information), key="c4")
    st.toggle("Location Information", value=bool(crow.location_information), key="c5")
    st.toggle("Caregiver Information", value=bool(crow.caregiver_information), key="c6")
    st.caption("(Demo toggles reflect current synthetic consent record; wire to DB writes for production use.)")

elif screen == "Evaluation Dashboard":
    st.title("Evaluation Dashboard — Baseline vs Prototype")
    results_path = os.path.join(PROC_DIR, "experiment_results.csv")
    if not os.path.exists(results_path):
        st.warning("Run `scripts/run_experiment.py` first to generate evaluation results.")
    else:
        df = pd.read_csv(results_path)
        n = len(df)
        metrics = {
            "Family Understanding": (df.baseline_understanding.mean()*100, df.prototype_understanding.mean()*100),
            "Unauthorised Disclosure": (df.baseline_unauthorised_disclosure.mean()*100, df.prototype_unauthorised_disclosure.mean()*100),
            "False Information": (df.baseline_false_information.mean()*100, df.prototype_false_information.mean()*100),
            "Uncertainty Calibration": (df.baseline_uncertainty_correct.mean()*100, df.prototype_uncertainty_correct.mean()*100),
        }
        high_risk = df[df.prototype_high_risk == True]
        escalation_recall = high_risk.prototype_escalated.mean()*100 if len(high_risk) else None

        cols = st.columns(len(metrics))
        for col, (name, (b, p)) in zip(cols, metrics.items()):
            col.metric(name, f"{p:.1f}%", f"{p-b:+.1f} pts vs baseline")
        st.metric("Human Escalation Recall (high-risk cases)",
                   f"{escalation_recall:.1f}%" if escalation_recall is not None else "N/A", f"{len(high_risk)} high-risk cases")

        comp_df = pd.DataFrame({"Metric": list(metrics.keys()) * 2,
            "Value": [v[0] for v in metrics.values()] + [v[1] for v in metrics.values()],
            "System": ["Baseline"] * len(metrics) + ["Prototype"] * len(metrics)})
        fig = px.bar(comp_df, x="Metric", y="Value", color="System", barmode="group", title="Baseline vs Prototype Metrics (%)")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Sample Scenarios")
        st.dataframe(df.sample(min(15, n)), use_container_width=True)

        eval_report = os.path.join(os.path.dirname(__file__), "..", "reports", "evaluation_report.md")
        if os.path.exists(eval_report):
            with open(eval_report) as f:
                st.markdown(f.read())
