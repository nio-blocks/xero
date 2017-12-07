import json
from xero import Xero
from xero.auth import PrivateCredentials

from nio import Block
from nio.signal.base import Signal
from nio.properties import VersionProperty, ObjectProperty, StringProperty, \
    PropertyHolder, FloatProperty, IntProperty


class XeroUpdate(Block):

    version = VersionProperty('0.1.0')
    consumer_key = StringProperty(title='Xero Consumer Key',
                                  default='[[XERO_CONSUMER_KEY]]',
                                  allow_none=False)

    # status = StringProperty(title='Invoice Status', default='PAID')
    contact_name = StringProperty(title='Contact Name (Stripe customerID)',
                                  default='{{ $customer }}')
    description = StringProperty(title='Transaction Description',
                                 default='Description')
    payment_amount = FloatProperty(title='Amount Paid', default='{{ $amount }}')

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
            invoice_resp_signal = self.xero.invoices.filter(
                Contact_Name=self.contact_name(signal),
                Status='AUTHORISED',
                order='UpdatedDateUTC DESC')[0]

            invoice_id = invoice_resp_signal['InvoiceID']
            invoice_subtotal = invoice_resp_signal['Subtotal']
            invoice_tax = invoice_resp_signal['TotalTax']
            invoice_total = invoice_resp_signal['Total']

            self.xero.payments.put({
                'Invoice': {
                    'InvoiceID': invoice_id
                },
                'Account': {
                    'Code': 310
                },
                'Amount': self.payment_amount(signal)
            })

            manual_journal_resp_signal_1 = self.xero.manualjournals.put({
                'Narration': self.description(signal),
                'JournalLines': [{
                    'LineAmount': invoice_total,
                    'AccountCode': 210                                      # cash account
                },
                {
                    'LineAmount': invoice_total*-1,                         # receivables account
                    'AccountCode': 210
                }]
            })

            manual_journal_resp_signal_2 = self.xero.manualjournals.put({
                'Narration': self.description(signal),
                'JournalLines': [{
                    'LineAmount': invoice_total,
                    'AccountCode': 210                                      # unearned revenue account
                },
                {
                    'LineAmount': invoice_subtotal*-1,
                    'AccountCode': 210                                      # revenue receivables
                },
                {
                    'LineAmount': invoice_tax*-1,
                    'AccountCode': 210                                      # taxes payable amount
                }]
            })

            manual_journal_resp_signal_3 = self.xero.manualjournals.put({
                'Narration': self.description(signal),
                'JournalLines': [{
                    'LineAmount': invoice_subtotal*0.29 + 0.30,
                    'AccountCode': 210                                      # fees CC account
                },
                {
                    'LineAmount': (invoice_subtotal*0.29 + 0.30)*-1,        # cash account
                    'AccountCode': 210
                }]
            })

        self.notify_signals([Signal(invoice_resp_signal[0]),
                             Signal(manual_journal_resp_signal_1[0]),
                             Signal(manual_journal_resp_signal_2[0]),
                             Signal(manual_journal_resp_signal_3[0])])
