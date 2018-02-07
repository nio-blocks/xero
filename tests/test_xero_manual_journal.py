from unittest.mock import MagicMock, patch, mock_open

from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase

from ..xero_manual_journal_block import XeroManualJournals


class TestXero(NIOBlockTestCase):

    @patch(XeroManualJournals.__module__ + '.Xero')
    @patch(XeroManualJournals.__module__ + '.PrivateCredentials')
    def test_process_signals(self, patched_creds, patched_xero):
        """Xero is called with proper credentials,
        signal created from put response"""

        blk = XeroManualJournals()
        mock_rsa = mock_open(read_data='private_key')
        with patch('builtins.open', mock_rsa):
            self.configure_block(blk, {})

            blk.start()
            blk.process_signals([Signal({
                'customer': 'Customer Number 1',
                'amount': 9.99,
            })])
            blk.stop()
            patched_creds.assert_called_once_with(
                '[[XERO_CONSUMER_KEY]]', 'private_key')
