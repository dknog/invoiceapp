"""Test Payments."""

import stripe

from invoiceapp.payments import StripeInvoice


def test_stripe_api_base():
    """Test that the API can be reached."""
    balance = stripe.Balance.retrieve()
    assert len(balance) > 0


def test_invoice(api_key, customer_email, receipt_id):
    """Test the invoice generation."""
    invoice = StripeInvoice(api_key)
    receipt = invoice.generate_receipt(customer_email, receipt_id)
    assert len(receipt) > 0
    assert receipt["amount"] == 800.0
    assert receipt["currency"] is not None
    assert receipt["timestamp"] is not None
    assert receipt["charge"] is not None
    assert receipt["country"] == "Denmark"
    assert receipt["receipt_number"] == receipt_id


def test_request_receipt(client, customer_email, receipt_id):
    """Test whether a receipt can be requested."""
    response = client.post(
        "/receipt",
        data={
            "email": customer_email,
            "receiptid": receipt_id,
        },
    )
    assert response.status_code == 200

    assert (
        "<td></td><td></td><td>Subtotal</td><td></td><td>800.0</td>\n"
        in response.text
    )


def test_pdf_generation(client, customer_email, receipt_id):
    """Test whether a PDF file can be generated."""
    response = client.get(f"/pdf/{customer_email}/{receipt_id}")

    assert response.status_code == 200


def test_address_override(client, customer_email, receipt_id):
    """Test whether the address override works."""
    response = client.post(
        "/receipt",
        data={
            "email": customer_email,
            "receiptid": receipt_id,
            "recipientname": "Test Surnameson",
            "recipientaddress": "Test Road 5\r\nTestville",
            "recipientcountry": "Norway",
        },
    )

    assert "Test Road 5<br>Testville" in response.text
