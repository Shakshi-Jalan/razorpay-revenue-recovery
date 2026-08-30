import streamlit as st
import pandas as pd
import os

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Revenue Recovery",
    page_icon="💰",
    layout="wide"
)

# =========================================================
# LOAD DATA
# =========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AUDIT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "recovery_audit_log.csv"
)

if not os.path.exists(AUDIT_FILE):
    st.error("Recovery audit log not found.")
    st.stop()

df = pd.read_csv(AUDIT_FILE)

# =========================================================
# TITLE
# =========================================================

st.title("💰 AI Revenue Recovery Agent")

st.markdown(
    "AI-powered payment failure detection, recovery prioritization "
    "and bounded recovery actions."
)

st.success("Recovery audit data loaded successfully.")

# =========================================================
# KEY BUSINESS NUMBERS
# =========================================================

total_payments = len(df)
total_amount = df["amount"].sum()

approved = int((df["status"] == "APPROVED").sum())
human_review = int((df["status"] == "PENDING").sum())

# Batch experiment numbers
baseline_net = 938854.78
ai_net = 2243148.72
additional_recovery = 1304293.94
improvement = 138.92

attempts = 500
outreach_cost = 12500

# =========================================================
# RECOVERY OVERVIEW
# =========================================================

st.header("📊 Recovery Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Failed Payments",
        f"{total_payments:,}"
    )

with col2:
    st.metric(
        "Amount at Risk",
        f"₹{total_amount:,.0f}"
    )

with col3:
    st.metric(
        "Approved Recoveries",
        f"{approved:,}"
    )

with col4:
    st.metric(
        "Human Reviews",
        f"{human_review:,}"
    )

# =========================================================
# BUSINESS IMPACT
# =========================================================

st.header("💰 Business Impact")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Baseline Net Recovery",
        f"₹{baseline_net:,.0f}"
    )

with col2:
    st.metric(
        "AI Net Recovery",
        f"₹{ai_net:,.0f}",
        delta=f"₹{additional_recovery:,.0f}"
    )

with col3:
    st.metric(
        "Improvement",
        f"{improvement:.2f}%"
    )

st.info(
    f"Using the same {attempts} recovery attempts and the same "
    f"₹{outreach_cost:,} outreach cost, the AI-prioritized strategy "
    f"produced ₹{additional_recovery:,.2f} more net recovery than the baseline."
)

# =========================================================
# BASELINE VS AI
# =========================================================

st.header("⚖️ Baseline vs AI Prioritized Strategy")

comparison = pd.DataFrame({
    "Strategy": [
        "Baseline",
        "AI Prioritized"
    ],
    "Attempts": [
        500,
        500
    ],
    "Outreach Cost": [
        12500,
        12500
    ],
    "Net Recovery": [
        baseline_net,
        ai_net
    ]
})

st.dataframe(
    comparison,
    width="stretch",
    hide_index=True
)

# =========================================================
# PRIORITY DISTRIBUTION
# =========================================================

st.header("🎯 Recovery Priority Distribution")

priority_counts = df["recovery_priority"].value_counts()

st.bar_chart(priority_counts)

# =========================================================
# CONFIDENCE DISTRIBUTION
# =========================================================

st.header("🧠 Model Confidence Distribution")

confidence_counts = df["confidence"].value_counts()

st.bar_chart(confidence_counts)

# =========================================================
# ACTION DISTRIBUTION
# =========================================================

st.header("⚙️ Recovery Action Distribution")

action_counts = df["action"].value_counts()

st.bar_chart(action_counts)
# =========================================================
# MODEL EXCEPTIONS
# =========================================================

st.header("🚨 Model Exceptions")

# Low-confidence cases sent for human review
exceptions = df[
    (df["action"] == "HUMAN_REVIEW") |
    (df["confidence"] == "Low")
].copy()

st.metric(
    "Exception Cases",
    f"{len(exceptions):,}"
)

st.info(
    "These cases require additional attention because the model "
    "has low confidence or the recovery opportunity requires human review."
)

if len(exceptions) > 0:

    exception_columns = [
        "payment_id",
        "amount",
        "recovery_probability",
        "expected_recoverable_revenue",
        "recovery_priority",
        "confidence",
        "action",
        "status",
        "reason"
    ]

    available_columns = [
        col for col in exception_columns
        if col in exceptions.columns
    ]

    st.dataframe(
        exceptions[available_columns],
        width="stretch",
        height=400
    )

else:

    st.success("No model exception cases found.")
# =========================================================
# AUDIT TRAIL
# =========================================================

st.header("📋 Recovery Audit Trail")

st.dataframe(
    df,
    width="stretch",
    height=450
)