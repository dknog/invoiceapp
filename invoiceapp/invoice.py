"""Invoice Views."""
from flask import Blueprint, current_app, render_template, request, abort

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

    recipient = {
        "name": receipt["charge"]["billing_details"]["name"],
        "address": [receipt["charge"]["billing_details"]["email"]],
        "country": receipt["country"],
        "email": email,
        "receiptid": receiptid,
    }

    if override_name := request.form.get("recipientname", None):
        recipient["name"] = override_name

    if override_address := request.form.get("recipientaddress", None):
        current_app.logger.info(repr(override_address))
        address_lines = str(override_address).splitlines()
        recipient["address"] = address_lines

    if override_country := request.form.get("recipientcountry", None):
        recipient["country"] = override_country

    current_app.logger.info("Recipient: %r", recipient)

    return render_template(
        "receipt.html",
        download=True,
        save=False,
        receipt=receipt,
        pdf=False,
        recipient=recipient,
    )


@blueprint.route("/pdf/<email>/<receipt_number>")
def pdfreceipt(email, receipt_number):
    wkhtmltopdf = Wkhtmltopdf(current_app)
    stripe = StripeInvoice(settings.STRIPE_API_KEY)
    receipt = stripe.generate_receipt(email, receipt_number)
    charge_address = [receipt["charge"]["billing_details"]["email"]]
    recipient = {
        "name": request.args.get(
            "name", receipt["charge"]["billing_details"]["name"]
        ),
        "address": request.args.getlist("address"),
        "country": request.args.get("country", receipt["country"]),
    }
    if not recipient["address"]:
        recipient["address"] = charge_address

    return wkhtmltopdf.render_template_to_pdf(
        "receipt.html",
        receipt=receipt,
        recipient=recipient,
        pdf=True,
    )
