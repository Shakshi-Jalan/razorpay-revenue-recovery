# -----------------------------------
# Mock Razorpay Payment Link Adapter
# -----------------------------------

import uuid
from datetime import datetime


def create_payment_link(payment_id, amount, customer_id=None):
    """
    Simulates a Razorpay Payment Link API response.

    No real Razorpay API call is made.
    The response structure is designed to mirror
    the fields used by the real Payment Link workflow.
    """

    payment_link_id = f"plink_test_{uuid.uuid4().hex[:12]}"

    short_url = (
        f"https://rzp.io/i/mock_{payment_link_id[-8:]}"
    )

    response = {
        "id": payment_link_id,
        "entity": "payment_link",
        "amount": int(round(amount * 100)),
        "currency": "INR",
        "status": "created",
        "short_url": short_url,
        "reference_id": payment_id,
        "customer_id": customer_id,
        "created_at": datetime.now().isoformat()
    }

    return response


# -----------------------------------
# Test
# -----------------------------------

if __name__ == "__main__":

    response = create_payment_link(
        payment_id="P00001",
        amount=5000,
        customer_id="C0001"
    )

    print("\n--- MOCK PAYMENT LINK ---")
    print(response)