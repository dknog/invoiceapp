import os
from flask import Flask, render_template, request, abort
from payments import (
    StripeInvoice,
    CustomerNotFoundException,
    ChargeNotFoundException,
)
from dotenv import load_dotenv
from flask_wkhtmltopdf import Wkhtmltopdf


APP_ROOT = os.path.dirname(__file__)
dotenv_path = os.path.join(APP_ROOT, ".env")
load_dotenv(dotenv_path)

app = Flask(__name__)
app.config["WKHTMLTOPDF_BIN_PATH"] = os.getenv("WKHTMLTOPDF_BIN_PATH")
app.config["PDF_DIR_PATH"] = os.path.join(APP_ROOT, "static", "pdf")
app.config["SITE_URL"] = os.getenv("SITE_URL")
wkhtmltopdf = Wkhtmltopdf(app)

stripe_key = os.getenv("STRIPE_KEY")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/receipt", methods=["POST"])
def receipt():
    stripe = StripeInvoice(stripe_key)
    email = request.form.get("email", None)
    if email is None:
        # TODO Proper error handling
        abort(401)
    receiptid = request.form.get("receiptid", None)
    if receiptid is None:
        # TODO Proper error handling
        abort(401)

    try:
        receipt = stripe.generate_receipt(email, receiptid)
    except (CustomerNotFoundException, ChargeNotFoundException):
        return render_template("error.html")

    return render_template(
        "receipt.html", download=True, save=False, receipt=receipt, pdf=False
    )


@app.route("/pdf/<email>/<receipt_number>")
def pdfreceipt(email, receipt_number):
    stripe = StripeInvoice(stripe_key)
    receipt = stripe.generate_receipt(email, receipt_number)

    return wkhtmltopdf.render_template_to_pdf(
        "receipt.html",
        receipt=receipt,
        pdf=True,
    )
