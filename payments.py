#!/usr/bin/env python
import stripe
from datetime import datetime
from iso3166 import countries


class CustomerNotFoundException(Exception):
    pass


class ChargeNotFoundException(Exception):
    pass


class StripeInvoice(object):
    """ Class to fetch invoice data from stripe, given receipt number and email address """

    def __init__(self, stripe_key):
        stripe.api_key = stripe_key


    def find_customer(self, email):
        return stripe.Customer.list(email=email)

    def lookup_customer(self, id):
        return stripe.Customer.retrieve(id)

    def find_payments(self, customer_id):
        return stripe.Charge.list(customer=customer_id)

    def find_charge_by_receipt(self, charges, receipt_number):
        relevant_charge = None
        for charge in charges['data']:
            if charge['receipt_number'] == receipt_number:
                relevant_charge = charge
                break

        return relevant_charge

    def generate_receipt(self, email, receipt_number):
        """ Generate a receipt based on email address and the receipt number"""
        customers = self.find_customer(email)
        customer_ids = []
        for customer in customers['data']:
            customer_ids.append(customer['id'])

        charge = None
        receipt = {}

        if len(customer_ids) > 0:
            for customer_id in customer_ids:
                charges = self.find_payments(customer_id)
                charge = self.find_charge_by_receipt(charges, receipt_number)
                if charge is not None:
                    country = countries.get(charge['billing_details']['address']['country'])
                    receipt['amount'] = charge['amount'] / 100
                    receipt['currency'] = charge['currency']
                    receipt['timestamp'] = datetime.fromtimestamp(charge['created'])
                    receipt['charge'] = charge
                    receipt['country'] = country.name
                    receipt['email'] = email
                    receipt['receipt_number'] = receipt_number

                    break

        else:
            raise CustomerNotFoundException('Customer Not Found')

        if len(receipt) == 0:
            raise ChargeNotFoundException('No charge could be found')

        return receipt
