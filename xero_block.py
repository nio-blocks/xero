from datetime import datetime, timedelta
from xero import Xero
from xero.auth import PrivateCredentials

from nio.block.base import Block
from nio.signal.base import Signal
from nio.properties import (StringProperty, PropertyHolder, Property,
                            ListProperty, VersionProperty, IntProperty,
                            FloatProperty, ObjectProperty)


class JournalLines(PropertyHolder):
    line_amount = Property(default='{{ $amount }}', title='Line Amount')
    account_code = Property(default=100, title='Account Code')
    line_description = Property(default='Description', title='Description')


class ManualJournals(PropertyHolder):
    narration = StringProperty(default='Narration', title="Narration")
    journal_lines = ListProperty(JournalLines, title='Journal Lines', default=[])


class LineItems(PropertyHolder):
    description = StringProperty(title='Line Item Description',
                                 default='Invoice Description')
    quantity = IntProperty(title='Quantity', default=1)
    unit_amount = FloatProperty(title='Unit Amount', default='{{ $amount }}')
    tax_amount = FloatProperty(title='Tax Amount', default='{{ $sales_tax }}')
    invoice_type = StringProperty(title='Invoice Type',
                                  default='ACCREC',
                                  allow_none=False)
    invoice_account_code = IntProperty(title='Invoice Account Code',
                                       default=100)


class XeroDev(Block):

    manual_journal_entries = ListProperty(ManualJournals,
                                          title='Manual Journal Entries',
                                          default=[])
    line_items = ObjectProperty(LineItems,
                              title='Invoice Line Item',
                              default={})
    version = VersionProperty('0.1.0')
    consumer_key = StringProperty(title='Xero Consumer Key',
                                  default='[[XERO_CONSUMER_KEY]]',
                                  allow_none=False)
    contact_name = StringProperty(title='Contact Name (Stripe customerID)',
                                  default='{{ $customer }}')

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
        response_signal = []
        for signal in signals:
            response_signal.append(Signal(self.xero.invoices.put({
                'Type': self.line_items().invoice_type(),                          # ACCREC
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
                    'AccountCode': self.line_items().invoice_account_code()
                }],
                'Status': 'SUBMITTED'
            })[0]))

            for man_jour in self.manual_journal_entries():
                line_items_list = []
                for jour_line in man_jour.journal_lines():
                    line_items_list.append({
                        'Description': jour_line.line_description(),
                        'LineAmount': jour_line.line_amount(signal),
                        'AccountCode': jour_line.account_code()
                    })
                response_signal.append(Signal(self.xero.manualjournals.put({
                    'Narration': man_jour.narration(),
                    'JournalLines': line_items_list
                })[0]))

        self.notify_signals(response_signal)
