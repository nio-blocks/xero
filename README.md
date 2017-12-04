XeroPut
=======
Block to add invoices and manual journal entries to a Xero account

Properties
----------
- **consumer_key**: API Key from Xero
- **contact_name**: Name of customer invoiced
- **invoice_type**: Either ACCREC for receivables or ACCPAY for payables
- **line_items**: Information about the transaction

Inputs
------
- **default**: Any list of signals containing relevant accounting data

Outputs
-------
- **default**: Put esponse from Xero invoice and manual journal

Commands
--------
None

Extra Info
----------
The Xero API requires RSA-SH1 authentication.  The block requires a `privatekey.pem` 
file inside this block's directory and linked to a public key uploaded to your Xero application.
Follow the [Xero Docs](https://developer.xero.com/documentation/api-guides/create-publicprivate-key)
to sync up your application.


