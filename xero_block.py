import json
from xero import Xero
from xero.auth import PrivateCredentials

from nio import Block
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
        self.xero = None
        self.credentials = None
        super().__init__()

    def configure(self, context):
        super().configure(context)
        print('@@@@@@@@@@@')
        print('CONFIGURE')
        print('@@@@@@@@@@@')
        # json_dict = {}
        con_key = "BHLXMHJQPUUBM8ZKVBJCQLKTN860JE"
        rsa_private_key = '-----BEGIN RSA PRIVATE KEY-----\nMIICXgIBAAKBgQC5zDwUVG6XvG8QJJ3TIj66JfmIrHWLeCqiTMleF7R2/SbVVynX\neS5v59yEGccfIArsuG9sHWczizvMSa31JJCPdvyRCXm06n4dTSXABSFZ6rQsjeJI\n3tvEuxNCvvZYRjwk1NWpaYPSslx25CE/Bh8M5Np6IwvtlwcG+6lRj8UFwwIDAQAB\nAoGBAI7EoDni8yRHmHQoHtpZSygQ/CEInD4ydVhHdsiFoJd6STfQBYfcR1GYMfuU\nL0z8e0iRJJVINsAFskp1J2Xi1e0GsunwNaBV6npOFjP/Ta2C1BIqRClW1IR/gmCk\nuX9sBb6Edg+xDriQyIckhbR4eivj0FQprZvl4XbdfP8UDkABAkEA8ksbWWrn9i4M\n2bdv9MVBKltFl4mVBJdhGnCwPE1sscLGLmXgS546hGV1/Ok5UtK8yKoYe8ViMWsS\nuvzFKzjlwwJBAMRO9WURd3eqkI/6LgRiejhGNc+NefOaolj6iVLwuAaKu3LKWjwg\nV19dp7AArFORQ39+ermnUPG/0cq0/orhYAECQQCamXPs/TrfKQkIDnUAULDA7xYb\nmC0ejdzmuwqon5qAXlCIIHcaqO6btgWwB7yM7WyJ+Ya/yvVZpQGBkHHan2ZzAkAg\nD0EWW27mVS28xb/kKW0KabT6C4HiHdvrqibpK7TyJJAOZCuubB24zmPHY6TBFRUv\n6ikCzudyQ8BwWXTEm6ABAkEAkJhnQujZd5qBiEfR1gdNApqQQ8SrVE2gNDUNsb3/\nqpAP6WlWybok798iPoBzMWJdPpXaZe8V1oe/1/cB3S1Z8A==\n-----END RSA PRIVATE KEY-----\n'
        self.credentials = PrivateCredentials(con_key, rsa_private_key)
        self.xero = Xero(self.credentials)
        # json_dict['Type'] = self.invoice_type()
        # json_dict['Contact'] = {'Name': self.contact_name()}
        # json_dict['LineItems'] = {
        #     'Description': self.line_items().description(),
        #     'UnitAmount': self.line_items().unit_amount(),
        #     'TaxAmount': self.line_items().tax_amount()
        # }
        # json_dict['Status'] = self.status()

        # self.json = json.loads(json_dict)
        resp_signal = self.xero.invoices.put({
            'Type': 'ACCREC',
            'Contact': {
                'Name': 'Kevin Force'
            },
            'LineItems': [{
                'Description': 'Force Description',
                'Quantity': 4,
                'UnitAmount': 9.99,
                'TaxAmount': 1.11
            }]
        })
        print('%%%%%%%%%%')
        print(resp_signal)
        print('%%%%%%%%%%')

    def start(self):
        super().start()
        # self.xero = Xero(self.credentials)
        print('&&&&&&&&&&')
        print('START')
        print('&&&&&&&&&&')

    def process_signals(self, signals):
        print('!!!!!!!!!!')
        print('PROCESS_SIGNALS')
        print('!!!!!!!!!!')
        json_dict = {}
        for signal in signals:
            pass
        # self.notify_signals(resp_signal)


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
