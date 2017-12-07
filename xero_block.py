from datetime import datetime, timedelta
from xero import Xero
from xero.auth import PrivateCredentials

from nio import Block
from nio.signal.base import Signal
from nio.properties import VersionProperty, ObjectProperty, StringProperty, \
    PropertyHolder, FloatProperty, IntProperty


class LineItems(PropertyHolder):
    description = StringProperty(title='Line Item Description',
                                 default='Invoice Description')
    quantity = IntProperty(title='Quantity', default=1)
    unit_amount = FloatProperty(title='Unit Amount', default='{{ $amount }}')
    tax_amount = FloatProperty(title='Tax Amount', default='{{ $sales_tax }}')


class XeroPut(Block):

    version = VersionProperty('0.1.0')
    consumer_key = StringProperty(title='Xero Consumer Key',
                                  default='[[XERO_CONSUMER_KEY]]',
                                  allow_none=False)

    # status = StringProperty(title='Invoice Status', default='SUBMITTED')
    contact_name = StringProperty(title='Contact Name (Stripe customerID)',
                                  default='{{ $customer }}')
    invoice_type = StringProperty(title='Invoice Type',
                          default='ACCREC',
                          allow_none=False)
    line_items = ObjectProperty(LineItems,
                              title='Invoice Line Item',
                              default={})

    def __init__(self):
        self.xero = None
        self.credentials = None
        super().__init__()

    def configure(self, context):
        super().configure(context)

        con_key = self.consumer_key()
        with open('blocks/xero/privatekey.pem') as keyfile:
            rsa_private_key = keyfile.read()

        self.credentials = PrivateCredentials(con_key, rsa_private_key)
        self.xero = Xero(self.credentials)

    def start(self):
        super().start()

    def process_signals(self, signals):
        print('')
        print('@@@@@@')
        print(self.line_items().unit_amount(signals[0]))
        print('@@@@@@')
        print('')
        for signal in signals:
            invoice_resp_signal = self.xero.invoices.put({
                'Type': self.invoice_type(signal),                          # ACCREC
                # TODO: Should this be hardcoded? Or do we want ACCPAY option?
                'Contact': {
                    'Name': self.contact_name(signal)                       # Stripe customer ('cus_000...')
                },
                'DueDate': datetime.utcnow() + timedelta(days=30),
                'LineItems': [{
                    'Description': self.line_items().description(signal),
                    'Quantity': self.line_items().quantity(signal),
                    'UnitAmount': self.line_items().unit_amount(signal),
                    'TaxAmount': self.line_items().tax_amount(signal),
                    'TaxType': 'NONE',
                    'AccountCode': 310                                      # SVB account
                }],
                'Status': 'SUBMITTED'
            })

            manual_journal_resp_signal_1 = self.xero.manualjournals.put({
                'Narration': self.line_items().description(signal),
                'JournalLines': [{
                    'LineAmount': self.line_items().unit_amount(signal),    # + debited subtotal
                    'AccountCode': 210                                      # receivables account
                },
                {
                    'LineAmount': self.line_items().unit_amount(signal)*-1, # - credited subtotal
                    'AccountCode': 210                                      # stripe clearing account
                }]
            })

            manual_journal_resp_signal_2 = self.xero.manualjournals.put({
                'Narration': self.line_items().description(signal),
                'JournalLines': [{
                    'LineAmount': self.line_items().unit_amount(signal),      # + debited subtotal
                    'AccountCode': 220                                      # stripe clearing account
                },
                {
                    'LineAmount': self.line_items().unit_amount(signal)*-1,   # - credited subtotal
                    'AccountCode': 220                                      # unearned revenue account
                }]
            })

        self.notify_signals([Signal(invoice_resp_signal[0]),
                             Signal(manual_journal_resp_signal_1[0]),
                             Signal(manual_journal_resp_signal_2[0])])
