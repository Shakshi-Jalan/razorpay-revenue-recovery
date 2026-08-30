import numpy as np
import pandas as pd

# Reproducible results
np.random.seed(42)

# Number of customers
N_CUSTOMERS = 1000

# Create customer IDs
customer_ids = [
    f"C{str(i).zfill(4)}"
    for i in range(1, N_CUSTOMERS + 1)
]

# Create customer dataset
customers = pd.DataFrame({
    "customer_id": customer_ids,

    "customer_tenure_days": np.random.randint(
        30, 1500, N_CUSTOMERS
    ),

    "previous_success_count": np.random.poisson(
        8, N_CUSTOMERS
    ),

    "previous_failure_count": np.random.poisson(
        2, N_CUSTOMERS
    ),

    "customer_recent_activity": np.random.choice(
        ["low", "medium", "high"],
        size=N_CUSTOMERS,
        p=[0.20, 0.45, 0.35]
    )
})

# Calculate historical recovery rate
customers["historical_recovery_rate"] = (
    customers["previous_success_count"] /
    (
        customers["previous_success_count"]
        + customers["previous_failure_count"]
        + 1
    )
)

# Display first 5 customers
print(customers.head())

# Display dataset size
print("\nDataset shape:")
print(customers.shape)

# Save the dataset
customers.to_csv(
    "data/customers.csv",
    index=False
)

print("\nCustomer dataset saved successfully.")
# -----------------------------------
# Generate payment transactions
# -----------------------------------

N_PAYMENTS = 10000

# Randomly assign customers to payments
payment_customers = np.random.choice(
    customers["customer_id"],
    size=N_PAYMENTS
)

payments = pd.DataFrame({
    "payment_id": [
        f"P{str(i).zfill(5)}"
        for i in range(1, N_PAYMENTS + 1)
    ],

    "customer_id": payment_customers,

    "amount": np.round(
        np.random.lognormal(
            mean=8,
            sigma=1,
            size=N_PAYMENTS
        ),
        2
    ),

    "payment_method": np.random.choice(
        ["card", "upi", "netbanking", "wallet"],
        size=N_PAYMENTS,
        p=[0.40, 0.40, 0.15, 0.05]
    ),

    "hour_of_day": np.random.randint(
        0, 24, N_PAYMENTS
    ),

    "day_of_week": np.random.choice(
        ["Monday", "Tuesday", "Wednesday",
         "Thursday", "Friday", "Saturday", "Sunday"],
        size=N_PAYMENTS
    ),

    "retry_count": np.random.choice(
        [0, 1, 2],
        size=N_PAYMENTS,
        p=[0.65, 0.25, 0.10]
    )
})

print("\nPayment dataset:")
print(payments.head())

print("\nPayment dataset shape:")
print(payments.shape)

# Save payments
payments.to_csv(
    "data/payments.csv",
    index=False
)

print("\nPayment dataset saved successfully.")
# -----------------------------------
# -----------------------------------
# Generate realistic failure information
# -----------------------------------

def generate_failure_reason(payment_method):
    if payment_method == "card":
        return np.random.choice(
            [
                "insufficient_funds",
                "card_declined",
                "incorrect_otp",
                "expired_card",
                "authentication_failed"
            ],
            p=[0.25, 0.25, 0.15, 0.15, 0.20]
        )

    elif payment_method == "upi":
        return np.random.choice(
            [
                "insufficient_funds",
                "bank_error",
                "network_error",
                "authentication_failed"
            ],
            p=[0.25, 0.30, 0.25, 0.20]
        )

    elif payment_method == "netbanking":
        return np.random.choice(
            [
                "bank_error",
                "network_error",
                "authentication_failed"
            ],
            p=[0.40, 0.30, 0.30]
        )

    else:
        return np.random.choice(
            [
                "insufficient_funds",
                "authentication_failed",
                "network_error"
            ],
            p=[0.40, 0.30, 0.30]
        )


# Generate failure reason based on payment method
payments["failure_reason"] = payments["payment_method"].apply(
    generate_failure_reason
)


# Generate failure source based on reason
def generate_failure_source(reason):

    if reason in [
        "insufficient_funds",
        "card_declined",
        "expired_card"
    ]:
        return "issuer"

    elif reason in [
        "bank_error",
        "authentication_failed"
    ]:
        return "bank"

    elif reason == "network_error":
        return "gateway"

    else:
        return "customer"


payments["failure_source"] = payments["failure_reason"].apply(
    generate_failure_source
)


# Generate failure step
def generate_failure_step(reason):

    if reason in [
        "incorrect_otp",
        "authentication_failed"
    ]:
        return "payment_authorization"

    elif reason in [
        "network_error",
        "bank_error"
    ]:
        return "payment_processing"

    else:
        return "payment_authorization"


payments["failure_step"] = payments["failure_reason"].apply(
    generate_failure_step
)


# Generate failure code
def generate_failure_code(source):

    if source == "gateway":
        return "GATEWAY_ERROR"

    elif source == "bank":
        return "BAD_REQUEST_ERROR"

    elif source == "issuer":
        return "BAD_REQUEST_ERROR"

    else:
        return "SERVER_ERROR"


payments["failure_code"] = payments["failure_source"].apply(
    generate_failure_code
)


# Display sample
print("\nRealistic payment failure data:")

print(
    payments[
        [
            "payment_id",
            "payment_method",
            "failure_code",
            "failure_reason",
            "failure_source",
            "failure_step"
        ]
    ].head(10)
)


# Save updated dataset
payments.to_csv(
    "data/payments.csv",
    index=False
)

print("\nRealistic payment dataset saved successfully.")
# -----------------------------------
# Merge customer history with payments
# -----------------------------------

payments = payments.merge(
    customers,
    on="customer_id",
    how="left"
)

print("\nMerged payment + customer data:")

print(
    payments[
        [
            "payment_id",
            "customer_id",
            "amount",
            "payment_method",
            "failure_reason",
            "previous_success_count",
            "previous_failure_count",
            "historical_recovery_rate",
            "customer_recent_activity"
        ]
    ].head()
)

print("\nMerged dataset shape:")
print(payments.shape)

# Save final merged dataset
payments.to_csv(
    "data/payments.csv",
    index=False
)

print("\nMerged payment dataset saved successfully.")
# -----------------------------------
# -----------------------------------
# Generate recovery outcome
# -----------------------------------

# Start with customer's historical recovery behaviour
recovery_score = (
    payments["historical_recovery_rate"] * 0.50
)


# Customer recent activity
recovery_score += (
    payments["customer_recent_activity"]
    .map({
        "high": 0.12,
        "medium": 0.04,
        "low": -0.08
    })
)


# Failure reason impact
recovery_score += (
    payments["failure_reason"]
    .map({
        "insufficient_funds": 0.12,
        "incorrect_otp": 0.10,
        "network_error": 0.06,
        "bank_error": 0.00,
        "authentication_failed": -0.06,
        "card_declined": -0.10,
        "expired_card": -0.14
    })
)


# Retry history
recovery_score -= (
    payments["retry_count"] * 0.10
)


# Very large payments are slightly harder to recover
recovery_score -= (
    payments["amount"] > 15000
).astype(int) * 0.05


# Add realistic randomness
noise = np.random.normal(
    loc=0,
    scale=0.08,
    size=len(payments)
)

recovery_score += noise


# Keep score between 0 and 1
recovery_score = recovery_score.clip(0, 1)


# Convert recovery probability into actual outcome
payments["recovered"] = (
    np.random.random(len(payments)) < recovery_score
).astype(int)


# Save final dataset
payments.to_csv(
    "data/payments.csv",
    index=False
)


print("\nRecovery outcome generated.")

print(
    payments["recovered"].value_counts()
)

print("\nRecovery rate:")
print(
    payments["recovered"].mean()
)

print("\nFinal dataset shape:")
print(payments.shape)

# Dataset sanity checks
# -----------------------------------

print("\n--- DATASET SANITY CHECK ---")

# Missing values
print("\nMissing values:")
print(payments.isnull().sum())

# Duplicate payment IDs
print("\nDuplicate payment IDs:")
print(payments["payment_id"].duplicated().sum())

# Amount statistics
print("\nPayment amount statistics:")
print(payments["amount"].describe())

# Recovery distribution
print("\nRecovery distribution:")
print(payments["recovered"].value_counts())

# Recovery rate
print("\nOverall recovery rate:")
print(payments["recovered"].mean())