"""Webapp settings."""

import os
from environs import Env

env = Env()
env.read_env()

ENV = env.str("FLASK_ENV", default="production")

STRIPE_API_KEY = env.str("STRIPE_KEY")

SITE_URL = env.str("SITE_URL")

WKHTMLTOPDF_BIN_PATH = env.str("WKHTMLTOPDF_BIN_PATH")

PDF_DIR_PATH = os.path.join(os.path.dirname(__file__), "static", "pdf")
