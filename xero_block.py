import json
from xero import Xero
from xero.auth import PrivateCredentials

from nio import Block
from nio.signal.base import Signal
from nio.properties import VersionProperty, ObjectProperty, StringProperty, \
    PropertyHolder, FloatProperty


# class LineItems(PropertyHolder):
#     description = StringProperty(title='Line Item Description',
#                                  default='Invoice Description')
#     unit_amount = FloatProperty(title='Unit Amount', default='{{ $amount }}')
#     tax_amount = FloatProperty(title='Tax Amount', default='{{ $sales_tax }}')


class XeroPut(Block):

    # version = VersionProperty('0.1.0')
    # consumer_key = StringProperty(title='Xero Consumer Key',
    #                               default='[[XERO_CONSUMER_KEY]]',
    #                               allow_none=False)
    # rsa_key = StringProperty(title='RSA Private Key',
    #                          default='[[RSA_PRIVATE_KEY]]',
    #                          allow_none=False)

    # TODO: Modify defaults to sync with Stripe Payment Received output
        # What other properties wanting to pass along?
        # Easier to have just one kwargs field? Input pre-formatted incoming signal dict?

    # status = StringProperty(title='Invoice Status', default='PAID')
    # contact_name = StringProperty(title='Contact Name',
    #                               default='{{ $contact_name }}')
    # invoice_type = StringProperty(title='Invoice Type',
    #                       default='ACCREC',
    #                       allow_none=False)
    # line_items = ObjectProperty(LineItems, title='Invoice Line Item')

    def __init__(self):
        self.xero = None
        self.credentials = None
        super().__init__()

    def configure(self, context):
        super().configure(context)
        # json_dict = {}
        con_key = "3L3FFYWBR1AK83EOLI9JUWOXWEMSHF"
        with open('blocks/xero/privatekey.pem') as keyfile:
            rsa_private_key = keyfile.read()

        self.credentials = PrivateCredentials(con_key,
                                              rsa_private_key)
        self.xero = Xero(self.credentials)

    def start(self):
        super().start()

    def process_signals(self, signals):
        for signal in signals:
            resp_signal = self.xero.invoices.put({
                'Type': 'ACCREC',
                'Contact': {
                    'Name': 'Kevin Cowley'
                },
                'LineItems': [{
                    'Description': 'Desc',
                    'Quantity': 1,
                    'UnitAmount': 9.99,
                    'TaxAmount': 1.11
                }]
            })
            # TODO: ALSO NEEDS TO ADD A JOURNAL ENTRY FOR SIGNAL
            
        self.notify_signals([Signal(resp_signal[0])])


# TODO: Turn this into a base block?

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
