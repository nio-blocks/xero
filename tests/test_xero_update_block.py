from unittest.mock import MagicMock, patch, mock_open

from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase

from ..xero_update_invoice_block import XeroUpdateInvoice


class TestXero(NIOBlockTestCase):

    @patch(XeroUpdateInvoice.__module__ + '.Xero')
    @patch(XeroUpdateInvoice.__module__ + '.PrivateCredentials')
    def test_process_signals(self, patched_creds, patched_xero):
        """Xero is called with proper credentials,
        signal created from put response"""

        blk = XeroUpdateInvoice()
        mock_rsa = mock_open(read_data='private_key')
        with patch('builtins.open', mock_rsa):
            self.configure_block(blk, {})
            # define patched_xero return values
            patched_xero.return_value.invoices.put.return_value = \
                [{'InvoiceID': 'invoiceinvoiceinvoice'}]
            patched_xero.return_value.payments.put.return_value = \
                [{'a': 1, 'b':2}]

            blk.start()
            blk.process_signals([Signal({
                'customer': 'Customer Number 1',
                'amount': 9.99,
            })])
            blk.stop()
            patched_creds.assert_called_once_with(
                '[[XERO_CONSUMER_KEY]]', 'private_key')
            self.assert_num_signals_notified(1)
            self.assertDictEqual(
                self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
                {'a': 1, 'b': 2})
