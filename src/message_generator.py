# -----------------------------------
# Recovery Message Generator
# -----------------------------------

def generate_recovery_message(row):

    failure_reason = row["failure_reason"]
    amount = row["amount"]

    if failure_reason == "expired_card":
        reason_text = "your card appears to have expired."

    elif failure_reason == "insufficient_funds":
        reason_text = "there were insufficient funds to complete the payment."

    elif failure_reason == "card_declined":
        reason_text = "your card payment was declined by the issuing bank."

    elif failure_reason == "incorrect_otp":
        reason_text = "the OTP verification was unsuccessful."

    elif failure_reason == "authentication_failed":
        reason_text = "the payment authentication could not be completed."

    elif failure_reason == "bank_error":
        reason_text = "your bank was unable to complete the payment."

    elif failure_reason == "network_error":
        reason_text = "a temporary network issue interrupted the payment."

    else:
        reason_text = "the payment could not be completed."


    message = f"""
Hi,

Your recent payment of ₹{amount:,.2f} could not be completed because {reason_text}

You can complete the payment using the secure payment link provided below.

If you have already completed the payment, please ignore this message.

Thank you.
"""

    return message.strip()


# -----------------------------------
# Test
# -----------------------------------

if __name__ == "__main__":

    test_payment = {
        "failure_reason": "insufficient_funds",
        "amount": 5000
    }

    print("Generated recovery message:\n")

    print(
        generate_recovery_message(test_payment)
    )