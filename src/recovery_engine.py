from datetime import datetime


# -----------------------------------
# Recovery Decision Engine
# -----------------------------------

def decide_action(row):

    retry_count = int(row["retry_count"])
    priority = row["recovery_priority"]
    confidence = row["confidence"]

    # STOPPING RULE
    if retry_count >= 2:
        return "STOP"

    # HIGH VALUE + HIGH CONFIDENCE
    if priority == "High" and confidence == "High":
        return "GENERATE_PAYMENT_LINK"

    # HIGH VALUE + LOW CONFIDENCE
    if priority == "High" and confidence == "Low":
        return "HUMAN_REVIEW"

    # MEDIUM VALUE + ACCEPTABLE CONFIDENCE
    if (
        priority == "Medium"
        and confidence in ["High", "Medium"]
    ):
        return "GENERATE_PAYMENT_LINK"

    # LOW VALUE OR OTHER CASE
    return "STOP"


# -----------------------------------
# Execute Recovery Action
# -----------------------------------

def execute_recovery_action(row):

    action = decide_action(row)

    timestamp = datetime.now().isoformat()

    if action == "GENERATE_PAYMENT_LINK":

        return {
            "payment_id": row["payment_id"],
            "action": action,
            "status": "APPROVED",
            "timestamp": timestamp,
            "reason": (
                "Recovery opportunity is suitable "
                "for automated customer recovery"
            )
        }

    elif action == "HUMAN_REVIEW":

        return {
            "payment_id": row["payment_id"],
            "action": action,
            "status": "PENDING",
            "timestamp": timestamp,
            "reason": (
                "High-value opportunity but "
                "model confidence is low"
            )
        }

    else:

        return {
            "payment_id": row["payment_id"],
            "action": "STOP",
            "status": "BLOCKED",
            "timestamp": timestamp,
            "reason": (
               "Recovery attempt limit reached or "
            "recovery opportunity is not suitable"
            )
        }


# -----------------------------------
# Test
# -----------------------------------

if __name__ == "__main__":

    print("Recovery Engine loaded successfully.")

    print("\nAvailable actions:")
    print("1. GENERATE_PAYMENT_LINK")
    print("2. HUMAN_REVIEW")
    print("3. STOP")

    print("\nStopping rule:")
    print("Maximum recovery attempts = 2")