import json
from xero import Xero
from xero.auth import PrivateCredentials

from nio import Block
from nio.signal.base import Signal
from nio.properties import VersionProperty, ObjectProperty, StringProperty, \
    PropertyHolder, FloatProperty, IntProperty


class AccountCodes(PropertyHolder):
    cash_code = IntProperty(title='Cash Account Code', default = 300)
    receivables_code = IntProperty(title='Receivables Account Code',
                                   default = 210)
    fees_cc_code = IntProperty(title='Credit Card Fees Account Code',
                                       default=240)
    unearned_code = IntProperty(title='Unearned Revenue Account Code',
                                default=230)
    revenue_receivables_code = IntProperty(
        title='Revenue Receivables Account Code',
        default=250
    )
    taxes_payable_code = IntProperty(title='Taxes Payable Account Code',
                                     default=260)



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
    payment_amount = FloatProperty(title='Amount Paid',
                                   default='{{ $amount }}')
    account_codes = ObjectProperty(AccountCodes,
                                   title='Account Codes',
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
            invoice_resp_signal = self.xero.invoices.filter(
                Contact_Name=self.contact_name(signal),
                Status='AUTHORISED',
                order='UpdatedDateUTC DESC')[0]

            invoice_id = invoice_resp_signal['InvoiceID']
            invoice_subtotal = invoice_resp_signal['SubTotal']
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
                    'AccountCode': self.account_codes().cash_code()
                },
                {
                    'LineAmount': invoice_total*-1,
                    'AccountCode': self.account_codes().receivables_code()
                }]
            })

            manual_journal_resp_signal_2 = self.xero.manualjournals.put({
                'Narration': self.description(signal),
                'JournalLines': [{
                    'LineAmount': invoice_total,
                    'AccountCode': self.account_codes().unearned_code()
                },
                {
                    'LineAmount': invoice_subtotal*-1,
                    'AccountCode': self.account_codes().revenue_receivables_code()
                },
                {
                    'LineAmount': invoice_tax*-1,
                    'AccountCode': self.account_codes().taxes_payable_code()
                }]
            })

            manual_journal_resp_signal_3 = self.xero.manualjournals.put({
                'Narration': self.description(signal),
                'JournalLines': [{
                    'LineAmount': invoice_subtotal*0.29 + 0.30,
                    'AccountCode': self.account_codes().fees_cc_code()
                },
                {
                    'LineAmount': (invoice_subtotal*0.29 + 0.30)*-1,
                    'AccountCode': self.account_codes().cash_code()
                }]
            })

        self.notify_signals([Signal(invoice_resp_signal),
                             Signal(manual_journal_resp_signal_1[0]),
                             Signal(manual_journal_resp_signal_2[0]),
                             Signal(manual_journal_resp_signal_3[0])])
