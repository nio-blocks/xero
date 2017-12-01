import json
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

    # status = StringProperty(title='Invoice Status', default='PAID')
    contact_name = StringProperty(title='Customer(Contact) Name',
                                  default='{{ $customer_name }}')
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
        for signal in signals:
            invoice_resp_signal = self.xero.invoices.put({
                'Type': self.invoice_type(signal),
                # TODO: add status for created/paid/authorized or whatever
                # TODO: add 'reference'
                'Contact': {
                    'Name': self.contact_name(signal)
                },
                'LineItems': [{
                    'Description': self.line_items().description(signal),
                    'Quantity': self.line_items().quantity(signal),
                    'UnitAmount': self.line_items().unit_amount(signal),
                    'TaxAmount': self.line_items().tax_amount(signal)
                }]
            })

            # invoice created (2 journal entries):
                # journal lines (1st):
                    # 1: receivables account debited subtotal
                    # 2: stripe clearing account credited subtotal
                # journal lines (2nd):
                    # 1: debits stripe clearing account
                    # 2: credits unearned revenue account

            # **invoice needs to be approved before it can be paid**

            # invoice paid:
                # update corresponding invoice
                    # send amount paid, date paid, account paid to (SVB), reference (stripe payment)
                # journal lines:
                    # 1: debit cash
                    # 2: credit receivables
                    # 3: debit Fees CC
                # journal lines:
                    # 1: debit unearned revue
                    # 2: credit receivables
                    # 3: credit Taxes payable

            manual_journal_resp_signal = self.xero.manualjournals.put({
                # TODO: What should LineAmount equal?
                    # sum of LineAmounts needs to = 'total credits'
                'Narration': self.line_items().description(signal),
                'JournalLines': [{
                    'LineAmount': self.line_items().unit_amount(signal),
                    'AccountCode': 210
                    # TODO: Signify if its a debit or credit?
                },
                {
                    'LineAmount': self.line_items().unit_amount(signal)*-1,
                    'AccountCode': 210
                }]
            })

        self.notify_signals([Signal(invoice_resp_signal[0]),
                             Signal(manual_journal_resp_signal[0])])
