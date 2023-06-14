"""Test Payments."""

import os
import random
import requests
import pytest
import string
import stripe

from datetime import datetime, timedelta
from dotenv import load_dotenv

from invoiceapp.payments import StripeInvoice


def generate_random_email(domain="test.dknog.dk"):
    """Generate a random email address."""
    length = 7
    username = "".join(random.choices(string.ascii_lowercase, k=length))
    return f"{username}@{domain}"


def fetch_invoice(url):
    """Fetch the invoice to generate a receipt number."""
    response = requests.get(url)
    response.raise_for_status()


def generate_card():
    """Generate a test credit card."""
    today = datetime.today()
    expire = today + timedelta(days=180)
    return {
        "number": "4242424242424242",
        "exp_month": expire.month,
        "exp_year": expire.year,
        "cvc": "314",
    }


@pytest.fixture
def payment_method():
    """Generate a payment method."""
    pm = stripe.PaymentMethod.create(
        type="card",
        billing_details={"address": {"country": "DK"}},
        card=generate_card(),
    )
    return pm


@pytest.fixture
def api_key():
    """Load the API key from environment."""
    APP_ROOT = os.path.dirname(__file__)
    dotenv_path = os.path.join(APP_ROOT, "../.env")
    load_dotenv(dotenv_path)
    api_key = os.getenv("STRIPE_KEY")
    assert api_key is not None
    return api_key


@pytest.fixture(autouse=True)
def setup_stripe(api_key):
    """Register the api key."""
    stripe.api_key = api_key


@pytest.fixture(scope="module")
def customer():
    """Create a test customer."""
    customer = stripe.Customer.create(
        description="User created by pytest test_payments.py",
        email=generate_random_email(),
        address={"country": "DK"},
    )
    yield customer
    customer.delete()


@pytest.fixture
def charge(customer, payment_method):
    """Set up a payment and return the Charge object."""
    payment_intent = stripe.PaymentIntent.create(
        amount=80000,
        currency="dkk",
        automatic_payment_methods={"enabled": True},
        customer=customer,
        description="Payment intent created by pytest test_payments.py",
        payment_method=payment_method,
    )
    result = payment_intent.confirm(
        return_url="https://test.dknog.dk/returnurl"
    )
    assert "charges" in result and len(result["charges"]["data"]) == 1
    return result["charges"]["data"][0]


@pytest.fixture
def receipt_id(charge):
    """Get the receipt ID."""
    # Fetch the receipt to generate a receipt ID
    receipt_url = charge.get("receipt_url", None)
    assert receipt_url is not None
    fetch_invoice(receipt_url)
    charge.refresh()
    receipt_number = charge.get("receipt_number")
    assert receipt_number is not None
    return receipt_number


@pytest.fixture
def customer_email(customer):
    """Get the customer email."""
    return customer.get("email")


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
