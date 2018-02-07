XeroCreateInvoice
=================
The XeroCreateInvoice block creates invoices in a Xero account.

Properties
----------
- **consumer_key**: API Consumer Key from Xero application.
- **contact_name**: Name of invoiced customer.
- **line_items**: Information about the transactions.

Inputs
------
- **default**: Any list of signals containing relevant invoice data.

Outputs
-------
- **default**: Create Invoice request response from Xero

Commands
--------
None

***

XeroManualJournals
==================
Create manual journal entries in a Xero account.

Properties
----------
- **consumer_key**: API Consumer Key from Xero application.
- **manual_journal_entries**: Journal entries to add to xero.  Each entry can have multiple lines containing different accounting data.

Inputs
------
- **default**: Any list of signals containing relevant manual journal data.

Outputs
-------
- **default**: Post manual journal response from Xero.

Commands
--------
None

***

XeroUpdateInvoice
=================
Add a payment to a previously created invoice in a Xero account.

Properties
----------
- **consumer_key**: API Consumer Key from Xero application.
- **contact_name**: Name of invoiced customer.
- **invoice_account_code**: Account code to apply the payment to.
- **payment_amount**: Amount paid by customer, should be equal to original invoice amount.

Inputs
------
- **default**: Any list of signals containing relevant payment data.

Outputs
-------
- **default**: Post payment response from Xero application.

Commands
--------
None

Authentication Information
==========================
The Xero API requires RSA-SH1 authentication. The block requires a `privatekey.pem` file inside this block's directory and linked to a public key uploaded to your Xero application. Follow the [Xero Docs](https://developer.xero.com/documentation/api-guides/create-publicprivate-key) to sync up your application.