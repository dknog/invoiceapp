"""Various testing utilities."""
import random
import requests
import string

from datetime import datetime, timedelta


def fetch_invoice(url):
    """Fetch the invoice to generate a receipt number."""
    response = requests.get(url)
    response.raise_for_status()


def generate_random_email(domain="test.dknog.dk"):
    """Generate a random email address."""
    length = 7
    username = "".join(random.choices(string.ascii_lowercase, k=length))
    return f"{username}@{domain}"


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
