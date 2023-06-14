"""Fixtures and other supporting functions."""
import os
import pytest
import stripe

from dotenv import load_dotenv

from .utils import fetch_invoice, generate_card, generate_random_email

from invoiceapp.app import create_app


def generate_payment_method(email):
    """Generate a payment method."""
    pm = stripe.PaymentMethod.create(
        type="card",
        billing_details={
            "name": "Test User",
            "email": email,
            "address": {"country": "DK"},
        },
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
def charge(customer):
    """Set up a payment and return the Charge object."""
    payment_method = generate_payment_method(customer["email"])
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


@pytest.fixture
def app():
    """Get the flask app."""
    return create_app()


@pytest.fixture
def client(app):
    return app.test_client()
