import pandas as pd
import json

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from recovery_engine import execute_recovery_action
from message_generator import generate_recovery_message
from payment_link import create_payment_link

# -----------------------------------
# 1. Load dataset
# -----------------------------------

data = pd.read_csv("data/payments.csv")

print("Dataset loaded successfully.")

print("\nShape:")
print(data.shape)

print("\nColumns:")
print(data.columns.tolist())


# -----------------------------------
# 2. Select features and target
# -----------------------------------

features = [
    "amount",
    "payment_method",
    "hour_of_day",
    "day_of_week",
    "retry_count",
    "failure_reason",
    "failure_source",
    "failure_step",
    "customer_tenure_days",
    "previous_success_count",
    "previous_failure_count",
    "customer_recent_activity",
    "historical_recovery_rate"
]

target = "recovered"

X = data[features]
y = data[target]

print("\nFeature columns:")
print(X.columns.tolist())

print("\nTarget:")
print(target)

print("\nFeature shape:")
print(X.shape)

print("\nTarget shape:")
print(y.shape)


# -----------------------------------
# 3. Split data
# -----------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining data shape:")
print(X_train.shape)

print("\nTesting data shape:")
print(X_test.shape)

print("\nTraining target distribution:")
print(y_train.value_counts())

print("\nTesting target distribution:")
print(y_test.value_counts())


# -----------------------------------
# 4. Identify feature types
# -----------------------------------

categorical_features = [
    "payment_method",
    "day_of_week",
    "failure_reason",
    "failure_source",
    "failure_step",
    "customer_recent_activity"
]

numerical_features = [
    "amount",
    "hour_of_day",
    "retry_count",
    "customer_tenure_days",
    "previous_success_count",
    "previous_failure_count",
    "historical_recovery_rate"
]

print("\nCategorical features:")
print(categorical_features)

print("\nNumerical features:")
print(numerical_features)


# -----------------------------------
# 5. Preprocessing
# -----------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "numerical",
            "passthrough",
            numerical_features
        )
    ]
)


# -----------------------------------
# 6. Random Forest model
# -----------------------------------

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=8,
    min_samples_leaf=20,
    random_state=42,
    n_jobs=-1
)


# -----------------------------------
# 7. Create ML pipeline
# -----------------------------------

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# -----------------------------------
# 8. Train model
# -----------------------------------

print("\nTraining Random Forest...")

pipeline.fit(X_train, y_train)

print("Model training complete.")
# -----------------------------------
# 9. Evaluate model
# -----------------------------------

from sklearn.metrics import (
    roc_auc_score,
    accuracy_score,
    classification_report,
    confusion_matrix
)

# Predict recovery probability
y_probability = pipeline.predict_proba(X_test)[:, 1]

# Predict final class
y_prediction = pipeline.predict(X_test)

# Calculate metrics
auc = roc_auc_score(y_test, y_probability)
accuracy = accuracy_score(y_test, y_prediction)

print("\n--- MODEL EVALUATION ---")

print(f"\nROC-AUC: {auc:.4f}")
print(f"Accuracy: {accuracy:.4f}")

print("\nClassification Report:")
print(classification_report(y_test, y_prediction))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_prediction))

# -----------------------------------
# 10. Check predicted probabilities
# -----------------------------------

print("\n--- PREDICTED PROBABILITY CHECK ---")

print("\nMinimum probability:")
print(y_probability.min())

print("\nMaximum probability:")
print(y_probability.max())

print("\nAverage probability:")
print(y_probability.mean())

print("\nProbability distribution:")
print(
    pd.Series(y_probability).describe()
)
# -----------------------------------
# 11. Check recovery patterns
# -----------------------------------

print("\n--- RECOVERY RATE BY FAILURE REASON ---")

recovery_by_reason = (
    data.groupby("failure_reason")["recovered"]
    .agg(["count", "mean"])
    .sort_values("mean", ascending=False)
)

print(recovery_by_reason)


print("\n--- RECOVERY RATE BY PAYMENT METHOD ---")

recovery_by_method = (
    data.groupby("payment_method")["recovered"]
    .agg(["count", "mean"])
    .sort_values("mean", ascending=False)
)

print(recovery_by_method)


print("\n--- RECOVERY RATE BY RETRY COUNT ---")

recovery_by_retry = (
    data.groupby("retry_count")["recovered"]
    .agg(["count", "mean"])
    .sort_values("mean", ascending=False)
)

print(recovery_by_retry)
# -----------------------------------
# 12. Expected Recoverable Revenue
# -----------------------------------

results = X_test.copy()

results["payment_id"] = data.loc[X_test.index, "payment_id"].values
results["actual_recovered"] = y_test.values

results["recovery_probability"] = y_probability

results["expected_recoverable_revenue"] = (
    results["amount"] * results["recovery_probability"]
)

results = results.sort_values(
    "expected_recoverable_revenue",
    ascending=False
)

print("\n--- TOP RECOVERY OPPORTUNITIES ---")

print(
    results[
        [
            "payment_id",
            "amount",
            "recovery_probability",
            "expected_recoverable_revenue"
        ]
    ].head(10)
)
# -----------------------------------
# 13. Recovery Priority
# -----------------------------------

high_threshold = results["expected_recoverable_revenue"].quantile(0.80)
low_threshold = results["expected_recoverable_revenue"].quantile(0.30)


def assign_priority(value):
    if value >= high_threshold:
        return "High"
    elif value >= low_threshold:
        return "Medium"
    else:
        return "Low"


results["recovery_priority"] = (
    results["expected_recoverable_revenue"]
    .apply(assign_priority)
)


print("\n--- RECOVERY PRIORITY DISTRIBUTION ---")

print(
    results["recovery_priority"].value_counts()
)


print("\n--- TOP RECOVERY OPPORTUNITIES WITH PRIORITY ---")

print(
    results[
        [
            "payment_id",
            "amount",
            "recovery_probability",
            "expected_recoverable_revenue",
            "recovery_priority"
        ]
    ].head(10)
)
# -----------------------------------
# 14. Ensemble disagreement
# -----------------------------------

print("\nCalculating model uncertainty...")

# Transform test data using the same preprocessing
X_test_transformed = pipeline.named_steps["preprocessor"].transform(X_test)

forest_model = pipeline.named_steps["model"]

# Get probability prediction from every tree
tree_probabilities = []

for tree in forest_model.estimators_:
    tree_probability = tree.predict_proba(
        X_test_transformed
    )[:, 1]

    tree_probabilities.append(tree_probability)

# Convert to DataFrame
tree_probabilities = pd.DataFrame(
    tree_probabilities
).T

# Standard deviation = disagreement between trees
results["prediction_std"] = (
    tree_probabilities.std(axis=1).values
)

print("\nPrediction disagreement:")
print(
    results["prediction_std"].describe()
)
# -----------------------------------
# 15. Confidence level
# -----------------------------------

confidence_high = results["prediction_std"].quantile(0.30)
confidence_low = results["prediction_std"].quantile(0.70)


def assign_confidence(value):
    if value <= confidence_high:
        return "High"
    elif value >= confidence_low:
        return "Low"
    else:
        return "Medium"


results["confidence"] = (
    results["prediction_std"]
    .apply(assign_confidence)
)


print("\n--- CONFIDENCE DISTRIBUTION ---")

print(
    results["confidence"].value_counts()
)
# -----------------------------------
# 16. Recovery Decision Engine
# -----------------------------------

def recovery_decision(row):

    # Stopping rule: maximum 2 recovery attempts
    if row["retry_count"] >= 2:
        return "Stop / Do Not Pursue"

    # High-value opportunity
    if (
        row["recovery_priority"] == "High"
        and row["confidence"] == "High"
    ):
        return "Approve Recovery"

    # High-value but uncertain
    if (
        row["recovery_priority"] == "High"
        and row["confidence"] == "Low"
    ):
        return "Human Review"

    # Medium opportunity
    if (
        row["recovery_priority"] == "Medium"
        and row["confidence"] != "Low"
        and row["retry_count"] < 2
    ):
        return "Standard Recovery"

    # Everything else
    return "Stop / Do Not Pursue"


results["decision"] = results.apply(
    recovery_decision,
    axis=1
)


print("\n--- RECOVERY DECISION DISTRIBUTION ---")

print(
    results["decision"].value_counts()
)
# -----------------------------------
# 17. Batch Money Recovery Experiment
# -----------------------------------

OUTREACH_COST = 25

# Number of recovery attempts we allow
MAX_ATTEMPTS = 500


# -----------------------------------
# Baseline Strategy
# -----------------------------------

baseline = results.copy()

# Keep original test-set order
baseline = baseline.sort_index()

baseline = baseline.head(MAX_ATTEMPTS)

baseline_cost = (
    len(baseline) * OUTREACH_COST
)

baseline_recovered_revenue = (
    baseline.loc[
        baseline["actual_recovered"] == 1,
        "amount"
    ].sum()
)


baseline_net_recovery = (
    baseline_recovered_revenue - baseline_cost
)


# -----------------------------------
# AI Prioritized Strategy
# -----------------------------------

ai_strategy = results.copy()

ai_strategy = ai_strategy.sort_values(
    "expected_recoverable_revenue",
    ascending=False
)

ai_strategy = ai_strategy.head(MAX_ATTEMPTS)

ai_cost = (
    len(ai_strategy) * OUTREACH_COST
)

ai_recovered_revenue = (
    ai_strategy.loc[
        ai_strategy["actual_recovered"] == 1,
        "amount"
    ].sum()
)


ai_net_recovery = (
    ai_recovered_revenue - ai_cost
)


# -----------------------------------
# Compare strategies
# -----------------------------------

print("\n--- BATCH RECOVERY EXPERIMENT ---")

print(f"\nTotal test batch: {len(results)}")
print(f"Recovery attempts allowed: {MAX_ATTEMPTS}")
print(f"Outreach cost per attempt: ₹{OUTREACH_COST}")

print("\nBASELINE STRATEGY")
print(f"Attempts: {len(baseline)}")
print(f"Outreach cost: ₹{baseline_cost:,.2f}")
print(
    f"Recovered revenue: ₹{baseline_recovered_revenue:,.2f}"
)
print(
    f"Net recovery: ₹{baseline_net_recovery:,.2f}"
)

print("\nAI PRIORITIZED STRATEGY")
print(f"Attempts: {len(ai_strategy)}")
print(f"Outreach cost: ₹{ai_cost:,.2f}")
print(
    f"Recovered revenue: ₹{ai_recovered_revenue:,.2f}"
)
print(
    f"Net recovery: ₹{ai_net_recovery:,.2f}"
)


# Improvement
improvement = (
    ai_net_recovery - baseline_net_recovery
)

print("\n--- BUSINESS IMPACT ---")

print(
    f"Additional net recovery: ₹{improvement:,.2f}"
)

if baseline_net_recovery != 0:
    improvement_percent = (
        improvement / abs(baseline_net_recovery)
    ) * 100

    print(
        f"Improvement: {improvement_percent:.2f}%"
    )
    # Save business impact results for dashboard
business_impact = {
    "baseline_net": float(baseline_net_recovery),
    "ai_net": float(ai_net_recovery),
    "additional_recovery": float(improvement),
    "improvement_percent": float(improvement_percent),
    "attempts": int(MAX_ATTEMPTS),
    "outreach_cost": float(baseline_cost),
    "baseline_recovered_revenue": float(baseline_recovered_revenue),
    "ai_recovered_revenue": float(ai_recovered_revenue)
}

with open("data/business_impact.json", "w") as f:
    json.dump(business_impact, f, indent=2)

print("\nBusiness impact saved to: data/business_impact.json")
    # -----------------------------------
# 18. Strategy Validation
# -----------------------------------

baseline_recovery_rate = (
    baseline["actual_recovered"].mean()
)

ai_recovery_rate = (
    ai_strategy["actual_recovered"].mean()
)

baseline_avg_amount = (
    baseline["amount"].mean()
)

ai_avg_amount = (
    ai_strategy["amount"].mean()
)


print("\n--- STRATEGY VALIDATION ---")

print(
    f"Baseline recovery rate: "
    f"{baseline_recovery_rate:.4f}"
)

print(
    f"AI recovery rate: "
    f"{ai_recovery_rate:.4f}"
)

print(
    f"Baseline average payment: "
    f"₹{baseline_avg_amount:,.2f}"
)

print(
    f"AI average payment: "
    f"₹{ai_avg_amount:,.2f}"
)
# -----------------------------------
# 19. Execute Recovery Actions
# -----------------------------------

print("\n--- RECOVERY ACTION EXECUTION ---")

action_results = []

for _, row in results.iterrows():

    action_result = execute_recovery_action(row)

    # -----------------------------------
    # Generate payment link for approved actions
    # -----------------------------------

    if action_result["action"] == "GENERATE_PAYMENT_LINK":

        payment_link_response = create_payment_link(
    payment_id=row["payment_id"],
    amount=row["amount"]
)

        action_result["payment_link_id"] = (
            payment_link_response["id"]
        )

        action_result["payment_link_url"] = (
            payment_link_response["short_url"]
        )

        action_result["payment_link_status"] = (
            payment_link_response["status"]
        )

        # Generate recovery message
        recovery_message = generate_recovery_message(row)

    else:

        action_result["payment_link_id"] = None
        action_result["payment_link_url"] = None
        action_result["payment_link_status"] = None

        recovery_message = None

    action_result["recovery_message"] = recovery_message

    action_results.append(action_result)


action_log = pd.DataFrame(action_results)
# -----------------------------------
# 20. Persistent Audit Trail
# -----------------------------------

audit_log = results[
    [
        "payment_id",
        "amount",
        "recovery_probability",
        "expected_recoverable_revenue",
        "recovery_priority",
        "confidence",
        "retry_count"
    ]
].copy()


# Add action information
audit_log = audit_log.merge(
   action_log[
    [
        "payment_id",
        "action",
        "status",
        "timestamp",
        "reason",
        "recovery_message",
        "payment_link_id",
        "payment_link_url",
        "payment_link_status"
    ]
],
    on="payment_id",
    how="left"
)


# Save audit log
audit_path = "data/recovery_audit_log.csv"

audit_log.to_csv(
    audit_path,
    index=False
)


print("\n--- AUDIT TRAIL ---")

print(
    f"Audit log saved to: {audit_path}"
)

print(
    f"Audit records: {len(audit_log)}"
)

print("\nAudit log preview:")

print(
    audit_log.head(10)
)

print("\nAction distribution:")

print(
    action_log["action"].value_counts()
)


print("\nAction status distribution:")

print(
    action_log["status"].value_counts()
)


print("\nSample recovery actions:")

print(
    action_log.head(10)
)