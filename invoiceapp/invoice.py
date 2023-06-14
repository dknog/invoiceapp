"""Invoice Views."""
from flask import Blueprint, current_app, render_template

from invoiceapp.custom_wkhtmltopdf import Wkhtmltopdf

from invoiceapp.payments import (
    StripeInvoice,
    CustomerNotFoundException,
    ChargeNotFoundException,
)
from invoiceapp import settings

blueprint = Blueprint("invoice", __name__)


@blueprint.route("/")
def index():
    """Render front page."""
    return render_template("index.html")


@blueprint.route("/receipt", methods=["POST"])
def receipt():
    stripe = StripeInvoice(settings.STRIPE_API_KEY)
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


@blueprint.route("/pdf/<email>/<receipt_number>")
def pdfreceipt(email, receipt_number):
    wkhtmltopdf = Wkhtmltopdf(current_app)
    stripe = StripeInvoice(stripe_key)
    receipt = stripe.generate_receipt(email, receipt_number)

    return wkhtmltopdf.render_template_to_pdf(
        "receipt.html",
        receipt=receipt,
        pdf=True,
    )
