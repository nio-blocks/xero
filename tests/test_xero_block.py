from unittest.mock import MagicMock, patch, mock_open

from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase

from ..xero_create_invoice_block import XeroCreateInvoice


class TestXero(NIOBlockTestCase):

    @patch(XeroCreateInvoice.__module__ + '.Xero')
    @patch(XeroCreateInvoice.__module__ + '.PrivateCredentials')
    def test_process_signals(self, patched_creds, patched_xero):
        """Xero is called with proper credentials,
        signal created from put response"""

        blk = XeroCreateInvoice()
        mock_rsa = mock_open(read_data='private_key')
        with patch('builtins.open', mock_rsa):
            self.configure_block(blk, {})
            # define patched_xero return values
            patched_xero.return_value.invoices.put.return_value = \
                [{'a': 1, 'b':2}]

            blk.start()
            blk.process_signals([Signal({
                "amount": 9.99,
                'sales_tax': 1.11,
                'customer': 'Customer Number 1'
            })])
            blk.stop()
            patched_creds.assert_called_once_with(
                '[[XERO_CONSUMER_KEY]]', 'private_key')
            self.assert_num_signals_notified(1)
            self.assertDictEqual(
                self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
                {'a': 1, 'b': 2})

