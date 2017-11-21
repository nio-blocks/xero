import json
from xero import Xero
from xero.auth import PrivateCredentials

from nio.block.base import Block
from nio.properties import VersionProperty, ObjectProperty, StringProperty, \
    PropertyHolder, FloatProperty


class LineItems(PropertyHolder):
    description = StringProperty(title='Line Item Description',
                                 default='Invoice Description')
    unit_amount = StringProperty(title='Unit Amount', default='{{ $amount }}')
    tax_amount = StringProperty(title='Tax Amount', default='{{ $sales_tax }}')


class XeroPut(Block):

    version = VersionProperty('0.1.0')
    consumer_key = StringProperty(title='Xero Consumer Key',
                                  default='[[XERO_CONSUMER_KEY]]',
                                  allow_none=False)
    rsa_key = StringProperty(title='RSA Private Key',
                             default='[[RSA_PRIVATE_KEY]]',
                             allow_none=False)

    # Required Parameter for creating new invoice
    # TODO: Modify defaults to sync with Stripe Payment Received output
        # Any other properties to pass along?
        # Easier to have just one kwargs field? Input pre-formatted incoming signal dict?
    # sales_amount = FloatProperty(title='Sales Amount',
    #                              default='{{ $sales_amount }}')
    # sales_tax = FloatProperty(title='Sales Tax',
    #                              default='{{ $sales_tax }}')
    status = StringProperty(title='Invoice Status', default='PAID')
    contact_name = StringProperty(title='Contact Name',
                                  default='{{ $contact_name }}')
    invoice_type = StringProperty(title='Invoice Type',
                          default='ACCREC',
                          allow_none=False)
    line_items = ObjectProperty(LineItems, title='Invoice Line Item')

    def __init__(self):
        super().__init__()
        self.xero = None
        self.json = None

    def start(self):
        credentials = PrivateCredentials(self.consumer_key(), self.rsa_key())
        self.xero = Xero(credentials)

    def process_signals(self, signals):
        json_dict = {}
        for signal in signals:
            json_dict['Type'] = self.invoice_type(signal)
            json_dict['Contact'] = {'Name': self.contact_name(signal)}
            json_dict['LineItems'] = {
                'Description': self.line_items().description(signal),
                'UnitAmount': self.line_items().unit_amount(signal),
                'TaxAmount': self.line_items().tax_amount(signal)
            }
            json_dict['Status'] = self.status(signal)

            # self.json = json.loads(json_dict)
            resp_signal = self.xero.invoices.put(json_dict)
        self.notify_signals(resp_signal)

# "Private Application"
    # Generate RSA bs and create key in app.xero.com
    # use keys from Xero to make reqs
    # store generated RSA key as a string for reference (don't upload to github)

# PUT req block - will create new invoice
    # use xero.invoices.put({json})

# Follow facebook_post_block
    # no rest_polling mixin
    # no driver needed; input signal from Stripe will drive

# Need OAuth or just access token?
    # create access token in API

# NEED:
    # Create invoice in Xero
    # Update Stripe clearing account in Xero
    # Update SVB account in Xero
    # Update Revenue in Xero

# Questions:
    # How will Stripe & Xero be linked?  Customer name? email?
